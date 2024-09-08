import tkinter as tk
import random
import time

class SortVisualizer:
    def __init__(self, root):
        self.root = root

        # Canvas for visualization
        self.canvas = tk.Canvas(root, width=600, height=400, bg='white')
        self.canvas.pack()

        # Array entry for sorting algorithms
        self.array_entry_label = tk.Label(root, text="Enter array (space-separated integers):")
        self.array_entry_label.pack()
        self.array_entry = tk.Entry(root)
        self.array_entry.pack()

        # Speed control
        self.speed_scale_label = tk.Label(root, text="Adjust Speed:")
        self.speed_scale_label.pack()
        self.speed_scale = tk.Scale(root, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL)
        self.speed_scale.set(0.1)  # Default speed
        self.speed_scale.pack()

        # Buttons to choose algorithms
        self.bubble_button = tk.Button(root, text="Bubble Sort", command=self.bubble_sort)
        self.bubble_button.pack(side='left')

        self.selection_button = tk.Button(root, text="Selection Sort", command=self.selection_sort)
        self.selection_button.pack(side='left')

        self.binary_button = tk.Button(root, text="Binary Search", command=self.binary_search)
        self.binary_button.pack(side='left')

        # Element entry for binary search (hidden by default)
        self.element_entry_label = tk.Label(root, text="Enter element to search:", fg='red')
        self.element_entry_label.pack_forget()  # Hide by default
        self.element_entry = tk.Entry(root)
        self.element_entry.pack_forget()  # Hide by default

        self.data = []

    def draw_data(self, data=None, highlight_index=None, highlight_color='red', message=None, message_color='black'):
        self.canvas.delete('all')
        if data is None:
            data = self.data
        width = 600 / len(data)
        for i, value in enumerate(data):
            color = 'blue' if highlight_index is None or i != highlight_index else highlight_color
            # Draw the bar
            self.canvas.create_rectangle(i * width, 400 - value, (i + 1) * width, 400, fill=color)
            # Display the value above the bar
            self.canvas.create_text(i * width + width / 2, 400 - value - 10, text=str(value), fill='black', font=('Arial', 12))
        if message:
            self.canvas.create_text(300, 20, text=message, fill=message_color, font=('Arial', 16, 'bold'))  # Display message at the top
        self.root.update()

    def bubble_sort(self):
        self.show_array_entry_only()
        self.update_data()
        data = self.data
        n = len(data)
        for i in range(n):
            for j in range(n - i - 1):
                if data[j] > data[j + 1]:
                    data[j], data[j + 1] = data[j + 1], data[j]
                    self.draw_data(data, j + 1)
                    time.sleep(self.speed_scale.get())
        self.draw_data(data)

    def selection_sort(self):
        self.show_array_entry_only()
        self.update_data()
        data = self.data
        n = len(data)
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                if data[j] < data[min_idx]:
                    min_idx = j
            data[i], data[min_idx] = data[min_idx], data[i]
            self.draw_data(data, i)
            time.sleep(self.speed_scale.get())
        self.draw_data(data)

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
            self.draw_data(data, message=f'Searching for: {target}')
            self.canvas.create_line(mid * 600 / len(data), 0, mid * 600 / len(data), 400, fill='red', width=2)
            self.root.update()
            time.sleep(self.speed_scale.get())

            if data[mid] == target:
                self.draw_data(data, mid, highlight_color='green', message='Element found!', message_color='green')
                return
            elif data[mid] < target:
                left = mid + 1
            else:
                right = mid - 1

        self.draw_data(data, message='Element not found.', message_color='red')

    def update_data(self):
        user_input = self.array_entry.get()
        try:
            # Split the input by spaces and convert to integers
            self.data = list(map(int, user_input.split()))
            self.draw_data()
        except ValueError:
            self.draw_data(message='Invalid input. Please enter only integers.', message_color='red')

    def show_array_entry_only(self):
        """Show array entry and hide element entry for sorting algorithms."""
        self.array_entry_label.pack()
        self.array_entry.pack()
        self.element_entry_label.pack_forget()
        self.element_entry.pack_forget()

    def show_element_entry(self):
        """Show element entry for binary search."""
        self.show_array_entry_only()  # Shows array entry as well
        self.element_entry_label.pack()
        self.element_entry.pack()

root = tk.Tk()
root.title('Algorithm Visualizer')
app = SortVisualizer(root)
root.mainloop()
