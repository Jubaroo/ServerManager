import tkinter as tk


class Tooltip:
    def __init__(self, widget, text, duration=3000, bg="lightyellow", fg="black", font=("Arial", 10), wraplength=200):
        self.widget = widget
        self.text = text
        self.duration = duration
        self.bg = bg
        self.fg = fg
        self.font = font
        self.wraplength = wraplength
        self.tooltip_window = None
        self.tooltip_id = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<FocusOut>", self.hide_tooltip)
        self.widget.bind("<Unmap>", self.hide_tooltip)

    def show_tooltip(self, event):
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 2
        y = self.widget.winfo_rooty()
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, bg=self.bg, fg=self.fg, font=self.font,
                         wraplength=self.wraplength, relief="solid", borderwidth=1)
        label.pack()

        self.tooltip_id = self.widget.after(self.duration, self.hide_tooltip)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
        if self.tooltip_id:
            self.widget.after_cancel(self.tooltip_id)
            self.tooltip_id = None

    def update_text(self, text):
        self.text = text
