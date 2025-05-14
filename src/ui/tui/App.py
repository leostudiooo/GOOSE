from pathlib import Path
from textual.app import App
from textual.binding import Binding
from textual.widgets import Header, Footer

from src.service.main_service import Service

from .ConfigSelector import ConfigSelector
from .UserConfigPanel import UserConfigPanel
from .ActionPanel import ActionPanel


class GOOSEApp(App):
    """GOOSE 配置管理与上传应用"""
    
    TITLE = "GOOSE - 东南大学课外锻炼助手"
    BINDINGS = [
        Binding("q", "quit", "退出"),
        Binding("s", "save", "保存配置"),
        Binding("v", "validate", "验证配置"),
        Binding("u", "upload", "上传记录"),
    ]
    
    def __init__(self):
        super().__init__()
        self.service = Service(Path("config/"), Path("resources/default_tracks/"))
    
    def compose(self):
        """创建应用布局"""
        yield Header()
        yield ConfigSelector()
        yield UserConfigPanel()
        yield ActionPanel()
        yield Footer()
    
    def action_save(self) -> None:
        """保存当前配置"""
        active_panel = self.get_active_panel()
        if active_panel:
            active_panel.save_config()
    
    def action_validate(self) -> None:
        """验证配置"""
        self.query_one(ActionPanel).validate_config()
    
    def action_upload(self) -> None:
        """上传记录"""
        self.query_one(ActionPanel).upload_record()
    
    def get_active_panel(self):
        """获取当前活动的配置面板"""
        for panel in [UserConfigPanel]:
            try:
                panel_instance = self.query_one(f"#{panel.__name__.lower()}")
                if panel_instance.display:
                    return panel_instance
            except:
                pass
        return None

if __name__ == "__main__":
    app = GOOSEApp()
    app.run()