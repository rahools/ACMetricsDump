"""
ACMetricDump is a simple app that logs race related telemetry data to a source.

Currently it logs the data in a CSV format. In the future it will be extended to
log to a database or stream data to kafka.

The data is logged to a file called metricdump_{car_name}_{track_name}_{session_start_time}.csv in the same directory as the
app.

The data is logged in the following format:
    {
        "timestamp": 0.0,

        # car scalar state
        "speed": 0.0,
        "rpm": 0.0,
        "gear": 0,

        # car vector state
        "local_velocity": [0.0, 0.0, 0.0],
        "local_angular_velocity": [0.0, 0.0, 0.0],

        # tyre state
        "thermal_state": [0.0, 0.0, 0.0, 0.0],
        "dynamic_pressure": [0.0, 0.0, 0.0, 0.0],
        "tyre_loaded_radius": [0.0, 0.0, 0.0, 0.0],
        "suspension_travel": [0.0, 0.0, 0.0, 0.0],
        "tyre_dirty_level": [0.0, 0.0, 0.0, 0.0],
        "slip_angle": [0.0, 0.0, 0.0, 0.0],

        # input state
        "gas": 0.0,
        "brake": 0.0,
        "clutch": 0.0,
        "last_ff": 0.0,
        "steer": 0.0,

        # session state
        "lap_count": 0,
        "lap_invalidated": 0,
        "lap_time": 0.0,
        "normalized_spline_position": 0.0,
        "performance_meter": 0.0,
    }

NOTE: This script is meant for python 3.3.7.
"""
# ----------------------------------- #
# ------------- imports ------------- #
# ----------------------------------- #

import ac
import acsys


import os
import io
from queue import Queue
import threading
import time
import csv
from datetime import datetime

# ------------------------------------ #
# ------------- settings ------------- #
# ------------------------------------ #

log_file_path = os.path.dirname(os.path.abspath(__file__))

# setting speed format
# it could be:
#   - SpeedKMH
#   - SpeedMS
#   - SpeedMPH
SPEED_FORMAT = "SpeedKMH"

# ------------------------------------- #
# ------------- constants ------------- #
# ------------------------------------- #

columns = [
    "timestamp",
    "speed",
    "rpm",
    "gear",
    "local_velocity",
    "local_angular_velocity",
    # "thermal_state",
    # "dynamic_pressure",
    # "tyre_loaded_radius",
    # "suspension_travel",
    # "tyre_dirty_level",
    # "slip_angle",
    "gas",
    "brake",
    "clutch",
    "last_ff",
    "steer",
    "lap_count",
    "lap_invalidated",
    "lap_time",
    "normalized_spline_position",
    "performance_meter",
]
last_spline_position = -1

# ------------------------------------- #
# ------------- functions ------------- #
# ------------------------------------- #

def dumpHelper(csv_path: str, buffer: Queue):
    """
    This is a helper function that is responsible for:
        - reading the buffer queue
        - writing the data to the dump file
    """
    ac.log("Dump helper started...")

    # open the csv file
    csv_file = open(csv_path, "a", newline='')
    csv_writer = csv.writer(csv_file)

    while True:
        data = buffer.get()

        # break condition for the thread
        if data is None:
            csv_file.flush()
            csv_file.close()
            break

        # ac.log(str(data))
        # csv_file.write(",".join([str(data[column]) for column in columns]) + "\n")
        csv_writer.writerow([data[column] for column in columns])

def acMain(ac_version):
    """
    This is the setup function for the app. It is called when the app is loaded
    into Assetto Corsa. In other words, this is the entry point for the app and 
    this function runs once. 

    This function is responsible:
        - creating the app window
        - creating the buffer queue
        - creating/opening the dump file
        - starting the dump helper thread
    """
    # create the app
    appWindow = ac.newApp("ACMetricsDump")
    ac.setSize(appWindow, 200, 75)

    # create buffer queue
    global buffer
    buffer = Queue()

    # get the car name and track name
    car_name = ac.getCarName(0)
    track_name = ac.getTrackName(0)

    # dump file initialization
    global csv_path
    csv_path = "{}/metricdump_{}_{}_{}.csv".format(log_file_path, car_name, track_name, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    csv_file_exists = os.path.exists(csv_path)

    # if csv doesn't exists, create one. 
    # Otherwise, open it.
    if not csv_file_exists:
        csv_file = open(csv_path, "w", newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(columns)
        csv_file.close()

    # start the dump helper in a new thread
    global dump_thread
    dump_thread = threading.Thread(target=dumpHelper, args=(csv_path, buffer))
    dump_thread.start()

    # add a label to tell buffer size
    global buffer_size_label
    buffer_size_label = ac.addLabel(appWindow, "Buffer size: 0")
    ac.setPosition(buffer_size_label, 10, 30)

    return "ACMetricsDump"

def acUpdate(deltaT):
    """
    This function is called every frame. It is responsible for:
        - reading the telemetry data
        - adding the data to the buffer
    """
    global buffer
    global last_spline_position

    # read the telemetry data
    data = {}
    data["timestamp"] = time.time()
    data["speed"] = ac.getCarState(0, getattr(acsys.CS, SPEED_FORMAT))
    data["rpm"] = ac.getCarState(0, acsys.CS.RPM)
    data["gear"] = ac.getCarState(0, acsys.CS.Gear)
    data["local_velocity"] = ac.getCarState(0, acsys.CS.LocalVelocity)
    data["local_angular_velocity"] = ac.getCarState(0, acsys.CS.LocalAngularVelocity)
    # data["thermal_state"] = ac.getCarState(0, acsys.CS.ThermalState)
    # data["dynamic_pressure"] = ac.getCarState(0, acsys.CS.DynamicPressure)
    # data["tyre_loaded_radius"] = ac.getCarState(0, acsys.CS.TyreLoadedRadius)
    # data["suspension_travel"] = ac.getCarState(0, acsys.CS.SuspensionTravel)
    # data["tyre_dirty_level"] = ac.getCarState(0, acsys.CS.TyreDirtyLevel)
    # data["slip_angle"] = ac.getCarState(0, acsys.CS.SlipAngle)
    data["gas"] = ac.getCarState(0, acsys.CS.Gas)
    data["brake"] = ac.getCarState(0, acsys.CS.Brake)
    data["clutch"] = ac.getCarState(0, acsys.CS.Clutch)
    data["last_ff"] = ac.getCarState(0, acsys.CS.LastFF)
    data["steer"] = ac.getCarState(0, acsys.CS.Steer)
    data["lap_count"] = ac.getCarState(0, acsys.CS.LapCount)
    data["lap_invalidated"] = ac.getCarState(0, acsys.CS.LapInvalidated)
    data["lap_time"] = ac.getCarState(0, acsys.CS.LapTime)
    data["normalized_spline_position"] = float(str(ac.getCarState(0, acsys.CS.NormalizedSplinePosition))[:7])
    data["performance_meter"] = ac.getCarState(0, acsys.CS.PerformanceMeter)

    # add the data to the buffer, only if the spline position has changed
    if data["normalized_spline_position"] != last_spline_position:
        buffer.put(data)

    # calculate the spline position
    last_spline_position = data["normalized_spline_position"]

    # update the buffer size label
    global buffer_size_label
    ac.setText(buffer_size_label, "Buffer size: {}".format(buffer.qsize()))

def acShutdown():
    """
    This function is called when the app is closed. It is responsible for:
        - stopping the dump helper thread
        - closing the dump file
    """
    # send stop signal to the thread
    global buffer
    buffer.put(None)
    buffer.put(None)
    buffer.put(None)
    buffer.put(None)

    # wait for the thread to stop
    global dump_thread
    dump_thread.join()