#!/usr/bin/env python3
import sys
import os
import json
import argparse
import subprocess

def get_device_info(device):
    name = device["ifname"]
    state = device["operstate"]
    addr = ""
    for addr_info in device["addr_info"]:
        if addr_info["family"] == "inet":
            addr = addr_info["local"]
    return name, state, addr

def netstate(opts):
    iface_cmd = "ip -json -det address"
    status, output = subprocess.getstatusoutput(iface_cmd)
    if status != 0:
        return status
    
    is_wifi = False
    ssid = ""
    state = ""
    ip = ""

    iface_data = json.loads(output)
    if opts.iface:
        for iface in iface_data:
            if iface["ifname"] != opts.iface:
                continue
            name, state, ip = get_device_info(iface)
            if name.startswith("wlan"):
                is_wifi = True
    else:
        # Check if the WIFI interface is up
        devices = [dev for dev in iface_data if dev["ifname"].startswith("wlan")]
        for dev in devices:
            if dev["operstate"] == "UP":
                is_wifi = True
            name, state, ip = get_device_info(dev)
        
    if is_wifi:
        status, output = subprocess.getstatusoutput("iwgetid")
        if status == 0:
            dev, ssid = output.split()
            if dev == name:
                ssid = ssid.rpartition(':')[2][1:-1]

    print(f"VALUE_UPDATE:wifi={int(is_wifi)}")
    print(f"VALUE_UPDATE:state={state}")
    print(f"VALUE_UPDATE:ip={ip}")
    print(f"VALUE_UPDATE:ssid={ssid}")
    return 0

def netop(opts):
    cmd = "systemctl restart network"
    status, output = subprocess.getstatusoutput(cmd)
    if status != 0:
        return status
    
    return netstate(opts)

parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(title="Network Commands")
state_parser = subparser.add_parser("netstate")
state_parser.add_argument("-i", dest="iface", help="Network interface")
state_parser.set_defaults(handler=netstate)
op_parser = subparser.add_parser("netrestart", help="Restart network")
op_parser.set_defaults(handler=netop)

def main():
    opts = parser.parse_args()

    return opts.handler(opts)

sys.exit(main())