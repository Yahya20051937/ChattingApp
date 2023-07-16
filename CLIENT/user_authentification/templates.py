import tkinter as tk
import json
from collections import deque

ROOT = tk.Tk()
ROOT.geometry('600x400')

displayed_pages = deque()  # this data structure will hold the last displayed frame


def user_auth_home_page(func1, func2):
    from functions import handle_new_page

    main_frame = handle_new_page(displayed_pages, ROOT)
    main_frame.pack()

    title_label = tk.Label(main_frame, text='Chatting App', font=('Arial', 20))
    title_label.pack(side='top')

    frame = tk.Frame(main_frame)
    log_in_button = tk.Button(frame, text='Log in', font=('Arial', 12), command=lambda: log_in_page(func2))
    sign_up_button = tk.Button(frame, text='Sign up', font=('Arial', 12), command=lambda: sign_up_page(func1))

    frame.pack(side='top', pady=70)
    log_in_button.pack()
    sign_up_button.pack()


def sign_up_page(func, statement=''):
    from functions import handle_new_page
    from user_authentification.handle_server import user_auth_request, send_user_auth_request

    main_frame = handle_new_page(displayed_pages, ROOT)

    title_label = tk.Label(main_frame, text='Sign up', font=('Arial', 20))
    title_label.pack(side='top')

    frame = tk.Frame(main_frame)
    frame.pack(fill='both', expand=True, pady=80)

    statement_label = tk.Label(frame, text=statement)
    statement_label.pack()

    user_name_frame = tk.Frame(frame)
    user_name = tk.StringVar()
    user_name_label = tk.Label(user_name_frame, text='username:  ', font=('Arial', 12))
    user_name_input = tk.Entry(user_name_frame, textvariable=user_name)
    user_name_frame.pack(fill='x', expand=True)
    user_name_label.pack(side='left', fill='x', expand=True)
    user_name_input.pack(side='right', fill='x', expand=True)

    email_frame = tk.Frame(frame)
    email = tk.StringVar()
    email_label = tk.Label(email_frame, text='email:  ', font=('Arial', 12))
    email_input = tk.Entry(email_frame, textvariable=email)
    email_frame.pack(fill='x', expand=True)
    email_label.pack(side='left', fill='x', expand=True)
    email_input.pack(side='right', fill='x', expand=True)

    password_frame = tk.Frame(frame)
    password = tk.StringVar()
    password_label = tk.Label(password_frame, text='password:  ', font=('Arial', 12))
    password_input = tk.Entry(password_frame, textvariable=password, show='*')
    password_frame.pack(fill='x', expand=True)
    password_label.pack(side='left', fill='x', expand=True)
    password_input.pack(side='right', fill='x', expand=True)

    check_password_frame = tk.Frame(frame)
    check_password = tk.StringVar()
    check_password_label = tk.Label(check_password_frame, text='confirm password:  ', font=('Arial', 12))
    check_password_input = tk.Entry(check_password_frame, textvariable=check_password, show='*')
    check_password_frame.pack(fill='x', expand=True)
    check_password_label.pack(side='left', fill='x', expand=True)
    check_password_input.pack(side='right', fill='x', expand=True)

    submit_button = tk.Button(main_frame, text='Submit', command=lambda: func.send((func,
                                                                                    json.dumps(
                                                                                        {'username': user_name.get(),
                                                                                         'email': email.get(),
                                                                                         'password': password.get(),
                                                                                         'confirm_password': check_password.get()}))))
    submit_button.pack(side='right')


def log_in_page(func, statement=''):
    from functions import handle_new_page
    from user_authentification.handle_server import user_auth_request, send_user_auth_request

    main_frame = handle_new_page(displayed_pages, ROOT)

    title_label = tk.Label(main_frame, text='Log in', font=('Arial', 20))
    title_label.pack(side='top')

    frame = tk.Frame(main_frame)
    frame.pack(fill='both', expand=True, pady=80)

    statement_label = tk.Label(frame, text=statement)
    statement_label.pack()

    user_name_frame = tk.Frame(frame)
    user_name = tk.StringVar()
    user_name_label = tk.Label(user_name_frame, text='username:  ', font=('Arial', 12))
    user_name_input = tk.Entry(user_name_frame, textvariable=user_name)
    user_name_frame.pack(fill='x', expand=True)
    user_name_label.pack(side='left', fill='x', expand=True)
    user_name_input.pack(side='right', fill='x', expand=True)

    password_frame = tk.Frame(frame)
    password = tk.StringVar()
    password_label = tk.Label(password_frame, text='password:  ', font=('Arial', 12))
    password_input = tk.Entry(password_frame, textvariable=password, show='*')
    password_frame.pack(fill='x', expand=True)
    password_label.pack(side='left', fill='x', expand=True)
    password_input.pack(side='right', fill='x', expand=True)

    submit_button = tk.Button(main_frame, text='Submit', command=lambda: func.send((func,
                                                                                    json.dumps(
                                                                                        {'username': user_name.get(),
                                                                                         'password': password.get(),
                                                                                         }))))
    submit_button.pack(side='right')
