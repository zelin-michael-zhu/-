from bs4 import BeautifulSoup


def clean_html(html: str) -> str:
    return clean_page(html)["text_content"]


def clean_page(html: str) -> dict:
    soup = BeautifulSoup(html or "", "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside"]):
        tag.decompose()
    for tag in soup.find_all(attrs={"aria-label": lambda value: value and "cookie" in value.lower()}):
        tag.decompose()
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    chunks: list[str] = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li", "th", "td"]):
        text = tag.get_text(" ", strip=True)
        if text:
            chunks.append(text)
    text_content = "\n".join(chunks) if chunks else "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
    return {"title": title, "text_content": text_content}
