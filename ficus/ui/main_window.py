import tkinter as tk
from tkinter import ttk

class TradingTableApp:
    def __init__(self, root, data):
        self.root = root
        self.root.title("Trading Table")

        # Define columns
        self.columns = ["Trading Pair", "Profit", "Volume", "Stop Loss", "Take Profit"]

        # Create Treeview (table)
        self.tree = ttk.Treeview(root, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=100)

        # Insert data into the table
        self.insert_data(data)

        # Pack the treeview
        self.tree.pack(fill=tk.BOTH, expand=True)

    def insert_data(self, data):
        for row in data:
            self.tree.insert("", "end", values=row)

# Sample data
data = [
    ("BTC/USD", "500", "10", "450", "550"),
    ("ETH/USD", "-300", "15", "290", "320"),
    ("LTC/USD", "100", "5", "90", "120"),
]

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingTableApp(root, data)
    root.mainloop()