#!/usr/bin/env python3

from i3ipc import Connection
import sys

i3 = Connection()
workspaces = i3.get_workspaces()
focused_workspace = i3.get_tree().find_focused().workspace()
focused_window = i3.get_tree().find_focused()

windows = [desc.id for desc in focused_workspace.leaves()]

index = windows.index(focused_window.id)

if len(sys.argv) != 2:
    print("specify 'prev' or 'next' argument")
    exit(1)

if sys.argv[1] == "next":
   index += 1
if sys.argv[1] == "prev":
   index -= 1

if index < 0:
    index = len(windows) - 1
if index >= len(windows):
    index = 0

i3.command('[con_id="%d"] focus' % windows[index])
