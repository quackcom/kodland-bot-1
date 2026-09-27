import json

CONFIG_PATH = ".botconfig"

def load_config() -> dict:
    """ Reads .botconfig from the disk and if it doesn't exist, it returns an empty dict."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_config(config: dict):
    """ Saves .botconfig to the disk, if it doesn't exist, it gets created. """
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
