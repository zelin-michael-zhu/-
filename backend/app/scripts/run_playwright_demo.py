from app.services.browser_agent.playwright_executor import PlaywrightExecutor


if __name__ == "__main__":
    print(PlaywrightExecutor().run_local_form_demo())
