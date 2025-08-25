from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from src.listeners.SyncEnterEventListener import SyncEnterEventListener


class HomepageExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, SyncEnterEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
        items.append(
            ExtensionResultItem(
                icon="images/icon.png",
                name="Update Data",
                description="Click to synchronize services from the Homepage API",
                on_enter=ExtensionCustomAction({"action": "sync"}, keep_app_open=False),
            )
        )
        return RenderResultListAction(items)


if __name__ == "__main__":
    HomepageExtension().run()
