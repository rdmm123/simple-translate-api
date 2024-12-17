from __future__ import annotations
from playwright.async_api import async_playwright, Playwright, Browser


class Scraper:
    _instance:  Scraper | None = None

    def __init__(self):
        self.playwright: Playwright | None = None
        self._browser: Browser | None = None

    @classmethod
    async def create(cls) -> Scraper:
        if not cls._instance:
            cls._instance = cls()
            cls._instance.playwright = await async_playwright().start()
        return cls._instance

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def get_browser(self) -> Browser:
        if not self._browser:
            self._browser = await self.playwright.chromium.launch(
                headless=True
            )
        return self._browser


async def get_scraper() -> Scraper:
    return await Scraper.create()