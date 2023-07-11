import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry
import tkinter.font as tkfont 
import matplotlib.pyplot as plt

class ExpenseTracker:
    def __init__(self):
        self.db = sqlite3.connect('expenses.db')
        self.cursor = self.db.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS my_expenses (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          date DATE,
          category TEXT,
          amount REAL,
          description TEXT,
          location TEXT
        )
        ''')

    def add_expense(self, date, category, amount, description, location):
        # Validate the input data
        if not date:
            messagebox.showerror("Error", "Please select a date.")
            return

        if not category:
            messagebox.showerror("Error", "Please enter a category.")
            return

        if not amount:
            messagebox.showerror("Error", "Please enter an amount.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount. Please enter a number.")
            return

        if amount <= 0:
            messagebox.showerror("Error", "Amount must be greater than zero.")
            return

        if not description:
            messagebox.showerror("Error", "Please enter a description.")
            return

        if not location:
            messagebox.showerror("Error", "Please enter a location.")
            return

        try:
            self.tracker.add_expense(date, category, amount, description, location)
            self.update_expenses()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            
        if location == '':
            raise ValueError('Please enter a location')

        self.cursor.execute('''
        INSERT INTO my_expenses (date, category, amount, description, location) VALUES (?, ?, ?, ?, ?)
        ''', (date, category, amount, description, location))
        self.db.commit()
        
    # Retrieve all expenses from the database
    def get_expenses(self):
        self.cursor.execute('''
        SELECT * FROM my_expenses
        ''')
        expenses = self.cursor.fetchall()
        return expenses

    # Calculate the total amount of all expenses
    def get_total_expenses(self):
        self.cursor.execute('''
        SELECT SUM(amount) FROM my_expenses
        ''')
        total_expenses = self.cursor.fetchone()[0]
        return total_expenses

    # Retrieve expenses that match the specified category
    def get_expenses_by_category(self, category):
        self.cursor.execute('''
        SELECT * FROM my_expenses WHERE category = ?
        ''', (category,))
        expenses = self.cursor.fetchall()
        return expenses

    # Retrieve expenses that match the specified date
    def get_expenses_by_date(self, date):
        self.cursor.execute('''
        SELECT * FROM my_expenses WHERE date = ?
        ''', (date,))
        expenses = self.cursor.fetchall()
        return expenses

    # Retrieve expenses that match the specified location
    def get_expenses_by_location(self, location):
        self.cursor.execute('''
        SELECT * FROM my_expenses WHERE location = ?
        ''', (location,))
        expenses = self.cursor.fetchall()
        return expenses

    # Remove an expense from the database based on its ID
    def remove_expense(self, expense_id):
        self.cursor.execute('''
        DELETE FROM my_expenses WHERE id = ?
        ''', (expense_id,))
        self.db.commit()
        
    # Retrieve expenses that match the specified month
    def get_expenses_by_month(self, month):
        self.cursor.execute('''
        SELECT * FROM my_expenses WHERE strftime('%m', date) = ?
        ''', (month,))
        expenses = self.cursor.fetchall()
        return expenses

    # Retrieve expenses that match both the specified category and location
    def get_expenses_by_category_and_location(self, category, location):
        if category == 'All Categories' and location == 'All Locations':
            return self.get_expenses()
        elif category == 'All Categories':
            return self.get_expenses_by_location(location)
        elif location == 'All Locations':
            return self.get_expenses_by_category(category)
        else:
            self.cursor.execute('''
            SELECT * FROM my_expenses WHERE category = ? AND location = ?
            ''', (category, location))
            expenses = self.cursor.fetchall()
            return expenses

    # Retrieve an expense based on its ID
    def get_expense_by_id(self, expense_id):
        self.cursor.execute('''
        SELECT * FROM my_expenses WHERE id = ?
        ''', (expense_id,))
        expense = self.cursor.fetchone()
        return expense

    # Retrieve distinct values from the specified column
    def get_distinct_values(self, column):
        self.cursor.execute(f"SELECT DISTINCT {column} FROM my_expenses")
        distinct_values = [row[0] for row in self.cursor.fetchall()]
        return distinct_values

    # Retrieve monthly expense trends (total amount per month)
    def get_expense_trends(self):
        self.cursor.execute('''
        SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total_amount
        FROM my_expenses
        GROUP BY strftime('%Y-%m', date)
        ''')
        trends = self.cursor.fetchall()
        return trends
    
    def edit_expense(self, expense_id, date, category, amount, description, location):
        # Validate the input data
        if not date:
            raise ValueError("Please select a date.")

        if not category:
            raise ValueError("Please enter a category.")

        if not amount:
            raise ValueError("Please enter an amount.")

        try:
            amount = float(amount)
        except ValueError:
            raise ValueError("Invalid amount. Please enter a number.")

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if not description:
            raise ValueError("Please enter a description.")

        if not location:
            raise ValueError("Please enter a location.")

        self.cursor.execute('''
        UPDATE my_expenses SET date = ?, category = ?, amount = ?, description = ?, location = ? WHERE id = ?
        ''', (date, category, amount, description, location, expense_id))
        self.db.commit()
        
class ExpenseTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        bold_font = tkfont.Font(weight="bold")
        
        #Create an instance of ExpenseTracker
        self.tracker = ExpenseTracker()
        
        # Button to open the Line Chart visualization
        self.line_chart_button = ttk.Button(self.root, text="Show Line Chart", style='Accent.TButton', command=self.show_line_chart)
        self.line_chart_button.grid(row=7, column=0, padx=5, pady=10)

        # Button to open the bar chart visualization
        self.bar_chart_button = ttk.Button(self.root, text="Show Bar Chart", style='Accent.TButton', command=self.show_bar_chart)
        self.bar_chart_button.grid(row=7, column=1, padx=5, pady=10)
        
        # Button to open the pie chart visualization
        self.pie_chart_button = ttk.Button(self.root, text="Show Pie Chart", style='Accent.TButton', command=self.show_pie_chart)
        self.pie_chart_button.grid(row=7, column=2, pady=10) 

        #Label to display total expenses
        self.total_expenses_label = ttk.Label(self.root, text="Total Expenses: $0.00", font=bold_font)
        self.total_expenses_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        #Filter options: Category, location, and month
        self.filter_category_label = ttk.Label(self.root, text="Category:", font=bold_font)
        self.filter_category_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_category_combobox = ttk.Combobox(self.root, state="readonly")
        self.filter_category_combobox.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="w")
        self.filter_category_combobox.set("All Categories")

        self.filter_location_label = ttk.Label(self.root, text="Location:", font=bold_font)
        self.filter_location_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.filter_location_combobox = ttk.Combobox(self.root, state="readonly")
        self.filter_location_combobox.grid(row=0, column=3, padx=5, pady=5)
        self.filter_location_combobox.set("All Locations")

        self.filter_month_label = ttk.Label(self.root, text="Month:", font=bold_font)
        self.filter_month_label.grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.filter_month_combobox = ttk.Combobox(self.root, state="readonly")
        self.filter_month_combobox.grid(row=0, column=5, padx=5, pady=5)
        self.filter_month_combobox.set("All Months")

        self.filter_button = ttk.Button(self.root, text="Filter", style='Accent.TButton', command=self.filter_expenses)
        self.filter_button.grid(row=0, column=6, padx=5, pady=5)

        #Treeview to display the expenses 
        self.treeview = ttk.Treeview(self.root, columns=("Date", "Category", "Amount", "Description", "Location"))
        
        #Define column headings for the treeview
        self.treeview.heading("#0", text="ID")
        self.treeview.heading("Date", text="Date")
        self.treeview.heading("Category", text="Category")
        self.treeview.heading("Amount", text="Amount")
        self.treeview.heading("Description", text="Description")
        self.treeview.heading("Location", text="Location")
        self.treeview.column("#0", width=50, anchor="center")
        self.treeview.column("Date", width=100)
        self.treeview.column("Category", width=100)
        self.treeview.column("Amount", width=100)
        self.treeview.column("Description", width=200)
        self.treeview.column("Location", width=100)
        self.treeview.grid(row=1, column=0, columnspan=7, sticky="nsew")

        #Buttons that allow user to add/delete expenses  
        self.add_expense_button = ttk.Button(self.root, text="Add Expense", style='Accent.TButton', command=self.open_add_expense_window)
        self.add_expense_button.grid(row=2, column=0, pady=10)
        self.remove_expense_button = ttk.Button(self.root, text="Remove Expense", style='Accent.TButton', command=self.remove_selected_expense)
        self.remove_expense_button.grid(row=2, column=1, pady=10)
        
        # Creates a button that allows user to edit expenses 
        edit_button = ttk.Button(self.root, text="Edit Expense", style='Accent.TButton', command=self.edit_selected_expense)
        edit_button.grid(row=2, column=2, pady=10)
        
        #Ability to sort the data by ascending/descending order
        self.data_sort_order = None
        self.price_sort_order = None
        self.treeview.heading("Date", text="Date", command=self.sort_by_data)
        self.treeview.heading("Amount", text="Amount", command=self.sort_by_price)

        #Update treeview with initial data
        self.update_treeview()

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure((0, 1), weight=1)

        self.update_dropdown_menus()
        self.update_expenses()
    
    def update_dropdown_menus(self):
        # Retrieve distinct values for categories, locations, and months from the tracker
        categories = self.tracker.get_distinct_values("category")
        locations = self.tracker.get_distinct_values("location")
        months = self.get_distinct_months()
        # Insert "All Categories", "All Locations", and "All Months" at the beginning of the respective lists
        categories.insert(0, "All Categories")
        locations.insert(0, "All Locations")
        months.insert(0, "All Months")
        # Update the dropdown menus with the retrieved values
        self.filter_category_combobox['values'] = categories
        self.filter_location_combobox['values'] = locations
        self.filter_month_combobox['values'] = months

    def get_distinct_months(self):
        # Retrieve all expenses from the tracker
        expenses = self.tracker.get_expenses()
        # Extract unique months from the expenses and return them as a list
        months = set()
        for expense in expenses:
            date = datetime.strptime(expense[1], "%Y-%m-%d")
            month = date.strftime("%B %Y")
            months.add(month)
        return list(months)

    def filter_expenses(self):
        # Retrieve selected category, location, and month from the dropdown menus
        category = self.filter_category_combobox.get()
        location = self.filter_location_combobox.get()
        month = self.filter_month_combobox.get()
        # Convert the selected month to a standardized format if it is not "All Months"
        if month != "All Months":
            month = datetime.strptime(month, "%B %Y").strftime("%m")
         # Retrieve filtered expenses based on the selected category, location, and month
        expenses = self.tracker.get_expenses_by_category_and_location(category, location)
        # Further filter expenses if a specific month is selected
        if month != "All Months":
            expenses = [expense for expense in expenses if datetime.strptime(expense[1], "%Y-%m-%d").strftime("%m") == month]
        # Calculate the total expenses and update the Treeview and total expenses label
        total_expenses = sum(expense[3] for expense in expenses)
        self.update_treeview(expenses)
        self.update_total_expenses(total_expenses)

    def update_expenses(self):
        # Retrieve all expenses and total expenses from the tracker
        expenses = self.tracker.get_expenses()
        total_expenses = self.tracker.get_total_expenses()
        # Update the Treeview and total expenses label with the retrieved data
        self.update_treeview(expenses)
        self.update_total_expenses(total_expenses)
        
    # Function to update the Treeview with expense data
    def update_treeview(self, expenses=None, sort_column=None):
        # Clear existing items from the Treeview
        self.treeview.delete(*self.treeview.get_children())
        
        # If no expenses are provided, retrieve all expenses from the tracker
        if expenses is None:
            expenses = self.tracker.get_expenses()
            
        # Sort expenses based on the selected column if specified
        if sort_column == "Date":
            expenses.sort(key=lambda expense: expense[1], reverse=self.data_sort_order == "desc")
            self.data_sort_order = "asc" if self.data_sort_order == "desc" else "desc"
            
        # Sort expenses based on the amount column
        elif sort_column == "Amount":
            expenses.sort(key=lambda expense: expense[3], reverse=self.price_sort_order == "desc")
            self.price_sort_order = "asc" if self.price_sort_order == "desc" else "desc"
            
        # Iterate through the sorted expenses
        for expense in expenses:
            formatted_date = datetime.strptime(expense[1], "%Y-%m-%d").strftime("%d-%b-%Y")
            formatted_amount = "${:,.2f}".format(expense[3])

            self.treeview.insert("", "end", text=expense[0], values=(formatted_date, expense[2], formatted_amount, expense[4], expense[5]))
        # Update the root window to reflect the changes
        self.root.update_idletasks()

        
    def sort_by_data(self):
        self.update_treeview(sort_column="Date")

    def sort_by_price(self):
        self.update_treeview(sort_column="Amount")

    # Open a new window for adding an expense
    def open_add_expense_window(self):
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add Expense")

        date_label = ttk.Label(self.add_window, text="Date:")
        date_label.grid(row=0, column=0, padx=5, pady=5)

        self.date_picker = DateEntry(self.add_window)
        self.date_picker.grid(row=0, column=1, padx=5, pady=5)

        category_label = ttk.Label(self.add_window, text="Category:")
        category_label.grid(row=1, column=0, padx=5, pady=5)
        self.category_entry = ttk.Entry(self.add_window)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)

        amount_label = ttk.Label(self.add_window, text="Amount:")
        amount_label.grid(row=2, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(self.add_window)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        description_label = ttk.Label(self.add_window, text="Description:")
        description_label.grid(row=3, column=0, padx=5, pady=5)
        self.description_entry = ttk.Entry(self.add_window)
        self.description_entry.grid(row=3, column=1, padx=5, pady=5)

        location_label = ttk.Label(self.add_window, text="Location:")
        location_label.grid(row=4, column=0, padx=5, pady=5)
        self.location_entry = ttk.Entry(self.add_window)
        self.location_entry.grid(row=4, column=1, padx=5, pady=5)

        add_button = ttk.Button(self.add_window, text="Add", style='Accent.TButton', command=lambda: self.add_expense(
            self.date_picker.get_date(),
            self.category_entry.get(),
            self.amount_entry.get(),
            self.description_entry.get(),
            self.location_entry.get()
        ))
        add_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        clear_button = ttk.Button(self.add_window, text="Clear", style='Accent.TButton', command=self.clear_fields)
        clear_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    # Clear all the entry fields in the add expense window
    def clear_fields(self):
        self.date_picker.set_date(None)  # Clear the date picker
        self.category_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)

    # Add the expense to the tracker
    def add_expense(self, date, category, amount, description, location):
        try:
            self.tracker.add_expense(date, category, amount, description, location)
            self.update_expenses()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            
    # Remove the selected expense from the Treeview
    def remove_selected_expense(self):
      selected_item = self.treeview.selection()
      if selected_item:
          expense_id = self.treeview.item(selected_item)["text"]
          self.tracker.remove_expense(expense_id)
          self.update_expenses()
          
    # Update the total expenses label with the formatted total expenses
    def update_total_expenses(self, total_expenses):
        formatted_total_expenses = "${:,.2f}".format(total_expenses)
        self.total_expenses_label.config(text="Total Expenses: " + formatted_total_expenses)
        
    # Edit the selected expense
    def edit_selected_expense(self):
        selected_item = self.treeview.focus()
        if selected_item:
            expense_id = self.treeview.item(selected_item)["text"]
            expense = self.tracker.get_expense_by_id(expense_id)
            if expense:
                self.open_edit_expense_window(expense)
            else:
                messagebox.showerror("Error", "Expense not found.")
        else:
            messagebox.showerror("Error", "No expense selected.")
            
    # Open a new window for editing an expense
    def open_edit_expense_window(self, expense):
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Edit Expense")

        date_label = ttk.Label(self.edit_window, text="Date:")
        date_label.pack()

        self.date_picker = DateEntry(self.edit_window)
        self.date_picker.pack()
        self.date_picker.set_date(datetime.strptime(expense[1], "%Y-%m-%d"))

        category_label = ttk.Label(self.edit_window, text="Category:")
        category_label.pack()

        self.category_entry = ttk.Entry(self.edit_window)
        self.category_entry.pack()
        self.category_entry.insert(tk.END, expense[2])

        amount_label = ttk.Label(self.edit_window, text="Amount:")
        amount_label.pack()

        self.amount_entry = ttk.Entry(self.edit_window)
        self.amount_entry.pack()
        self.amount_entry.insert(tk.END, str(expense[3]))

        description_label = ttk.Label(self.edit_window, text="Description:")
        description_label.pack()

        self.description_entry = ttk.Entry(self.edit_window)
        self.description_entry.pack()
        self.description_entry.insert(tk.END, expense[4])

        location_label = ttk.Label(self.edit_window, text="Location:")
        location_label.pack()

        self.location_text = tk.StringVar()
        self.location_entry = ttk.Entry(self.edit_window, textvariable=self.location_text)
        self.location_entry.pack()
        self.location_text.set(expense[5])

        save_button = ttk.Button(self.edit_window, text="Save", style='Accent.TButton', command=self.save_changes)
        save_button.pack(pady=10)

        # Store the expense ID to be used in the save_changes method
        self.edit_window.expense_id = expense[0]

    # Save the changes made to an expense
    def save_changes(self):
        expense_id = self.edit_window.expense_id
        date = self.date_picker.get_date()
        category = self.category_entry.get()
        amount = self.amount_entry.get()
        description = self.description_entry.get()
        location = self.location_entry.get()

        try:
            self.tracker.edit_expense(expense_id, date, category, amount, description, location)
            self.edit_window.destroy()
            self.load_expenses()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def load_expenses(self):
        # Implement the loading of expenses from the database and update the GUI
        expenses = self.tracker.get_expenses()
        self.update_treeview(expenses)
        total_expenses = self.tracker.get_total_expenses()
        self.update_total_expenses(total_expenses)
        
    def show_bar_chart(self):
        # Retrieve expenses and categories
        expenses = self.tracker.get_expenses()
        categories = self.tracker.get_distinct_values("category")

        # Calculate total expenses for each category
        total_expenses_by_category = {}
        for category in categories:
            category_expenses = self.tracker.get_expenses_by_category(category)
            total_expenses = sum(expense[3] for expense in category_expenses)
            total_expenses_by_category[category] = total_expenses

        # Create a bar chart
        plt.bar(total_expenses_by_category.keys(), total_expenses_by_category.values())
        plt.xlabel('Category')
        plt.ylabel('Total Expenses')
        plt.title('Expense Distribution by Category')

        # Display the bar chart
        plt.show()
    
    def show_line_chart(self):
        trends = self.tracker.get_expense_trends()

        months = [trend[0] for trend in trends]
        amounts = [trend[1] for trend in trends]

        # Create line chart
        plt.plot(months, amounts, marker='o')
        plt.xlabel("Month")
        plt.ylabel("Total Amount")
        plt.title("Expense Trends Over Time")
        plt.xticks(rotation=45)
        
        # Display the line chart
        plt.show()
    
    def show_pie_chart(self):
        expenses = self.tracker.get_expenses()
        categories = {}
        for expense in expenses:
            category = expense[2]
            amount = expense[3]
            if category in categories:
                categories[category] += amount
            else:
                categories[category] = amount

        # Create lists for labels and sizes of each category
        labels = list(categories.keys())
        sizes = list(categories.values())

        # Create a pie chart
        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)

        # Set aspect ratio to be equal so that pie is drawn as a circle
        plt.axis('equal')

        # Set title for the pie chart
        plt.title("Expense Distribution by Category")

        # Display the pie chart
        plt.show()
        
        
    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    tracker = ExpenseTracker()
    root = tk.Tk()
    root.tk.call('source', r'C:\Users\Josh\Downloads\Forest-ttk-theme-master\Forest-ttk-theme-master\forest-dark.tcl')
    ttk.Style().theme_use('forest-dark')
    root.grid_rowconfigure(1, weight=1)  # Make the expenses listbox row expand vertically
    root.grid_columnconfigure((0, 1), weight=1)  # Make the columns expand horizontally
    app = ExpenseTrackerGUI(root)
    app.run()