#!/usr/bin/env python3

from i3ipc import Connection
import sys

NUM_WORKSPACE = 10

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

#print(screens)

windows = [desc.id for desc in focused_workspace.leaves()]

#print(f"[focus] output: '{focused_output}' | workspace: {focused_workspace.num}")

if len(sys.argv) != 2 or sys.argv[1] not in ["next", "prev"]:
    print("specify 'prev' or 'next' argument")
    exit(1)

if sys.argv[1] == "next":
    # find_next_active
    if len(windows) > 0:
        # if we have an active window, then it's just the next workspace (to be created if necessary)
        next_workspace = (focused_workspace.num - screens[focused_output]["index"] * NUM_WORKSPACE) % NUM_WORKSPACE
    else:
        index = focused_workspace.num - screens[focused_output]["index"] * NUM_WORKSPACE - 1
        # if we don't have an active window, then just pick
        next_workspace = 0
        for i in range(index + 1, NUM_WORKSPACE):
            if screens[focused_output]["workspaces"][i]:
                next_workspace = i
                break

if sys.argv[1] == "prev":
    # find_next_active
    if len(windows) > 0:
        # if we have an active window, then it's just the next workspace (to be created if necessary)
        next_workspace = (focused_workspace.num - screens[focused_output]["index"] * NUM_WORKSPACE) - 2 % NUM_WORKSPACE
    else:
        index = focused_workspace.num - screens[focused_output]["index"] * NUM_WORKSPACE - 1
        # if we don't have an active window, then just pick
        next_workspace = 0
        for i in range(0, index):
            rev_index = index - 1 - i
            if screens[focused_output]["workspaces"][rev_index]:
                next_workspace = rev_index
                break
    if next_workspace < 0:
        next_workspace += NUM_WORKSPACE

next_workspace_num = screens[focused_output]["index"] * NUM_WORKSPACE + next_workspace + 1

#print(f"[next_workspace] num : {next_workspace_num} | output {focused_output} | index on output: {next_workspace}")

i3.command("workspace %s" % next_workspace_num)

