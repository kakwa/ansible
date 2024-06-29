#!/usr/bin/env python3

from i3ipc import Connection
import sys

NUM_WORKSPACE = 10

import logging
import logging.handlers

logger = logging.getLogger('sway-workspace-switcher')
syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
syslog_handler.setFormatter(formatter)
logger.addHandler(syslog_handler)

logger.setLevel(logging.INFO)
# uncomment to activate logging
#logger.setLevel(logging.DEBUG)

i3 = Connection()
workspaces = i3.get_workspaces()
focused_workspace = i3.get_tree().find_focused().workspace()

screens = {} 
outputs = i3.get_outputs()
index = 0

for output in filter(lambda o: o.active, outputs):
    screens[output.name] = {}
    screens[output.name]["focused"] = output.focused
    if output.focused:
        focused_output = output.name
    screens[output.name]["workspaces"] = [False for i in range(NUM_WORKSPACE)]
    screens[output.name]["index"] = index
    index += 1

for workspace in workspaces:
    workspace_index = workspace.num - screens[workspace.output]["index"] * NUM_WORKSPACE - 1
    if workspace_index < 0 or workspace_index >= NUM_WORKSPACE:
        workspace_index = 0
    screens[workspace.output]["workspaces"][workspace_index] = True

windows = [desc.id for desc in focused_workspace.leaves()]

if len(sys.argv) != 2 or sys.argv[1] not in ["next", "prev"]:
    print("specify 'prev' or 'next' argument")
    exit(1)

first_focused_screen_workspace = screens[focused_output]["index"] * NUM_WORKSPACE + 1
last_focused_screen_workspace = screens[focused_output]["index"] * NUM_WORKSPACE + NUM_WORKSPACE

logger.debug(f"focused screen: {screens[focused_output]['index']} | fisrt workspace: {first_focused_screen_workspace} | last workspace: {last_focused_screen_workspace}")

if sys.argv[1] == "next":
    # find_next_active
    if len(windows) > 0:
        logger.debug(f"workspace in use, {len(windows)} windows opened")
        # if we have an active window, then it's just the next workspace (to be created if necessary)
        next_workspace = (focused_workspace.num - screens[focused_output]["index"] * NUM_WORKSPACE) % NUM_WORKSPACE
    else:
        logger.debug(f"workspace empty")
        index = focused_workspace.num - screens[focused_output]["index"] * NUM_WORKSPACE - 1
        next_workspace = 0
        # if we don't have an active window, then just pick
        for i in range(index + 1, NUM_WORKSPACE):
            if screens[focused_output]["workspaces"][i]:
                next_workspace = i
                break

if sys.argv[1] == "prev":
    # find_next_active
    if len(windows) > 0:
        logger.debug(f"workspace in use, {len(windows)} windows opened")
        # if we have an active window, then it's just the next workspace (to be created if necessary)
        next_workspace = (focused_workspace.num - screens[focused_output]["index"] * NUM_WORKSPACE) - 2 % NUM_WORKSPACE
    else:
        logger.debug(f"workspace empty")
        index = focused_workspace.num - screens[focused_output]["index"] * NUM_WORKSPACE - 1
        # if we don't have an active window, then just pick
        next_workspace = -1
        for i in range(0, index):
            rev_index = index - 1 - i
            if screens[focused_output]["workspaces"][rev_index]:
                next_workspace = rev_index
                break
    if next_workspace < 0:
        next_workspace += NUM_WORKSPACE

next_workspace_num = screens[focused_output]["index"] * NUM_WORKSPACE + next_workspace + 1

logger.debug(f"[focus] output: '{focused_output}' | workspace: {focused_workspace.num} | next workspace: {next_workspace} | next workspace_num: {next_workspace_num}")

i3.command("workspace %s" % next_workspace_num)

