async def fetch_playwright(url: str) -> dict:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        title = await page.title()
        await browser.close()
    return {"url": url, "final_url": url, "http_status": 200, "content_type": "text/html", "title": title, "html": html}
