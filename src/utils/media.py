from os.path import dirname, join

from ulauncher.config import CACHE_DIR

ICON_FILE = "images/icon.png"
_CACHED_ICON_PATH = None

SERVICE_ICON_FOLDER = "icon"
_CACHED_SERVICE_ICON_PATH = None

PROJECT_ROOT = dirname(dirname(dirname(__file__)))


def get_icon_path():
    global _CACHED_ICON_PATH
    if _CACHED_ICON_PATH is None:
        _CACHED_ICON_PATH = join(PROJECT_ROOT, ICON_FILE)

    return _CACHED_ICON_PATH


def get_service_icon_folder_path():
    global _CACHED_SERVICE_ICON_PATH
    if _CACHED_SERVICE_ICON_PATH is None:
        _CACHED_SERVICE_ICON_PATH = join(get_cache_path(), SERVICE_ICON_FOLDER)

    return _CACHED_SERVICE_ICON_PATH


def get_cache_path():
    return join(CACHE_DIR, "ulauncher-homepage")
