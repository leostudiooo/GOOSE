import asyncio
import logging
from pathlib import Path

import httpx
from textual.app import ComposeResult
from textual.containers import Container, HorizontalGroup
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Label, LoadingIndicator, Static


def get_version() -> str:
    """Get version from package metadata or pyproject.toml."""
    try:
        # Best practice: Try to get from installed package metadata first
        from importlib.metadata import version
        return version("goose")
    except (ImportError, Exception):
        # Fallback: Read from pyproject.toml when running from source
        try:
            import tomli
            # Find project root by looking for pyproject.toml
            current_file = Path(__file__).resolve()
            for parent in current_file.parents:
                pyproject_path = parent / "pyproject.toml"
                if pyproject_path.exists():
                    with open(pyproject_path, "rb") as f:
                        data = tomli.load(f)
                        return data["project"]["version"]
        except (ImportError, KeyError, FileNotFoundError):
            pass

    # Final fallback if all else fails
    return "unknown"


# 当前应用版本
CURRENT_VERSION = get_version()


class AboutScreen(ModalScreen):
    """关于GOOSE的信息屏幕"""

    BINDINGS = [
        ("escape", "dismiss", "关闭"),
        ("a", "dismiss", "关闭"),
    ]

    class UpdateCheckComplete(Message):
        """更新检查完成的消息"""

        def __init__(self, has_update: bool, latest_version: str, error: str = None) -> None:
            self.has_update = has_update
            self.latest_version = latest_version
            self.error = error
            super().__init__()

    def compose(self) -> ComposeResult:
        with Container(id="about-dialog"):
            yield Label("关于 GOOSE 🪿", id="about-title")

            with Container(id="about-content"):
                yield Static(
                    f"GOOSE - Opens workOut for SEU undErgraduates v{CURRENT_VERSION}\n\n"
                    "这是自由软件；您可以在遵循 GNU 通用公共许可证的条款下重新分发和/或修改它。详见 <https://www.gnu.org/licenses/>。\n\n"
                    "(C) 2025 GOOSE 贡献者们\n"
                    "项目地址: https://github.com/leostudiooo/GOOSE\n\n"
                    """
软件按“原样”（as-is）提供，不附带任何明示或暗示的担保，包括但不限于对特定用途适用性的担保。作者不对因使用本软件产生的任何直接或间接损失、数据丢失、法律责任或其他风险承担责任。

本项目基于学习和研究目的开发。软件不对用户上传数据的真实性、准确性、完整性和合法性负责。用户应对其上传的数据承担全部责任，确保其符合实际情况。

使用本项目即表示你同意上述条款。若不同意，请立即将本项目从你的计算机中删除。"""
                )

            yield Label("", id="update-info")
            loading_indicator = LoadingIndicator(id="update-loader")
            loading_indicator.visible = False
            yield loading_indicator

            with HorizontalGroup(id="about-buttons"):
                yield Button("检查更新", id="check-update", variant="primary")
                yield Button("关闭", id="close-about", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "close-about":
            self.dismiss()
        elif button_id == "check-update":
            self.check_for_updates()

    def action_dismiss(self) -> None:
        """关闭关于页面"""
        self.app.pop_screen()

    def check_for_updates(self) -> None:
        """检查更新"""
        update_info = self.query_one("#update-info")
        update_info.update("正在检查更新...")

        # 显示加载指示器
        loader = self.query_one("#update-loader")
        loader.visible = True

        # 在后台运行检查更新的任务
        asyncio.create_task(self._check_updates_task())

    async def _check_updates_task(self) -> None:
        """异步检查更新任务"""
        has_update = False
        latest_version = CURRENT_VERSION
        error = None

        try:
            # 使用 httpx 访问 GitHub API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.github.com/repos/leostudiooo/GOOSE/releases/latest",
                    headers={"Accept": "application/vnd.github.v3+json"},
                    timeout=10.0,
                )
                response.raise_for_status()

                release_data = response.json()
                latest_version = release_data["tag_name"].lstrip("v")

                # 比较版本号 (简单字符串比较，实际项目可能需要更复杂的版本比较)
                if latest_version != CURRENT_VERSION:
                    has_update = True

        except Exception as e:
            error = str(e)
            logging.error(f"检查更新失败: {error}")

        finally:
            # 发送更新检查完成的消息
            self.post_message(self.UpdateCheckComplete(has_update, latest_version, error))

    def on_about_screen_update_check_complete(self, message: UpdateCheckComplete) -> None:
        """处理更新检查完成的消息"""
        # 隐藏加载指示器
        loader = self.query_one("#update-loader")
        loader.visible = False

        # 更新状态信息
        update_info = self.query_one("#update-info")

        if message.error:
            update_info.update(f"检查更新失败: {message.error}")
        elif message.has_update:
            update_info.update(f"发现新版本: v{message.latest_version}，请前往 GitHub 下载")
            update_info.add_class("update-available")
        else:
            update_info.update("您使用的已经是最新版本")
            update_info.remove_class("update-available")
