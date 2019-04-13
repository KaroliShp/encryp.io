import tkinter as tk

window = tk.Tk()

window.title("ENCRYP.IO CLIENT")
window.geometry("400x400")

# # --- FUNCTIONS ---
def authenticate():
    id = str(entry_uid.get())
    passw = str(entry_passw.get())
    print(id)
    print(passw)

    validator = tk.Text(master=window, height=10, width=30)
    validator.grid(column=1, row=4)

    
    if (id == '123' and passw == '789'):
        validator.insert(tk.END, "You are logged in!")
        
    elif (id == '' and passw == ''):
        validator.insert(tk.END, "Standard")
    else:
        validator.insert(tk.END, "LOGIN FAILED")
        


# LABEL
title = tk.Label(text="Welcome to Encryp.IO", font=("Times New Roman", 16))
title.grid(column=1, row=0)

# User ID Entry Field
# uid_text =tk.StringVar()
entry_uid = tk.Entry()
entry_uid.grid(column=1, row=1)
# self.entry_uid.insert(0,"your ID")

# Password Entry Field
# passw_text = tk.StringVar()
entry_passw = tk.Entry()
entry_passw.grid(column=1, row=2)
# self.entry_passw.insert(0,"your password")
    

# Submit button
# is_authenticated = authenticate('123', '789')
submit_button = tk.Button(text="Log In", bg="red", command= lambda:authenticate())
submit_button.grid(column=1, row=3)

# validator = tk.Text(master=window, height=10, width=30)
# validator.grid(column=1, row=4)

window.mainloop()