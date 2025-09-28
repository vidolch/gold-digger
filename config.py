#!/usr/bin/env python3
"""
Configuration module for Gold Digger
Loads settings from environment variables with sensible defaults.
"""

import os
import logging
from pathlib import Path
from typing import Union, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration class that loads all settings from environment variables."""

    def __init__(self):
        """Initialize configuration with environment variables."""
        self._setup_logging()

    # ==========================================================================
    # OLLAMA CONFIGURATION
    # ==========================================================================

    @property
    def ollama_host(self) -> str:
        """Ollama server host and port."""
        return os.getenv('OLLAMA_HOST', 'http://localhost:11434')

    @property
    def ollama_model(self) -> str:
        """AI model to use for analysis."""
        return os.getenv('OLLAMA_MODEL', 'gpt-oss:20b')

    @property
    def ollama_timeout(self) -> int:
        """Ollama request timeout in seconds."""
        return int(os.getenv('OLLAMA_TIMEOUT', '120'))

    # ==========================================================================
    # DATABASE CONFIGURATION
    # ==========================================================================

    @property
    def database_path(self) -> str:
        """SQLite database file path."""
        return os.getenv('DATABASE_PATH', 'gold_prices.db')

    # ==========================================================================
    # TRADING ANALYSIS CONFIGURATION
    # ==========================================================================

    @property
    def default_interval(self) -> str:
        """Default analysis interval."""
        return os.getenv('DEFAULT_INTERVAL', '15m')

    @property
    def default_analysis_hours(self) -> int:
        """Default hours of data to analyze."""
        return int(os.getenv('DEFAULT_ANALYSIS_HOURS', '24'))

    @property
    def prompt_file(self) -> str:
        """Trading prompt template file path."""
        return os.getenv('PROMPT_FILE', 'trading_prompt.txt')

    # ==========================================================================
    # DATA FETCHING CONFIGURATION
    # ==========================================================================

    @property
    def default_fetch_days(self) -> int:
        """Default number of days to fetch."""
        return int(os.getenv('DEFAULT_FETCH_DAYS', '14'))

    @property
    def gold_symbol(self) -> str:
        """Gold symbol to track."""
        return os.getenv('GOLD_SYMBOL', 'GC=F')

    @property
    def yfinance_timeout(self) -> int:
        """Yahoo Finance request timeout in seconds."""
        return int(os.getenv('YFINANCE_TIMEOUT', '30'))

    # ==========================================================================
    # LOGGING CONFIGURATION
    # ==========================================================================

    @property
    def log_level(self) -> str:
        """Log level."""
        return os.getenv('LOG_LEVEL', 'INFO').upper()

    @property
    def log_format(self) -> str:
        """Log format string."""
        return os.getenv('LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')

    @property
    def enable_file_logging(self) -> bool:
        """Enable file logging."""
        return os.getenv('ENABLE_FILE_LOGGING', 'false').lower() == 'true'

    @property
    def log_file(self) -> str:
        """Log file path."""
        return os.getenv('LOG_FILE', 'gold_digger.log')

    # ==========================================================================
    # EXPORT CONFIGURATION
    # ==========================================================================

    @property
    def export_dir(self) -> str:
        """Export directory for CSV files."""
        return os.getenv('EXPORT_DIR', 'exports')

    @property
    def export_include_volume(self) -> bool:
        """Include volume in exports."""
        return os.getenv('EXPORT_INCLUDE_VOLUME', 'true').lower() == 'true'

    # ==========================================================================
    # API CONFIGURATION
    # ==========================================================================

    @property
    def api_delay(self) -> float:
        """Rate limiting delay between API calls."""
        return float(os.getenv('API_DELAY', '1.0'))

    @property
    def max_retries(self) -> int:
        """Maximum retries for failed API calls."""
        return int(os.getenv('MAX_RETRIES', '3'))

    # ==========================================================================
    # RISK MANAGEMENT DEFAULTS
    # ==========================================================================

    @property
    def default_risk_level(self) -> str:
        """Default risk level for analysis."""
        return os.getenv('DEFAULT_RISK_LEVEL', 'MEDIUM').upper()

    @property
    def default_position_size(self) -> float:
        """Default position size as percentage of portfolio."""
        return float(os.getenv('DEFAULT_POSITION_SIZE', '0.05'))

    # ==========================================================================
    # DEVELOPMENT/DEBUG OPTIONS
    # ==========================================================================

    @property
    def debug_mode(self) -> bool:
        """Enable debug mode."""
        return os.getenv('DEBUG_MODE', 'false').lower() == 'true'

    @property
    def skip_model_check(self) -> bool:
        """Skip model availability check."""
        return os.getenv('SKIP_MODEL_CHECK', 'false').lower() == 'true'

    @property
    def use_mock_data(self) -> bool:
        """Use mock data instead of real API calls."""
        return os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'

    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================

    def _setup_logging(self):
        """Setup logging configuration based on environment variables."""
        log_level = getattr(logging, self.log_level, logging.INFO)

        # Configure basic logging
        handlers = [logging.StreamHandler()]

        # Add file handler if enabled
        if self.enable_file_logging:
            # Create log directory if it doesn't exist
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(self.log_file))

        logging.basicConfig(
            level=log_level,
            format=self.log_format,
            handlers=handlers,
            force=True  # Override any existing configuration
        )

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.export_dir,
            Path(self.database_path).parent,
            Path(self.log_file).parent if self.enable_file_logging else None
        ]

        for directory in directories:
            if directory and directory != Path('.'):
                Path(directory).mkdir(parents=True, exist_ok=True)

    def validate_config(self) -> list:
        """Validate configuration and return list of warnings/errors."""
        warnings = []

        # Check if .env file exists
        if not Path('.env').exists():
            warnings.append("No .env file found. Using default values. Copy .env.example to .env for customization.")

        # Validate intervals
        valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
        if self.default_interval not in valid_intervals:
            warnings.append(f"Invalid default interval '{self.default_interval}'. Valid options: {valid_intervals}")

        # Validate risk level
        valid_risk_levels = ['LOW', 'MEDIUM', 'HIGH']
        if self.default_risk_level not in valid_risk_levels:
            warnings.append(f"Invalid default risk level '{self.default_risk_level}'. Valid options: {valid_risk_levels}")

        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_log_levels:
            warnings.append(f"Invalid log level '{self.log_level}'. Valid options: {valid_log_levels}")

        # Check for prompt file
        if not Path(self.prompt_file).exists():
            warnings.append(f"Prompt file '{self.prompt_file}' not found.")

        # Validate numeric values
        if self.default_analysis_hours <= 0:
            warnings.append("DEFAULT_ANALYSIS_HOURS must be greater than 0")

        if self.default_fetch_days <= 0:
            warnings.append("DEFAULT_FETCH_DAYS must be greater than 0")

        if self.default_position_size <= 0 or self.default_position_size > 1:
            warnings.append("DEFAULT_POSITION_SIZE must be between 0 and 1")

        return warnings

    def print_config_summary(self):
        """Print a summary of current configuration."""
        print("\n" + "=" * 60)
        print("📋 GOLD DIGGER CONFIGURATION SUMMARY")
        print("=" * 60)

        print(f"🤖 Ollama Host: {self.ollama_host}")
        print(f"🧠 AI Model: {self.ollama_model}")
        print(f"💾 Database: {self.database_path}")
        print(f"📊 Default Interval: {self.default_interval}")
        print(f"⏱️  Analysis Hours: {self.default_analysis_hours}")
        print(f"📅 Fetch Days: {self.default_fetch_days}")
        print(f"📈 Gold Symbol: {self.gold_symbol}")
        print(f"🔧 Log Level: {self.log_level}")
        print(f"🚨 Debug Mode: {'ON' if self.debug_mode else 'OFF'}")

        # Show warnings if any
        warnings = self.validate_config()
        if warnings:
            print(f"\n⚠️  Configuration Warnings:")
            for warning in warnings:
                print(f"   • {warning}")
        else:
            print(f"\n✅ Configuration is valid")

        print("=" * 60)

    def create_env_file(self):
        """Create a .env file with current values (useful for first-time setup)."""
        if Path('.env').exists():
            response = input(".env file already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Skipping .env file creation.")
                return

        env_content = f"""# Gold Digger Configuration
# Generated on {os.popen('date').read().strip()}

# Ollama Configuration
OLLAMA_HOST={self.ollama_host}
OLLAMA_MODEL={self.ollama_model}
OLLAMA_TIMEOUT={self.ollama_timeout}

# Database Configuration
DATABASE_PATH={self.database_path}

# Trading Analysis Configuration
DEFAULT_INTERVAL={self.default_interval}
DEFAULT_ANALYSIS_HOURS={self.default_analysis_hours}
PROMPT_FILE={self.prompt_file}

# Data Fetching Configuration
DEFAULT_FETCH_DAYS={self.default_fetch_days}
GOLD_SYMBOL={self.gold_symbol}
YFINANCE_TIMEOUT={self.yfinance_timeout}

# Logging Configuration
LOG_LEVEL={self.log_level}
LOG_FORMAT={self.log_format}
ENABLE_FILE_LOGGING={'true' if self.enable_file_logging else 'false'}
LOG_FILE={self.log_file}

# Export Configuration
EXPORT_DIR={self.export_dir}
EXPORT_INCLUDE_VOLUME={'true' if self.export_include_volume else 'false'}

# API Configuration
API_DELAY={self.api_delay}
MAX_RETRIES={self.max_retries}

# Risk Management
DEFAULT_RISK_LEVEL={self.default_risk_level}
DEFAULT_POSITION_SIZE={self.default_position_size}

# Development Options
DEBUG_MODE={'true' if self.debug_mode else 'false'}
SKIP_MODEL_CHECK={'true' if self.skip_model_check else 'false'}
USE_MOCK_DATA={'true' if self.use_mock_data else 'false'}
"""

        with open('.env', 'w') as f:
            f.write(env_content)

        print("✅ .env file created successfully!")


# Global configuration instance
config = Config()

# Convenience function for getting configuration
def get_config() -> Config:
    """Get the global configuration instance."""
    return config


# Configuration validation on import
if __name__ == "__main__":
    # When run directly, show configuration summary
    config.print_config_summary()

    # Option to create .env file
    if not Path('.env').exists():
        response = input("\nCreate .env file with current settings? (y/N): ")
        if response.lower() == 'y':
            config.create_env_file()
else:
    # When imported, just ensure directories exist
    config.ensure_directories()
