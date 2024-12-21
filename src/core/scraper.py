from __future__ import annotations
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Playwright, Browser


class Scraper:
    _instance:  Scraper | None = None

    def __init__(self) -> None:
        self.playwright: Playwright | None = None
        self._browser: Browser | None = None

    @classmethod
    async def create(cls) -> Scraper:
        if not cls._instance:
            cls._instance = cls()
        if not cls._instance.playwright:
            cls._instance.playwright = await async_playwright().start()
        return cls._instance

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    @asynccontextmanager
    async def get_browser(self) -> AsyncGenerator[Browser]:
        try:
            if not self._browser:
                assert self.playwright
                self._browser = await self.playwright.chromium.launch(
                    headless=True
                )
            yield self._browser
        finally:
            self._browser.close()
            self._browser = None

