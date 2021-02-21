#!/usr/bin/env python3

import os
import re
import subprocess
import sys

SUBPROCESS_ENV = os.environ.copy()
SUBPROCESS_ENV["LC_ALL"] = "C"
PROP_RE = re.compile(" = |: ")


def get_cmd_output(cmd, **kwargs) -> str:
    return (
        subprocess.run(cmd, env=SUBPROCESS_ENV, stdout=subprocess.PIPE, **kwargs)
        .stdout.decode()
        .strip()
    )


def call_menu_gui(choices, prompt):
    lines = str(len(choices))
    value = get_cmd_output(
        # ["rofi", "-dmenu", "-p", prompt, "-lines", lines],
        [
            "wofi",
            "--dmenu",
            "--prompt",
            prompt,
            "--lines",
            lines,
            "--cache-file",
            "/dev/null",
        ],
        input="\n".join(sorted(choices.keys())).encode(),
    )

    if not value:
        return None

    return choices[value]


def node_walk(nodes):
    for node in nodes:
        yield node
        yield from node_walk(node.get("nodes") or [])


def line_to_prop(line):
    splitted = PROP_RE.split(line)

    if len(splitted) != 2:
        return None

    key, value = splitted

    return key, value.strip('"')


def pacmd_to_props(output, separator):
    result = []

    for group in filter(None, output.split(separator)):
        lines = (line.strip() for line in group.splitlines())

        result.append(
            dict([("INDEX", next(lines)), *filter(None, map(line_to_prop, lines))])
        )

    return result


def get_current_node():
    import json

    sway_tree_parsed = json.loads(
        get_cmd_output(["/usr/bin/swaymsg", "-t", "get_tree"])
    )

    nodes = sway_tree_parsed.get("nodes") or []
    return next((_ for _ in node_walk(nodes) if _.get("focused")), None)


def get_matching_inputs_for_pid(pid):
    all_inputs = pacmd_to_props(
        get_cmd_output(["pactl", "list", "sink-inputs"]), "Sink Input #"
    )

    return [
        sink_input
        for sink_input in all_inputs
        if sink_input.get("application.process.id") == str(pid)
    ]


def get_matching_inputs_for_app(app):
    all_inputs = pacmd_to_props(
        get_cmd_output(["pactl", "list", "sink-inputs"]), "Sink Input #"
    )

    return [
        sink_input
        for sink_input in all_inputs
        if sink_input.get("application.icon_name") == app
    ]


def get_all_sinks():
    sinks = pacmd_to_props(get_cmd_output(["pactl", "list", "sinks"]), "Sink #")

    return {sink["Description"]: sink["Name"] for sink in sinks}


select_for = "Default sink"
matching_inputs = None

if "default" not in sys.argv[1:]:
    if current_node := get_current_node():
        if "pid" in current_node:
            if matching_inputs := get_matching_inputs_for_pid(current_node["pid"]):
                select_for = current_node["name"]

            if not matching_inputs and "app_id" in current_node:
                # Probably a flatpak application
                if matching_inputs := get_matching_inputs_for_app(current_node["app_id"]):
                    select_for = current_node["name"]


if chosen_sink_id := call_menu_gui(choices=get_all_sinks(), prompt=select_for):
    if matching_inputs:
        for m_input in matching_inputs:
            subprocess.call(
                ["pactl", "move-sink-input", m_input["INDEX"], chosen_sink_id]
            )
    else:
        subprocess.call(["pactl", "set-default-sink", chosen_sink_id])
