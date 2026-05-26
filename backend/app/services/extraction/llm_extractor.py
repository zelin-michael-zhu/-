from app.services.extraction.mock_llm_extractor import extract_program


def extract_with_provider(text: str, source_url: str, provider: str = "mock"):
    # Real OpenAI, Claude, and DeepSeek adapters can be plugged in here.
    return extract_program(text, source_url)
