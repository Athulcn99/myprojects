import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt

# Database setup
conn = sqlite3.connect("finance.db")
cursor = conn.cursor()
#cursor.execute("DROP TABLE IF EXISTS transactions")
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    description TEXT,
    date TEXT DEFAULT (DATE('now'))
)
""")
conn.commit()

# Functions
def add_transaction():
    try:
        amount = float(amount_entry.get())
        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")
        category = category_var.get()
        if not category:
            raise ValueError("Category is required.")
        description = description_entry.get()
        if not description:
            raise ValueError("Description cannot be empty.")
        
        # Insert into the database
        cursor.execute("INSERT INTO transactions (amount, category, description) VALUES (?, ?, ?)",
                       (amount, category, description))
        conn.commit()

        # Get the inserted transaction with the date
        cursor.execute("SELECT date FROM transactions WHERE id = last_insert_rowid()")
        entry_date = cursor.fetchone()[0]

        # Update the list box
        transactions_list.insert(tk.END, f"{entry_date} | {amount} | {category} | {description}")


        # Clear input fields
        amount_entry.delete(0, tk.END)
        description_entry.delete(0, tk.END)
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid input: {e}")


def show_summary():
    cursor.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
    data = cursor.fetchall()
    if data:
        categories, amounts = zip(*data)
        plt.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=140)
        plt.title("Spending Distribution")
        plt.show()
    else:
        messagebox.showinfo("Info", "No transactions to summarize.")

def export_data():
    import pandas as pd
    cursor.execute("SELECT * FROM transactions")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["ID", "Amount", "Category", "Description", "Date"])
    df.to_csv("transactions.csv", index=False)
    messagebox.showinfo("Success", "Data exported to transactions.csv")


# Reset data function
def reset_data():
    confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to clear all data? This action cannot be undone.")
    if confirm:
        cursor.execute("DELETE FROM transactions")  # Clear all data from the table
        conn.commit()
        transactions_list.delete(0, tk.END)  # Clear the listbox
        messagebox.showinfo("Reset Complete", "All data has been cleared.")


# UI setup
root = tk.Tk()
root.title("Expense Tracker")

# Input fields
tk.Label(root, text="Amount:").grid(row=0, column=0, padx=10, pady=5)
amount_entry = tk.Entry(root)
amount_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Category:").grid(row=1, column=0, padx=10, pady=5)
category_var = tk.StringVar()
category_dropdown = ttk.Combobox(root, textvariable=category_var, values=["Food", "Rent", "Entertainment", "Other"])
category_dropdown.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Description:").grid(row=2, column=0, padx=10, pady=5)
description_entry = tk.Entry(root)
description_entry.grid(row=2, column=1, padx=10, pady=5)

# Buttons
tk.Button(root, text="Add Transaction", command=add_transaction).grid(row=3, column=0, columnspan=2, pady=10)
tk.Button(root, text="Show Summary", command=show_summary).grid(row=4, column=0, columnspan=2, pady=10)
tk.Button(root, text="Export Data", command=export_data).grid(row=5, column=0, columnspan=2, pady=10)
tk.Button(root, text="Reset Data", command=reset_data, bg="red", fg="white").grid(row=7, column=0, columnspan=2, pady=10)

# Transaction history
transactions_list = tk.Listbox(root, width=50)
transactions_list.grid(row=6, column=0, columnspan=2, pady=10)

# Run the app
root.mainloop()
