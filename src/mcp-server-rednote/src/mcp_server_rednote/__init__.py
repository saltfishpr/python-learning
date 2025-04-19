import asyncio
import base64
import logging
import sys
from io import BytesIO

import click
from PIL import Image
from playwright.async_api import async_playwright

from .rednote import RedNote, SearchNoteParams

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--headless", type=bool, default=False, help="")
def main(headless: bool) -> None:
    asyncio.run(async_main(headless))


async def async_main(headless: bool) -> None:
    async with async_playwright() as p:
        async with RedNote(p, headless=headless) as rednote:
            if not await rednote.is_user_logged_in():
                # 登录
                qr_code_base64 = await rednote.login()
                # 展示二维码
                image_data = base64.b64decode(qr_code_base64)
                image = Image.open(BytesIO(image_data))
                image.show()
                await rednote.wait_for_login_success(timeout=60)

            page = await rednote.new_page("https://www.xiaohongshu.com/explore")
            notes = await rednote.search_notes(
                page=page, params=SearchNoteParams(keyword="附近的美食")
            )
            for note in notes:
                print(note.model_dump_json(indent=2))
                print("\n")
            input("Press Enter to exit...")


if __name__ == "__main__":
    main()
