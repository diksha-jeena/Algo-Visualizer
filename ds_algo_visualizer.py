import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import mysql.connector

class AlgorithmVisualizer:
    def __init__(self, master):
        self.master = master
        self.master.title("Algorithm Visualizer")
        self.master.geometry("800x600")

        self.array_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.speed_var = tk.DoubleVar(value=1.0)
        self.db_connection = self.connect_to_db()  # Connect to the database
        self.user_id = None
        self.status_var = tk.StringVar(value="Ready")  # Initialize status variable

        self.create_login_window()  # New: Login to choose user

    def connect_to_db(self):
        """Establish connection to MySQL database."""
        try:
            conn = mysql.connector.connect(
                host="127.0.0.1",
                user="root", 
                password="10062007",  
                database="sort_visualizer"
            )
            return conn
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error connecting to the database: {err}")
            return None

    def create_login_window(self):
        """Login window for user to select their account."""
        login_frame = ttk.Frame(self.master)
        login_frame.pack(expand=True)

        ttk.Label(login_frame, text="Select User:").pack(pady=10)
        self.user_combobox = ttk.Combobox(login_frame, state="readonly")
        self.user_combobox.pack(pady=10)
        self.load_users()

        ttk.Button(login_frame, text="Login", command=self.select_user).pack(pady=20)

    def load_users(self):
        """Load users from the database into the combobox."""
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        self.user_combobox['values'] = [user[1] for user in users]
        self.user_dict = {user[1]: user[0] for user in users}  # Map usernames to user_ids

    def select_user(self):
        """Select the user and proceed to the array selection."""
        selected_user = self.user_combobox.get()
        if selected_user:
            self.user_id = self.user_dict[selected_user]  # Get the user_id
            self.create_input_window()  # Move to input window after login

    def create_input_window(self):
        input_frame = ttk.Frame(self.master)
        input_frame.pack(expand=True)

        ttk.Label(input_frame, text="Enter array (space-separated numbers):").pack(pady=10)
        ttk.Entry(input_frame, textvariable=self.array_var, width=40).pack(pady=10)
        
        # Option to load saved array from the database
        ttk.Button(input_frame, text="Load Saved Array", command=self.load_saved_array).pack(pady=5)
        
        ttk.Button(input_frame, text="Create Visualizer", command=self.create_visualizer).pack(pady=20)

    def load_saved_array(self):
        """Load the saved array from the database for the current user."""
        if not self.user_id:
            messagebox.showerror("Error", "User not logged in.")
            return
        cursor = self.db_connection.cursor()
        cursor.execute(f"SELECT array_data FROM user_arrays WHERE user_id = {self.user_id}")
        result = cursor.fetchone()

        if result:
            self.array_var.set(result[0])
            messagebox.showinfo("Loaded", "Array loaded from the database!")
        else:
            messagebox.showwarning("No Array", "No array found for the current user.")

    def create_visualizer(self):
        try:
            self.array = [int(x) for x in self.array_var.get().split()]
            if not self.array:
                raise ValueError("Array is empty")
        except ValueError as e:
            tk.messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            return

        # Store the new array in the database
        self.save_array_to_db()

        for widget in self.master.winfo_children():
            widget.destroy()

        self.create_visualizer_window()

    def save_array_to_db(self):
        """Save the user's array to the database."""
        if self.user_id and self.array_var.get():
            cursor = self.db_connection.cursor()
            cursor.execute(
                "INSERT INTO user_arrays (user_id, array_data) VALUES (%s, %s)",
                (self.user_id, self.array_var.get())
            )
            self.db_connection.commit()

    def create_visualizer_window(self):
        self.plot_frame = ttk.Frame(self.master)
        self.plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(self.master)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.update_plot(self.array, "Initial Array")

        speed_frame = ttk.Frame(control_frame)
        speed_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT, padx=5)
        ttk.Scale(speed_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL, variable=self.speed_var, length=200).pack(side=tk.LEFT, padx=5)

        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Bubble Sort", command=self.run_bubble_sort).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Selection Sort", command=self.run_selection_sort).pack(side=tk.LEFT, padx=5)

        # New "Change Array" button to update the array and restart the visualizer
        ttk.Button(button_frame, text="Change Array", command=self.update_array).pack(side=tk.LEFT, padx=5)

        binary_frame = ttk.Frame(control_frame)
        binary_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        ttk.Label(binary_frame, text="Binary Search Value:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(binary_frame, textvariable=self.search_var, width=10)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(binary_frame, text="Search", command=self.run_binary_search).pack(side=tk.LEFT, padx=5)

        search_entry.bind('<Return>', self.run_binary_search_keypress)

        ttk.Label(control_frame, textvariable=self.status_var).pack(side=tk.BOTTOM, pady=5)

    def update_plot(self, arr, title, color='blue', highlight_indices=None, message=None):
        self.ax.clear()
        bars = self.ax.bar(range(len(arr)), arr, color=color)
        
        if highlight_indices:
            for i in highlight_indices:
                if 0 <= i < len(arr):
                    bars[i].set_color('green')  # Highlight found element in green

        # Only set title if it's not a binary search
        if "Binary Search" not in title:
            self.ax.set_title(title)
        
        for i, v in enumerate(arr):
            self.ax.text(i, v/2, str(v), ha='center', va='center')

        # Display message if provided
        if message:
            max_height = max(arr) if arr else 1
            self.ax.text(len(arr) / 2, max_height * 1.05, message, ha='center', va='bottom', fontsize=12, color='red', fontweight='bold')

        self.canvas.draw()
        self.master.update()
        time.sleep(1 / self.speed_var.get())

    def bubble_sort(self, arr):
        """Bubble Sort algorithm."""
        n = len(arr)
        for i in range(n):
            for j in range(0, n-i-1):
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                    yield arr.copy(), [j, j+1]

    def run_bubble_sort(self):
        self.status_var.set("Running Bubble Sort...")
        arr = self.array.copy()
        for step, highlight in self.bubble_sort(arr):
            self.update_plot(step, "Bubble Sort", highlight_indices=highlight)
        self.update_plot(arr, "Bubble Sort - Sorted", color='green')
        self.status_var.set("Bubble Sort completed")

    def selection_sort(self, arr):
        """Selection Sort algorithm."""
        n = len(arr)
        for i in range(n):
            min_idx = i
            for j in range(i+1, n):
                if arr[j] < arr[min_idx]:
                    min_idx = j
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            yield arr.copy(), [i, min_idx]

    def run_selection_sort(self):
        self.status_var.set("Running Selection Sort...")
        arr = self.array.copy()
        for step, highlight in self.selection_sort(arr):
            self.update_plot(step, "Selection Sort", highlight_indices=highlight)
        self.update_plot(arr, "Selection Sort - Sorted", color='green')
        self.status_var.set("Selection Sort completed")

    def binary_search(self, arr, target):
        """Binary Search algorithm."""
        left, right = 0, len(arr) - 1
        while left <= right:
            mid = (left + right) // 2
            yield arr.copy(), [mid]  # Highlight the mid index
            if arr[mid] < target:
                left = mid + 1
            elif arr[mid] > target:
                right = mid - 1
            else:
                return mid  # Element found
        return -1  # Element not found

    def run_binary_search(self):
        target = self.search_var.get()
        if not target:
            messagebox.showwarning("Input Error", "Please enter a value to search.")
            return
        
        try:
            target = int(target)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number.")
            return

        self.status_var.set("Running Binary Search...")
        arr = sorted(self.array.copy())  # Ensure the array is sorted for binary search

        for step, highlight in self.binary_search(arr, target):
            self.update_plot(step, "Binary Search", highlight_indices=highlight)

        # Final check if the element was found
        found_index = arr.index(target) if target in arr else -1  # Get index of found element

        if found_index != -1:
            self.update_plot(arr, "Binary Search", highlight_indices=[found_index], message=f"Element {target} found at index {found_index}!")
        else:
            self.update_plot(arr, "Binary Search", message=f"Element {target} not found.")
        
        self.status_var.set("Binary Search completed")

    def run_binary_search_keypress(self, event):
        self.run_binary_search()

    def update_array(self):
        """Restart the input window to change the array."""
        for widget in self.master.winfo_children():
            widget.destroy()
        self.create_input_window()

    def on_close(self):
        """Close the database connection on exit."""
        if self.db_connection:
            self.db_connection.close()
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = AlgorithmVisualizer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)  # Ensure database closes on exit
    root.mainloop()

