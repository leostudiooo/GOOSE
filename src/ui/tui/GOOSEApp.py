from pathlib import Path
import logging

from textual.app import App
from textual.binding import Binding
from textual.widgets import Header, Footer

from ...service.main_service import Service

from .UserConfigPanel import UserConfigPanel
from .ActionPanel import ActionPanel
from .LogViewer import LogViewer
from .NotificationManager import NotificationManager
from .LogManager import LogStore, setup_logging
from .AboutScreen import AboutScreen

class GOOSEApp(App):
    """GOOSE 配置管理与上传应用"""
    
    TITLE = "GOOSE 🪿"
    BINDINGS = [
        Binding("q", "quit", "退出"),
        Binding("s", "save", "保存配置"),
        Binding("v", "validate", "验证配置"),
        Binding("u", "upload", "上传记录"),
        Binding("l", "toggle_logs", "显示日志"),
        Binding("a", "show_about", "关于"),
    ]
    
    # 添加 CSS 样式
    CSS = """
    #action_panel {
        dock: bottom;
        height: auto;
        margin: 1 0;
        padding: 1;
        content-align: center middle;
        background: $surface;
    }
    
    Button {
        margin: 0 1;
        min-width: 15;
    }
    
    UserConfigPanel {
        height: 1fr;
        padding: 1 1;
    }
    
    .panel-title {
        text-align: center;
        text-style: bold;
        width: 100%;
        color: $accent;
        margin-bottom: 1;
    }
    
    .section-title {
        text-style: bold;
        color: $text-muted;
        margin-top: 1;
        margin-bottom: 1;
        border-bottom: solid $primary;
        padding-bottom: 1;
    }
    
    .field-label {
        margin-top: 1;
        margin-bottom: 1;
        color: $text;
    }
    
    .date-time-input {
        width: 100%;
        height: 3;
    }
    
    .date-input {
        width: 1fr;
        margin-right: 1;
    }
    
    .time-input {
        width: 1fr;
        margin-right: 1;
    }
    
    .now-button {
        width: auto;
    }
    
    .save-button {
        margin: 1;
        width: 100%;
    }
    
    #log_viewer {
        width: 100%;
        height: 100%;
        background: $surface;
        display: none;
    }
    
    #log_viewer.visible {
        display: block;
        layer: overlay;
    }

    /* 关于对话框样式 */
    #about-dialog {
        width: 60;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
        margin: 1 2;
    }
    
    #about-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        width: 100%;
        margin-bottom: 1;
        padding-bottom: 1;
        border-bottom: solid $primary;
    }
    
    #about-content {
        margin: 1 0;
        height: auto;
        min-height: 10;
    }
    
    #update-info {
        text-align: center;
        margin: 1 0;
        height: 1;
    }
    
    #update-info.update-available {
        color: $success;
        text-style: bold;
    }
    
    #update-loader {
        margin: 1 0;
    }
    
    #about-buttons {
        width: 100%;
        align-horizontal: center;
        margin-top: 1;
    }
    
    #check-update {
        margin-right: 1;
    }
    
    #close-about {
        margin-left: 1;
    }
    """
    
    def __init__(self):
        # 创建通知管理器
        self.notification_mgr = NotificationManager()
        
        # 设置日志和通知系统
        self.log_store = setup_logging(notification_handler=self.notification_mgr)
        
        super().__init__()
        
        # 初始化业务服务
        self.service = Service(Path("config/"), Path("resources/default_tracks/"))
        
        # 设置通知管理器的app引用
        self.notification_mgr.set_app(self)
        
        # 添加一些初始日志
        logging.info("GOOSE 应用已启动")
        logging.info(f"配置目录: {Path('config/').absolute()}")
        logging.info(f"默认轨迹目录: {Path('resources/default_tracks/').absolute()}")
    
    def compose(self):
        """创建应用布局"""
        yield Header()
        yield UserConfigPanel()
        yield ActionPanel()
        yield Footer()
        yield LogViewer(self.log_store)
    
    def action_save(self) -> None:
        """保存当前配置"""
        panel = self.query_one(UserConfigPanel)
        if panel:
            # 直接调用用户面板的方法
            panel.save_user_config()
            logging.info("用户配置已保存")
    
    def action_validate(self) -> None:
        """验证配置"""
        logging.info("开始验证配置...")
        self.query_one(ActionPanel).validate_config()
    
    def action_upload(self) -> None:
        """上传记录"""
        logging.info("开始上传记录...")
        self.query_one(ActionPanel).upload_record()
    
    def action_toggle_logs(self) -> None:
        """切换日志查看器的显示状态"""
        log_viewer = self.query_one(LogViewer)
        log_viewer.toggle()
    
    def action_show_about(self) -> None:
        """显示关于页面"""
        self.push_screen(AboutScreen())
    
    def get_active_panel(self):
        """获取当前活动的配置面板"""
        return self.query_one(UserConfigPanel)

if __name__ == "__main__":
    app = GOOSEApp()
    app.run()