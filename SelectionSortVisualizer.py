import matplotlib.pyplot as plt
import numpy as np
import time


def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        yield arr        

def visualize_selection_sort():
    arr = np.random.randint(1, 100, 20)
    fig, ax = plt.subplots()
    bars = ax.bar(range(len(arr)), arr)
    for sorted_arr in selection_sort(arr):
        for bar, height in zip(bars, sorted_arr):
            bar.set_height(height)
        plt.pause(0.1) 

    plt.show()

visualize_selection_sort()