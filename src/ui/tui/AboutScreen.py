import asyncio
import httpx
import logging
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static, LoadingIndicator
from textual.message import Message

# 当前应用版本
CURRENT_VERSION = "0.1.1"

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
                    "本软件不作任何品质担保。这是自由软件；您可以在遵循 GNU 通用公共许可证的条款下重新分发和/或修改它。详见 <https://www.gnu.org/licenses/>。\n\n"
                    "(C) 2025 GOOSE 贡献者们\n"
                    "项目地址: https://github.com/leostudiooo/GOOSE"
                )
            
            yield Label("", id="update-info")
            loading_indicator = LoadingIndicator(id="update-loader")
            loading_indicator.visible = False
            yield loading_indicator
            
            with Container(id="about-buttons"):
                yield Button("检查更新", id="check-update", variant="primary")
                yield Button("关闭", id="close-about", variant="primary")
    
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
                    timeout=10.0
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