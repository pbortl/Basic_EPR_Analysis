import os
import json


def load_settings():
    config_path = os.path.join(os.getcwd(), 'config', 'settings.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"language": "en"}


def save_settings(config):
    config_dir = os.path.join(os.getcwd(), 'config')
    os.makedirs(config_dir, exist_ok=True)
    with open(os.path.join(config_dir, 'settings.json'), 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)


def load_translations():
    trans_path = os.path.join(os.getcwd(), 'config', 'translations.json')
    with open(trans_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def setup_language():
    config = load_settings()
    translations = load_translations()

    print("Select language / Wybierz język (1: EN, 2: PL):")
    choice = input("> ").strip()

    lang = "en" if choice == "1" else "pl"
    config["language"] = lang
    save_settings(config)

    return translations[lang]
