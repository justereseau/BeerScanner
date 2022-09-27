#!/usr/bin/python3

# Require Sudo

# Requirements: linux-headers-$(uname -r) 
# apt-get install python-gobject libnotify-bin libnotify-dev python-devel
# sudo pip3 install requests evdev 

import os
import sys
import evdev
import requests
import json
from time import sleep
from threading import Thread

class DeviceManager:
    def __init__(self, device_name):
        self.listening_devices = []
        self.device_name = device_name

    def device_in_listeners(self, device):
        for listener in self.listening_devices:
            if listener.get_name() == device.phys:
                return True
        return False

    def listener_in_devices(self, devices, listener):
        for device in devices:
            if device.phys == listener.get_name():
                return True
        return False

    def update_devices(self):
        found_devices = [evdev.InputDevice(dev) for dev in evdev.list_devices()]
        # Add new connected devices
        for device in found_devices:
            if device.name == self.device_name and not self.device_in_listeners(device):
                self.add_device(device)

        # Remove missing devices listeners
        for device in self.listening_devices:
            if not self.listener_in_devices(found_devices, device):
                self.listening_devices.remove(device)

    def add_device(self, device):
        self.listening_devices.append(DeviceListener(device))

    def print_devices(self):
        for device in self.listening_devices:
            print(device.get_name())

class DeviceListener:
    def __init__(self, device):
        self.device = device
        self.device.grab()
        self.thread = Thread(target=self.listening_loop, daemon=True)
        self.thread.start()
    
    def listening_loop(self):
        uid = []
        try:
            for event in self.device.read_loop():
                if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                    e_code = event.code - 1
                    if e_code >= 1 and e_code <= 10:
                        if e_code == 10:
                            uid.append(str(0))
                        else:
                            uid.append(str(e_code))
                        sys.stdout.flush()
                    elif e_code == 27: # enter minus one
                        on_read(self.get_name(), ''.join(uid))
                        uid = []
        except OSError:
            del self

    def get_name(self):
        return self.device.phys

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def on_read(reader, uid):
    parameters = {
        "reader_id": reader,
        "tag_id": uid
    }
    response = requests.post("http://beer.justereseau.ca/api/scan/", data=parameters, timeout=3)
    # Notify.Notification.new("Hi").show()
    if response.status_code == 200 or response.status_code == 201:
        jprint(response.json())
    elif response.status_code == 404:
        print("Unknown tag or reader.")
    else:
        print(response)


device_manager = DeviceManager("Sycreader RFID Technology Co., Ltd SYC ID&IC USB Reader")

while True:
    device_manager.update_devices()
    sleep(1)
