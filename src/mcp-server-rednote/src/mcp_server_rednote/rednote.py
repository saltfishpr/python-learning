import asyncio
import base64
import logging
from datetime import datetime
from typing import List, Optional

from playwright.async_api import BrowserContext, Page, Playwright
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Note(BaseModel):
    title: str
    content: str
    tags: list[str]
    author: str
    link: str
    date: datetime


class Cookie(BaseModel):
    name: str
    value: str
    domain: str


class RedNoteError(Exception):
    """自定义异常类，用于处理小红书相关的错误"""

    message: str

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class RedNote:
    BASE_URL = "https://www.xiaohongshu.com"

    @property
    async def cookies(self) -> List[Cookie]:
        """获取登录后的 cookies"""
        if self.__cookies is None:
            raise RedNoteError("请先登录")
        return await self.__cookies

    def __init__(self) -> None:
        self.__context: BrowserContext = None

    @classmethod
    async def create(cls, playwright: Playwright, headless: bool = False) -> "RedNote":
        logger.info(f"Args: headless={headless}")
        instance = cls()
        browser = await playwright.chromium.launch(headless=headless)
        instance.__context = await browser.new_context()
        return instance

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.__context:
            await self.__context.close()

    async def login(self) -> str:
        page = await self.__context.new_page()
        qr_code_base64 = await self.__get_qr_code(page)
        self.__cookies = self.__wait_for_login(page)
        return qr_code_base64

    async def __wait_for_login(self, page: Page) -> List[Cookie]:
        try:
            # 等待扫码
            status_element = page.locator(".qrcode .status .status-text")
            await status_element.wait_for(state="visible", timeout=60000)
            status_text = (await status_element.text_content()).strip()
            if status_text != "扫码成功":
                raise RedNoteError(f"登录失败: {status_text}")
            # 等待登录
            user_element = page.locator(".side-bar .user")
            await user_element.wait_for(state="visible", timeout=60000)  # 等待60秒
            # 返回 cookies
            cookies = await self.__context.cookies()
            return [
                Cookie(
                    name=cookie["name"],
                    value=cookie["value"],
                    domain=cookie["domain"],
                )
                for cookie in cookies
            ]
        finally:
            await page.close()

    async def __get_qr_code(self, page: Page) -> str:
        try:
            await page.goto(self.BASE_URL + "/explore")

            # 等待二维码元素加载完成
            qrcode_element = page.locator(".qrcode .qrcode-img")
            await qrcode_element.wait_for(state="visible")

            # 获取二维码图片的src属性（如果是<img>标签）
            qr_code_src = await qrcode_element.get_attribute("src")

            # 如果src是data:image/png;base64形式，直接提取base64部分
            if qr_code_src and "data:image" in qr_code_src:
                return qr_code_src.split("base64,")[1]
            # 如果src是URL，需要下载图片并转换
            elif qr_code_src:
                # 使用Playwright下载图片
                image_buffer = await (await page.request.get(qr_code_src)).body()
                return base64.b64encode(image_buffer).decode("utf-8")
            else:
                # 无法获取src时，尝试截图
                screenshot_buffer = await qrcode_element.screenshot()
                return base64.b64encode(screenshot_buffer).decode("utf-8")
        except Exception as e:
            await page.close()
