# arduino-logger
Arduino serial data logger using the serial package. Data is stored in a .csv file and can be plotted in a continuously updating graph.

instructions
  - usb port address can be found in the arduino ide when arduino board is connected
  - baud rate depends on the arduino
  - time step should match delay between measurements taken by the arduino
  - serial data is read assuming 00.0,00.0,00.0 etc. format
  - total_time/time_step/batch_size has to be an integer value
  - sensor limits are unused when data plotter is turned off
  - timestamps are an approximation of the actual time the measurement was taken
  - use the delay between measurements in the C++ code as the best time indication
