import os
import json
from dotenv import load_dotenv

CONFIG_PATH = "config.json"
ENV_PATH = ".env"


class Config:
    def __init__(self):
        load_dotenv(ENV_PATH)
        self.config = self._load_config()

    def _load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return self._get_default_config()

    def _get_default_config(self):
        import pyautogui
        screen_size = pyautogui.size()
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        return {
            "api_key": os.environ.get("ARK_API_KEY", ""),
            "endpoint_id": os.environ.get("ARK_ENDPOINT_ID", ""),
            "model": "doubao-seed-2-0-pro-260215",
            "screen_size": [screen_size.width, screen_size.height],
            "desktop_path": desktop_path
        }

    def save_config(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    @property
    def api_key(self):
        return self.config.get("api_key", "")

    @api_key.setter
    def api_key(self, value):
        self.set("api_key", value)

    @property
    def endpoint_id(self):
        return self.config.get("endpoint_id", "")

    @endpoint_id.setter
    def endpoint_id(self, value):
        self.set("endpoint_id", value)

    @property
    def model(self):
        return self.config.get("model", "doubao-seed-2-0-pro-260215")

    @model.setter
    def model(self, value):
        self.set("model", value)

    @property
    def screen_size(self):
        return self.config.get("screen_size", [1920, 1080])

    @property
    def desktop_path(self):
        return self.config.get("desktop_path", "")


config = Config()
