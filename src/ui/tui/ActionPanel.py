import logging

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button

from src.infrastructure.exceptions import AppError
from src.service.main_service import Service


class ActionPanel(Horizontal):
    """操作按钮面板"""

    def __init__(self):
        super().__init__(id="action_panel")
        self._service = Service()

    def compose(self) -> ComposeResult:
        # 添加退出按钮，并设置所有按钮的样式
        yield Button("验证配置", id="validate", variant="primary")
        yield Button("上传记录", id="upload", variant="success")
        yield Button("退出程序", id="quit", variant="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "validate":
            await self.validate_config()
        elif event.button.id == "upload":
            await self.upload_record()
        elif event.button.id == "quit":
            # 退出应用
            self.app.exit()

    async def validate_config(self) -> None:
        """验证配置"""
        try:
            await self._service.validate()
            logging.info("配置验证通过！")
            self.app.notify("配置验证通过！", severity="information")
        except AppError as e:
            logging.error(e.explain())
        except Exception as e:
            logging.error(f"配置验证失败: {e}")

    async def upload_record(self) -> None:
        """上传记录"""
        try:
            await self._service.upload()
            logging.info("记录上传成功！")
            self.app.notify("记录上传成功！", severity="information")
        except AppError as e:
            logging.error(e.explain())
        except Exception as e:
            logging.error(f"上传记录失败: {e}")
