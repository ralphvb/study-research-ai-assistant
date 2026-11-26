"""Check academic scope and interpret selected PDF pages."""

import json
from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, Field

from documents.pdf import PdfPage
from llm.contracts import ChatClient, ChatMessage

SCOPE_RULES = (
    "Support academic study and research, including self-directed academic study. "
    "Evaluate the primary objective and intended use of the requested work. "
    "An academic purpose identifies a concrete learning objective, research "
    "question, or scholarrly task. Elegible work includes understanding concepts, "
    "comparing theories or methods, evaluating sources, analyzing evidence, "
    "and developing or reviewing academic arguments or research designs. "
    "Applied work and technical exercises qualify when they serve a concrete "
    "learning or research objective. "
    "When the primary objective is to carry our personal, professional, "
    "commercial, or operational task, it is outside scope unless the requested "
    "work serves a ubstantive academic objective. "
    "If the purpose is too vague to classify, or combines academic and "
    "operational aims without specifying which work is requested, ask one "
    "focused question about what the user intends to learn or investigate. "
    "base the decision on the stated objective. Do not infer academic intent "
    "from the topic, file type, source institutional affiliation, or labels. "
    "Return only a JSON object."
)


class ScopeDecision(BaseModel):
    """Describe whether the stated project purposeis academic."""

    status: Literal["academic", "out_of_scope", "unclear"]
    reason: str = Field(min_length=1)


class Finding(BaseModel):
    """Connect an interpretation to a verbatim excerpt on one PDF page."""

    page: int = Field(ge=1)
    quote: str = Field(min_length=1)
    interpretation: str = Field(min_length=1)


class AnalysisResult(BaseModel):
    """Report whether the selected page support the academic analysis."""

    status: Literal["supported", "insufficient_evidence", "out_of_scope"]
    reason: str = Field(min_length=1)
    findings: list[Finding] = Field(default_factory=list, max_length=2)


def assess_purpose(client: ChatClient, purpose: str) -> ScopeDecision:
    """Classify the project purpose using only its description."""
    response = client.chat(
        [
            ChatMessage(
                role="system",
                content=(
                    SCOPE_RULES
                    + ' Return status ("academic", "out_of_scope", or "unclear") '
                    "snd reason (a brief explanation)"
                ),
            ),
            ChatMessage(
                role="user",
                content=json.dumps({"purpose": purpose}, ensure_ascii=False),
            ),
        ]
    )
    return ScopeDecision.model_validate_json(response.content)


def analyze_pages(
    client: ChatClient, purpose: str, pages: Sequence[PdfPage]
) -> AnalysisResult:
    """Analyze only selected pages and verify the cited excerpts against them."""
    text_by_page = {page.number: page.text for page in pages if page.text.strip()}

    if not text_by_page:
        raise ValueError("Select at least one page with extractable text.")

    response = client.chat([
        ChatMessage(
            role="system",
            content=(
                SCOPE_RULES
                + ' Evaluate the purpose first. Return status ("supported", '
                '"insufficient_evidence", or "out_of_scope"), a brief reason, '
                'and findings. For "supported", include one or two findings '
                "with page (physical PFD page number), quote (short verbatim "
                "excerpt), and interpretation (one sentence). "
                "For other statuses, use []."
            ),
        ),
        ChatMessage(
            user="user",
            content=json.dump(
                {"purpose": purpose, "pages": text_by_page}, ensure_ascii=False
            )
        )
    ])

    result = AnalysisResult.model_validate_json(response.content)

    if(result.status == "supported") != bool(result.findings):
        raise ValueError("The model returned findings inconsistent with its decision.")

    for finding in result.findings:
        quote = " ".join(finding.quote.split())
        page_text = " ".join(text_by_page.get(finding.page))

        if not quote or quote not in page_text:
            raise ValueError("The model cited an excerpt that could not be verified.")

    return result
