import tkinter as tk
from tkinter import ttk


class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Server Manager")
        self.root.geometry("600x400")

        style = ttk.Style()
        style.theme_use('clam')

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        server_label = ttk.Label(main_frame, text="Select Server:")
        server_label.grid(row=0, column=0, sticky=tk.W)

        self.server_var = tk.StringVar()
        server_combobox = ttk.Combobox(main_frame, textvariable=self.server_var, state="readonly")
        server_combobox.grid(row=0, column=1, sticky=(tk.W, tk.E))

        install_button = ttk.Button(main_frame, text="Install", command=self.install_server)
        install_button.grid(row=1, column=1, sticky=tk.E)

    def install_server(self):
        selected_server = self.server_var.get()
        # Implement installation logic


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernApp(root)
    root.mainloop()
