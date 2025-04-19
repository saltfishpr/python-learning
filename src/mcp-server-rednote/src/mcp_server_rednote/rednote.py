import asyncio
import base64
import logging
import os
from datetime import datetime

from playwright.async_api import Page, Playwright
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Note(BaseModel):
    title: str
    content: str
    tags: list[str]
    author: str
    link: str
    date: datetime


class RedNoteError(Exception):
    """自定义异常类，用于处理小红书相关的错误"""

    message: str

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class RedNote:
    BASE_URL = "https://www.xiaohongshu.com"

    def __init__(
        self,
        playwright: Playwright,
        headless: bool = False,
        storage_state_path: str = "~/.mcp/rednote/state.json",
    ):
        """
        初始化 Rednote 类。

        Args:
            playwright (Playwright): Playwright 库的一个实例，用于浏览器自动化。
            headless (bool, 可选): 决定浏览器是否在无头模式下运行。默认为 False。
            storage_state_path (str, 可选): 用于会话持久性的存储状态文件的路径。
                默认为 "~/.mcp/rednote/state.json"。

        Attributes:
            _playwright (Playwright): Playwright 库的实例。
            _headless (bool): 指示浏览器是否在无头模式下运行。
            _storage_state_path (str): 存储状态文件的展开路径。
            _event_login_success (asyncio.Event): 用于标记成功登录的事件。
        """
        logger.info(
            f"Args: headless={headless}, storage_state_path={storage_state_path}"
        )
        self._playwright = playwright
        self._headless = headless
        self._storage_state_path = os.path.expanduser(storage_state_path)
        os.makedirs(os.path.dirname(self._storage_state_path), exist_ok=True)
        self.__event_login_success: asyncio.Event = asyncio.Event()

    async def __aenter__(self):
        self._browser = await self._playwright.chromium.launch(headless=self._headless)
        try:
            self._context = await self._browser.new_context(
                storage_state=self._storage_state_path
            )
        except Exception as e:
            logger.warning(f"Failed to load storage state: {e}")
            self._context = await self._browser.new_context()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._context:
            await self._context.storage_state(path=self._storage_state_path)
            await self._context.close()
            await self._browser.close()

    async def check_login(self, page: Page) -> bool:
        """
        通过检查用户元素是否可见来判断是否已登录

        Args:
            page (Page): Playwright 页面对象

        Returns:
            bool: 是否已登录
        """
        try:
            user_element = page.locator(".side-bar .user")
            await user_element.wait_for(state="visible", timeout=5000)
            return True
        except Exception as e:
            logger.warning(f"check_login: {e}")
            return False

    async def wait_for_login_success(self, timeout: float) -> None:
        """
        等待登录成功的事件

        Args:
            timeout (float): 超时时间，单位为秒
        """
        try:
            await asyncio.wait_for(self.__event_login_success.wait(), timeout)
        except asyncio.TimeoutError:
            raise RedNoteError("登录超时，请重新扫码登录")

    async def login(self) -> str:
        page = await self._context.new_page()
        await page.goto(self.BASE_URL + "/explore")
        qr_code_base64 = await self.__get_qr_code(page)
        # 使用异步函数在后台等待登录
        asyncio.create_task(self.__wait_for_login(page))
        # 立即返回二维码
        return qr_code_base64

    async def __get_qr_code(self, page: Page) -> str:
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
            async with page.request.get(qr_code_src) as response:
                image_buffer = await response.body()
                return base64.b64encode(image_buffer).decode("utf-8")
        else:
            # 无法获取src时，尝试截图
            screenshot_buffer = await qrcode_element.screenshot()
            return base64.b64encode(screenshot_buffer).decode("utf-8")

    async def __wait_for_login(self, page: Page) -> None:
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
            # 登录成功
            await self._context.storage_state(path=self._storage_state_path)
            self.__event_login_success.set()
        except Exception as e:
            logger.error(f"Login error: {e}")
        finally:
            await page.close()

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
