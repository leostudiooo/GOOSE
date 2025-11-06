from textual.widgets import Input, Label, Button, Switch
from textual.containers import VerticalScroll

from textual.app import ComposeResult
from .DateTimeInput import DateTimeInput
from .RouteSelector import RouteSelector
from .CustomTrack import CustomTrack

from pathlib import Path
from src.service.main_service import Service

import logging

class UserConfigPanel(VerticalScroll):
    """用户配置编辑面板"""
    
    def __init__(self):
        super().__init__(id="user_config")
        self._user = None
        # 直接创建Service实例，不依赖app
        self._service = Service()
    
    def compose(self) -> ComposeResult:
        """创建用户配置编辑表单"""
        yield Label("用户配置", classes="panel-title")
        yield Input(id="token", placeholder="Token")
        yield DateTimeInput(id_prefix="date_time")
        yield Input(id="start_image", placeholder="开始图片路径")
        yield Input(id="finish_image", placeholder="结束图片路径")
        
        # 使用路线选择器组件
        yield RouteSelector(id="route")
        
        # 使用自定义轨迹组件
        yield CustomTrack(id="custom_track")
        
        yield Button("保存", id="save_user_config")
    
    def on_mount(self) -> None:
        """加载用户配置"""
        self.load_user_config()
    
    def load_user_config(self) -> None:
        """从配置文件加载用户配置"""
        try:
            # 使用本地service实例
            user = self._service.get_user()
            self._user = user
            
            # 填充表单
            self.query_one("#token").value = user.token

            date_time_input = self.query_one(DateTimeInput)
            date_time_input.set_value(user.date_time)
            
            self.query_one("#start_image").value = user.start_image
            self.query_one("#finish_image").value = user.finish_image
            self.query_one("#route").value = user.route
            
            # 使用自定义轨迹组件的set_config方法设置值
            custom_track = self.query_one("#custom_track", CustomTrack)
            custom_track.set_config(user.custom_track.enable, user.custom_track.file_path)

            logging.info("用户配置已加载")
            if hasattr(self.app, 'notify'):
                self.app.notify("用户配置已加载", severity="information")
            
        except Exception as e:
            logging.error(f"加载用户配置失败: {e}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """保存用户配置"""
        if event.button.id == "save_user_config":
            self.save_user_config()
    
    def save_user_config(self) -> None:
        """保存用户配置到文件"""
        try:
            user = self._user
            user.token = self.query_one("#token").value
            date_time_input = self.query_one(DateTimeInput)
            user.date_time = date_time_input.get_value()
            user.start_image = self.query_one("#start_image").value
            user.finish_image = self.query_one("#finish_image").value
            user.route = self.query_one("#route").value
            
            # 从自定义轨迹组件获取配置
            custom_track_config = self.query_one("#custom_track").get_config()
            user.custom_track.enable = custom_track_config["enable"]
            user.custom_track.file_path = custom_track_config["file_path"]
            
            # 使用本地service保存
            self._service.save_user(user)
            
            logging.info("用户配置已保存")
            if hasattr(self.app, 'notify'):
                self.app.notify("用户配置已保存", severity="information")
                
        except Exception as e:
            logging.error(f"保存用户配置失败: {e}")

    def save_config(self) -> None:
        """保存配置（与save_user_config相同，用于兼容App的调用）"""
        self.save_user_config()