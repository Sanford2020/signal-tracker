from app.modules.extraction.schemas import ExtractionInput, ExtractionOutput, PROMPT_VERSION


def build_prompt(input_data: ExtractionInput) -> str:
    return (
        f"You are Signal Tracker extraction prompt `{PROMPT_VERSION}`.\n"
        "Return strict JSON with summary, signal_type, entities, keywords, claims, "
        "suggested_tracking_queries, novelty_score, relevance_score, credibility_hint, "
        "risk_hint, opportunity_types, rationale, and language.\n"
        f"Title: {input_data.title}\n"
        f"URL: {input_data.url or ''}\n"
        f"Content: {input_data.content or ''}\n"
        f"Source: {input_data.source.name} ({input_data.source.source_type})\n"
    )
