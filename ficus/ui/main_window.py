import tkinter as tk
from tkinter import messagebox


class UserInterface:
    def __init__(self, master):
        self.master = master
        master.title('Phone Validator')

        self.phone_number = tk.StringVar()
        self.followup_code = tk.StringVar()
        self.logs = []

        self.phone_label = tk.Label(master, text='Phone number')
        self.phone_label.pack()
        self.phone_entry = tk.Entry(master, textvariable=self.phone_number)
        self.phone_entry.pack()

        self.code_label = tk.Label(master, text='Followup Code')
        self.code_label.pack()
        self.code_entry = tk.Entry(master, textvariable=self.followup_code)
        self.code_entry.pack()

        self.submit_button = tk.Button(master, text='Submit', command=self.submit)
        self.submit_button.pack()

        self.print_button = tk.Button(master, text='Print Logs', command=self.print_logs)
        self.print_button.pack()

    def submit(self):
        self.logs.append(f'Phone Number: {self.phone_number.get()} Followup Code: {self.followup_code.get()}')
        messagebox.showinfo("Success", "Data Saved")

    def print_logs(self):
        for log in self.logs:
            print(log)


root = tk.Tk()
ui = UserInterface(root)
root.mainloop()
