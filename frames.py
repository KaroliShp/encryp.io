import tkinter as tk


class StartWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # LAYOUT:
        self.header = tk.Label(self, text="Welcome to Encryp.IO", font=("Times New Roman", 16))
        # self.header.grid(column=2, row=2)
        self.header.pack()


        # User ID Entry Field
        self.entry_uid = tk.Entry()
        # self.entry_uid.grid(column=2, row=6)
        self.entry_uid.pack()
        # self.entry_uid.insert(0,"your ID")

        # Password Entry Field
        self.entry_passw = tk.Entry()
        # self.entry_passw.grid(column=2, row=7)
        self.entry_passw.pack(side=tk.TOP, pady=10,padx=10)
        # self.entry_passw.insert(0,"your password")
    
        # Submit button
        self.submit_button = tk.Button(text="Log In", bg="red", command=lambda:self.authenticate())
        # self.submit_button.grid(column=1, row=8)
        self.submit_button.pack(side=tk.TOP)
    
    # --- FUNCTIONS ---
    def authenticate(self):
        id = str(self.entry_uid.get())
        passw = str(self.entry_passw.get())
        # print(id)
        # print(passw)
        
        try:
            self.validator.destroy()
        except Exception as e:
            print(e)
        
        self.validator = tk.Text(master=self, height=10, width=30)
        # self.validator.grid(column=1, row=4)
        self.validator.pack(side=tk.TOP)

        if (id == '123' and passw == '789'):
            # self.validator.insert(tk.END, "You are logged in!")
            self.lower()
            self.controller.show_frame(Lobby)

            
        elif (id == '' and passw == ''):
            self.validator.insert(tk.END, "No data was put in.")

        else:
            self.validator.insert(tk.END, "LOGIN FAILED")
            self.entry_uid.delete(0, tk.END)
            self.entry_passw.delete(0, tk.END)

class Lobby(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.tkraise()

        # LAYOUT:
        self.header = tk.Label(self, text="MESSAGE ROOMS", font=("Times New Roman", 16))
        # self.header.grid(column=1, row=0)
        self.header.pack(pady=10,padx=10)

class ChatRoom(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # LAYOUT:
        self.header = tk.Label(self, text="CHAT ROOM NO. X", font=("Times New Roman", 16))
        # self.header.grid(column=1, row=0)
        self.header.pack(pady=10,padx=10)


# if __name__ == "__main__":
#     window = StartWindow()

#     window.mainloop()