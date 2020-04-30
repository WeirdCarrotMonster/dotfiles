#!/usr/bin/env python3

import datetime
import subprocess
import json
import time
from sys import stdout


CLOCK_ICON = {
    "01": "🕐",
    "02": "🕑",
    "03": "🕒",
    "04": "🕓",
    "05": "🕔",
    "06": "🕕",
    "07": "🕖",
    "08": "🕗",
    "09": "🕘",
    "10": "🕙",
    "11": "🕚",
    "12": "🕛"
}


def get_sensor_readings():
    sensor_data_raw = subprocess.check_output(["sensors", "-j"])
    return json.loads(sensor_data_raw)


BASE_READINGS = get_sensor_readings()
CPU_SENSOR = next(
    (
        key
        for key in BASE_READINGS.keys()
        if key.startswith("k10temp-pci")
    ),
    None
)

GPU_SENSOR = next(
    (
        key
        for key in BASE_READINGS.keys()
        if key.startswith("amdgpu-pci")
    ),
    None
)


def get_cpu_temp(sensor_data):
    if not CPU_SENSOR:
        return 0

    value = sensor_data[CPU_SENSOR]["Tdie"]["temp1_input"]
    return int(value)


def get_gpu_temp(sensor_data):
    if not GPU_SENSOR:
        return 0

    value = sensor_data[GPU_SENSOR]["edge"]["temp1_input"]
    return int(value)


def get_gpu_fan_percent(sensor_data):
    if not GPU_SENSOR:
        return 0

    gpu_fan_max = sensor_data[GPU_SENSOR]["fan1"]["fan1_max"]
    gpu_fan_cur = sensor_data[GPU_SENSOR]["fan1"]["fan1_input"]
    return int(100 * gpu_fan_cur / gpu_fan_max)


def do_print_line():
    sensor_data = get_sensor_readings()

    cpu_temp = get_cpu_temp(sensor_data)
    gpu_temp = get_gpu_temp(sensor_data)
    gpu_fan = get_gpu_fan_percent(sensor_data)

    now = datetime.datetime.now()

    _date = now.strftime("%F")
    _time = now.strftime("%H:%M")

    clock = CLOCK_ICON[now.strftime("%I")]

    status_line = f"🌡️ CPU:{cpu_temp} GPU:{gpu_temp} FAN:{gpu_fan}% 📅 {_date} {clock} {_time}\n"

    stdout.write(status_line)
    stdout.flush()


while True:
    do_print_line()
    time.sleep(5)
