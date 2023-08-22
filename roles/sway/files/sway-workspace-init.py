#!/usr/bin/env python3

from i3ipc import Connection
import sys

NUM_WORKSPACE = 10

i3 = Connection()
outputs = i3.get_outputs()
index = 0

for output in filter(lambda o: o.active, outputs):
    next_workspace_num = index * NUM_WORKSPACE + 1
    if output.focused:
        starting_output = output.name
    i3.command("focus output %s" % output.name)
    i3.command("workspace %s" % next_workspace_num)
    index += 1

i3.command("focus output %s" % starting_output)
