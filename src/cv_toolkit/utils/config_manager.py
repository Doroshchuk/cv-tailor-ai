from typing import Dict, Any, Optional
import os
import json
from .log_helper import LogHelper
from .models.settings import SettingsModel
from dotenv import load_dotenv


# Load .env file from src directory
src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(src_dir, ".env")
load_dotenv(env_path)

class ConfigManager:
    _instance: Optional['ConfigManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.logger = LogHelper("config_manager")
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._settings: SettingsModel = SettingsModel(**self._load_config())

    def _load_config(self) -> Dict[str, Any]:
        # Try to get config path from environment, fallback to default
        config_path = os.getenv("CONFIG_PATH", "src/configs/settings.json")
        
        # Debug logging to see what's happening
        self.logger.info(f"Looking for config file at: {config_path}")
        self.logger.info(f"CONFIG_PATH env var: {os.getenv('CONFIG_PATH')}")
        
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        else:
            error_message = f"No settings file found at {config_path}"
            self.logger.error(error_message)
            raise FileNotFoundError(error_message)

    @property
    def settings(self) -> SettingsModel:
        return self._settings
    
    def reload(self):
        self._settings = SettingsModel(**self._load_config())
