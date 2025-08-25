from gi.repository import Notify

from src.utils.media import get_icon_path


class Notification:
    def __init__(self):
        self.notification = None
        if not Notify.is_initted():
            Notify.init("Homepage Ulauncher")
            Notify.set_app_icon(get_icon_path())

    def show(self, title, body):
        icon = get_icon_path()
        if self.notification is None:
            self.notification = Notify.Notification.new(title, body, icon)
        else:
            self.notification.update(title, body, icon)

        self.notification.show()
