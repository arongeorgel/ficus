import tkinter as tk

root = tk.Tk()
root.title("Test Window")
label = tk.Label(root, text="If you see this, tkinter is working!", font=("Arial", 18))
label.pack(pady=20, padx=20)
root.mainloop()