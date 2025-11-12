import logging

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, LoadingIndicator

from src.infrastructure.exceptions import AppError
from src.service.main_service import Service


class ActionPanel(Horizontal):
    """操作按钮面板"""

    def __init__(self):
        super().__init__(id="action_panel")
        self._service = Service()
        self._is_processing = False

    def compose(self) -> ComposeResult:
        # 添加退出按钮，并设置所有按钮的样式
        yield Button("验证配置", id="validate", variant="primary")
        yield Button("上传记录", id="upload", variant="success")
        yield Button("退出程序", id="quit", variant="error")
        yield LoadingIndicator(id="loading")

    def on_mount(self) -> None:
        """组件挂载时隐藏加载指示器"""
        loading = self.query_one("#loading", LoadingIndicator)
        loading.display = False

    def _set_buttons_disabled(self, disabled: bool) -> None:
        """设置按钮的禁用状态"""
        validate_btn = self.query_one("#validate", Button)
        upload_btn = self.query_one("#upload", Button)
        loading = self.query_one("#loading", LoadingIndicator)
        
        validate_btn.disabled = disabled
        upload_btn.disabled = disabled
        loading.display = disabled

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        # 如果正在处理，忽略按钮点击
        if self._is_processing and event.button.id in ["validate", "upload"]:
            return
            
        if event.button.id == "validate":
            await self.validate_config()
        elif event.button.id == "upload":
            await self.upload_record()
        elif event.button.id == "quit":
            # 退出应用
            self.app.exit()

    async def validate_config(self) -> None:
        """验证配置"""
        self._is_processing = True
        self._set_buttons_disabled(True)
        
        try:
            await self._service.validate()
            logging.info("配置验证通过！")
            self.app.notify("配置验证通过！", severity="information")
        except AppError as e:
            logging.error(e.explain())
        except Exception as e:
            logging.error(f"配置验证失败: {e}")
        finally:
            self._is_processing = False
            self._set_buttons_disabled(False)

    async def upload_record(self) -> None:
        """上传记录"""
        self._is_processing = True
        self._set_buttons_disabled(True)
        
        try:
            await self._service.upload()
            logging.info("记录上传成功！")
            self.app.notify("记录上传成功！", severity="information")
        except AppError as e:
            logging.error(e.explain())
        except Exception as e:
            logging.error(f"上传记录失败: {e}")
        finally:
            self._is_processing = False
            self._set_buttons_disabled(False)
