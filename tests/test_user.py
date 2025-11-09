import base64
import json
import unittest
from datetime import datetime

from pydantic import ValidationError

from src.infrastructure.exceptions import InvalidTokenError
from src.model.user import User, CustomTrack


class TestUserInitialization(unittest.TestCase):
    def test_required_fields(self):
        """测试必填字段是否存在且类型正确"""
        user = User(
            token="valid.eyJ1c2VyaWQiOiAiMTIzIn0.token",
            date_time="2023-10-01 12:00:00",
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1",
        )

        self.assertIsInstance(user.token, str)
        self.assertIsInstance(user.date_time, datetime)
        self.assertEqual(user.start_image, "start.jpg")
        self.assertEqual(user.finish_image, "finish.jpg")
        self.assertEqual(user.route, "route1")


class TestTokenValidator(unittest.TestCase):
    def test_invalid_token_parts(self):
        """测试token部分数量不正确"""
        with self.assertRaises(InvalidTokenError) as cm:
            User(
                token="invalid.token",
                date_time=datetime.now(),
                start_image="start.jpg",
                finish_image="finish.jpg",
                route="route1",
            ).decode_token()
        self.assertIn("必须包含", str(cm.exception))

    def test_invalid_base64(self):
        """测试无法解码的token中间部分"""
        invalid_payload = base64.b64encode(b"{invalid_json").decode().rstrip("=")
        token = f"header.{invalid_payload}.signature"

        with self.assertRaises(InvalidTokenError) as cm:
            User(
                token=token,
                date_time=datetime.now(),
                start_image="start.jpg",
                finish_image="finish.jpg",
                route="route1",
            ).decode_token()
        self.assertIn("无法被解码", str(cm.exception))

    def test_token_with_base64url_characters(self):                                                                   
        """测试带有base64url特殊字符的token"""                                                                        
        payload = (                                                                                                   
            base64.urlsafe_b64encode('{"name": "灵感菇", "userid": "123"}'.encode())                                  
            .decode()                                                                                                 
            .rstrip("=")                                                                                              
        )                                                                                                             
        valid_data = {                                                                                                
            "token": f"header.{payload}.sign",                                                                        
            "date_time": datetime.now().isoformat(),                                                                  
            "start_image": "start.jpg",                                                                               
            "finish_image": "finish.jpg",                                                                             
            "route": "route1",                                                                                        
        }                                                                                                             
        user = User.model_validate(valid_data)                                                                        
        self.assertEqual(user.student_id, "123") 

    def test_missing_userid(self):
        """测试token中缺少userid字段"""
        payload = (
            base64.b64encode(json.dumps({"name": "test"}).encode()).decode().rstrip("=")
        )
        token = f"header.{payload}.signature"

        with self.assertRaises(InvalidTokenError) as cm:
            User(
                token=token,
                date_time=datetime.now(),
                start_image="start.jpg",
                finish_image="finish.jpg",
                route="route1",
            ).decode_token()
        self.assertIn("没有userid字段", str(cm.exception))

    def test_valid_token(self):
        """测试有效token解析"""
        payload = (
            base64.b64encode(json.dumps({"userid": "456"}).encode())
            .decode()
            .rstrip("=")
        )
        token = f"header.{payload}.signature"

        user = User(
            token=token,
            date_time=datetime.now(),
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1",
        )
        self.assertEqual(user.student_id, "456")


class TestCustomTrackValidator(unittest.TestCase):
    def test_custom_track_object(self):
        """测试直接传入CustomTrack对象"""
        ct = CustomTrack(enable=True, file_path="/custom/path")
        user = User(
            token="valid.eyJ1c2VyaWQiOiAiMTIzIn0.token",
            date_time=datetime.now(),
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1",
            custom_track=ct,
        )
        self.assertIs(user.custom_track, ct)


class TestStudentIdProperty(unittest.TestCase):
    def test_student_id_extraction(self):
        """测试从token中正确提取userid"""
        payload = (
            base64.b64encode(json.dumps({"userid": "789"}).encode())
            .decode()
            .rstrip("=")
        )
        token = f"header.{payload}.signature"

        user = User(
            token=token,
            date_time=datetime.now(),
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1",
        )
        self.assertEqual(user.student_id, "789")


class TestCustomTrackPathProperty(unittest.TestCase):
    def test_enabled_custom_track(self):
        """测试启用的自定义轨迹路径"""
        ct = CustomTrack(enable=True, file_path="/new/path")
        user = User(
            token="valid.eyJ1c2VyaWQiOiAiMTIzIn0.token",
            date_time=datetime.now(),
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1",
            custom_track=ct,
        )
        self.assertEqual(user.custom_track_path, "/new/path")

    def test_disabled_custom_track(self):
        """测试未启用的自定义轨迹路径"""
        ct = CustomTrack(enable=False, file_path="/no/path")
        user = User(
            token="valid.eyJ1c2VyaWQiOiAiMTIzIn0.token",
            date_time=datetime.now(),
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1",
            custom_track=ct,
        )
        self.assertEqual(user.custom_track_path, "")


# 在原有测试类中添加以下新测试类
class TestModelValidate(unittest.TestCase):
    def test_valid_dict_input(self):
        """测试通过字典输入构造有效模型"""
        valid_data = {
            "token": "valid.eyJ1c2VyaWQiOiAiMTIzIn0=.token",
            "date_time": "2023-10-01 12:00:00",
            "start_image": "start.jpg",
            "finish_image": "finish.jpg",
            "route": "route2",
        }
        user = User.model_validate(valid_data)
        self.assertEqual(user.student_id, "123")
        self.assertIsInstance(user.custom_track, CustomTrack)

    def test_token_validation_via_dict(self):
        """测试通过字典输入时的token验证"""
        invalid_data = {
            "token": "bad_token",
            "date_time": datetime.now(),
            "start_image": "start.jpg",
            "finish_image": "finish.jpg",
            "route": "route1",
        }
        with self.assertRaises(InvalidTokenError) as cm:
            User.model_validate(invalid_data).decode_token()
        self.assertIn("必须包含", str(cm.exception))

    def test_custom_track_dict_input(self):
        """测试直接传入CustomTrack字典结构"""
        test_data = {
            "token": "valid.eyJ1c2VyaWQiOiAiMTIzIn0=.token",
            "date_time": datetime.now().isoformat(),
            "start_image": "start.jpg",
            "finish_image": "finish.jpg",
            "route": "route1",
            "custom_track": {"enable": True, "file_path": "/data/special.csv"},
        }
        user = User.model_validate(test_data)
        self.assertIsInstance(user.custom_track, CustomTrack)
        self.assertTrue(user.custom_track.enable)
        self.assertEqual(user.custom_track.file_path, "/data/special.csv")

    def test_mixed_custom_track_types(self):
        """测试混合类型custom_track输入"""
        # 测试无效类型
        invalid_data = {
            "token": "invalid.token",
            "date_time": datetime.now(),
            "start_image": "start.jpg",
            "finish_image": "finish.jpg",
            "route": "route1",
            "custom_track": 123,  # 错误类型
        }
        with self.assertRaises(ValidationError):
            User.model_validate(invalid_data)

    def test_nested_token_validation(self):
        """测试嵌套的token验证逻辑"""
        # 有效负载缺少userid
        payload = (
            base64.b64encode(json.dumps({"group": "A"}).encode()).decode().rstrip("=")
        )
        invalid_data = {
            "token": f"header.{payload}.sign",
            "date_time": datetime.now().isoformat(),
            "start_image": "start.jpg",
            "finish_image": "finish.jpg",
            "route": "route1",
        }
        with self.assertRaises(InvalidTokenError) as cm:
            User.model_validate(invalid_data).decode_token()
        self.assertIn("没有userid字段", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
