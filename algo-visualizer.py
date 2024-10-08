import tkinter as tk
import random
import time
import sqlite3
from tkinter import messagebox

class SortVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title('Algorithm Visualizer')
        
        # Database setup
        self.conn = sqlite3.connect('sort_visualizer.db')
        self.create_tables()
        
        # User authentication
        self.current_user = None
        self.setup_login_ui()
        
        # Main UI (initially hidden)
        self.main_frame = tk.Frame(root)
        self.setup_main_ui()

    # ... (previous methods remain the same)
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_arrays (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                array_data TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS algorithm_info (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            )
        ''')
        self.conn.commit()

    def setup_login_ui(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack()
        
        tk.Label(self.login_frame, text="Username:").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)
        
        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)
        
        tk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, column=0)
        tk.Button(self.login_frame, text="Sign Up", command=self.signup).grid(row=2, column=1)

    def setup_main_ui(self):
        # Canvas for visualization
        self.canvas = tk.Canvas(self.main_frame, width=600, height=400, bg='white')
        self.canvas.pack()

        # Array entry for sorting algorithms
        self.array_frame = tk.Frame(self.main_frame)
        self.array_frame.pack()
        
        self.array_entry_label = tk.Label(self.array_frame, text="Enter array (space-separated integers):")
        self.array_entry_label.pack(side='left')
        self.array_entry = tk.Entry(self.array_frame, width=50)
        self.array_entry.pack(side='left')
        self.update_button = tk.Button(self.array_frame, text="Update", command=self.update_data)
        self.update_button.pack(side='left')

        # Speed control
        self.speed_frame = tk.Frame(self.main_frame)
        self.speed_frame.pack()
        
        self.speed_scale_label = tk.Label(self.speed_frame, text="Adjust Speed:")
        self.speed_scale_label.pack(side='left')
        self.speed_scale = tk.Scale(self.speed_frame, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, length=200)
        self.speed_scale.set(0.1)  # Default speed
        self.speed_scale.pack(side='left')

        # Buttons to choose algorithms
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack()
        
        self.bubble_button = tk.Button(self.button_frame, text="Bubble Sort", command=self.bubble_sort)
        self.bubble_button.pack(side='left')
        self.selection_button = tk.Button(self.button_frame, text="Selection Sort", command=self.selection_sort)
        self.selection_button.pack(side='left')
        self.binary_button = tk.Button(self.button_frame, text="Binary Search", command=self.binary_search)
        self.binary_button.pack(side='left')

        # Element entry for binary search (hidden by default)
        self.search_frame = tk.Frame(self.main_frame)
        self.element_entry_label = tk.Label(self.search_frame, text="Enter element to search:", fg='red')
        self.element_entry = tk.Entry(self.search_frame, width=10)
        
        # Load previous array button
        self.load_button = tk.Button(self.button_frame, text="Load Previous Array", command=self.load_previous_array)
        self.load_button.pack(side='left')

        self.data = []
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        
        if user:
            self.current_user = user[0]
            self.login_frame.pack_forget()
            self.main_frame.pack()
            messagebox.showinfo("Login", "Login successful!")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            messagebox.showinfo("Sign Up", "Account created successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Sign Up Failed", "Username already exists")

    def load_previous_array(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please log in first")
            return
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT array_data FROM user_arrays WHERE user_id = ? ORDER BY id DESC LIMIT 1", (self.current_user,))
        result = cursor.fetchone()
        
        if result:
            self.array_entry.delete(0, tk.END)
            self.array_entry.insert(0, result[0])
            self.update_data()
        else:
            messagebox.showinfo("Info", "No previous array found")

    def save_array(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please log in first")
            return
        
        array_data = ' '.join(map(str, self.data))
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO user_arrays (user_id, array_data) VALUES (?, ?)", (self.current_user, array_data))
        self.conn.commit()

    def update_data(self):
        user_input = self.array_entry.get()
        try:
            self.data = list(map(int, user_input.split()))
            self.draw_data()
            self.save_array()
        except ValueError:
            self.draw_data(message='Invalid input. Please enter only integers.', message_color='red')

    def show_element_entry(self):
        """Shows element entry for binary search."""
        self.search_frame.pack()
        self.element_entry_label.pack(side='left')
        self.element_entry.pack(side='left')

    def hide_element_entry(self):
        """Hides element entry for binary search."""
        self.search_frame.pack_forget()

    def show_array_entry_only(self):
        """Show array entry and hide element entry for sorting algorithms."""
        self.hide_element_entry()

    def draw_data(self, data=None, highlight_index=None, highlight_color='red', message=None, message_color='black', sorted_indices=None):
        """
        Draws a visual representation of the data on a canvas.

        Parameters:
        data (list, optional): The list of numerical values to be visualized. Defaults to self.data if not provided.
        highlight_index (int, optional): The index of the data to be highlighted. Defaults to None.
        highlight_color (str, optional): The color used to highlight the specified index. Defaults to 'red'.
        message (str, optional): A message to be displayed at the top of the canvas. Defaults to None.
        message_color (str, optional): The color of the message text. Defaults to 'black'.
        sorted_indices (list, optional): A list of indices that are considered sorted and will be colored differently. Defaults to None.

        This method clears the canvas and draws a bar for each value in the data list. Each bar's color is determined by its
        index: green if the index is in sorted_indices, highlight_color if it matches highlight_index, or blue otherwise.
        The value of each bar is displayed above it. If a message is provided, it is displayed at the top of the canvas.
        """
        self.canvas.delete('all')
        if data is None:
            data = self.data
        width = 600 / len(data)
        for i, value in enumerate(data):
            if sorted_indices and i in sorted_indices:
                color = 'green'
            elif highlight_index is not None and i == highlight_index:
                color = highlight_color
            else:
                color = 'blue'
            # Draw the bar
            self.canvas.create_rectangle(i * width, 400 - value, (i + 1) * width, 400, fill=color)
            # Display the value above the bar
            self.canvas.create_text(i * width + width / 2, 400 - value - 10, text=str(value), fill='black', font=('Arial', 12))
        if message:
            self.canvas.create_text(300, 20, text=message, fill=message_color, font=('Arial', 16, 'bold'))  # Display message at the top
        self.root.update()  
        self.canvas.delete('all')
        if data is None:
            data = self.data
        width = 600 / len(data)
        for i, value in enumerate(data):
            if sorted_indices and i in sorted_indices:
                color = 'green'
            elif highlight_index is not None and i == highlight_index:
                color = highlight_color
            else:
                color = 'blue'
            # Draw the bar
            self.canvas.create_rectangle(i * width, 400 - value, (i + 1) * width, 400, fill=color)
            # Display the value above the bar
            self.canvas.create_text(i * width + width / 2, 400 - value - 10, text=str(value), fill='black', font=('Arial', 12))
        if message:
            self.canvas.create_text(300, 20, text=message, fill=message_color, font=('Arial', 16, 'bold'))  # Display message at the top
        self.root.update()

    def binary_search(self):
        self.show_element_entry()  # Shows element entry for binary search
        self.update_data()
        data = sorted(self.data)

        # Gets the target element from the input box
        try:
            target = int(self.element_entry.get())
        except ValueError:
            self.draw_data(data, message='Invalid input. Please enter an integer.', message_color='red')
            return

        left, right = 0, len(data) - 1
        while left <= right:
            mid = (left + right) // 2
            self.draw_data(data, mid, highlight_color='yellow', message=f'Searching for: {target}')
            time.sleep(self.speed_scale.get())

            if data[mid] == target:
                self.draw_data(data, mid, highlight_color='green', message='Element found!', message_color='green')
                return
            elif data[mid] < target:
                left = mid + 1
            else:
                right = mid - 1

        self.draw_data(data, message='Element not found.', message_color='red')
    def bubble_sort(self):
        self.show_array_entry_only()
        self.update_data()
        data = self.data
        n = len(data)
        sorted_indices = set()
        for i in range(n):
            for j in range(n - i - 1):
                if data[j] > data[j + 1]:
                    data[j], data[j + 1] = data[j + 1], data[j]
                self.draw_data(data, j + 1, sorted_indices=sorted_indices)
                time.sleep(self.speed_scale.get())
            sorted_indices.add(n - i - 1)
        self.draw_data(data, sorted_indices=set(range(n)))

    def selection_sort(self):
        self.show_array_entry_only()
        self.update_data()
        data = self.data
        n = len(data)
        sorted_indices = set()
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                if data[j] < data[min_idx]:
                    min_idx = j
            data[i], data[min_idx] = data[min_idx], data[i]
            sorted_indices.add(i)
            self.draw_data(data, i, sorted_indices=sorted_indices)
            time.sleep(self.speed_scale.get())
        self.draw_data(data, sorted_indices=set(range(n)))
    def __del__(self):
        self.conn.close()

root = tk.Tk()
app = SortVisualizer(root)
root.mainloop()