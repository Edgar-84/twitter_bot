import json
from http import HTTPStatus

import aiohttp
from selectolax.parser import HTMLParser


class Youtube:
    def __init__(self):
        self.base_url = "https://www.youtube.com/results"

    async def get_url(self, query: str):
        url = await self._search_youtube(query=query)
        if url:
            return url
        return await self.get_url(query=query)

    async def _search_youtube(self, query: str) -> str | None:
        """Search YouTube videos by keyword without API."""

        try:
            html = await self.get_youtube_response(query)

            parser = HTMLParser(html)
            main_script = self._get_json_from_scripts(parser)
            video = main_script["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"][
                "contents"
            ][0]["itemSectionRenderer"]["contents"][1]["videoRenderer"]

            return f"https://www.youtube.com/watch?v={video['videoId']}"
        except Exception:
            return None

    async def get_youtube_response(self, _query: str) -> str:
        """
        Get the HTML response of a YouTube search page.

        Params:
            _query: The search query.
        """
        params = {"search_query": _query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params, headers=headers) as response:
                if response.status != HTTPStatus.OK:
                    raise Exception(f"Failed to fetch YouTube data. Status code: {response.status}")
                return await response.text()

    @staticmethod
    def _get_json_from_scripts(_parser: HTMLParser) -> dict:
        """
        Extracts the main JSON object and the player info JSON object from the HTML content of the video page.
        Params:
            _parser: The HTML parser object containing the video page's HTML content.
        """
        MAIN_SCRIPT_START_TEXT = "var ytInitialData = "
        main_json = {}
        scripts = _parser.css("script")
        for script in scripts:
            text = script.text()
            if main_json:
                break
            if not main_json and MAIN_SCRIPT_START_TEXT in text:
                main_json = json.loads(text.split(MAIN_SCRIPT_START_TEXT)[1].strip(";"))
        return main_json
