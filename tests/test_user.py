import unittest
import json
import base64
from datetime import datetime
from src.model.user import User, CustomTrack


class TestUserInitialization(unittest.TestCase):
    def test_required_fields(self):
        """测试必填字段是否存在且类型正确"""
        user = User(
            token="valid.eyJ1c2VyaWQiOiAiMTIzIn0.token",
            date_time="2023-10-01 12:00:00",
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1"
        )

        self.assertIsInstance(user.token, str)
        self.assertIsInstance(user.date_time, datetime)
        self.assertEqual(user.start_image, "start.jpg")
        self.assertEqual(user.finish_image, "finish.jpg")
        self.assertEqual(user.route, "route1")


class TestTokenValidator(unittest.TestCase):
    def test_invalid_token_parts(self):
        """测试token部分数量不正确"""
        with self.assertRaises(ValueError) as cm:
            User(
                token="invalid.token",
                date_time=datetime.now(),
                start_image="start.jpg",
                finish_image="finish.jpg",
                route="route1"
            )
        self.assertIn("必须包含三个部分", str(cm.exception))

    def test_invalid_base64(self):
        """测试无法解码的token中间部分"""
        invalid_payload = base64.b64encode(b"{invalid_json").decode().rstrip("=")
        token = f"header.{invalid_payload}.signature"

        with self.assertRaises(ValueError) as cm:
            User(
                token=token,
                date_time=datetime.now(),
                start_image="start.jpg",
                finish_image="finish.jpg",
                route="route1"
            )
        self.assertIn("无法被解码", str(cm.exception))

    def test_missing_userid(self):
        """测试token中缺少userid字段"""
        payload = base64.b64encode(json.dumps({"name": "test"}).encode()).decode().rstrip("=")
        token = f"header.{payload}.signature"

        with self.assertRaises(ValueError) as cm:
            User(
                token=token,
                date_time=datetime.now(),
                start_image="start.jpg",
                finish_image="finish.jpg",
                route="route1"
            )
        self.assertIn("没有userid字段", str(cm.exception))

    def test_valid_token(self):
        """测试有效token解析"""
        payload = base64.b64encode(json.dumps({"userid": "456"}).encode()).decode().rstrip("=")
        token = f"header.{payload}.signature"

        user = User(
            token=token,
            date_time=datetime.now(),
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1"
        )
        self.assertEqual(user.student_id, "456")


class TestCustomTrackValidator(unittest.TestCase):
    def test_empty_string_conversion(self):
        """测试空字符串转换为默认CustomTrack"""
        user = User(
            token="valid.eyJ1c2VyaWQiOiAiMTIzIn0.token",
            date_time=datetime.now(),
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1",
            custom_track=""
        )
        self.assertIsInstance(user.custom_track, CustomTrack)
        self.assertFalse(user.custom_track.enable)
        self.assertEqual(user.custom_track.file_path, "")

    def test_non_empty_string_conversion(self):
        """测试非空字符串转换为启用的CustomTrack"""
        user = User(
            token="valid.eyJ1c2VyaWQiOiAiMTIzIn0.token",
            date_time=datetime.now(),
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1",
            custom_track="/path/to/file"
        )
        self.assertIsInstance(user.custom_track, CustomTrack)
        self.assertTrue(user.custom_track.enable)
        self.assertEqual(user.custom_track.file_path, "/path/to/file")

    def test_custom_track_object(self):
        """测试直接传入CustomTrack对象"""
        ct = CustomTrack(enable=True, file_path="/custom/path")
        user = User(
            token="valid.eyJ1c2VyaWQiOiAiMTIzIn0.token",
            date_time=datetime.now(),
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1",
            custom_track=ct
        )
        self.assertIs(user.custom_track, ct)


class TestStudentIdProperty(unittest.TestCase):
    def test_student_id_extraction(self):
        """测试从token中正确提取userid"""
        payload = base64.b64encode(json.dumps({"userid": "789"}).encode()).decode().rstrip("=")
        token = f"header.{payload}.signature"

        user = User(
            token=token,
            date_time=datetime.now(),
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1"
        )
        self.assertEqual(user.student_id, "789")


class TestCustomTrackPathProperty(unittest.TestCase):
    def test_legacy_string_path(self):
        """测试旧版字符串路径兼容性"""
        user = User(
            token="valid.eyJ1c2VyaWQiOiAiMTIzIn0.token",
            date_time=datetime.now(),
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1",
            custom_track="/old/path"
        )
        self.assertEqual(user.custom_track_path, "/old/path")

    def test_enabled_custom_track(self):
        """测试启用的自定义轨迹路径"""
        ct = CustomTrack(enable=True, file_path="/new/path")
        user = User(
            token="valid.eyJ1c2VyaWQiOiAiMTIzIn0.token",
            date_time=datetime.now(),
            start_image="start.jpg",
            finish_image="finish.jpg",
            route="route1",
            custom_track=ct
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
            custom_track=ct
        )
        self.assertEqual(user.custom_track_path, "")


if __name__ == "__main__":
    unittest.main()
