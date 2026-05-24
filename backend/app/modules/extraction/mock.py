from app.modules.extraction.schemas import ExtractionInput, ExtractionOutput


class MockExtractor:
    model_name = "mock"

    def extract(self, input_data: ExtractionInput) -> tuple[ExtractionOutput, dict]:
        text = f"{input_data.title} {input_data.content or ''}".lower()

        if "hiring" in text and "hardware" in text:
            output = ExtractionOutput(
                summary=(
                    "Example AI appears to be hiring for hardware supply chain roles. "
                    "This may indicate movement into AI hardware operations."
                ),
                signal_type="hiring",
                entities=[{"name": "Example AI", "type": "org"}],
                keywords=["Example AI", "AI hardware", "supply chain hiring", "hardware"],
                claims=[
                    {
                        "text": "Example AI appears to be hiring for hardware supply chain roles.",
                        "claim_type": "inference",
                        "confidence": 0.62,
                    }
                ],
                suggested_tracking_queries=[
                    "Example AI hardware hiring",
                    "Example AI supply chain role",
                ],
                novelty_score=7.0,
                relevance_score=8.0,
                credibility_hint=5.5,
                risk_hint=2.0,
                opportunity_types=["product", "startup", "technical"],
                rationale="This is an early hiring signal tied to a possible product direction.",
                language="en",
            )
        elif "funding" in text or "series" in text:
            output = ExtractionOutput(
                summary="Signal suggests a funding or financing event may be underway.",
                signal_type="funding",
                entities=[{"name": "Unknown company", "type": "org"}],
                keywords=["funding", "investment"],
                claims=[
                    {
                        "text": "A funding event may be in progress.",
                        "claim_type": "rumor",
                        "confidence": 0.5,
                    }
                ],
                suggested_tracking_queries=["funding rumor follow-up"],
                novelty_score=6.5,
                relevance_score=7.5,
                credibility_hint=4.5,
                risk_hint=3.0,
                opportunity_types=["investment_clue", "startup"],
                rationale="Funding language detected in the submitted signal.",
                language="en",
            )
        else:
            output = ExtractionOutput(
                summary=f"Signal captured: {input_data.title}. Further review is recommended.",
                signal_type="other",
                entities=[],
                keywords=[word for word in input_data.title.split()[:3] if word],
                claims=[],
                suggested_tracking_queries=[input_data.title[:80]],
                novelty_score=5.0,
                relevance_score=5.0,
                credibility_hint=4.0,
                risk_hint=2.0,
                opportunity_types=["none"],
                rationale="Generic mock extraction for unmatched signal patterns.",
                language="en",
            )

        raw_output = output.model_dump()
        return output, raw_output
