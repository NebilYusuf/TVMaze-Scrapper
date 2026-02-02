import asyncio
import httpx
from typing import Any, Optional

BASE_URL = "https://api.tvmaze.com"

class TVMazeClient:
    def __init__(self, timeout: float = 20.0, max_retries: int = 5):
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers={"User-Agent": "tvmaze-scraper/1.0"},
        )

    async def close(self):
        await self.client.aclose()

    async def _get(self, path: str, params: Optional[dict] = None) -> Any:
        url = f"{BASE_URL}{path}"

        for attempt in range(self.max_retries):
            r = await self.client.get(url, params=params)

            # Rate-limit handling (429)
            if r.status_code == 429:
                await asyncio.sleep(2 ** attempt)
                continue

            r.raise_for_status()
            return r.json()

        raise RuntimeError(f"Rate limited too long: {url}")

    async def get_show(self, show_id: int):
        return await self._get(f"/shows/{show_id}")

    async def get_show_cast(self, show_id: int):
        return await self._get(f"/shows/{show_id}/cast")
    
    async def list_shows_by_page(self, page: int):
        return await self._get("/shows", params={"page": page})

