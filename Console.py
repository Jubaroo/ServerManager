import tkinter as tk


class ConsoleText(tk.Text):
    """A Tkinter Text widget that acts as a console."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(state='disabled')

    def write(self, message):
        self.configure(state='normal')
        self.insert(tk.END, message)
        self.configure(state='disabled')
        self.see(tk.END)

    def flush(self):
        pass  # Required for file-like object compatibility
