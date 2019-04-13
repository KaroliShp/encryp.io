import tkinter as tk

class StartWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ENCRYP.IO CLIENT")
        self.geometry("400x400")

        # LABEL
        self.header = tk.Label(self, text="Welcome to Encryp.IO", font=("Times New Roman", 16))
        self.header.grid(column=1, row=0)

        # User ID Entry Field
        self.entry_uid = tk.Entry()
        self.entry_uid.grid(column=1, row=1)
        # self.entry_uid.insert(0,"your ID")

        # Password Entry Field
        self.entry_passw = tk.Entry()
        self.entry_passw.grid(column=1, row=2)
        # self.entry_passw.insert(0,"your password")
    
        # Submit butto
        self.submit_button = tk.Button(text="Log In", bg="red", command=lambda:self.authenticate())
        self.submit_button.grid(column=1, row=3)
    
    # # --- FUNCTIONS ---
    def authenticate(self):
        id = str(self.entry_uid.get())
        passw = str(self.entry_passw.get())
        print(id)
        print(passw)

        self.validator = tk.Text(master=self, height=10, width=30)
        self.validator.grid(column=1, row=4)

        if (id == '123' and passw == '789'):
            self.validator.insert(tk.END, "You are logged in!")
            
        elif (id == '' and passw == ''):
            self.validator.insert(tk.END, "No data was put in.")
        else:
            self.validator.insert(tk.END, "LOGIN FAILED")

if __name__ == "__main__":
    window = StartWindow()

    window.mainloop()