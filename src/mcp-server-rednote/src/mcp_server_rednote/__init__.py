import asyncio
import base64
import logging
import sys
from io import BytesIO

import click
from PIL import Image
from playwright.async_api import async_playwright

from .rednote import RedNote

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--headless", type=bool, default=False, help="")
def main(headless: bool) -> None:
    asyncio.run(async_main(headless))


async def async_main(headless: bool) -> None:
    async with async_playwright() as p:
        rn = await RedNote.create(p, headless=headless)
        async with rn as rednote:
            # 登录
            qr_code_base64 = await rednote.login()
            # 展示二维码
            image_data = base64.b64decode(qr_code_base64)
            image = Image.open(BytesIO(image_data))
            image.show()
            cookies = await rednote.wait_for_cookies(timeout=60)
            image.close()
            for cookie in cookies:
                logger.info(f"Cookie: {cookie.name}=$$$")


if __name__ == "__main__":
    main()
