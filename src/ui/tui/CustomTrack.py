from textual.widgets import Switch, Input, Static, Label
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from textual import on

class CustomTrack(Vertical):
    """自定义轨迹配置组件"""
    
    DEFAULT_CSS = """
    CustomTrack {
        height: auto;
        margin: 1;
    }
    
    .switch-container {
        height: 3;
        align-vertical: middle;
        margin-bottom: 1;
    }
    
    CustomTrack Label {
        width: auto;
        margin: 1 0;
        text-style: bold;
    }
    
    CustomTrack Input {
        margin: 1 1;
    }
    
    .hidden {
		display: none;
	}
    """
    
    def __init__(self, id="custom_track"):
        super().__init__(id=id)
        self._enable = False
        self._path = ""
    
    def compose(self) -> ComposeResult:
        """创建自定义轨迹配置表单"""
        with Horizontal(classes="switch-container"):
            yield Label("启用自定义轨迹", id=f"{self.id}_switch_label")
            yield Switch(id=f"{self.id}_enable", value=self._enable)
        
        # 默认隐藏文件路径输入框
        yield Input(id=f"{self.id}_path", placeholder="自定义轨迹文件路径", 
                   value=self._path, classes="hidden" if not self._enable else "")
    
    @on(Switch.Changed)
    def on_switch_changed(self, event: Switch.Changed) -> None:
        """响应开关状态变化"""
        if event.switch.id == f"{self.id}_enable":
            self._enable = event.value
            path_input = self.query_one(f"#{self.id}_path")
            
            # 根据开关状态显示或隐藏输入框和标签
            if event.value:
                path_input.remove_class("hidden")
            else:
                path_input.add_class("hidden")
    
    @property
    def enable(self) -> bool:
        """获取启用状态"""
        return self._enable
    
    @enable.setter
    def enable(self, value: bool) -> None:
        """设置启用状态"""
        self._enable = value
        switch = self.query_one(f"#{self.id}_enable", Switch)
        switch.value = value
        
        # 更新输入框和标签可见性
        path_input = self.query_one(f"#{self.id}_path", Input)
        if value:
            path_input.remove_class("hidden")
        else:
            path_input.add_class("hidden")
    
    @property
    def path(self) -> str:
        """获取文件路径"""
        return self._path
    
    @path.setter
    def path(self, value: str) -> None:
        """设置文件路径"""
        self._path = value
        path_input = self.query_one(f"#{self.id}_path", Input)
        path_input.value = value
    
    def get_config(self) -> dict:
        """获取配置信息"""
        return {
            "enable": self.query_one(f"#{self.id}_enable").value,
            "file_path": self.query_one(f"#{self.id}_path").value
        }
    
    def set_config(self, enable: bool, path: str) -> None:
        """设置配置信息"""
        self.enable = enable
        self.path = path