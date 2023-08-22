#!/usr/bin/python3

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sensor_facts

short_description: Gather hardware sensors informations 

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: Gather hardware sensors informations

author:
    - kakwa (@kakwa)
'''

EXAMPLES = r'''
'''

RETURN = r'''
TODO
'''

from ansible.module_utils.basic import AnsibleModule
import os
import re

CATEGORIES = {
    "cpu": ["k10temp", "coretemp"],
    "gpu": ["amdgpu"],
    "disk": ["nvme"],
}

BASE_HWMON = "/sys/class/hwmon/"

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
    # Create a list of tuples containing (file_name, file_content)
    file_contents = []
    for file_name in file_list:
        with open(file_name, 'r') as file:
            content = int(file.read().strip())  # Read and convert content to integer
            file_contents.append((file_name, content))
    
    # Sort the list of tuples based on file content
    sorted_files = sorted(file_contents, key=lambda x: x[1], reverse=True)
    
    # Extract and return the sorted file names
    sorted_file_names = [file_name for file_name, _ in sorted_files]
    return sorted_file_names

def list_temp_sensors():
    dirs = os.listdir("/sys/class/hwmon/")
    ret = init_temp_ret()
    for hwmon in dirs:
        hwmon_dir = os.path.join(BASE_HWMON, hwmon)
        path_name = os.path.join(hwmon_dir, "name")
        # if we don't have a name, stop
        if not os.path.isfile(path_name):
            continue
        temp_sensors = get_temp_sensors(hwmon_dir)
        # no temperature sensors
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
    # define available arguments/parameters a user can pass to the module
    module_args = dict()

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    temp_sensors = list_temp_sensors()
    #result = dict(
    #        sensors_facts={"temp": temp_sensors,},
    #)
    result = dict(ansible_facts=dict(temp_sensors=temp_sensors))

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
