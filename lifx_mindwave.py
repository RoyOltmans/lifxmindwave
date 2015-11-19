#!/usr/bin/python
# -*- coding: utf-8 -*-

from mindwave.parser import ThinkGearParser, TimeSeriesRecorder
import bluetooth
import time
import sys
import argparse
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
from mindwave_startup import mindwave_startup


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
            option = {'color': 'hsb:' + str(light['hue']) + ',' + str(light['saturation']) + ',' + str(light['brightness']), 'duration': duration, 'power': power}
            chooseBulb = lifxCloud + '/' + urllib.quote('id:') + light['id'] + '/color.json'
            requests.put(chooseBulb, json=option, headers=header)
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

    confpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lifx.cfg')
    config = ConfigParser.RawConfigParser()
    config.readfp(open(confpath))

    apiKey = config.get('Authentication', 'apiKey')
    apiKey = 'Bearer ' + apiKey
    header = {'content-type': 'application/json', 'authorization': apiKey}

    bulbs = {'type': config.get('Bulbs', 'type'), 'set': config.get('Bulbs', 'set')}
    bulbURL = urllib.quote(bulbs['type'] + ':' + bulbs['set'])
    setColor = lifxCloud + bulbURL + '/color.json'

if __name__ == '__main__':
    extra_args=[dict(name='measure', type=str, nargs='?',
            const="attention", default="attention",
            help="""Measure you want feedback on. Either "meditation"
            or "attention\"""")]
    socket, args = mindwave_startup(description=description,
                              extra_args=extra_args)

    if args.measure not in ["attention", "meditation"]:
        print "Unknown measure %s" % repr(args.measure)
        sys.exit(-1)
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
        data = socket.recv(20000)
        parser.feed(data)
        vm = 0
        va = 0
        if len(recorder.attention)>0:
            va = recorder.attention[-1]
            vm = recorder.meditation[-1]
            bar.start()
        if va>0:
            attention_val = ((0.5/100)*float(vm))+0.5
            print(attention_val)
            setLight([{'hue': 100.097047379263, 'saturation': attention_val, 'power': u'on', 'brightness': 1.0, 'label': u'PFLab Bulb 2', 'id': u'd073d5009e89'}, {'hue': 5.097047379263, 'saturation': meditation_val, 'power': u'on', 'brightness': 1.0, 'label': u'PFLab Bulb 1', 'id': u'd073d501a034'}],0)
            measure_name = 'Attention'
            bar = ProgressBar(widgets=[measure_name, Percentage(), Bar()]).start()
            meditation_val = ((0.5/100)*float(vm))+0.5
            print(meditation_val)
            setLight([{'hue': 100.097047379263, 'saturation': attention_val, 'power': u'on', 'brightness': 1.0, 'label': u'PFLab Bulb 2', 'id': u'd073d5009e89'}, {'hue': 5.097047379263, 'saturation': meditation_val, 'power': u'on', 'brightness': 1.0, 'label': u'PFLab Bulb 1', 'id': u'd073d501a034'}],0)
            bar.update(va)
            measure_name = 'Meditation'
            bar = ProgressBar(widgets=[measure_name, Percentage(), Bar()]).start()
            bar.update(vm)

