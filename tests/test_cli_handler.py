#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for CLI handler functionality
"""

import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
import tempfile
import shutil

from src.ui.cli.handler import CLIHandler
from src.model.user import User, CustomTrack


class TestCLIHandler(unittest.TestCase):
    """Test cases for CLIHandler class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.tracks_dir = Path(self.temp_dir) / "tracks"
        self.config_dir.mkdir()
        self.tracks_dir.mkdir()
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.ui.cli.handler.Service')
    def test_parse_args_upload_flag(self, mock_service):
        """Test parsing --upload flag"""
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        args = handler.parse_args(['--upload'])
        
        self.assertTrue(args.upload)
        self.assertIsNone(args.configs)
        self.assertFalse(args.validate)
    
    @patch('src.ui.cli.handler.Service')
    def test_parse_args_config_single(self, mock_service):
        """Test parsing single -c config"""
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        args = handler.parse_args(['-c', 'route=体育场'])
        
        self.assertEqual(args.configs, ['route=体育场'])
        self.assertFalse(args.upload)
    
    @patch('src.ui.cli.handler.Service')
    def test_parse_args_config_multiple(self, mock_service):
        """Test parsing multiple -c configs"""
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        args = handler.parse_args([
            '-c', 'route=体育场',
            '-c', 'custom_track.enable=true',
            '-c', 'custom_track.file_path=/path/to/file'
        ])
        
        self.assertEqual(len(args.configs), 3)
        self.assertIn('route=体育场', args.configs)
        self.assertIn('custom_track.enable=true', args.configs)
    
    @patch('src.ui.cli.handler.Service')
    def test_parse_args_combined(self, mock_service):
        """Test parsing combined flags"""
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        args = handler.parse_args([
            '--upload',
            '-c', 'route=体育场',
            '-c', 'date_time=2025-05-14 10:00:00'
        ])
        
        self.assertTrue(args.upload)
        self.assertEqual(len(args.configs), 2)
    
    @patch('src.ui.cli.handler.Service')
    def test_parse_config_value_boolean_true(self, mock_service):
        """Test parsing boolean true values"""
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        
        self.assertTrue(handler.parse_config_value('true'))
        self.assertTrue(handler.parse_config_value('True'))
        self.assertTrue(handler.parse_config_value('yes'))
        self.assertTrue(handler.parse_config_value('1'))
    
    @patch('src.ui.cli.handler.Service')
    def test_parse_config_value_boolean_false(self, mock_service):
        """Test parsing boolean false values"""
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        
        self.assertFalse(handler.parse_config_value('false'))
        self.assertFalse(handler.parse_config_value('False'))
        self.assertFalse(handler.parse_config_value('no'))
        self.assertFalse(handler.parse_config_value('0'))
    
    @patch('src.ui.cli.handler.Service')
    def test_parse_config_value_datetime_full(self, mock_service):
        """Test parsing full datetime format"""
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        
        result = handler.parse_config_value('2025-05-14 10:30:45')
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 2025)
        self.assertEqual(result.month, 5)
        self.assertEqual(result.day, 14)
        self.assertEqual(result.hour, 10)
        self.assertEqual(result.minute, 30)
        self.assertEqual(result.second, 45)
    
    @patch('src.ui.cli.handler.Service')
    def test_parse_config_value_datetime_date_only(self, mock_service):
        """Test parsing date-only format"""
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        
        result = handler.parse_config_value('2025-05-14')
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 2025)
        self.assertEqual(result.month, 5)
        self.assertEqual(result.day, 14)
    
    @patch('src.ui.cli.handler.Service')
    def test_parse_config_value_string(self, mock_service):
        """Test parsing string values"""
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        
        self.assertEqual(handler.parse_config_value('体育场'), '体育场')
        self.assertEqual(handler.parse_config_value('"path/to/file"'), 'path/to/file')
        self.assertEqual(handler.parse_config_value("'path/to/file'"), 'path/to/file')
    
    @patch('src.ui.cli.handler.Service')
    def test_apply_config_simple_field(self, mock_service):
        """Test applying simple field configuration"""
        mock_service_instance = mock_service.return_value
        mock_user = User(
            token='test.eyJ1c2VyaWQiOiAiMTIzIn0.token',
            date_time=datetime(2025, 1, 1, 10, 0, 0),
            start_image='start.jpg',
            finish_image='finish.jpg',
            route='梅园田径场',
            custom_track=CustomTrack()
        )
        mock_service_instance.get_user.return_value = mock_user
        
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        result = handler.apply_config(['route=体育场'])
        
        self.assertEqual(result.route, '体育场')
    
    @patch('src.ui.cli.handler.Service')
    def test_apply_config_nested_custom_track_enable(self, mock_service):
        """Test applying nested custom_track.enable configuration"""
        mock_service_instance = mock_service.return_value
        mock_user = User(
            token='test.eyJ1c2VyaWQiOiAiMTIzIn0.token',
            date_time=datetime(2025, 1, 1, 10, 0, 0),
            start_image='start.jpg',
            finish_image='finish.jpg',
            route='梅园田径场',
            custom_track=CustomTrack(enable=False, file_path='')
        )
        mock_service_instance.get_user.return_value = mock_user
        
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        result = handler.apply_config(['custom_track.enable=true'])
        
        self.assertIsInstance(result.custom_track, CustomTrack)
        self.assertTrue(result.custom_track.enable)
    
    @patch('src.ui.cli.handler.Service')
    def test_apply_config_nested_custom_track_file_path(self, mock_service):
        """Test applying nested custom_track.file_path configuration"""
        mock_service_instance = mock_service.return_value
        mock_user = User(
            token='test.eyJ1c2VyaWQiOiAiMTIzIn0.token',
            date_time=datetime(2025, 1, 1, 10, 0, 0),
            start_image='start.jpg',
            finish_image='finish.jpg',
            route='梅园田径场',
            custom_track=CustomTrack()
        )
        mock_service_instance.get_user.return_value = mock_user
        
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        result = handler.apply_config(['custom_track.file_path=path/to/track.json'])
        
        self.assertIsInstance(result.custom_track, CustomTrack)
        self.assertEqual(result.custom_track.file_path, 'path/to/track.json')
    
    @patch('src.ui.cli.handler.Service')
    def test_apply_config_multiple_values(self, mock_service):
        """Test applying multiple configuration values"""
        mock_service_instance = mock_service.return_value
        mock_user = User(
            token='test.eyJ1c2VyaWQiOiAiMTIzIn0.token',
            date_time=datetime(2025, 1, 1, 10, 0, 0),
            start_image='start.jpg',
            finish_image='finish.jpg',
            route='梅园田径场',
            custom_track=CustomTrack()
        )
        mock_service_instance.get_user.return_value = mock_user
        
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        result = handler.apply_config([
            'route=体育场',
            'custom_track.enable=true',
            'custom_track.file_path=path/to/file'
        ])
        
        self.assertEqual(result.route, '体育场')
        self.assertTrue(result.custom_track.enable)
        self.assertEqual(result.custom_track.file_path, 'path/to/file')
    
    @patch('src.ui.cli.handler.Service')
    def test_apply_config_datetime(self, mock_service):
        """Test applying datetime configuration"""
        mock_service_instance = mock_service.return_value
        mock_user = User(
            token='test.eyJ1c2VyaWQiOiAiMTIzIn0.token',
            date_time=datetime(2025, 1, 1, 10, 0, 0),
            start_image='start.jpg',
            finish_image='finish.jpg',
            route='梅园田径场',
            custom_track=CustomTrack()
        )
        mock_service_instance.get_user.return_value = mock_user
        
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        result = handler.apply_config(['date_time=2025-05-14 10:30:45'])
        
        self.assertEqual(result.date_time.year, 2025)
        self.assertEqual(result.date_time.month, 5)
        self.assertEqual(result.date_time.day, 14)
    
    @patch('src.ui.cli.handler.Service')
    def test_run_config_only(self, mock_service):
        """Test running with config only (no upload)"""
        mock_service_instance = mock_service.return_value
        mock_user = User(
            token='test.eyJ1c2VyaWQiOiAiMTIzIn0.token',
            date_time=datetime(2025, 1, 1, 10, 0, 0),
            start_image='start.jpg',
            finish_image='finish.jpg',
            route='梅园田径场',
            custom_track=CustomTrack()
        )
        mock_service_instance.get_user.return_value = mock_user
        
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        exit_code = handler.run(['-c', 'route=体育场'])
        
        self.assertEqual(exit_code, 0)
        mock_service_instance.save_user.assert_called_once()
        mock_service_instance.upload.assert_not_called()
    
    @patch('src.ui.cli.handler.Service')
    def test_run_validate(self, mock_service):
        """Test running with validate flag"""
        mock_service_instance = mock_service.return_value
        
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        exit_code = handler.run(['--validate'])
        
        self.assertEqual(exit_code, 0)
        mock_service_instance.validate.assert_called_once()
    
    @patch('src.ui.cli.handler.Service')
    def test_run_upload(self, mock_service):
        """Test running with upload flag"""
        mock_service_instance = mock_service.return_value
        
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        exit_code = handler.run(['--upload'])
        
        self.assertEqual(exit_code, 0)
        mock_service_instance.upload.assert_called_once()
    
    @patch('src.ui.cli.handler.Service')
    def test_run_config_and_upload(self, mock_service):
        """Test running with config and upload"""
        mock_service_instance = mock_service.return_value
        mock_user = User(
            token='test.eyJ1c2VyaWQiOiAiMTIzIn0.token',
            date_time=datetime(2025, 1, 1, 10, 0, 0),
            start_image='start.jpg',
            finish_image='finish.jpg',
            route='梅园田径场',
            custom_track=CustomTrack()
        )
        mock_service_instance.get_user.return_value = mock_user
        
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        exit_code = handler.run([
            '-c', 'route=体育场',
            '-c', 'custom_track.enable=true',
            '--upload'
        ])
        
        self.assertEqual(exit_code, 0)
        mock_service_instance.save_user.assert_called_once()
        mock_service_instance.upload.assert_called_once()
    
    @patch('src.ui.cli.handler.Service')
    def test_run_error_handling(self, mock_service):
        """Test error handling during run"""
        mock_service_instance = mock_service.return_value
        mock_service_instance.upload.side_effect = Exception("Upload failed")
        
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        exit_code = handler.run(['--upload'])
        
        self.assertEqual(exit_code, 1)
    
    @patch('src.ui.cli.handler.Service')
    def test_invalid_config_format(self, mock_service):
        """Test handling invalid config format (missing =)"""
        mock_service_instance = mock_service.return_value
        mock_user = User(
            token='test.eyJ1c2VyaWQiOiAiMTIzIn0.token',
            date_time=datetime(2025, 1, 1, 10, 0, 0),
            start_image='start.jpg',
            finish_image='finish.jpg',
            route='梅园田径场',
            custom_track=CustomTrack()
        )
        mock_service_instance.get_user.return_value = mock_user
        
        handler = CLIHandler(self.config_dir, self.tracks_dir)
        # Should not crash, just log warning
        result = handler.apply_config(['invalid_config'])
        
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
