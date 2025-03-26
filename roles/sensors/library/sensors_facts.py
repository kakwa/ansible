#!/usr/bin/python3

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
import multiprocessing
import threading
import math
import time
import re
import os
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sensor_facts

short_description: Gather hardware sensors information with Python-based stress testing

version_added: "1.3.0"

description:
    - Gather hardware sensors information
    - Perform stress testing using pure Python methods
    - Supports configurable stress duration and intensity for CPU and GPU

options:
    stress_duration:
        description:
            - Duration of stress testing in seconds
            - Applies to both CPU and GPU if stress testing is enabled
        required: false
        type: int
        default: 60

    stress_cpu:
        description: Perform CPU stress testing
        required: false
        type: bool
        default: true

    stress_threads:
        description: Number of threads to use for CPU stress
        required: false
        type: int
        default: 0  # 0 means auto-detect number of CPU cores

author:
    - kakwa (@kakwa)
'''

EXAMPLES = r'''
- name: Gather sensor facts with Python stress testing
  sensor_facts:
    stress_duration: 120
    stress_cpu: true
    stress_threads: 4

- name: Gather sensor facts without stress testing
  sensor_facts:
    stress_cpu: false
'''

RETURN = r'''
ansible_facts:
    description: Dictionary of temperature sensors by category
    type: dict
    contains:
        temp_sensors:
            description: List of temperature sensor files for each category
            type: dict
            contains:
                cpu:
                    description: CPU temperature sensors
                    type: list
                gpu:
                    description: GPU temperature sensors
                    type: list
                disk:
                    description: Disk temperature sensors
                    type: list
'''


CATEGORIES = {
    "cpu": ["k10temp", "coretemp"],
    "gpu": ["amdgpu"],
    "disk": ["nvme"],
}

BASE_HWMON = "/sys/class/hwmon/"


def cpu_stress_worker(duration_per_thread, stop_event):
    """
    Worker function to stress a single CPU core

    Args:
        duration_per_thread (float): Duration to stress this thread
        stop_event (threading.Event): Event to signal thread to stop
    """
    start_time = time.time()

    while not stop_event.is_set():
        # Perform computationally intensive operations
        # Using a mix of floating-point and integer calculations
        x = 0.0001
        for _ in range(300):
            x = math.sin(x) * math.cos(x)
            x = x * x + math.sqrt(abs(x))

        # Check if we've exceeded the designated duration
        if time.time() - start_time > duration_per_thread:
            break


def stress_cpu(duration, num_threads=0):
    """
    Stress test the CPU using Python threads

    Args:
        duration (int): Total stress test duration in seconds
        num_threads (int): Number of threads to use. 0 means auto-detect
    """
    # Determine number of threads
    if num_threads <= 0:
        num_threads = multiprocessing.cpu_count()

    # Create a stop event to coordinate thread termination
    stop_event = threading.Event()

    # Create threads
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(
            target=cpu_stress_worker,
            args=(duration, stop_event)
        )
        thread.start()
        threads.append(thread)

    # Signal threads to stop
    stop_event.set()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()


def get_temp_sensors(hwmon_dir):
    files = os.listdir(hwmon_dir)
    ret = []
    for file in files:
        if re.match(r"temp[0-9]*_input", file):
            temp_sensor = os.path.join(hwmon_dir, file)
            ret.append(temp_sensor)
    return ret


def get_category(name):
    for cat in CATEGORIES:
        if name in CATEGORIES[cat]:
            return cat
    return None


def init_temp_ret():
    ret = {}
    for cat in CATEGORIES:
        ret[cat] = []
    return ret


def sort_files_by_content(file_list):
    file_contents = []
    for file_name in file_list:
        with open(file_name, 'r') as file:
            content = int(file.read().strip())
            file_contents.append((file_name, content))

    sorted_files = sorted(file_contents, key=lambda x: x[1], reverse=True)
    sorted_file_names = [file_name for file_name, _ in sorted_files]
    return sorted_file_names


def list_temp_sensors():
    dirs = os.listdir("/sys/class/hwmon/")
    ret = init_temp_ret()
    for hwmon in dirs:
        hwmon_dir = os.path.join(BASE_HWMON, hwmon)
        path_name = os.path.join(hwmon_dir, "name")
        if not os.path.isfile(path_name):
            continue
        temp_sensors = get_temp_sensors(hwmon_dir)
        if len(temp_sensors) == 0:
            continue
        with open(path_name, "r") as f:
            name = f.read().rstrip()

        category = get_category(name)
        if category is not None:
            ret[category] += temp_sensors

    # Sort the Sensors by temperature
    for cat in ret:
        ret[cat] = sort_files_by_content(ret[cat])

    return ret


def run_module():
    # Define module arguments
    module_args = dict(
        stress_duration=dict(type='int', required=False, default=1),
        stress_cpu=dict(type='bool', required=False, default=True),
        stress_threads=dict(type='int', required=False, default=0)
    )

    # Initialize the Ansible module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    # Extract parameters
    stress_duration = module.params['stress_duration']
    stress_cpu_enabled = module.params['stress_cpu']
    stress_threads = module.params['stress_threads']

    # Perform stress testing if enabled
    try:
        if stress_cpu_enabled:
            stress_cpu(stress_duration, stress_threads)

        # Short pause after stress testing to stabilize temperatures
    except Exception as e:
        module.fail_json(msg="Python stress testing failed: {}".format(str(e)))

    # Gather temperature sensors
    temp_sensors = list_temp_sensors()
    result = dict(ansible_facts=dict(temp_sensors=temp_sensors))

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
