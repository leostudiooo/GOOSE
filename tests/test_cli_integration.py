#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integration tests for CLI functionality
Tests the complete workflow as described in the issue
"""

import unittest
import subprocess
import tempfile
import shutil
import yaml
from pathlib import Path


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI handler"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_dir = self.temp_dir / "config"
        self.config_dir.mkdir()
        
        # Copy example config
        example_config = Path("config/user_example.yaml")
        if example_config.exists():
            shutil.copy(example_config, self.config_dir / "user.yaml")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_issue_example_workflow(self):
        """
        Test the exact example from the issue:
        ./GOOSE.py --upload -c date_time=2025-05-14 -c route=体育场 
                   -c custom_track.enable=true -c custom_track.file_path="path/to/file"
        
        Note: We test without --upload to avoid network calls
        """
        result = subprocess.run(
            [
                "python", "GOOSE.py",
                "-c", "date_time=2025-05-14",
                "-c", "route=体育场",
                "-c", "custom_track.enable=true",
                "-c", "custom_track.file_path=path/to/file"
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        # Check command executed successfully
        self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")
        
        # Check output messages
        self.assertIn("Applying 4 configuration item(s)", result.stdout)
        self.assertIn("Configuration saved successfully", result.stdout)
        
        # Verify config was updated
        config_path = Path("config/user.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        self.assertEqual(config['route'], '体育场')
        self.assertTrue(config['custom_track']['enable'])
        self.assertEqual(config['custom_track']['file_path'], 'path/to/file')
        # Date should be parsed as datetime
        self.assertIn('2025-05-14', str(config['date_time']))
    
    def test_help_output(self):
        """Test that help output is informative"""
        result = subprocess.run(
            ["python", "GOOSE.py", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("GOOSE - Opens workOut for SEU undErgraduates", result.stdout)
        self.assertIn("--upload", result.stdout)
        self.assertIn("-c", result.stdout)
        self.assertIn("--config", result.stdout)
        self.assertIn("--validate", result.stdout)
    
    def test_multiple_config_updates(self):
        """Test multiple sequential config updates"""
        # First update
        result1 = subprocess.run(
            ["python", "GOOSE.py", "-c", "route=梅园田径场"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        self.assertEqual(result1.returncode, 0)
        
        # Second update
        result2 = subprocess.run(
            ["python", "GOOSE.py", "-c", "custom_track.enable=false"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        self.assertEqual(result2.returncode, 0)
        
        # Verify both changes persisted
        config_path = Path("config/user.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        self.assertEqual(config['route'], '梅园田径场')
        self.assertFalse(config['custom_track']['enable'])


if __name__ == '__main__':
    unittest.main()
