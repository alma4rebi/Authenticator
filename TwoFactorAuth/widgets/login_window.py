from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import logging
from hashlib import sha256
from gettext import gettext as _

class LoginWindow(Gtk.Box):
    password_entry = None
    unlock_button = None

    def __init__(self, application, window):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.app = application
        self.window = window
        self.password_entry = Gtk.Entry()
        self.unlock_button = Gtk.Button()
        self.generate()
        self.window.connect("key-press-event", self.__on_key_press)

    def generate(self):
        password_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.password_entry.set_visibility(False)
        self.password_entry.set_placeholder_text(_("Enter your password"))
        password_box.pack_start(self.password_entry, False, False, 6)

        self.unlock_button.set_label(_("Unlock"))
        self.unlock_button.connect("clicked", self.on_unlock)

        password_box.pack_start(self.unlock_button, False, False, 6)
        self.pack_start(password_box, True, False, 6)

    def on_unlock(self, *args):
        """
            Password check and unlock
        """
        typed_pass = self.password_entry.get_text()
        ecrypted_pass = sha256(typed_pass.encode("utf-8")).hexdigest()
        login_pass = self.app.cfg.read("password", "login")
        if ecrypted_pass == login_pass or login_pass == typed_pass == "":
            self.password_entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, None)
            self.toggle_lock()
            self.password_entry.set_text("")
        else:
            self.password_entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, "dialog-error-symbolic")

    def __on_key_press(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval).lower()
        if self.window.is_locked():
            if keyname == "return":
                self.on_unlock()
                return True
        else:
            pass_enabled = self.app.cfg.read("state", "login")
            if keyname == "l" and pass_enabled:
                if event.state & Gdk.ModifierType.CONTROL_MASK:
                    self.toggle_lock()
                    return True

        return False

    def toggle_lock(self, *args):
        """
            Lock/unlock the application
        """
        pass_enabled = self.app.cfg.read("state", "login")
        if pass_enabled:
            self.app.locked = not self.app.locked
            if self.app.locked:
                self.focus()
            self.app.refresh_menu()
            self.app.win.refresh_window()

    def toggle(self, visible):
        self.set_visible(visible)
        self.set_no_show_all(not visible)

    def hide(self):
        self.toggle(False)

    def show(self):
        self.toggle(True)

    def focus(self):
        self.password_entry.grab_focus_without_selecting()
