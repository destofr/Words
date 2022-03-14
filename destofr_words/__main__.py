import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from pkg_resources import resource_string
import secrets

from . import APP_ID, VERSION


def main():
    app = Gtk.Application(application_id=APP_ID)
    app.connect("activate", GameWindow)
    app.run(None)


def template(c):
    return Gtk.Template(string=resource_string(__name__, c.__gtype_name__ + ".ui"))(c)


# Word generator
def generate_word():
    with open("/usr/share/dict/words") as f:
        lines = f.readlines()
        return secrets.choice(lines).strip().lower()


class GameRow(Gtk.Box):
    __gtype_name__ = "GameRow"

    def __init__(self, length=5):
        super().__init__()
        for i in range(length):
            letter = Gtk.Button(label="")
            letter.add_css_class("letter")
            self.append(letter)


@template
class GamePlayer(Gtk.Box):
    __gtype_name__ = "GamePlayer"
    __slots__ = (
        "word",
        "rows",
        "current_row",
        "entry",
    )

    def __init__(self, word=None):
        super().__init__(orientation=1)
        self.word = generate_word() if word is None else word
        self.rows = tuple(GameRow(len(self.word)) for i in range(5))
        for i in self.rows:
            self.append(i)
        self.current_row = 0
        self.entry = Gtk.Entry(max_length=len(self.word))
        self.append(self.entry)
        self.entry.connect("changed", lambda _d: self.on_change())
        self.entry.connect("activate", lambda _d: self.on_activate())

    def on_change(self):
        if self.current_row >= len(self.rows):
            return
        text = self.entry.get_text().upper()
        letters = list(text)
        while len(letters) < len(self.word):
            letters.append("")

        for letter, button in zip(letters, self.rows[self.current_row]):
            button.set_label(letter)

    def on_activate(self):
        text = self.entry.get_text().lower()
        if len(text) < len(self.word):
            return True
        scores = self.compare(text.lower(), self.word)
        for score, button in zip(scores, self.rows[self.current_row]):
            button.add_css_class(f"state-{score}")
        self.current_row += 1
        if all(score == 0 for score in scores):
            self.entry.set_editable(False)
            self.entry.set_max_length(0)
            self.entry.set_text("YOU WIN!")
        elif self.current_row >= len(self.rows):
            self.entry.set_editable(False)
            self.entry.set_max_length(0)
            self.entry.set_text("The word was: " + self.word)
        else:
            self.entry.set_text("")

    @staticmethod
    def compare(text, target):
        data = list(text)
        # Mark matching letters
        for i, letter in enumerate(target):
            if letter == data[i]:
                data[i] = 0

        # Check for letters that are in the wrong position
        for i, letter in enumerate(target):
            try:
                data[data.index(letter)] = 1
            except ValueError:
                pass

        # Mark all others as wrong
        for i, letter in enumerate(target):
            if not isinstance(data[i], int):
                data[i] = 2

        return data


class GameWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "GameWindow"

    def __init__(self, app):
        super().__init__(application=app, title="Words")
        self.set_child(GamePlayer())
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(resource_string(__name__, "main.css"))
        Gtk.StyleContext().add_provider_for_display(
            self.get_display(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
        self.present()


if __name__ == "__main__":
    main()
