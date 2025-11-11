import json
import os
from pathlib import Path

class Config:
    DEFAULT_CONFIG = {
        "max_retries": 3,
        "backoff_base": 2,
        "data_dir": ".queuectl"
    }
    
    def __init__(self):
        self.config_file = Path.home() / ".queuectl" / "config.json"
        self.config = self._load_config()
    
    def _load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return {**self.DEFAULT_CONFIG, **json.load(f)}
        return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self):
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self._save_config()
    
    def get_data_dir(self):
        data_dir = Path(self.config.get("data_dir", ".queuectl"))
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

_config_instance = None

def get_config():
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
