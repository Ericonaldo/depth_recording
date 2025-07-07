import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import random  # Replace with real USB data source

fig, ax = plt.subplots()
x_data, y_data = [], []

def update(frame):
    # Simulate USB bandwidth data (replace with actual data)
    x_data.append(time.time())
    y_data.append(random.randint(0, 500))  # Replace with KB/s from usbtop or /sys
    ax.clear()
    ax.plot(x_data, y_data, label="USB Bandwidth (KB/s)")
    ax.legend()
    plt.xlabel("Time")
    plt.ylabel("Bandwidth (KB/s)")

ani = animation.FuncAnimation(fig, update, interval=1000)  # Update every 1s
plt.show()
