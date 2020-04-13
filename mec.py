#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#vi: set autoindent noexpandtab tabstop=4 shiftwidth=4

import requests
from requests.auth import HTTPBasicAuth
import json
from ConfigParser import SafeConfigParser
from venus_meter import VenusMeter

from dbus.mainloop.glib import DBusGMainLoop
import gobject
from gobject import idle_add
import dbus
import dbus.service
import inspect
import pprint
import os
import sys
import threading
import time

global demo
demo = 1

def read_settings() :
	parser = SafeConfigParser()
	parser.read('mec.ini')
	global setting_url, setting_user, setting_pw
	setting_url = parser.get('MEC', 'url')
	setting_user = parser.get('MEC', 'username')
	setting_pw = parser.get('MEC', 'password')

def mec_read_example() :
	with open("example_mec.json") as f:
		data = json.load(f)
	return data

def mec_parse_data( data ) :
	powertotal = data['PT']
	time = data['TIME']
	print("++++++++++")
	print("POWER Phase A: " + str(data['PA']) + "W")
	print("POWER Phase B: " + str(data['PB']) + "W")
	print("POWER Phase C: " + str(data['PC']) + "W")
	print("POWER Total: " + str(data['PT']) + "W")
	print("Time: " + str(data['TIME']) + "ms")
	print("MEC Status: " + str(data['STATUS']))

def mec_data_read_cb( jsonstr ) :
	mec_parse_data ( jsonstr )
	return

def mec_read_data ( url ) :
	global setting_user, setting_pw, demo

	if demo == 0:
		response = requests.get( url, verify=False, auth=HTTPBasicAuth(setting_user, setting_pw))
		# For successful API call, response code will be 200 (OK)
		if(response.ok):
			print("code:"+ str(response.status_code))
			print("******************")
			print("headers:"+ str(response.headers))
			print("******************")
			#print("content text:"+ str(response.text))
			#print("******************")
			mec_data_read_cb( jsonstr=response.json() )
		else:
			print("Failure code:"+ str(response.status_code))
	else:
		data = mec_read_example()
		mec_data_read_cb(data)
	return

def mec_update_cyclic(run_event) :
	global setting_url

	while run_event.is_set():
		print("Thread: doing")
		mec_read_data( setting_url )
		time.sleep(1)
	print("Thread: Exit")
	return

global setting_url
DBusGMainLoop(set_as_default=True)
mec = VenusMeter('mec_tcp_50','tcp REST',50,'1234567','Mec Meter', '1.0','0.1' )
read_settings()
print("Using " + setting_url + " user: " + setting_user)

try:
	run_event = threading.Event()
	run_event.set()

	update_thread = threading.Thread(target=mec_update_cyclic, args=(run_event,))
	update_thread.start()

	gobject.threads_init()
	mainloop = gobject.MainLoop()
	mainloop.run()

except (KeyboardInterrupt, SystemExit):
	mainloop.quit()
	run_event.clear()
	update_thread.join()
	print("Host: KeyboardInterrupt")
