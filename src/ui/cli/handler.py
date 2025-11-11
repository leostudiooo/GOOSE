#!/usr/bin/env python3

"""
CLI Handler for GOOSE
Provides command-line interface for configuration and upload functionality.
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import Any

from src.model import User
from src.service.main_service import Service


class CLIHandler:
    """
    Command-line interface handler for GOOSE.

    Handles parsing command-line arguments and executing corresponding actions.
    """

    def __init__(self):
        """
        Initialize CLI handler.
        """
        self.service = Service()
        self.logger = logging.getLogger(__name__)

    def parse_args(self, args=None):
        """
        Parse command-line arguments.

        Args:
            args: Optional argument list (for testing)

        Returns:
            Parsed arguments namespace
        """
        parser = argparse.ArgumentParser(
            description="GOOSE - Opens workOut for SEU undErgraduates",
            epilog="Example: ./GOOSE.py --upload -c date_time='2025-05-14 10:00:00' -c route=体育场",
        )

        parser.add_argument(
            "--upload", action="store_true", help="Upload record after applying configuration"
        )

        parser.add_argument(
            "-c",
            "--config",
            action="append",
            dest="configs",
            metavar="KEY=VALUE",
            help="Set configuration value (can be used multiple times). "
            "Supports nested config like 'custom_track.enable=true'",
        )

        parser.add_argument(
            "-v", "--validate", action="store_true", help="Validate configuration only (no upload)"
        )

        return parser.parse_args(args)

    def parse_config_value(self, value_str: str) -> Any:
        """
        Parse configuration value from string.

        Handles various types: boolean, datetime, string.

        Args:
            value_str: String representation of the value

        Returns:
            Parsed value in appropriate type
        """
        # Handle boolean values
        if value_str.lower() in ("true", "yes", "1"):
            return True
        if value_str.lower() in ("false", "no", "0"):
            return False

        # Try to parse as datetime
        datetime_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]
        for fmt in datetime_formats:
            try:
                return datetime.strptime(value_str, fmt)
            except ValueError:
                continue

        # Return as string (remove quotes if present)
        return value_str.strip("\"'")

    def apply_config(self, config_items: list) -> User:
        """
        Apply configuration items to user config.

        Args:
            config_items: List of KEY=VALUE strings

        Returns:
            Updated User object
        """
        # Load current user config
        user = self.service.get_user(User.get_demo())

        for item in config_items:
            if "=" not in item:
                self.logger.warning(f"Invalid config format: {item}, expected KEY=VALUE")
                continue

            key, value_str = item.split("=", 1)
            value = self.parse_config_value(value_str)

            # Handle nested configuration (e.g., custom_track.enable)
            if "." in key:
                parts = key.split(".", 1)
                parent_key = parts[0]
                child_key = parts[1]

                if parent_key == "custom_track":
                    # Get current custom_track
                    custom_track = user.custom_track

                    # Update the nested field
                    if child_key == "enable":
                        custom_track.enable = value
                    elif child_key == "file_path":
                        custom_track.file_path = value
                    else:
                        self.logger.warning(f"Unknown custom_track field: {child_key}")
                        continue

                    user.custom_track = custom_track
                else:
                    self.logger.warning(f"Unknown nested config: {key}")
            else:
                # Direct field update
                if hasattr(user, key):
                    setattr(user, key, value)
                else:
                    self.logger.warning(f"Unknown config key: {key}")

        return user

    def run(self, args=None) -> int:
        """
        Run CLI handler with given arguments.

        Args:
            args: Optional argument list (for testing)

        Returns:
            Exit code (0 for success, 1 for error)
        """
        parsed_args = self.parse_args(args)

        try:
            # Apply configuration if provided
            if parsed_args.configs:
                self.logger.info(f"Applying {len(parsed_args.configs)} configuration item(s)")
                user = self.apply_config(parsed_args.configs)
                self.service.save_user(user)
                self.logger.info("Configuration saved successfully")

            # Validate configuration if requested
            if parsed_args.validate:
                self.logger.info("Validating configuration...")
                self.service.validate()
                self.logger.info("Configuration is valid")

            # Upload if requested
            if parsed_args.upload:
                self.logger.info("Starting upload...")
                self.service.upload()
                self.logger.info("Upload completed successfully!")
                return 0

            # If no action specified but configs provided, just save
            if parsed_args.configs and not parsed_args.validate:
                self.logger.info(
                    "Configuration updated. Use --upload to upload or --validate to check."
                )

            return 0

        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1


def setup_cli_logging():
    """Setup logging for CLI mode."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout)
