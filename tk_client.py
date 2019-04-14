# Mirrored after https://github.com/ani8897/Chat-Application-OptiChat/blob/master/client.py
import tkinter as tk
import tkinter.ttk as ttk

import threading # will use for threading.Thread()
import socket
import time
import json
import sys

from database import Client, db_find
from helper import receive_json_message, send_json_message, check_connection_client
from p2p import P2P_Server, P2P_Client

class ClientTkApp(tk.Tk):
    def launch_app(self, input_host='', input_port=5000):
        self.host = input_host
        self.port = input_port
        self.database_of_all_users = [Client("Klevas", "0000"), Client("Berzas", "0001"), Client("Pusis", "0005")]
        self.list_of_active_user = []

        self.title("ENCRYP.IO CLIENT")
        self.geometry("600x600")
        self.frame = tk.Frame()

        self.frame.style = ttk.Style()

        self.start_button = ttk.Button(self.frame, text = 'Launch Client', command = self.client_menu)
        self.start_button.grid(row = 2, column = 0, padx = 40, pady = 30)
        # self.frame.style = ttk.Style()

        self.frame.pack(fill="both", expand=True)
        self.theme_use = 'default'

        self.frame.style.theme_use(self.theme_use)

        self.mainloop()

    def client_menu(self):
        self.title('Log In')

        # Sets up initial menu with entries for credentials & host/port
        self.id_entry_label = ttk.Label(self.frame, text = 'Enter your ID', anchor = tk.W, justify = tk.LEFT)
        self.id_entry_label.grid(row = 0, column = 0, pady = 10, padx = 5)

        self.id_entry = ttk.Entry(self.frame)
        self.id_entry.grid(row = 0, column = 1, pady = 10, padx = 5)

        self.passw_entry_label = ttk.Label(self.frame, text = 'Enter your password', anchor = tk.W, justify = tk.LEFT)
        self.passw_entry_label.grid(row = 1, column = 0, pady = 10, padx = 5)

        self.passw_entry = ttk.Entry(self.frame)
        self.passw_entry.grid(row = 1, column = 1, pady = 10, padx = 5)

        self.host_entry_label = ttk.Label(self.frame, text = 'Server IP Address', anchor = tk.W, justify = tk.LEFT)
        self.host_entry_label.grid(row=2, column=0, pady=10,padx=5)

        self.host_entry = ttk.Entry(self.frame)
        self.host_entry.grid(row=2, column=1, pady=10,padx =5)

        self.port_entry_label = ttk.Label(self.frame, text = 'Port Number', anchor = tk.W, justify = tk.LEFT)
        self.port_entry_label.grid(row=3,column=0,pady=10,padx=5)

        self.port_entry = ttk.Entry(self.frame)
        self.port_entry.grid(row=3,column=1,pady=10,padx=5)

        #Attempt a Log in.
        self.launch_button = ttk.Button(self.frame, text = 'Log In', command = self.launch_client)
        self.launch_button.grid(row = 4, column = 1, pady = 10, padx = 5)

        self.id_entry.focus_set()
        self.frame.pack(fill=tk.BOTH, expand= True)

    def authenticate(self):
        if (db_find(self.database_of_all_users, self.UID) != None) and (db_find(self.database_of_all_users, self.UID).IK == self.IK):
            return True
        return False

    def launch_client(self):
        # Obtain log-in credentials
        self.UID = self.id_entry.get()
        self.IK = self.passw_entry.get()

        self.HOST = self.host_entry.get()
        self.PORT = int(self.port_entry.get())

        # Later change to normal DB handler
        if self.authenticate() == False:
            print(f"WRONG CREDENTIALS {self.UID} -- {self.IK}")
            self.id_entry.delete(0, tk.END)
            self.passw_entry.delete(0, tk.END)
            self.client_menu()

        print("SUCCESSFUL LOGIN")
        
        # Remove all redundant widgets
        self.id_entry_label.destroy()
        self.id_entry.destroy()
        self.passw_entry_label.destroy()
        self.passw_entry.destroy()

        self.host_entry_label.destroy()
        self.host_entry.destroy()
        self.port_entry_label.destroy()
        self.port_entry.destroy()        

        self.launch_button.destroy()
        self.frame.pack_forget()

        # SET UP A SOCKET LISTENING TO THE SERVER
        # Setup client (Karolio comment'as)
        print(f'Starting the client...')

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(f'Client socket created successfully')
        
        # Copied code continues
        self.conn.settimeout(2) # MAYBE SHOULD DELETE THIS

        try:
            self.conn.connect((self.HOST,self.PORT)) #Attempting to connect to the server
            print(f'Connected to: {self.HOST}:{str(self.PORT)}')
        except:
            self.client_menu() #Authentication failure

        # Verify with the server
        time.sleep(1)
        send_json_message(self.conn, { 'UID' : self.UID, 'IK' : self.IK })

        response_msg = receive_json_message(self.conn)
        check_connection_client(response_msg)
        print(f'Server ({response_msg["Response"]}): {response_msg["Message"]}')
        
        if response_msg['Response'] == 'Failure':
            print('Quitting...')
            sys.exit(0)

        # self.list_of_active_user = self.initial_setup() #Obtaining the list of active users on successful connection to the user
        # # FINISHED SETTING UP SOCKETS
        self.list_of_active_user.append(db_find(self.database_of_all_users,self.UID))
        #-------------------------------- CURRENT STATE -----------------

        self.title('ENCRYP.IO CHAT CLIENT') #Window title

        self.should_quit = False   
        
        self.protocol('WM_DELETE_WINDOW', self.client_quit)

        self.chat_frame = ttk.Frame(self.frame, borderwidth = 5)    #for the actual display of chat
        self.clients_frame = ttk.Frame(self.frame)                  #for radio buttons
        self.entry_frame = ttk.Frame(self)                          #for input text
        self.button_frame = ttk.Frame(self.entry_frame)

        ########## Stylising ############## 
        self.chat_frame.style = ttk.Style()
        self.chat_frame.style.theme_use(self.theme_use)

        self.clients_frame.style = ttk.Style()
        self.clients_frame.style.theme_use(self.theme_use)
   
        self.entry_frame.style = ttk.Style()
        self.entry_frame.style.theme_use(self.theme_use)

        self.button_frame.style = ttk.Style()
        self.button_frame.style.theme_use(self.theme_use)
        ####################################

         #state indicates the chat history so far, and is uneditable
        self.chat_text = tk.Text(self.chat_frame, state = tk.DISABLED)

        #Adding a scroll bar to the text Area
        self.scroll = tk.Scrollbar(self.chat_frame)
        self.scroll.configure(command = self.chat_text.yview)
        self.chat_text.configure(yscrollcommand = self.scroll.set) 

        #Chat entry area consists of Send Message, Send Multimedia and Chat entry
        self.chat_entry = ttk.Entry(self.entry_frame)  #Text box for sending messages
        self.send_button = ttk.Button(self.button_frame, text = 'Send Message')   #For actually sending the messages


        self.send_button.bind('<Button-1>', self.send) #press button-1 to send messages
        self.chat_entry.bind('<Return>', self.send) #Alternate to sending messages, hitting the return button


        #Packing the above created objects and giving them positions while packing
        self.entry_frame.pack(side = tk.BOTTOM, fill = tk.X)
        self.frame.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
        self.clients_frame.grid()
        # self.clients_frame.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        self.clients_frame.grid()
        # self.chat_frame.pack(side = tk.RIGHT, fill = tk.BOTH, expand = True)

        self.chat_entry.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        self.send_button.grid(row=0,column=0)
        self.button_frame.pack(side = tk.RIGHT)

        self.checks = []
        self.radio_label = ttk.Label(self.clients_frame,
                    width = 15,
                    wraplength = 125,
                    anchor = tk.W,
                    justify = tk.LEFT,
                    text = 'Choose receiver from the following connected clients:')

        self.radio_label.pack()
        self.scroll.pack(side = tk.RIGHT,fill=tk.Y)
        self.chat_text.pack(fill = tk.BOTH, expand = True)

         #############################################################

        self.enable = dict()
        
        # NEED TO FIRE UP DATABASE TO PREVENT SELECTION OF YOUR OWN NAME
        # for client in [i for i in self.list_of_active_user if i.UID !=self.UID]:
        for client in self.list_of_active_user:
            self.enable[client.UID] = tk.IntVar()
            l = ttk.Checkbutton(self.clients_frame, text=client.UID, variable=self.enable[client.UID])
            l.pack(anchor = tk.W)
            self.checks.append(l)

        self.chat_entry.focus_set()

        #for client we will intiate a thread to display chat
        self.clientchat_thread = threading.Thread(name = 'clientchat', target = self.clientchat)
        self.clientchat_thread.start()

    def send(self,event):
        message = self.chat_entry.get()
        #dest = self.dest.get()

        data = ""
        for client in self.list_of_active_user:
            if self.enable[client].get() == 1:
                data = data + "@" + client + ' '
        data = data + ':'
        data = data + message

        self.chat_entry.delete(0, tk.END)#input box empty after send
        
        self.conn.send(data.encode())               #Sending the encoded data to the server
        
        self.chat_text.config(state = tk.NORMAL)
        for client in self.list_of_active_user:
            if self.enable[client].get() == 1:
                self.chat_text.insert(tk.END, client +':'+ message +'\n',('tag{0}'.format(1)))
                self.chat_text.tag_config('tag{0}'.format(1),justify=tk.RIGHT,foreground='blue')
        self.chat_text.config(state = tk.DISABLED) #Again Disabling the edit functionality so that the user cannot edit it
        self.chat_text.see(tk.END) #Enables the user to see the edited chat history

    #Chatting time!
    def clientchat(self):
        while not self.should_quit:     #If we are not in the 'quit' state then do :
            try:
                data = self.conn.recv(10000000) #Receive and decode the data
                data = data.decode()
                data = data.rstrip()

                if len(data): #If there is data
                    #if there is an active user message received then it means a new 
                    #user has logged in and we need to update radios
                    if data[0] == "!":
                        self.list_of_active_user = data[1:].split(' ')

                        for l in self.checks:
                            l.destroy()

                        #Updating the new checkbox list
                        for client in self.list_of_active_user:
                            self.enable[client] = tk.IntVar()
                            l = ttk.Checkbutton(self.clients_frame, text=client, variable=self.enable[client])
                            l.pack(anchor = tk.W)
                            self.checks.append(l)

                    elif data[0] == "^":
                        data_recvd = data.split(':')
                        sendername = data_recvd[0][2:]
                        filename_process = data_recvd[1].split('/')
                        filename = filename_process[len(filename_process) - 1]
                        print(sendername) 
                        print('\n')
                        print(filename)
                        encoded_string = data_recvd[2]
                        decoded_string = base64.b64decode(encoded_string)

                        with open(filename, "wb") as file:
                            file.write(decoded_string)

                        print_data = sendername + ': ' + filename
                        self.chat_text.config(state = tk.NORMAL)
                        self.chat_text.insert(tk.END, print_data+'\n',('tag{0}'.format(2)))
                        self.chat_text.tag_config('tag{0}'.format(2),justify=tk.LEFT,foreground='red')
                        self.chat_text.config(state = tk.DISABLED)
                        self.chat_text.see(tk.END)
                    #it's not an activelist msg
                    else:
                        #Updating the chat history based on the new message received
                        self.chat_text.config(state = tk.NORMAL)
                        self.chat_text.insert(tk.END, data[1:]+'\n',('tag{0}'.format(2)))
                        self.chat_text.tag_config('tag{0}'.format(2),justify=tk.LEFT,foreground='red')
                        self.chat_text.config(state = tk.DISABLED)
                        self.chat_text.see(tk.END)
                else:
                    break
            except:
                continue
    
    # def initial_setup(self):
    #     #allow for it to communicate with server only once for 
    #     #the first time  till it gets the list of active users
    #     got_list = False
    #     list_of_active_user = []
        
    #     try:
    #         self.conn.send('0'.encode())    #Sending 0 to indicate that it is a non-registration message
    #     except:
    #         #Closing the connection and giving an option to reattempt 
    #         self.conn.close()
    #         self.wp_error = ttk.Label(self.frame, text='Cannot Connect to Server', anchor = tk.CENTER,justify = tk.CENTER)
    #         self.try_again = ttk.Button(self.frame, text='Try again', command = self.client_menu)
    #         self.wp_error.grid(row = 0, column=1, pady=10, padx=5)
    #         self.try_again.grid(row=0,column=1,pady=10,padx=5)
    #         self.frame.pack(fill=tk.BOTH, expand = True)

    #     while 1:
    #         if not got_list:
    #             try:
    #                 data = self.conn.recv(10000000) #Obtaining the list of all the active users
    #                 data = data.decode()
    #                 data = data.rstrip()
    #             except:
    #                 self.conn.close()
    #                 self.client_menu()
                
    #             if data == "What is your name?": #Getting the first message from the server
    #                 try:
    #                     self.conn.send((self.name+' '+self.pwd).encode())   #Sending the name and password to the server
    #                 except:
    #                     self.conn.close()
    #                     self.client_menu()    
    #                 try:
    #                     list_of_active_user = self.conn.recv(10000000).decode() #this will be a string of name separated by spaces
    #                 except:
    #                     self.conn.close()
    #                     self.client_menu() 
    #                 if list_of_active_user == 'authentication_error':   
    #                     #Authentication error implies that user is either not registered or password is incorrect. Redirecting to the Client menu
    #                     self.wp_error = ttk.Label(self.frame, text='Authentication_Error', anchor = tk.CENTER,justify = tk.CENTER)
    #                     self.try_again = ttk.Button(self.frame, text='Try again', command = self.client_menu)
    #                     self.wp_error.grid(row = 0, column=1, pady=10, padx=5)
    #                     self.try_again.grid(row=1,column=1,pady=10,padx=5)
    #                     self.try_again_bool = True
    #                     self.frame.pack(fill=tk.BOTH, expand = True)

    #                 list_of_active_user = list_of_active_user[1:].split(' ') #now it has all the names separately, its not a string
    #                 got_list = True
    #         else:
    #             return list_of_active_user    
    
    def client_quit(self):
        self.should_quit = True
        # self.conn.shutdown(socket.SHUT_WR)
        # self.clientchat_thread.join()
        # self.conn.close()
        self.destroy()


if __name__ == '__main__':
    HOST = ''
    PORT = 5000

    app = ClientTkApp()

    app.launch_app(HOST, PORT) #Launching the app