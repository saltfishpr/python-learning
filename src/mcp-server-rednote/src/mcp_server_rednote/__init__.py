import asyncio
import logging
import sys

import click
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
            logger.info("开始登录")
            qr_code_base64 = await rednote.login()
            logger.info("登录成功")

            # 显示二维码
            logger.info("请扫描二维码登录")
            # PIL 展示二维码
            import base64
            from io import BytesIO

            from PIL import Image

            image_data = base64.b64decode(qr_code_base64)
            image = Image.open(BytesIO(image_data))
            image.show()
            cookies = await rednote.cookies
            image.close()
            for cookie in cookies:
                logger.info(f"Cookie: {cookie.name}={cookie.value}")


if __name__ == "__main__":
    main()
