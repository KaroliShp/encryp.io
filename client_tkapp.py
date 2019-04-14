import tkinter as tk
from frames import StartWindow, Lobby, ChatRoom
# from tkinter.ttk import Style

class ClientTkApp(tk.Tk):
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        
        self.title("ENCRYP.IO CLIENT")
        self.geometry("600x600")

        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)
        # container.grid(row=0, column=0,columnspan=5, rowspan=6)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartWindow, Lobby, ChatRoom):
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartWindow)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    test = ClientTkApp()
    test.mainloop()