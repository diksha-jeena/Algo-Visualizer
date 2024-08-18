import matplotlib.pyplot as plt
import numpy as np 
import time

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0 , n-i-1):
            if(arr[j] > arr[j+1]):
                arr[j], arr[j+1] = arr[j+1], arr[j]
                yield arr

def visualize_bubble_sort():
    arr = np.random.randint(1,100,20)
    fig , ax = plt.subplots()
    bars = ax.bar(range(len(arr)) , arr)
    for sorted_arr in bubble_sort(arr):
        for bar , height in zip(bars , sorted_arr):
            bar.set_height(height)
        plt.pause(0.1)
    plt.show()

visualize_bubble_sort()
