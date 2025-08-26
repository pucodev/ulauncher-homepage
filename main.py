from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from src.db.db import search_services
from src.listeners.SyncEnterEventListener import SyncEnterEventListener
from src.utils.media import get_icon_path
from src.utils.utils import get_search_limit, is_valid_homepage_url


class HomepageExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, SyncEnterEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []

        # Add error message if api_url is empty
        if not is_valid_homepage_url(extension):
            items.append(
                ExtensionResultItem(
                    icon=get_icon_path(),
                    name="Error: Invalid Homepage url",
                    description="Please enter the homepage URL in the extension configuration",
                    on_enter=HideWindowAction(),
                )
            )

        # Search services
        services = search_services(
            event.get_argument() or "", get_search_limit(extension)
        )
        for service in services:
            items.append(
                ExtensionResultItem(
                    icon=service.get_icon_path(),
                    name=service.name,
                    description=service.get_full_description(),
                    on_enter=OpenUrlAction(service.href),
                )
            )

        # Add sync data
        items.append(
            ExtensionResultItem(
                icon="images/icon.png",
                name="Sync services",
                description="Select to synchronize services from the Homepage API",
                on_enter=ExtensionCustomAction({"action": "sync"}, keep_app_open=False),
            )
        )
        return RenderResultListAction(items)


if __name__ == "__main__":
    HomepageExtension().run()
