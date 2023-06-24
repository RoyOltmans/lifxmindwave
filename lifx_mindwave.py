#!/usr/bin/python
# -*- coding: utf-8 -*-

from mindwave.parser import ThinkGearParser, TimeSeriesRecorder
import bluetooth
import time
import sys
import argparse
import math
from progressbar import ProgressBar, Bar, Percentage

import os
import subprocess
from time import sleep
from subprocess import call

import requests
import json
import urllib
import ConfigParser

from mindwave.bluetooth_headset import connect_magic, connect_bluetooth_addr
from mindwave.bluetooth_headset import BluetoothError
from mindwave.mindwave_startup import mindwave_startup


description = """Simple Neurofeedback console application.

Make sure you paired the Mindwave to your computer. You need to
do that pairing for every operating system/user profile you run
seperately.

If you don't know the address, leave it out, and this program will
figure it out, but you need to put the MindWave Mobile headset into
pairing mode first.

"""

def getLightState(name, type='label'):
    """ This function checks what lights are in the group and what color they are currently set to """
    if name == 'all':
        getAvaliableLights = requests.get(lifxCloud + '/' + name, headers=header)
    else:
        getAvaliableLights = requests.get(lifxCloud + '/' + urllib.quote(type + ':' + name), headers=header)

    if getAvaliableLights.status_code == requests.codes.ok:
        avaliableLights = json.loads(getAvaliableLights.text)
        info = []
        for light in avaliableLights:
            info.append({'id': light['id'], 'label': light['label'], 'power': light['power'], 'hue': light['color']['hue'], 'saturation': light['color']['saturation'],
                'brightness': light['brightness']})
        return info
    return False

def setLight(LightStates, duration=1):
    """ This function's purpose is to set the lights to a given HSK from what they once were"""
    for light in LightStates:
        if light['power'] == 'on':
            power = 'true'
            payload = {
                "states": [
                  {
                       "selector" : "id:" + str(light['id']),
                       "hue": light['hue'],
                       "color": "blue saturation:" + str(light['va']),
                       #"color": "green saturation:" + str(light['vm']),
                       "brightness": light['brightness']
                  },
                  {
                       "selector" : "group:" + str(bulbs['set']),
                       "brightness": light['brightness']
                  }
                ],
                "defaults": {
                    "power": "on",
                    "saturation": str(light['saturation']),
                    "duration": 2.0
                }
            }
            response = requests.put(apiLifxURL, data=json.dumps(payload), headers=header)
            #print(response.content)
        else:
            power = 'false'
            turnOff(name=light['id'], type='id', duration=duration)
            continue

def turnOff(name, type='label', duration=1):
    """ This function turns off a given group or light """
    powerCommand = lifxCloud + '/' + urllib.quote(type + ':' + name) + '/power.json'
    option = {'state': 'off', 'duration': duration}
    requests.put(powerCommand, json=option, headers=header)
    return

def loadConfig ():
    global header
    global bulbs
    global setColor
    global config
    global apiLifxURL

    confpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lifx.cfg')
    config = ConfigParser.RawConfigParser()
    config.readfp(open(confpath))

    apiLifxURL = 'https://api.lifx.com/v1/lights/states'
    apiKey = config.get('Authentication', 'apiKey')
    apiKey = 'Bearer ' + apiKey
    header = {'content-type': 'application/json', 'Authorization': apiKey}

    bulbs = {'type': config.get('Bulbs', 'type'), 'set': config.get('Bulbs', 'set')}
    bulbURL = urllib.quote(bulbs['type'] + ':' + bulbs['set'])
    setColor = lifxCloud + bulbURL + '/color.json'

if __name__ == '__main__':
#    extra_args=[dict(name='measure', type=str, nargs='?',
#            const="attention", default="attention",
#            help="""Measure you want feedback on. Either "meditation"            or "attention\"""")]
#    socket, args = mindwave_startup(description=description,
#                              extra_args=extra_args)
#
#    if args.measure not in ["attention", "meditation"]:
#        print "Unknown measure %s" % repr(args.measure)
#        sys.exit(-1)
    recorder = TimeSeriesRecorder()
    parser = ThinkGearParser(recorders=[recorder])
    measure_name = 'Attention'
    meditation_val = 0
    bar = ProgressBar(widgets=[measure_name, Percentage(), Bar()]).start()
    lifxCloud = 'https://api.lifx.co/v1beta1/lights/'
    loadConfig()
    print(getLightState("all"))
    while 1:
        time.sleep(0.25)
        vm = 0
        va = 0
        try:
            try: 
                socket.send("")
            except:
                extra_args=[dict(name='measure', type=str, nargs='?',
                        const="attention", default="attention",
                        help="""Measure you want feedback on. Either "meditation"
                        or "attention\"""")]
                socket, args = mindwave_startup(description=description,
                                          extra_args=extra_args)
                if args.measure not in ["attention", "meditation"]:
                    print "Unknown measure %s" % repr(args.measure)
                    sys.exit(-1)
            data = socket.recv(1024)
            parser.feed(data)
            if len(recorder.attention)>0:
                va = recorder.attention[-1]
                vm = recorder.meditation[-1]
                bar.start()
            if va>0:
                attention_val = ((0.5/100)*float(va))+0.5
                meditation_val = ((0.5/100)*float(vm))+0.5
                print(attention_val)
                print(meditation_val)
                setLight([{'hue': 180, 'saturation': 0.576, 'vm': meditation_val,'va': attention_val, 'power': u'on', 'brightness':  0.5, 'label': u'Name of lam', 'id': u'xxxxxxxxx'}],0)
                print('changing light state')
                measure_name = 'Attention'
                bar = ProgressBar(widgets=[measure_name, Percentage(), Bar()]).start()
                meditation_val = ((0.5/100)*float(vm))+0.5
                print(meditation_val)
                bar.update(va)
                measure_name = 'Meditation'
                bar = ProgressBar(widgets=[measure_name, Percentage(), Bar()]).start()
                bar.update(vm)
                #time.sleep(1) # Sleep for x seconds
        except bluetooth.btcommon.BluetoothError as error:
            print "Caught BluetoothError: ", error
            time.sleep(5)
            socket.close()
            time.sleep(2)
            pass
