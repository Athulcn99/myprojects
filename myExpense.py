"""
Expense Tracker with GUI

A simple Python application to track expenses using:
- Tkinter for GUI
- SQLite for database storage
- Matplotlib for visualization of Expenses.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

# Database setup
conn = sqlite3.connect("finance.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    description TEXT,
    date TEXT DEFAULT (DATE('now')))
""")
conn.commit()

# Global variables
root = tk.Tk()
amount_entry = None
category_var = None
description_entry = None
transactions_list = None


def setup_gui():
    """Create and arrange all GUI components"""
    global amount_entry, category_var, description_entry, transactions_list

    root.title("Expense Tracker")

    # Input Fields
    tk.Label(root, text="Amount:").grid(row=0, column=0, padx=10, pady=5)
    amount_entry = tk.Entry(root)
    amount_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Category:").grid(row=1, column=0, padx=10, pady=5)
    category_var = tk.StringVar()
    category_dropdown = ttk.Combobox(
        root,
        textvariable=category_var,
        values=["Food", "Rent", "Entertainment", "Other"]
    )
    category_dropdown.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(root, text="Description:").grid(row=2, column=0, padx=10, pady=5)
    description_entry = tk.Entry(root)
    description_entry.grid(row=2, column=1, padx=10, pady=5)

    # Buttons
    tk.Button(root, text="Add Transaction", command=add_transaction).grid(
        row=3, column=0, columnspan=2, pady=10
    )
    tk.Button(root, text="Show Summary", command=show_summary).grid(
        row=4, column=0, columnspan=2, pady=10
    )
    tk.Button(root, text="Export Data", command=export_data).grid(
        row=5, column=0, columnspan=2, pady=10
    )

    # Transaction List
    transactions_list = tk.Listbox(root, width=50)
    transactions_list.grid(row=6, column=0, columnspan=2, pady=10)

    # Reset Button
    tk.Button(
        root,
        text="Reset Data",
        command=reset_data,
        bg="red",
        fg="white"
    ).grid(row=7, column=0, columnspan=2, pady=10)


def load_transactions():
    """Load existing transactions into the listbox"""
    transactions_list.delete(0, tk.END)
    cursor.execute("SELECT date, amount, category, description FROM transactions")
    for row in cursor.fetchall():
        transactions_list.insert(tk.END, f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")


def add_transaction():
    """Add a new transaction into the database"""
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

        cursor.execute(
            "INSERT INTO transactions (amount, category, description) VALUES (?, ?, ?)",
            (amount, category, description)
        )
        conn.commit()

        load_transactions()
        clear_fields()

    except ValueError as e:
        messagebox.showerror("Error", f"Invalid input: {e}")


def clear_fields():
    """Clear all input fields"""
    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)


def show_summary():
    """Show a pie chart of spending group by category"""
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
    """Export transaction data to CSV"""
    cursor.execute("SELECT * FROM transactions")
    data = cursor.fetchall()

    if data:
        df = pd.DataFrame(data, columns=["ID", "Amount", "Category", "Description", "Date"])
        df.to_csv("transactions.csv", index=False)
        messagebox.showinfo("Success", "Data exported to transactions.csv")
    else:
        messagebox.showinfo("Info", "No data to export")


def reset_data():
    """Clear all transaction data"""
    if messagebox.askyesno("Confirm Reset", "Are you sure you want to clear all data?"):
        cursor.execute("DELETE FROM transactions")
        conn.commit()
        transactions_list.delete(0, tk.END)
        messagebox.showinfo("Reset Complete", "All data has been cleared.")


def main():
    """Main function to run the application"""
    setup_gui()
    load_transactions()
    root.mainloop()
    conn.close()


if __name__ == "__main__":
    main()
