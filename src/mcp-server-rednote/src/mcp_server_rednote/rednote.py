import asyncio
import base64
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Literal

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
    path: str
    expires: float
    httpOnly: bool
    secure: bool
    sameSite: Literal["Lax", "None", "Strict"]


class RedNoteError(Exception):
    """自定义异常类，用于处理小红书相关的错误"""

    message: str

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class RedNote:
    BASE_URL = "https://www.xiaohongshu.com"

    _context: BrowserContext
    _cookies: list[Cookie] | None
    _cookies_ready_event: asyncio.Event

    def __init__(self, context: BrowserContext) -> None:
        self._context = context
        self._cookies = None
        self._cookies_ready_event = asyncio.Event()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._context:
            await self._context.close()

    @classmethod
    async def create(cls, playwright: Playwright, headless: bool = False) -> "RedNote":
        """
        创建 RedNote 实例

        Args:
            playwright (Playwright): Playwright 实例
            headless (bool): 是否以无头模式运行，默认为 False

        Returns:
            RedNote: RedNote 实例
        """
        logger.info(f"Args: headless={headless}")
        browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context()
        instance = cls(context)
        return instance

    @property
    def cookies(self) -> list[Cookie]:
        return self._cookies

    @cookies.setter
    def cookies(self, value: list[Cookie]) -> None:
        self._cookies = value
        self._cookies_ready_event.set()

    async def wait_for_cookies(self, timeout: float) -> list[Cookie]:
        """
        等待 cookies 准备就绪。

        如果 cookies 已经存在，则直接返回它们。
        否则，等待指定的超时时间内 cookies 的准备事件完成。

        Args:
            timeout (float): 等待 cookies 的超时时间（秒）。

        Returns:
            list[Cookie]: 准备就绪的 cookies 列表。

        Raises:
            RedNoteError: 如果在超时时间内 cookies 未准备好，则抛出此异常。
        """
        if self.cookies is not None:
            return self.cookies
        try:
            await asyncio.wait_for(self._cookies_ready_event.wait(), timeout)
            return self.cookies
        except asyncio.TimeoutError:
            raise RedNoteError("等待 cookies 超时")

    async def check_login(self, page: Page) -> bool:
        """检查是否已登录"""
        if self.cookies is None:
            return False
        try:
            user_element = page.locator(".side-bar .user")
            await user_element.wait_for(state="visible", timeout=5000)
            return True
        except Exception as e:
            logger.warning(f"check_login: {e}")
            return False

    async def login(self) -> str:
        page = await self._context.new_page()
        qr_code_base64 = await self._get_qr_code(page)

        # 使用异步函数在后台等待登录
        asyncio.create_task(self._wait_for_login(page))

        # 立即返回二维码
        return qr_code_base64

    async def _wait_for_login(self, page: Page) -> list[Cookie]:
        try:
            # 等待扫码
            status_element = page.locator(".qrcode .status .status-text")
            await status_element.wait_for(state="visible", timeout=60000)
            status_text = (await status_element.text_content()).strip()
            if status_text != "扫码成功":
                raise RedNoteError(f"登录失败: {status_text}")
            # 等待登录
            user_element = page.locator(".side-bar .user")
            await user_element.wait_for(state="visible", timeout=60000)
            # 存储 cookies
            cookies = await self._context.cookies()
            self.cookies = [
                Cookie(
                    name=cookie["name"],
                    value=cookie["value"],
                    domain=cookie["domain"],
                    path=cookie["path"],
                    expires=cookie["expires"],
                    httpOnly=cookie["httpOnly"],
                    secure=cookie["secure"],
                    sameSite=cookie["sameSite"],
                )
                for cookie in cookies
            ]
            return self.cookies
        finally:
            await page.close()

    async def _get_qr_code(self, page: Page) -> str:
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
            raise RedNoteError(f"获取二维码失败: {e}")

    # async def search_notes(self, keyword: str, limit: int = 10) -> list[Note]:
    #     """搜索笔记"""
    #     page = await self.__context.new_page()
    #     # Navigate to search page
    #     logger.info("Navigating to search page")
    #     await page.goto(
    #         f"{self.BASE_URL}/search_result?keyword={urllib.parse.quote(keywords)}"
    #     )
    #     if await self.check_login():
    #         raise RedNoteError("请先登录")


def store_cookies(self) -> None:
    """存储 cookies 到文件 ~/.cmp/rednote/cookies.json"""
    cookies = self.cookies
    # 创建目录
    cookies_dir = Path.home() / ".cmp" / "rednote"
    if not cookies_dir.exists():
        os.makedirs(cookies_dir)
    # 将 cookies 转换为可序列化的字典列表
    cookies_data = [cookie.model_dump() for cookie in cookies]
    # 写入文件
    cookies_file = cookies_dir / "cookies.json"
    with open(cookies_file, "w", encoding="utf-8") as f:
        json.dump(cookies_data, f, ensure_ascii=True, indent=2)
    logger.info(f"Cookies saved to {cookies_file}")


def load_cookies(self) -> None:
    """
    从文件 ~/.cmp/rednote/cookies.json 加载 cookies

    文件结构示例:
    [
        {
            "name": "cookie_name",
            "value": "cookie_value",
            "domain": "example.com"
        },
        ...
    ]
    """
    import json
    from pathlib import Path

    cookies_dir = Path.home() / ".cmp" / "rednote"
    cookies_file = cookies_dir / "cookies.json"
    if not cookies_file.exists():
        logger.info(f"Cookies file not found: {cookies_file}")
        return
    with open(cookies_file, "r", encoding="utf-8") as f:
        cookies_data = json.load(f)
    # 将字典列表转换为 Cookie 对象列表
    self.cookies = [Cookie(**cookie_data) for cookie_data in cookies_data]
