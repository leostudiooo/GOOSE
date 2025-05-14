from textual.widgets import Input, Label, Button, Switch
from textual.containers import VerticalScroll

from textual.app import ComposeResult

class UserConfigPanel(VerticalScroll):
    """用户配置编辑面板"""
    
    def __init__(self):
        super().__init__(id="user_config")
        self._user = None
    
    def compose(self) -> ComposeResult:
        """创建用户配置编辑表单"""
        yield Label("用户配置", classes="panel-title")
        yield Input(id="token", placeholder="Token")
        yield Input(id="date_time", placeholder="日期时间 (YYYY-MM-DD HH:MM:SS)")
        yield Input(id="start_image", placeholder="开始图片路径")
        yield Input(id="finish_image", placeholder="结束图片路径")
        yield Input(id="route", placeholder="路线名称")
        
        # 自定义轨迹配置
        yield Label("自定义轨迹")
        yield Switch(id="custom_track_enable")
        yield Input(id="custom_track_path", placeholder="自定义轨迹文件路径")
        
        yield Button("保存", id="save_user_config")
    
    def on_mount(self) -> None:
        """加载用户配置"""
        self.load_user_config()
    
    def load_user_config(self) -> None:
        """从配置文件加载用户配置"""
        try:
            service = self.app.service
            user = service.get_user()
            self._user = user
            
            # 填充表单
            self.query_one("#token").value = user.token
            self.query_one("#date_time").value = str(user.date_time)
            self.query_one("#start_image").value = user.start_image
            self.query_one("#finish_image").value = user.finish_image
            self.query_one("#route").value = user.route
            self.query_one("#custom_track_enable").value = user.custom_track.enable
            self.query_one("#custom_track_path").value = user.custom_track.file_path
        except Exception as e:
            self.app.notify(f"加载配置失败: {e}", severity="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """保存用户配置"""
        if event.button.id == "save_user_config":
            self.save_user_config()
    
    def save_user_config(self) -> None:
        """保存用户配置到文件"""
        try:
            user = self._user
            user.token = self.query_one("#token").value
            user.date_time = self.query_one("#date_time").value
            user.start_image = self.query_one("#start_image").value
            user.finish_image = self.query_one("#finish_image").value
            user.route = self.query_one("#route").value
            user.custom_track.enable = self.query_one("#custom_track_enable").value
            user.custom_track.file_path = self.query_one("#custom_track_path").value
            
            self.app.service.save_user(user)
            self.app.notify("用户配置已保存", severity="information")
        except Exception as e:
            self.app.notify(f"保存配置失败: {e}", severity="error")

def save_config(self) -> None:
    """保存配置（与save_user_config相同，用于兼容App的调用）"""
    self.save_user_config()