import serial
import time
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class DataLogger:
    def __init__(self, 
                 usb_port, 
                 baud_rate, 
                 time_step,
                 total_time, 
                 batch_size, 
                 sensors, 
                 filename, 
                 sensor_headers,
                 plot_data_while_running,
                 lower_sensor_limits,
                 upper_sensor_limits):

        # timestamps
        datetime_now = datetime.now()
        self.unix_offset = datetime.timestamp(datetime_now)

        # serial connection settings
        self.usb_port = usb_port
        self.baud_rate = baud_rate

        # number of samples to take
        self.time_step = time_step
        self.batch_size = batch_size
        self.total_time = total_time
        self.total_samples = int(total_time/time_step)
        self.batches = int(self.total_samples/batch_size)
        self.sensors = sensors

        # plot settings
        plt.style.use("bmh")
        self.plot_data_while_running = plot_data_while_running
        self.lower_sensor_limits = lower_sensor_limits
        self.upper_sensor_limits = upper_sensor_limits
        self.colors = ['blue', 'orange', 'green', 'red', 'purple',
                       'brown', 'pink', 'gray', 'olive', 'cyan']

        # space allocation
        self.sensor_values = np.empty([self.total_samples, sensors])
        self.elapsed_time = np.empty(self.total_samples)
        self.sensor_values[:] = np.nan
        self.elapsed_time[:] = np.nan
        self.batch_sensor_values = np.empty([batch_size, sensors])
        self.timestamps = np.empty(batch_size)
        
        # csv creation
        self.timestamped_filename = filename + "_" + str(datetime_now).split('.')[0] + ".csv"
        self.timestamp_header = "unix timestamp (s)"
        self.sensor_headers = sensor_headers
        header_data = {self.timestamp_header : []} | { self.sensor_headers[k] : [] for k in range(sensors) }
        pd.DataFrame(header_data).to_csv(self.timestamped_filename, index=False)


    def update(self, i):
        left_index = i*self.batch_size
        right_index = left_index + self.batch_size

        for j in range(self.batch_size): 
            received_line = self.ser.readline()
            self.batch_sensor_values[j] = np.array(received_line.decode('utf-8').split(',')).astype(float)
            self.timestamps[j] = datetime.timestamp(datetime.now())

        sensor_data = { self.sensor_headers[k] : self.batch_sensor_values.T[k] for k in range(self.sensors) }
        data = {self.timestamp_header : self.timestamps} | sensor_data
        pd.DataFrame(data).to_csv(self.timestamped_filename, mode='a', index=False, header=False)

        if self.plot_data_while_running == True:
            self.elapsed_time[left_index:right_index] = self.timestamps - self.unix_offset
            self.sensor_values[left_index:right_index] = self.batch_sensor_values

            for k in range(self.sensors):
                if self.total_time >= 3600:
                    self.line[k].set_data(self.elapsed_time/3600, self.sensor_values.T[k])
                else:
                    self.line[k].set_data(self.elapsed_time, self.sensor_values.T[k])

            return self.line,


    def animation_init(self):
        self.line = list(np.empty(self.sensors))
        if self.total_time >= 3600: 
            self.fig.gca().set_xlabel("elapsed time (hrs)")
        else:
            self.fig.gca().set_xlabel("elapsed time (s)")

        for k in range(self.sensors):
            self.axs[k].set_ylabel(self.sensor_headers[k])
            self.axs[k].set_xlim(0, self.total_samples + self.time_step)
            self.axs[k].set_ylim(self.lower_sensor_limits[k], self.upper_sensor_limits[k])

            if k > len(self.colors):
                p = int(k-np.floor(k/len(self.colors))*len(self.colors))
                color = self.colors[p]
            else:
                color = self.colors[k]
            self.line[k], = self.axs[k].plot([],[], '.', color="tab:"+color)

    
    def run(self):
        time.sleep(0.1)
        self.ser = serial.Serial(self.usb_port, self.baud_rate, timeout=1)

        if self.plot_data_while_running == True:
            self.fig, self.axs = plt.subplots(self.sensors)

            ani = FuncAnimation(self.fig, self.update, init_func=self.animation_init,
                                frames=self.batches, interval=1, repeat=False)
            plt.show()
        elif self.plot_data_while_running == False:
            for i in range(self.batches):
                self.update(i)

        self.ser.close()
        exit()
        

if __name__=='__main__':
    ### instructions
    # - usb port address can be found in the arduino ide
    # - baud rate depends on the arduino
    # - time step should match delay between measurements taken by the arduino
    # - serial data is read assuming 00.0,00.0,00.0 etc. format
    # - total_time/time_step/batch_size has to be an integer value
    # - sensor limits are unused when data plotter is turned off
    # - timestamps are an approximation of the actual time the measurement was taken
    #   - use the delay between measurements in the C++ code as the best time indication

    # total_time = int(input("Runtime in seconds? "))

    DataLogger(
        usb_port="/dev/cu.usbmodem11201", 
        baud_rate=9600, 
        time_step=1,
        total_time=30,
        batch_size=5,
        sensors=2,
        filename="log",
        sensor_headers=["ambient temp (degC)", "light level (0-256)"],
        plot_data_while_running=False,
        lower_sensor_limits=[0,0],
        upper_sensor_limits=[25,256]
    ).run()
