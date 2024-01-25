import random
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import threading
import time
import json
import csv

import socket
import sys
from time import sleep
import random
from struct import pack

class Gui(tk.Tk):
    def __init__(self):

        self.time_refresh = 2

        super().__init__()

        # setup the window
        self.title('Pressure Tests')
        
        # get users screen resolution and maximize window
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry('1000x600')

        # frame for the plot
        self.plot_frame = ttk.Frame(self, borderwidth=1, relief="solid")
        self.plot_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        
        # figure for the plot and create an axis, ** bug with tkinter, plt.subplots() breaks window size/zoom ??
        self.fig = Figure(figsize=(10, 5), dpi=75)
        self.axes = {
            'Pressure': self.fig.add_subplot(211),  # 2 rows, 1 column, first plot
            'Temperature': self.fig.add_subplot(212)  # 2 rows, 1 column, second plot
        }
        self.fig.subplots_adjust(left=0.04, right=0.96, bottom=0.07, top=0.95, wspace=0.1, hspace=0.25)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.grid(sticky='nsew', padx=0, pady=0)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)

        # Create the buttons
        self.control_frame = ttk.Frame(self)
        self.control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ttk.Button(self.control_frame, text='Start Test', command=self.start_test).grid(row=0, column=1, sticky="e")
        ttk.Button(self.control_frame, text='End Test', command=self.end_test).grid(row=0, column=2, sticky="e")

        # do i need all these?
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)


    def start_gui(self):
        """Starts the gui and the thread"""
        self.running = True
        self.thread = threading.Thread(target=self.update_data)
        self.thread.daemon = True
        self.mainloop()

    def update_data(self):
        """Updates the dataframe, df, from udp_data.csv"""
        last_run_time = time.time()
        while self.running:
            if time.time() - last_run_time >= self.time_refresh:
                try:
                    # Receive data over UDP
                    data, address = self.sock.recvfrom(4096)
                    data = data.decode()

                    # Write the data to the CSV file
                    self.csv_writer.writerow(data.split(','))

                    df = pd.read_csv("udp_data.csv")
                    
                    # Update the graph with the new data
                    self.safe_after(0, self.update_graph, df)            

                    last_run_time = time.time()
                except pd.errors.EmptyDataError:
                    print("udp_data.csv is empty. Waiting for data...")
                    
    def update_graph(self, df):
        """Updates the graph with the new data"""
        for ax in self.axes.values():
            ax.clear()

        for column in ['Pressure', 'Temperature']:
            ax = self.axes[column]
            ax.plot(df["Time"], df[column], marker='o', label=column)
            ax.set_title(f"{column}")
            ax.set_xlabel("Time")
            ax.set_ylabel(column)
            ax.grid(True)


        self.canvas.draw()


    def on_closing(self):
        """Called when closing the gui, destroys the gui and closes the thread"""
        # i think order is correct/safest but im not entirely sure
        self.running = False
        self.destroy()
        time.sleep(self.time_refresh)
        if self.thread.is_alive():
            self.thread.join()
        self.quit()


    def safe_after(self, delay, func, *args, **kwargs):
        """Executes a function after a delay, but only if the program is still running."""
        if self.running:
            self.after(delay, func, *args, **kwargs)

    def start_test(self):
        """Starts the test"""
        if self.thread is not None:
            # Create a UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Bind the socket to the port
            server_address = ('', 12345)  # '' means all available interfaces
            self.sock.bind(server_address)

            # Open the CSV file
            self.csv_file = open('udp_data.csv', 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)

            self.running = True
            self.thread.start()


    def end_test(self):
        """Ends the test"""
        if self.running == True:
            self.running = False
            if self.thread.is_alive():
                self.thread.join()
            self.thread = None
            self.current_time = 0

            # Close the CSV file and the UDP socket
            self.csv_file.close()
            self.sock.close()

if __name__ == "__main__":
        app = Gui()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.start_gui()
