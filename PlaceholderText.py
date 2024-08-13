import logging
import tkinter as tk


def _log_message(msg, level=logging.INFO):
    log_levels = {
        logging.INFO: logging.info,
        logging.ERROR: logging.error,
        logging.WARNING: logging.warning,
        logging.DEBUG: logging.debug
    }
    log_func = log_levels.get(level, logging.debug)
    log_func(msg)


class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', active_color='white', **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']
        self.active_color = active_color
        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)
        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self.get() == self.placeholder:
            self.delete(0, 'end')
            self['fg'] = self.default_fg_color
            _log_message("Placeholder Text FocusIn", logging.INFO)

    def foc_out(self, *args):
        print("FocusOut event triggered")
        _log_message("FocusOut event triggered", logging.INFO)
        if not self.get():
            self.put_placeholder()

    def clear_placeholder(self):
        if self.get() == self.placeholder:
            self.delete(0, 'end')
        self['fg'] = self.active_color  # Ensure the active color is always set
