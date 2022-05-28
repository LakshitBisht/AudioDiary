"""
                                                           --- A U D I O   D I A R Y --- 
This program performs basic operations of a Digital Diary, and helps create and maintain a log of all the tasks and events i the users life. A GUI integrates the whole program

"""

## imported modules

import tkinter as tk
import speech_recognition as sr
from PIL import ImageTk, Image
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import showinfo
from tkinter.filedialog import askopenfilename, asksaveasfilename
from cryptography.fernet import Fernet
from multipledispatch import dispatch
import datetime
import os
import threading
import pyttsx3
import sqlite3
from win10toast import ToastNotifier
import random


def Notify():
    r_no = random.randint(1,40)
    noti = ToastNotifier()
    f = open("Notify\\Quotes.txt")
    quotes = f.readlines()
    f.close()
    noti.show_toast('Thought of the Day',quotes[r_no],duration=10, icon_path="images\\diary.ico", threaded = True)

def encrypt_decrypt():
    """
    Allows the user to either encryt text or decrypt an encrypted text
    """
    global page_img
    # clearing the previous frames
    main_frame.pack_forget()
    menu_frame.pack_forget()
    # destroying the log_frame widgets 
    for widget in log_frame.winfo_children():
        widget.destroy()
    login_frame.pack_forget()
    TextArea.pack_forget()

    log_frame.pack(expand=True, fill=tk.BOTH)

    # Add a Backgroung Image
    page_img = tk.PhotoImage(file = "images/page_img.png")
    tk.Label(log_frame,bg="#707070",image = page_img).place(x=0, y=0, relwidth=1, relheight=1)

    def generate_key():
        """
        Generates a key for encryption and save it into a file
        """
        key = Fernet.generate_key()
        with open("encryption\\secret.key", "wb") as key_file:
            key_file.write(key)

    def load_key():
        """
        Load the previously generated key
        """
        return open("encryption\\secret.key", "rb").read()

    def encrypt_message():
        """
        Encrypts a message
        """
        message = Submit_text.get(1.0 , tk.END)
        # loading the key
        key = load_key()
        encoded_message = message.encode()
        f = Fernet(key)
        encrypted_message = f.encrypt(encoded_message)
        # clearing the text field
        Submit_text.delete(1.0 , tk.END)
        # inserting in the text field
        Submit_text.insert(1.0 , encrypted_message)

    def decrypt_message():
        """
        Decrypts an encrypted message
        """
        encrypted_message = bytes(Submit_text.get(1.0 , tk.END) , 'utf-8')
        key = load_key()
        f = Fernet(key)
        decrypted_message = f.decrypt(encrypted_message)
        # clearing the text field
        Submit_text.delete(1.0 , tk.END)
        # inserting in the text field
        Submit_text.insert(1.0 , decrypted_message.decode())

    # generating a key for encryption-needs to be executed only once
    generate_key()

    # creating a temporary frame
    temp_frame = tk.Frame(log_frame,bg="#707070",highlightthickness=5,highlightbackground="#cfd3ce")
    temp_frame.place(x=340,y=50,width=550,height=580)

    tk.Label(temp_frame,text="Write Below",font=("Sacramento",60,'bold'),bg="#707070").pack(pady=(60,30))
    Submit_text = tk.Text(temp_frame,height=10,width=50,font="lucida 13",bg="#cfd3ce")
    Submit_text.pack(pady=(20,0))

    # Encrypt and Decrypt buttons
    tk.Button(temp_frame,cursor='hand2',bg="#cfd3ce",text="Encrypt",font=("monotype corsiva",15,'bold'),width=15,command=encrypt_message).place(x=45,y=470)
    tk.Button(temp_frame,cursor='hand2',bg="#cfd3ce",text="Decrypt",font=("monotype corsiva",15,'bold'),width=15,command=decrypt_message).place(x=330,y=470)

def create_database():
    """
     create a table in the the database
    """
    ## create a new database or connect to one
    conn = sqlite3.connect("Database/AudioDiary_Users.db")

    ## create a cursor
    cur = conn.cursor()

    ## create table (needs to be executed only once)
    cur.execute("""CREATE TABLE User_Details (
            First_Name text,
            Last_Name text,
            Contact_No integer,
            Email text,
            Security_Ques text,
            Answer text,
            Password text
            )""")

    ## commit changes in the database
    conn.commit()

    ## close connection
    conn.close()

def hide_log_frame():
    """
    destroys all the widgets in the log_frame and hides the log_frame
    """

    # loop for destroying all the widgets inside the log_frame
    for widget in log_frame.winfo_children():
        widget.destroy()
    log_frame.pack_forget()

def hide_notepad():
    """
    destroys all the widgets in the TextArea and hides the TextArea
    """

    # loop for destroying all the widgets inside the TextArea
    for widget in TextArea.winfo_children():
        widget.destroy()
    TextArea.delete('1.0',tk.END)
    TextArea.forget()

def notepad():
    """
    creates an empty text area to be used as a notepad
    """
    # hides the main_frame
    main_frame.pack_forget()
    # hides the menu_frame
    menu_frame.pack_forget()
    # hides the log_frame
    hide_log_frame()
    # hides the login frame
    login_frame.pack_forget()

    if not TextArea.winfo_ismapped():
        # display a system message
        messagebox.showinfo("Audio Diary","Notepad - By Audio Diary",parent=root)
    if TextArea.winfo_exists():
        hide_notepad()
    # Checking if TextArea is already mapped
    # Packing the TextArea
    TextArea.pack(expand=True, fill=tk.BOTH)
    
    #Adding Scrollbar using Tkinter
    Scroll = tk.Scrollbar(TextArea)
    Scroll.pack(side=tk.RIGHT,  fill=tk.Y)
    Scroll.config(command=TextArea.yview)
    TextArea.config(yscrollcommand=Scroll.set)

def newFile():
    """
    create a new text file
    """
    # Calling the notepad function to create an empty TextArea 
    notepad()
    global file
    # changing the title of the GUI window
    root.title("Untitled - Audio Diary")
    file = None

def openFile():
    """
    open a pre-exsisting file
    """
    global file
    # Give the user an option to open a Specific File
    file = askopenfilename(defaultextension=".txt",
                           filetypes=[("All Files", "*.*"),
                                     ("Text Documents", "*.txt")])
    if file == "":
        file = None
    else:
        # change the title of the GUI
        root.title(os.path.basename(file) + " - Audio Diary")
        notepad()
        # read the specified file
        f = open(file, "r")
        # write the file in the TextArea
        TextArea.insert(1.0, f.read())
        # close the file
        f.close()

def saveFile():
    """
    Save the text of the TextArea into a file
    """
    # Checking if the TextArea is mapped
    if TextArea.winfo_ismapped():
        global file
        # Saving a new file
        if file == None:
            # Saving the file Directory
            file = asksaveasfilename(initialfile = 'Untitled.txt', defaultextension=".txt",
                            filetypes=[("All Files", "*.*"),
                                        ("Text Documents", "*.txt")])
            if file =="":
                file = None

            else:
                #Save as a new file
                f = open(file, "w")
                f.write(TextArea.get(1.0, tk.END))
                f.close()

                root.title(os.path.basename(file) + " - Audio Diary")
                print("File Saved")
        # Saving an exsisting file
        else:
            f = open(file, "w")
            f.write(TextArea.get(1.0, tk.END))
            f.close()

    else:
        # Displaying an Error Message
        messagebox.showerror("Error","Audio Diary - No File to Save",parent=root)

def quitApp():
    """
    Exiting the App
    """
    # destroying the root
    result = messagebox.askquestion("Exit","Do You Want to Quit?")
    if result == 'yes':
        messagebox.showinfo("Exit","Thanks for Using Audio Diary!!",parent=root)
        root.destroy()

def cut():
    """
    Providing the CUT Functionallity
    """
    TextArea.event_generate(("<<Cut>>"))

def copy():
    """
    Providing the COPY Functionallity
    """
    TextArea.event_generate(("<<Copy>>"))

def paste():
    """
    Providing the PASTE Functionallity
    """
    TextArea.event_generate(("<<Paste>>"))

def Speak():
    """
    provides user with a window to perform text to speech 
    """
    global page_img
    # clearing the previous frames
    main_frame.pack_forget()
    menu_frame.pack_forget()
    # destroying the log_frame widgets 
    for widget in log_frame.winfo_children():
        widget.destroy()
    login_frame.pack_forget()
    TextArea.pack_forget()

    log_frame.pack(expand=True, fill=tk.BOTH)

    # Add a Backgroung Image
    page_img = tk.PhotoImage(file = "images/page_img.png")
    tk.Label(log_frame,bg="#707070",image = page_img).place(x=0, y=0, relwidth=1, relheight=1)

    def multi():
        """
        creates a thread for speak1 function 
        """
        threading.Thread(target=speak1).start()

    def speak1():
        """
        perforn speech to text
        """
        text = Submit_text.get(1.0, tk.END)
        # init function to get an engine instance for the speech synthesis  
        engine = pyttsx3.init() 
  
        # say method on the engine that passing input text to be spoken 
        engine.say(text) 
  
        # run and wait method, it processes the voice commands.  
        engine.runAndWait()

    # creating a temporary frame
    temp_frame = tk.Frame(log_frame,bg="#707070",highlightthickness=5,highlightbackground="#cfd3ce")
    temp_frame.place(x=340,y=50,width=550,height=580)

    tk.Label(temp_frame,text="Write Below",font=("Sacramento",60,'bold'),bg="#707070").pack(pady=(60,30))
    Submit_text = tk.Text(temp_frame,height=10,width=50,font="lucida 13",bg="#cfd3ce")
    Submit_text.pack(pady=(20,0))

    # Speak and Home buttons
    tk.Button(temp_frame,cursor='hand2',bg="#cfd3ce",text="Speak",font=("monotype corsiva",15,'bold'),width=15,command=multi).place(x=45,y=470)
    tk.Button(temp_frame,cursor='hand2',bg="#cfd3ce",text="Home",font=("monotype corsiva",15,'bold'),width=15,command=Home).place(x=330,y=470)

def Home():
    """
    clears the GUi window and repacks the Home screen and resets the working directory to its original state
    """
    # clearing the login screen
    for widget in login_frame.winfo_children():
        widget.destroy()
    login_frame.pack_forget()

    # clearing the menu screen
    for widget in menu_frame.winfo_children():
        widget.destroy()
    menu_frame.pack_forget()

    # clearng the log frame
    hide_log_frame()

    # clearing the notepad screen
    TextArea.pack_forget()
    # repacking the home screen
    main_frame.pack(expand=True, fill=tk.BOTH)
    # Changing the directory to its original 
    global par_dir, counter_par_direct
    par_dir = counter_par_direct

def sign_up():
    """
    provides a window for registering in the database and creating an account
    """
    def clear():
        """
        Clears the entry fields once the registration form is submitted
        """
        entry_fname.delete(0,tk.END)
        entry_lname.delete(0,tk.END)
        entry_contact.delete(0,tk.END)
        entry_email.delete(0,tk.END)
        entry_pass.delete(0,tk.END)
        entry_cpass.delete(0,tk.END)
        entry_answer.delete(0,tk.END)
        combo_ques.current(0)

    def register():
        """
        Takes the values from the registration form and either registers the user or gives an appropriate error whichever is needed
        """
        # checking if any field in the form is empty
        if entry_fname.get()=="" or entry_lname.get()=="" or entry_contact.get()=="" or entry_email.get()=="" or combo_ques.get()=="Select" or entry_answer.get()=="" or entry_pass.get()=="" or entry_cpass.get()=="":
            messagebox.showerror("Error","All fields are Mandatory",parent=login_frame)
        # Checking if password is same as confirm password
        elif entry_pass.get() != entry_cpass.get() :
            messagebox.showerror("Error","Confirm Password should be same as Password",parent=login_frame)
        # Checking if the checkbox was selecked or not
        elif check_var.get() == 0 :
            messagebox.showerror("Error","Agree to our Terms and Conditions",parent=login_frame)
        else:
            try:
                ## create a new database or connect to one
                conn = sqlite3.connect("Database/AudioDiary_Users.db")
                ## create a cursor
                cur = conn.cursor()
                # checking if the email is already registered
                cur.execute("SELECT * FROM User_Details WHERE Email = ?",(entry_email.get(),))
                row = cur.fetchone()
                if row == None :
                    # inserting the data in the table in the database
                    cur.execute("INSERT INTO User_Details VALUES ( :First_Name, :Last_Name, :Contact_No, :Email, :Security_Ques, :Answer, :Password)",
                            {
                                'First_Name' : entry_fname.get(),
                                'Last_Name' : entry_lname.get(),
                                'Contact_No' : entry_contact.get(),
                                'Email' : entry_email.get(),
                                'Security_Ques' : combo_ques.get(),
                                'Answer' : entry_answer.get(),
                                'Password' : entry_pass.get()
                            })
                    ## commit changes
                    conn.commit()
                    messagebox.showinfo("Success","Registration Successfull",parent=login_frame)
                    # creating a folder for the newly registered user
                    temp_par_dir = os.path.join(par_dir , entry_email.get())
                    os.mkdir(temp_par_dir)
                    clear()
                else:
                    messagebox.showerror("Error","User Already Exists!",parent=login_frame)
                ## close connection
                conn.close()
                
            except Exception as e:
                messagebox.showerror("Error",f"Error due to {e}",parent=login_frame)
            
        
    # clearing the login screen
    global login_frame
    for widget in login_frame.winfo_children():
        widget.destroy()
    login_frame.pack_forget()
    ## making global image variables
    global register_bg , register_bg1 , register_left
    # creating the sign up screen
    login_frame = tk.Frame(root,bg="white")
    login_frame.pack(expand=True, fill=tk.BOTH)

    ## setting back-ground images
    register_bg1 = ImageTk.PhotoImage(file="images/login_bg2.png")
    tk.Label(login_frame,image=register_bg1).place(x=0,y=0,relwidth=1,relheight=1)
    register_bg = ImageTk.PhotoImage(file="images/register_bg.png")
    tk.Label(login_frame,image=register_bg).place(x=250,y=0,relwidth=1,relheight=1)
    register_left = ImageTk.PhotoImage(file="images/register_left.png")
    tk.Label(login_frame,image=register_left).place(x=80,y=100,width=400,height=500)

    # creating inside frame
    frame1 = tk.Frame(login_frame,bg="#bbbbbb")
    frame1.place(x=480,y=100,width=700,height=500)

    title = tk.Label(frame1,text="Sign Up Here",font=("times new roman",25,'bold'),bg="#bbbbbb",fg="#000000")
    title.pack(pady=(30,0))

    # creaing entries for the form

    #####-----row1(first name and last name)
    f_name = tk.Label(frame1,text="First Name :",font=("times new roman",15,'bold'),bg="#bbbbbb",fg="#433d3c")
    f_name.place(x=50,y=100)
    entry_fname = tk.Entry(frame1,font=("times new roman",15))
    entry_fname.place(x=50,y=130,width=250)

    l_name = tk.Label(frame1,text="Last Name :",font=("times new roman",15,'bold'),bg="#bbbbbb",fg="#433d3c")
    l_name.place(x=370,y=100)
    entry_lname = tk.Entry(frame1,font=("times new roman",15))
    entry_lname.place(x=370,y=130,width=250)

    #####-----row2(contact no. and email)
    contact_no = tk.Label(frame1,text="Contact No. :",font=("times new roman",15,'bold'),bg="#bbbbbb",fg="#433d3c")
    contact_no.place(x=50,y=170)
    entry_contact = tk.Entry(frame1,font=("times new roman",15),bg="#707070",fg="#ffffff")
    entry_contact.place(x=50,y=200,width=250)

    email = tk.Label(frame1,text="Email :",font=("times new roman",15,'bold'),bg="#bbbbbb",fg="#433d3c")
    email.place(x=370,y=170)
    entry_email = tk.Entry(frame1,font=("times new roman",15),bg="#707070",fg="#ffffff")
    entry_email.place(x=370,y=200,width=250)

    #####-----row3(security question and answer)
    question = tk.Label(frame1,text="Security Question :",font=("times new roman",15,'bold'),bg="#bbbbbb",fg="#433d3c")
    question.place(x=50,y=240)
    combo_ques = ttk.Combobox(frame1,font=("times new roman",13),state='readonly',justify=tk.CENTER)
    combo_ques['values'] = ("Select","Your Pet Name","Your Birth Place","Your Birth Date")
    combo_ques.place(x=50,y=270,width=250)
    combo_ques.current(0) 

    answer = tk.Label(frame1,text="Answer :",font=("times new roman",15,'bold'),bg="#bbbbbb",fg="#433d3c")
    answer.place(x=370,y=240)
    entry_answer = tk.Entry(frame1,font=("times new roman",15))
    entry_answer.place(x=370,y=270,width=250)

    #####-----row4(password and confirm password)
    password = tk.Label(frame1,text="Password :",font=("times new roman",15,'bold'),bg="#bbbbbb",fg="#433d3c")
    password.place(x=50,y=310)
    entry_pass = tk.Entry(frame1,font=("times new roman",15),bg="#707070",fg="#ffffff",show="*")
    entry_pass.place(x=50,y=340,width=250)

    c_password = tk.Label(frame1,text="Confirm Password :",font=("times new roman",15,'bold'),bg="#bbbbbb",fg="#433d3c")
    c_password.place(x=370,y=310)
    entry_cpass = tk.Entry(frame1,font=("times new roman",15),bg="#707070",fg="#ffffff",show="*")
    entry_cpass.place(x=370,y=340,width=250)

    # checkbox
    check_var = tk.IntVar()
    terms_check = tk.Checkbutton(frame1,text="I Agree With The Terms And Condtions *",font=("times new roman",12,'bold'),bg="#bbbbbb",fg="#433d3c",variable=check_var,onvalue=1,offvalue=0)
    terms_check.place(x=50,y=380)

    # sign up button
    reg_button = tk.Button(frame1,text="Sign Up -->",font=("times new roman",11,'bold'),bg="#000000",fg="#ffffff",cursor='hand2',command=register)
    reg_button.place(x=50,y=420,width=250)

    # login button
    login_button = tk.Button(login_frame,text="Sign In",font=("times new roman",20,'bold'),bg="#ffffff",fg="#000000",cursor='hand2',command=sign_in)
    login_button.place(x=180,y=520,width=200)

def sign_in():
    """
    creates a window and provides functionality for the login screen of the application
    """
    def login():
        """
        provides functionality to the login screen
        """
        # checks if the any entry fields are empty
        if entry_email.get()=="" or entry_pass.get()=="":
            messagebox.showerror("Error","All Fields are Mandatory!",parent=login_frame)
        # checks if the user is registered in the database
        else:
            try:
                ## create a new database or connect to one
                conn = sqlite3.connect("Database/AudioDiary_Users.db")
                ## create a cursor
                cur = conn.cursor()
                cur.execute("select * from User_Details where Email = ? AND Password = ?",(entry_email.get(),entry_pass.get()))
                row = cur.fetchone()
                ## close connection
                conn.close()
                if row == None:
                    messagebox.showerror("Error","INVALID USERNAME & PASSWORD",parent=login_frame)
                else:
                    messagebox.showinfo("Success","LOGIN Successful , Welcome",parent=login_frame)
                    # changing the directory to the users personal folder
                    global par_dir
                    par_dir = os.path.join(par_dir , entry_email.get())
                    # providing entry to the main menu
                    program_menu()
            except Exception as e:
                messagebox.showerror("Error",f"Error Due to : {str(e)}",parent=login_frame)


    # clearing the sign_up screen
    global login_frame
    for widget in login_frame.winfo_children():
        widget.destroy()
    login_frame.pack_forget()

    #clearing the main screen
    main_frame.pack_forget()

    ## making global image variables
    global login_bg1 , login_bg2 , login_left , icon_img
    
    # setting the base frame for login screen
    login_frame.pack(expand=True, fill=tk.BOTH)

    ## setting back-groung images
    login_bg1 = ImageTk.PhotoImage(file="images/login_bg1.png")
    tk.Label(login_frame,image=login_bg1).place(x=0,y=0,relwidth=1,relheight=1)

    login_bg2 = ImageTk.PhotoImage(file="images/login_bg2.png")
    tk.Label(login_frame,image=login_bg2).place(x=250,y=0,relwidth=1,relheight=1)

    login_left = ImageTk.PhotoImage(file="images/login_left.png")
    tk.Label(login_frame,image=login_left).place(x=80,y=100,width=400,height=500)

    # creating the inside frame
    frame1 = tk.Frame(login_frame,bg="#9ddfd3")
    frame1.place(x=480,y=100,width=700,height=500)

    # inserting an icon in the login screen
    icon_img = ImageTk.PhotoImage(file="images/img.png")
    tk.Label(frame1,image=icon_img,bg="#9ddfd3").place(x=470,y=170,width=150,height=150)

    title = tk.Label(frame1,text="Log In Here",font=("times new roman",35,'bold'),bg="#9ddfd3",fg="#B00857")
    title.pack(pady=(40,0))

    # setting an entry form
    #####-----row1(email address)
    email = tk.Label(frame1,text="Email Address :",font=("times new roman",18,'bold'),bg="#9ddfd3",fg="#433d3c")
    email.place(x=50,y=150)
    entry_email = tk.Entry(frame1,font=("times new roman",15),bg="#ffdada",fg="#6a097d")
    entry_email.place(x=50,y=180,width=350,height=30)

    #####-----row2(password)
    password = tk.Label(frame1,text="Password :",font=("times new roman",18,'bold'),bg="#9ddfd3",fg="#433d3c")
    password.place(x=50,y=250)
    entry_pass = tk.Entry(frame1,font=("times new roman",15),bg="#ffdada",fg="#6a097d",show="*")
    entry_pass.place(x=50,y=280,width=350,height=30)

    # registration button
    reg_button = tk.Button(frame1,text="Don't have an account? Sign Up",font=("times new roman",12),bg="#9ddfd3",fg="#6a097d",cursor='hand2',bd=0,command=sign_up)
    reg_button.place(x=45,y=315)

    # forget password button
    forget_button = tk.Button(frame1,text="Forgot Password?",font=("times new roman",12),bg="#9ddfd3",fg="#ec0101",cursor='hand2',bd=0,command=forget_pass)
    forget_button.place(x=280,y=315)

    # login button
    login_button = tk.Button(frame1,text="Login",font=("times new roman",20,'bold'),bg="#ea86b6",fg="#ffffff",cursor='hand2',command=login)
    login_button.place(x=45,y=355,width=180,height=40)

    # home button
    home_button = tk.Button(login_frame,text="Home",font=("times new roman",20,'bold'),bg="#ea86b6",fg="#ffffff",cursor='hand2',command=Home)
    home_button.place(x=180,y=570,width=200)

def forget_pass():
    """
    changes the password in the database based on the security question
    """

    # creating global image variables
    global lock_img
    # creating a top level window
    forget_frame = tk.Toplevel(bg="#a3d2ca")
    # changing top level title
    forget_frame.title("Forget Password")
    # changing top level icon
    forget_frame.wm_iconbitmap(r"images\diary.ico")
    # setting the dimensions for the top level
    forget_frame.geometry("500x600+480+50")
    # changing the focus to the top level by default
    forget_frame.focus_force()
    # prevents background activity while the top level is mapped
    forget_frame.grab_set()

    def submit():
        """
        checks if the said email is registered in the database or not
        """
        def pass_update():
            """
            changes the password with the new provided password in the database
            """
            # checks if the entry fields are empty
            if entry_npass.get()=="" or entry_cnpass.get()=="":
                messagebox.showerror("Error","All Fields are Mandatory!",parent=forget_frame)
            # checks if the new password and confirm new password are same
            elif entry_npass.get() != entry_cnpass.get() :
                messagebox.showerror("Error","Confirm Password should be same as Password",parent=forget_frame)
            else:
                try:
                    ## create a new database or connect to one
                    conn = sqlite3.connect("Database/AudioDiary_Users.db")
                    ## create a cursor
                    cur = conn.cursor()
                    # updates the old password with the new one
                    cur.execute("UPDATE User_Details SET Password = ? where Email = ?",(entry_npass.get(),row_email))
                    ## commit changes
                    conn.commit()
                    ## close connection
                    conn.close()
                    messagebox.showinfo("Success","Your Password has been Reset , Login with your new password",parent=forget_frame)
                    # destroying the top level
                    forget_frame.destroy()

                except Exception as e:
                    messagebox.showerror("Error",f"Error Due to : {str(e)}",parent=forget_frame)
            

        
        # checks if the entry fields are empty
        if entry_email.get()=="" or combo_ques.get()=="Select" or entry_answer.get()=="":
            messagebox.showerror("Error","All Fields are Mandatory!",parent=forget_frame)
        else:
            try:
                ## create a new database or connect to one
                conn = sqlite3.connect("Database/AudioDiary_Users.db")
                ## create a cursor
                cur = conn.cursor()
                cur.execute("select * from User_Details where Email = ? AND Security_Ques = ? AND Answer = ?",(entry_email.get(),combo_ques.get(),entry_answer.get()))
                row = cur.fetchone()
                row_email = entry_email.get()
                ## close connection
                conn.close()
                if row == None:
                    messagebox.showerror("Error","INVALID USER",parent=forget_frame)
                else:
                    # destroying the email labrl and entry fields
                    email.destroy()
                    entry_email.destroy()
                    # destroying the security ques label and entry fields
                    question.destroy()
                    combo_ques.destroy()
                    # destroying the answer label and entry fields
                    answer.destroy()
                    entry_answer.destroy()
                    # destroying the submit button
                    submit_button.destroy()

                    # creating new labels and fields for new password
                    new_password = tk.Label(forget_frame,text="New Password :",font=("times new roman",15,'bold'),bg="#a3d2ca",fg="#433d3c")
                    new_password.pack(pady=(30,0))
                    entry_npass = tk.Entry(forget_frame,font=("times new roman",15),show="*")
                    entry_npass.pack(pady=(0,10))

                    # creating new labels and fields for confirm new password
                    cn_password = tk.Label(forget_frame,text="Confirm New Password :",font=("times new roman",15,'bold'),bg="#a3d2ca",fg="#433d3c")
                    cn_password.pack(pady=(50,0))
                    entry_cnpass = tk.Entry(forget_frame,font=("times new roman",15),show="*")
                    entry_cnpass.pack(pady=(0,10))

                    # Reset pass button
                    submit_button1 = tk.Button(forget_frame,text="Reset Password",font=("times new roman",16,'bold'),bg="#892cdc",fg="#ffffff",cursor='hand2',command=pass_update,width=16)
                    submit_button1.pack(pady=(40,0))

            except Exception as e:
                messagebox.showerror("Error",f"Error Due to : {str(e)}",parent=forget_frame)

    # inserting a logo 
    lock_img = ImageTk.PhotoImage(file="images/padlock.png")
    tk.Label(forget_frame,image=lock_img,bg="#a3d2ca").pack(pady=(20,5))

    l1 = tk.Label(forget_frame,text="Trouble Logging In",font=("times new roman",20,"bold"),bg="#a3d2ca")
    l1.pack()

    email = tk.Label(forget_frame,text="Email Address :",font=("times new roman",15,'bold'),bg="#a3d2ca",fg="#433d3c")
    email.pack(pady=(30,0))
    entry_email = tk.Entry(forget_frame,font=("times new roman",15))
    entry_email.pack(pady=(0,10))

    question = tk.Label(forget_frame,text="Security Question :",font=("times new roman",15,'bold'),bg="#a3d2ca",fg="#433d3c")
    question.pack(pady=(20,0))

    # creating a combo box
    combo_ques = ttk.Combobox(forget_frame,font=("times new roman",13),state='readonly',justify=tk.CENTER)
    combo_ques['values'] = ("Select","Your Pet Name","Your Birth Place","Your Birth Date")
    combo_ques.pack(pady=(0,10))
    combo_ques.current(0) 

    answer = tk.Label(forget_frame,text="Answer :",font=("times new roman",15,'bold'),bg="#a3d2ca",fg="#433d3c")
    answer.pack(pady=(20,0))
    entry_answer = tk.Entry(forget_frame,font=("times new roman",15))
    entry_answer.pack(pady=(0,10))

    # submit button
    submit_button = tk.Button(forget_frame,text="Submit",font=("times new roman",16,'bold'),bg="#892cdc",fg="#ffffff",cursor='hand2',command=submit,width=16)
    submit_button.pack(pady=(40,0))

def about():
    """
    tells information about the software
    """
    showinfo("Audio Diary", "Audio Diary by Lakshit Bisht")

def program_menu1():
    """
    hides the log screen and repacks the menu frame
    """
    hide_log_frame()
    menu_frame.pack(expand=True, fill=tk.BOTH)

def program_menu():
    """
    clears the window and creates the main menu screen providing the various options
    """
    #clears the login/register screen
    login_frame.pack_forget()

    # packing the menu frame
    menu_frame.pack(expand=True, fill=tk.BOTH)

    # Add a Backgroung Image
    global menu_bg_img, log_img, review_img, edit_img,  delete_img, exit_img
    menu_bg_img = tk.PhotoImage(file = "images/menu_bg.png")
    tk.Label(menu_frame,image = menu_bg_img).place(x=0, y=0, relwidth=1, relheight=1)

    log_img = ImageTk.PhotoImage(Image.open("images\\Log.png"))
    review_img = ImageTk.PhotoImage(Image.open("images\\Review.png"))
    edit_img = ImageTk.PhotoImage(Image.open("images\\Edit.png"))
    delete_img = ImageTk.PhotoImage(Image.open("images\\Delete.png"))
    exit_img = ImageTk.PhotoImage(Image.open("images\\Exit.png"))

    # creating various buttons for various options
    tk.Button(menu_frame,image=log_img, bg="#374045",bd=0 ,cursor='hand2',command=log).place(x=1210,y=61)
    tk.Button(menu_frame,image=review_img, bg="#374045",bd=0 ,cursor='hand2',command=rev_view).place(x=1210,y=193)
    tk.Button(menu_frame,image=edit_img, bg="#374045",bd=0 ,cursor='hand2',command=update).place(x=1210,y=335)
    tk.Button(menu_frame,image=delete_img, bg="#374045",bd=0 ,cursor='hand2',command=dele).place(x=1210,y=476)
    tk.Button(menu_frame,image=exit_img, bg="#374045",bd=0 ,cursor='hand2',command=quitApp).place(x=1210,y=623)

def log():
    """
    logs the entries into the file with the current timestamp
    """
    # global image variable
    global page_img
    
    def typ():
        """
        provides a text area to type the entries
        """
        def get_data():
            """
            inputs the text from the text area and writes into the file
            """
            global content
            # taking input text from text area
            content = Submit_text.get(1.0, tk.END)
            # checking if text area is empty
            if content == "\n":
                tk.messagebox.showerror("Error","Text Field Cannot Be Empty!")
            else :
                # creating a new file if it doesn't already exists
                f = open(path+"\\"+file_name+".txt","a")
                # writing the time stamp into the file
                f.write(str(datetime.datetime.now()))
                # logging the entry
                f.write("\t"+content)
                f.close()
                messagebox.showinfo("Success","Logged Successfully!!",parent=log_frame)
                # clearing the text area
                Submit_text.delete(1.0,tk.END)

        # clearing the temp frame
        for widget in temp_frame.winfo_children():
            widget.pack_forget()
        tk.Label(temp_frame,text="Write Below",font=("Sacramento",60,'bold'),fg="#000000",bg="#bbbbbb").pack(pady=(60,30))
        # creating the input text field
        Submit_text = tk.Text(temp_frame,height=10,width=50,font="lucida 13",bg="#fff3e2")
        Submit_text.pack(pady=(5,5))
        # log button
        tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Log",font=("monotype corsiva",15,'bold'),width=13,cursor='hand2',command=get_data).place(x=40,y=450)
        # menu button
        tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Main Menu",font=("monotype corsiva",15,'bold'),width=13,cursor='hand2',command=program_menu1).place(x=345,y=450)

    def multi():
        """
        creates a second thread for speech recognition
        """
        # clearing the temp frame
        for widget in temp_frame.winfo_children():
            widget.pack_forget()
        # creating a secondary thread for listen function
        threading.Thread(target=listen).start()

    def listen():
        """
        performs speech to text conversion
        """
        content = ""

        # creating text field
        global entry_text
        entry_text = tk.Text(temp_frame,height=13,width=50,font="lucida 13",bg="#fff3e2")
        
        r = sr.Recognizer()
        mic = sr.Microphone(device_index=1)
        
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1)
            stat1 = tk.Label(temp_frame,text="Say Something......",bg="#bbbbbb",fg="#433d3c",font=("monotype corsiva",25,'bold'))
            stat1.pack(pady=(20,10))
            audio = r.listen(source)
            stat2 = tk.Label(temp_frame,text="Time's up, Thanks !!",bg="#bbbbbb",fg="#433d3c",font=("monotype corsiva",25,'bold'))
            stat2.pack(pady=(5,5))
        try:
            text = r.recognize_google(audio)
            content = text
            # packing the text field
            entry_text.pack(pady=(15,5))
            # inserting text into the field
            entry_text.insert(1.0,content)
            
        except:
            for widget in temp_frame.winfo_children():
                widget.destroy()
            # creating unable to understand label
            stat3 = tk.Label(temp_frame,text="Unable to understand, please repeat :",bg="#bbbbbb",fg="#433d3c",font=("monotype corsiva",25,'bold'))
            # checkng if label is mapped or not
            stat3.pack(pady=(10,5))
            listen()
        
        def store():
            """
            writes the text received after speech to text conversion into the file 
            """
            content = entry_text.get(1.0, tk.END)
            # creating a new file if it doesn't already exists
            f = open(path+"\\"+file_name+".txt","a")
            # writing the timestamp
            f.write(str(datetime.datetime.now()))
            # logging the actual entry
            f.write("\t"+content)
            f.close()
            messagebox.showinfo("Success","Logged Successfully!!",parent=log_frame)
            # diverting back to main menu
            program_menu1()
        
        # log button
        tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Log",font=("monotype corsiva",15,'bold'),width=13,cursor='hand2',command=store).place(x=40,y=500)
        # menu button
        tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Main Menu",font=("monotype corsiva",15,'bold'),width=13,cursor='hand2',command=program_menu1).place(x=345,y=500)


    # clearing the menu screen  
    menu_frame.pack_forget()
    # setting the log frame
    log_frame.pack(expand=True, fill=tk.BOTH)

    # creating a new folder if it doesn't exist
    date = datetime.date.today()
    folder_name = str(date.year)
    file_name = str(date.month)
    # creating a path for the new directory
    path = os.path.join(par_dir , folder_name)
    try:
        # creating the directory
        os.mkdir(path)
    except:
      pass

    # Add a Backgroung Image
    page_img = tk.PhotoImage(file = "images/page_img.png")
    tk.Label(log_frame,bg="#707070",image = page_img).place(x=0, y=0, relwidth=1, relheight=1)

    # creating a temporary frame
    temp_frame = tk.Frame(log_frame,bg="#bbbbbb",highlightthickness=5,highlightbackground="#433d3c")
    temp_frame.place(x=340,y=50,width=550,height=600)

    tk.Label(temp_frame,text="Select from the following :",font=("Sacramento",40,'bold'),fg="#000000",bg="#bbbbbb").pack(pady=(80,15))
    # speak button
    speak_button=tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="1. Speak",font=("monotype corsiva",18,'bold'),width=25,cursor='hand2',command=multi)
    # type button
    type_button=tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="2. Type",font=("monotype corsiva",18,'bold'),width=25,cursor='hand2',command=typ)
    # placing the buttons on the temp frame
    speak_button.pack(pady=(75,10))
    type_button.pack(pady=(35,10))

def rev_view():
    """
    reads the files and writes the entries onto the screen
    """
    # global image variable
    global page_img
    # clearing the menu screen
    menu_frame.pack_forget()
    log_frame.pack(expand=True, fill=tk.BOTH)
     # Add a Backgroung Image
    page_img = tk.PhotoImage(file = "images/page_img.png")
    tk.Label(log_frame,bg="#707070",image = page_img).place(x=0, y=0, relwidth=1, relheight=1)

    # creating a temporary frame
    temp_frame = tk.Frame(log_frame,bg="#bbbbbb",highlightthickness=5,highlightbackground="#433d3c")
    temp_frame.place(x=340,y=30,width=550,height=650)

    # creating a text area
    Submit_text = tk.Text(temp_frame,height=20,width=50,font="lucida 13",bg="#fff3e2")

    def multi():
        """
        creates a thread for speak1 function 
        """
        threading.Thread(target=speak1).start()

    def speak1():
        """
        perforn speech to text
        """
        text = Submit_text.get(1.0, tk.END)
        # init function to get an engine instance for the speech synthesis  
        engine = pyttsx3.init() 
  
        # say method on the engine that passing input text to be spoken 
        engine.say(text) 
  
        # run and wait method, it processes the voice commands.  
        engine.runAndWait()

    # @dispatch is used to implement function overloading
    @dispatch(str , str)
    def review(year , month):
        """
        reads and writes the entries of the whole month
        """
        # clearing the temp frame
        for widget in temp_frame.winfo_children():
            widget.pack_forget()
        # changing the path to that of the file
        path = par_dir + "\\" + year + "\\" + month + ".txt"
        try:
            # opening the file
            f = open(path)
            # changing the title of the application window
            root.title(os.path.basename(path) + " - Audio Diary")
            
            # packing the text area
            Submit_text.pack(pady=(50,30))
            # inserting text from the file to the text area
            Submit_text.insert(1.0, f.read())
            # closing the file
            f.close()
            # checking if there is entries of that particular day
            if Submit_text.get(1.0,tk.END) == "\n" :
                # destroying the text area
                Submit_text.destroy()
                messagebox.showerror("Error","No Data found!",parent=temp_frame)
                spin1()
            else:
                # speak button
                tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Speak",cursor='hand2',font=("monotype corsiva",15,'bold'),width=15,command=multi).place(x=45,y=480)
                # main menu button
                tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Main Menu",cursor='hand2',font=("monotype corsiva",15,'bold'),width=15,command=program_menu1).place(x=320,y=480)
        except:
            messagebox.showerror("Error","No File found!",parent=temp_frame)
            spin1()

    @dispatch(str , str , str)
    def review(year , month , day):
        """
        reads the complete file but only writes the entrirs of a particular day
        """
        # clearing the temp frame
        for widget in temp_frame.winfo_children():
            widget.pack_forget()

        # changing the path to that of the file
        path = par_dir + "\\" + year + "\\" + month + ".txt"
        try:
            f = open(path)
            # changing the title of the application window
            root.title(os.path.basename(path) + " - Audio Diary")
            # packing the text area
            Submit_text.pack(pady=(50,30))
            # reading the whole file line by line
            lines = f.readlines()
            for line in lines:
                # checking for the entries of a particular day
                if line[8:10] == day or line[8:10] == "0"+day:
                    # inserting the selected entries into the text area
                    Submit_text.insert(1.0, line)
            f.close()
            # checking if there is entries of that particular day
            if Submit_text.get(1.0,tk.END) == "\n" :
                # destroying the text area
                Submit_text.destroy()
                messagebox.showerror("Error","No Data found!",parent=temp_frame)
                spin2()
            else:
                # speak button
                tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Speak",cursor='hand2',font=("monotype corsiva",15,'bold'),width=15,command=multi).place(x=45,y=480)
                # main menu button
                tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Main Menu",cursor='hand2',font=("monotype corsiva",15,'bold'),width=15,command=program_menu1).place(x=320,y=480)

        except:
            messagebox.showerror("Error","No File found!",parent=temp_frame)
            spin2()

    def spin1():
        """
        creates window for reviewing files of the whole month
        """
        # clearing the screen
        button1.pack_forget()
        button2.pack_forget()
        lab1.pack_forget()

        lab1.pack(pady=(80,15))

        # declaring string variable for storing year and month 
        year_var=tk.StringVar() 
        month_var=tk.StringVar()

        def submit(): 
            """
            takes input from the spin box and calls the review function
            """
            # taking input from the spin boxes
            year=year_var.get() 
            month=month_var.get() 

            # calling the review function
            review(year,month)

            # resetting the spin box values
            year_var.set("2020") 
            month_var.set("1") 

        # year spinbox
        tk.Label(temp_frame,text="Year",bg="#bbbbbb",fg="#433d3c",font=("monotype corsiva",25,'bold')).pack(pady=(5,5))
        tk.Spinbox(temp_frame, from_=2020, to=2030, textvariable=year_var,font=("monotype corsiva",16),bg="#fff3e2",state='readonly').pack(pady=(5,10))
        # month spinbox
        tk.Label(temp_frame,text="Month",bg="#bbbbbb",fg="#433d3c",font=("monotype corsiva",25,'bold')).pack(pady=(5,5))
        tk.Spinbox(temp_frame, from_=1, to=12, textvariable=month_var,font=("monotype corsiva",16),bg="#fff3e2",state='readonly').pack(pady=(5,10))
        # submit button
        tk.Button(temp_frame,bg="#707070",text="Submit",cursor='hand2',font=("monotype corsiva",15,'bold'),width=17,command=submit).pack(pady=(30,10))
        # main menu button
        tk.Button(temp_frame,bg="#707070",text="Main Menu",cursor='hand2',font=("monotype corsiva",15,'bold'),width=17,command=program_menu1).pack(pady=(10,10))

    def spin2():
        """
        creates window for reviewing files of a particular month
        """
        button1.pack_forget()
        button2.pack_forget()
        lab1.pack_forget()

        lab1.pack(pady=(60,15))

        # declaring string variable for storing year, month and day
        year_var=tk.StringVar() 
        month_var=tk.StringVar()
        day_var=tk.StringVar()

        def submit(): 
            """
            takes input from the spin box and calls the review function
            """
            # storing values from the spinboxes
            year=year_var.get() 
            month=month_var.get() 
            day=day_var.get() 

            # calling the review function
            review(year,month,day)

            # resetting the spinbox values
            year_var.set("2020") 
            month_var.set("1") 
            day_var.set("1") 

        # year spinbox
        tk.Label(temp_frame,text="Year",bg="#bbbbbb",fg="#433d3c",font=("monotype corsiva",25,'bold')).pack(pady=(5,5))
        tk.Spinbox(temp_frame, from_=2020, to=2030, textvariable=year_var,font=("monotype corsiva",16),bg="#fff3e2",state='readonly').pack(pady=(5,10))
        # month spinbox
        tk.Label(temp_frame,text="Month",bg="#bbbbbb",fg="#433d3c",font=("monotype corsiva",25,'bold')).pack(pady=(5,5))
        tk.Spinbox(temp_frame, from_=1, to=12, textvariable=month_var,font=("monotype corsiva",16),bg="#fff3e2",state='readonly').pack(pady=(5,10))
        # day spinbox
        tk.Label(temp_frame,text="Day",bg="#bbbbbb",fg="#433d3c",font=("monotype corsiva",25,'bold')).pack(pady=(5,5))
        tk.Spinbox(temp_frame, from_=1, to=31, textvariable=day_var,font=("monotype corsiva",16),bg="#fff3e2",state='readonly').pack(pady=(5,10))
        # submit button
        tk.Button(temp_frame,bg="#707070",text="Submit",cursor='hand2',font=("monotype corsiva",15,'bold'),width=17,command=submit).pack(pady=(30,10))
        # main menu button
        tk.Button(temp_frame,bg="#707070",text="Main Menu",cursor='hand2',font=("monotype corsiva",15,'bold'),width=17,command=program_menu1).pack(pady=(10,10))

    lab1 = tk.Label(temp_frame,text="Select from the following :",font=("Sacramento",40,'bold'),fg="#000000",bg="#bbbbbb")
    lab1.pack(pady=(80,15))
    # whole month button
    button1=tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Whole Month",cursor='hand2',font=("monotype corsiva",18,'bold'),width=25,command=spin1)
    # particular day button
    button2=tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Particular Day",cursor='hand2',font=("monotype corsiva",18,'bold'),width=25,command=spin2)
    # mapping the buttons on the screen
    button1.pack(pady=(75,10))
    button2.pack(pady=(35,10))

def update():
    """
    updates the entries in the files
    """
    # global image variable
    global page_img
    # clearing menu screen
    menu_frame.pack_forget()
    # setting the log frame
    log_frame.pack(expand=True, fill=tk.BOTH)
    # Add a Backgroung Image
    page_img = tk.PhotoImage(file = "images/page_img.png")
    tk.Label(log_frame,bg="#707070",image = page_img).place(x=0, y=0, relwidth=1, relheight=1)

    def review(year , month):
        """
        reads and writes the entries of the whole month
        """
        def update1():
            """
            overwrites the current file with the updated file
            """
            # opening the file in write mode
            f = open(path,"w")
            # writes the updated entries into the file
            f.write(Submit_text.get(1.0, tk.END))
            # closing the file
            f.close()
            messagebox.showinfo("Success","Updated Successfully!!",parent=log_frame)
        
        # changing the directory to that of the file
        path = par_dir + "\\" + year + "\\" + month + ".txt"
        try:
            # opening the file in read mode
            f = open(path)
            # changing the title of the application window
            root.title(os.path.basename(path) + " - Audio Diary")
            
            # clearing the temp frame
            for widget in temp_frame.winfo_children():
                widget.pack_forget()

            tk.Label(temp_frame,text="Write Below",font=("Sacramento",60,'bold'),fg="#000000",bg="#bbbbbb").pack(pady=(60,30))
            # creating the text field
            Submit_text = tk.Text(temp_frame,height=10,width=50,font="lucida 13",bg="#fff3e2")
            Submit_text.pack(pady=(5,5))
            # inserting entries from the file into the text area
            Submit_text.insert(1.0, f.read())
            # closing the file
            f.close()
            # update button
            tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Update",cursor='hand2',font=("monotype corsiva",15,'bold'),width=13,command=update1).place(x=40,y=450)
            # main menu button
            tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Main Menu",cursor='hand2',font=("monotype corsiva",15,'bold'),width=13,command=program_menu1).place(x=345,y=450)
        except:
            messagebox.showerror("Error","No Data Found!!",parent=log_frame)

    # declaring string variable for storing year and month 
    year_var=tk.StringVar() 
    month_var=tk.StringVar()

    def submit(): 
        """
        takes input from the spin box and calls the review function
        """
        year=year_var.get() 
        month=month_var.get() 

        review(year,month)

        # resetting the spinbox values
        year_var.set("2020") 
        month_var.set("1") 

    # creating a temporary frame
    temp_frame = tk.Frame(log_frame,bg="#bbbbbb",highlightthickness=5,highlightbackground="#433d3c")
    temp_frame.place(x=340,y=50,width=550,height=600)

    tk.Label(temp_frame,text="Enter the Following :",font=("Sacramento",40,'bold'),fg="#000000",bg="#bbbbbb").pack(pady=(50,30))
    # year spinbox
    tk.Label(temp_frame,text="Year",bg="#bbbbbb",fg="#433d3c",font=("monotype corsiva",25,'bold')).pack(pady=(5,5))
    tk.Spinbox(temp_frame, from_=2020, to=2030, textvariable=year_var,font=("monotype corsiva",16),bg="#fff3e2",state='readonly').pack(pady=(5,10))
    # month spinbox
    tk.Label(temp_frame,text="Month",bg="#bbbbbb",fg="#433d3c",font=("monotype corsiva",25,'bold')).pack(pady=(5,5))
    tk.Spinbox(temp_frame, from_=1, to=12, textvariable=month_var,font=("monotype corsiva",16),bg="#fff3e2",state='readonly').pack(pady=(5,10))
    # submit button
    tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Submit",cursor='hand2',font=("monotype corsiva",15,'bold'),width=17,command=submit).pack(pady=(25,10))
    # main menu button
    tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Main Menu",cursor='hand2',font=("monotype corsiva",15,'bold'),width=17,command=program_menu1).pack(pady=(5,10))

def dele():
    """
    deletes the file of a particular month
    """
    # global image variable
    global page_img
    # clearing menu screen
    menu_frame.pack_forget()
    # setting log frame
    log_frame.pack(expand=True, fill=tk.BOTH)
    # Add a Backgroung Image
    page_img = tk.PhotoImage(file = "images/page_img.png")
    tk.Label(log_frame,bg="#707070",image = page_img).place(x=0, y=0, relwidth=1, relheight=1)

    def delete(year , month):
        """
        deletes the file
        """
        # changing the directory to that of the file
        path = par_dir + "\\" + year + "\\" + month + ".txt"
        # checking if directory exists
        if os.path.exists(path):
            # deleting the file
            result = messagebox.askquestion("Delete","Are you sure you want to delete the file?")
            if result == 'yes':
                os.remove(path)
                messagebox.showinfo("Success","The File was Deleted Successfully!!",parent=log_frame)
        else:
            messagebox.showerror("Error","File does not Exist!!",parent=log_frame)

    def submit():
        """
        takes input from the spin box and calls the review function
        """
        # stores values from the spin boxes
        year=year_var.get() 
        month=month_var.get() 

        delete(year,month)

        # resetting the spin box values
        year_var.set("2020") 
        month_var.set("1")

    # declaring string variable for storing year and month 
    year_var=tk.StringVar() 
    month_var=tk.StringVar()

    # creating a temporary frame
    temp_frame = tk.Frame(log_frame,bg="#bbbbbb",highlightthickness=5,highlightbackground="#433d3c")
    temp_frame.place(x=340,y=50,width=550,height=600)

    tk.Label(temp_frame,text="Enter the Following :",font=("Sacramento",40,'bold'),fg="#000000",bg="#bbbbbb").pack(pady=(50,30))
    # year spinbox
    tk.Label(temp_frame,text="Year",bg="#bbbbbb",fg="#433d3c",font=("monotype corsiva",25,'bold')).pack(pady=(5,5))
    tk.Spinbox(temp_frame, from_=2020, to=2030, textvariable=year_var,cursor='hand2',font=("monotype corsiva",16),bg="#fff3e2",state='readonly').pack(pady=(5,10))
    # month spinbox
    tk.Label(temp_frame,text="Month",bg="#bbbbbb",fg="#433d3c",font=("monotype corsiva",25,'bold')).pack(pady=(25,5))
    tk.Spinbox(temp_frame, from_=1, to=12, textvariable=month_var,cursor='hand2',font=("monotype corsiva",16),bg="#fff3e2",state='readonly').pack(pady=(5,30))
    # submit button
    tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Submit",cursor='hand2',font=("monotype corsiva",15,'bold'),width=17,command=submit).pack(pady=(25,10))
    # main menu button
    tk.Button(temp_frame,bg="#433d3c",fg="#ffffff",text="Main Menu",cursor='hand2',font=("monotype corsiva",15,'bold'),width=17,command=program_menu1).pack(pady=(5,10))


if __name__ == '__main__':
    ## creating a database for the users-needs to be executed only once
    try:
        create_database()
    except:
        pass
        
    # Path of the file
    par_dir =os.path.dirname(os.path.abspath(__file__))
    par_dir = os.path.join(par_dir , "Audio Diary")
    counter_par_direct = par_dir
    try:
        # creating the desired Directory
        os.mkdir(par_dir)    
    except:
        pass

    # Basic tkinter setup
    root = tk.Tk()
    root.geometry("1366x768+0+0")
    root.wm_iconbitmap("images/diary.ico")
    root.title("AUDIO Diary")
    root.resizable(False , False)
    

    # Creating Frames
    main_frame = tk.Frame(root)
    main_frame.pack(expand=True, fill=tk.BOTH)
    # login/register frame
    login_frame = tk.Frame(root)
    # menu frame
    menu_frame = tk.Frame(root)
    # log frame
    log_frame = tk.Frame(root)

    # Add a Backgroung Image
    bg_img = tk.PhotoImage(file = "images/back_g.png")
    tk.Label(main_frame,image = bg_img).place(x=0, y=0, relwidth=1, relheight=1)
    

    # # Add Icon
    # icon = tk.PhotoImage(file = "images/icon.png")
    # tk.Label(main_frame,bg="#532e1c",image = icon).pack(pady=(50,10))
     
    # # Add Heading and Sub-Heading
    # tk.Label(main_frame,bg="#532e1c",fg="#ff4646",text="Audio Diary",font=("Sacramento",70,'bold')).pack(pady=(5,0))
    # tk.Label(main_frame,bg="#532e1c",fg="#66BFBF",text="Keep a diary, and someday it'll keep you!!",font=("Sacramento",30)).pack()


    # Get Started Button
    tk.Button(main_frame,bg="#433d3c",fg="#fff76a",text="Get Started",font=("Times New Roman",15),width=16,command=sign_in,cursor='hand2').pack(pady=(480,5))

    # # Notepad Button
    # tk.Button(main_frame,bg="#433d3c",fg="#fff76a",text="Use as Notepad",font=("Times New Roman",15),width=20,command=notepad,cursor='hand2').pack(pady=(20,20))

    # Lets create a menubar
    MenuBar = tk.Menu(root)

    #File Menu Starts
    FileMenu = tk.Menu(MenuBar, tearoff=0)
    # To navigate to home page
    FileMenu.add_command(label = "Home", command = Home)
    FileMenu.add_separator()
    # To open new file
    FileMenu.add_command(label="New", command=newFile)

    #To Open already existing file
    FileMenu.add_command(label="Open", command = openFile)

    # To save the current file
    FileMenu.add_command(label = "Save", command = saveFile)
    FileMenu.add_separator()
    FileMenu.add_command(label = "Exit", command = quitApp)

    MenuBar.add_cascade(label = "File", menu=FileMenu)
    # File Menu ends

    # Edit Menu Starts
    EditMenu = tk.Menu(MenuBar, tearoff=0)
    # To give a feature of cut, copy and paste
    EditMenu.add_command(label = "Cut", command=cut)
    EditMenu.add_command(label = "Copy", command=copy)
    EditMenu.add_command(label = "Paste", command=paste)

    MenuBar.add_cascade(label="Edit", menu = EditMenu)
    # Edit Menu Ends

    # Miscellaneous Menu Starts
    MiscellaneousMenu = tk.Menu(MenuBar, tearoff=0)
    # To give miscellaneous feature of notepad , speak , encryption/decryption
    MiscellaneousMenu.add_command(label = "Notepad", command=notepad)
    # add a seperator line in the menu
    MiscellaneousMenu.add_separator()
    MiscellaneousMenu.add_command(label = "Speak", command=Speak)
    MiscellaneousMenu.add_separator()
    MiscellaneousMenu.add_command(label = "Encrypt/Decrypt", command=encrypt_decrypt)
    MiscellaneousMenu.add_separator()
    MiscellaneousMenu.add_command(label = "Random Thought", command=Notify)

    MenuBar.add_cascade(label="Miscellaneous", menu = MiscellaneousMenu)
    # Miscellaneous Menu Ends

    # Help Menu Starts
    HelpMenu = tk.Menu(MenuBar, tearoff=0)
    HelpMenu.add_command(label = "About Audio Diary", command=about)
    MenuBar.add_cascade(label="Help", menu=HelpMenu)
    # Help Menu Ends

    # placing the menu bar
    root.config(menu=MenuBar)

    # Add TextArea
    TextArea = tk.Text(root, font="lucida 15",bg="#e08f62")
    file = None
    # displaying thought of the day notification
    Notify()

    root.mainloop()