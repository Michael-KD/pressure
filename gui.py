import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter

import pandas as pd
import threading
import time

import subprocess
import paramiko

class Gui(tk.Tk):
    def __init__(self):

        self.time_refresh = 10 # time in seconds between each update of the graph

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
        self.fig.subplots_adjust(left=0.07, right=0.99, bottom=0.07, top=0.95, wspace=0.1, hspace=0.25)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.grid(sticky='nsew', padx=0, pady=0)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)

        # Create the buttons
        self.control_frame = ttk.Frame(self)
        self.control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ttk.Button(self.control_frame, text='Graph', command=self.graph_data).grid(row=0, column=1, sticky="e")
        ttk.Button(self.control_frame, text='SSH', command=self.ssh).grid(row=0, column=2, sticky="e")

        # do i need all these?
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)


    def start_gui(self):
        self.mainloop()
                    
    def update_graph(self, df):
        """Updates the graph with the new data"""
        for ax in self.axes.values():
            ax.clear()

        for column in ['Pressure', 'Temperature']:
            ax = self.axes[column]
            ax.plot(df["Time"], df[column], label=column)
            ax.set_title(f"{column}")
            ax.set_xlabel("Time")
            ax.set_ylabel(column)
            ax.grid(True)
            if column == 'Pressure':
                formatter = FuncFormatter(lambda y, _: '{:.16g}'.format(y))
                ax.yaxis.set_major_formatter(formatter)


        self.canvas.draw()

    def on_closing(self):
        """Called when closing the gui, destroys the gui"""
        self.running = False
        self.quit()
        self.destroy()
    
    def safe_after(self, delay, func, *args, **kwargs):
        """Executes a function after a delay, but only if the program is still running."""
        if self.running:
            self.after(delay, func, *args, **kwargs)


    def start_test(self):
        """Starts the test"""
        if self.thread is None or not self.thread.is_alive():
            print("Starting test...")

            # Create an SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the server
            print("Connecting to the server...")
            ssh.connect('169.231.49.78', username='lubin', password='spaceball') ### change ip
            print("Connected to the server.")

            # Use SCP to download the file
            print("Downloading the file...")
            scp = ssh.open_sftp()
            scp.get('/home/lubin/Code/pressuresensor/data.csv', 'C:/Users/micha/Documents/Code/LUBIN_LAB/pressuresensor/download_data.csv')
            scp.close()
            print("File downloaded.")

            # Start the thread to update the data
            print("Starting the data update thread...")
            self.running = True
            self.thread = threading.Thread(target=self.update_data)
            self.thread.start()
            print("Data update thread started.")

    def graph_data(self):
        """Downloads the file and graphs it"""
        print("Downloading the file...")

        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the server
        print("Connecting to the server...")
        ssh.connect('169.231.49.78', username='lubin', password='spaceball') ### change ip
        print("Connected to the server.")

        # Use SCP to download the file
        scp = ssh.open_sftp()
        scp.get('/home/lubin/Code/pressuresensor/data.csv', 'C:/Users/micha/Documents/Code/LUBIN_LAB/pressuresensor/download_data.csv')
        scp.close()
        print("File downloaded.")

        # Update the graph with the new data
        try:
            df = pd.read_csv("download_data.csv")
            self.update_graph(df)
        except pd.errors.EmptyDataError:
            print("download_data.csv is empty. Waiting for data...")

    def ssh(self):
        command = 'ssh -i C:\\Users\\micha\\.ssh\\id_rsa lubin@169.231.49.78'
        subprocess.Popen(['start', 'cmd', '/k', command], shell=True)



    def end_test(self):
        """Ends the test"""
        if self.running == True:
            self.running = False
            if self.thread is not None and self.thread.is_alive():
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
