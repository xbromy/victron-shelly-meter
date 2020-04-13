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
global mec_is_init
mec_is_init = 0

def read_settings() :
	parser = SafeConfigParser()
	parser.read('mec.ini')
	global setting_url, setting_user, setting_pw, setting_statusurl
	setting_url = parser.get('MEC', 'url')
	setting_statusurl = parser.get('MEC', 'statusurl')
	setting_user = parser.get('MEC', 'username')
	setting_pw = parser.get('MEC', 'password')

def mec_read_example(filename) :
	with open(filename) as f:
		data = json.load(f)
	#print(data)
	return data

def mec_parse_data( data ) :
	global mec, mec_is_init

	# read same variables only the first time
	if mec_is_init == 0:
		#mec.set('/ProductName', str(jsonstr['hardware']))
		mec_is_init = 1

	mec.set('/Ac/Power', (data['PT'],0))
	mec.set('/Ac/Current', (data['IN0']), 1)
	mec.set('/Ac/Voltage', (data['VT']))
	mec.set('/Ac/L1/Current', (data['IA']), 1)
	mec.set('/Ac/L1/Voltage', (data['VA']))
	mec.set('/Ac/L1/Power', (data['PA']))
	mec.set('/Ac/L2/Current', (data['IB']), 1)
	mec.set('/Ac/L2/Voltage', (data['VB']))
	mec.set('/Ac/L2/Power', (data['PB']))
	mec.set('/Ac/L3/Current', (data['IC']), 1)
	mec.set('/Ac/L3/Voltage', (data['VC']))
	mec.set('/Ac/L3/Power', (data['PC']))

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

def mec_status_read_cb( jsonstr ) :
	global mec
	mec = VenusMeter('mec_tcp_50','tcp REST',50,'0','Mec Meter', '0','0')
	mec.set('/ProductName', str(jsonstr['hardware']))
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
		data = mec_read_example("example_mec_data.json")
		mec_data_read_cb(data)
	return

def mec_read_status ( url ) :
	global demo

	if demo == 0:
		response = requests.get( url ) # no auth an status read
		# For successful API call, response code will be 200 (OK)
		if(response.ok):
			print("code:"+ str(response.status_code))
			print("******************")
			print("headers:"+ str(response.headers))
			print("******************")
			#print("content text:"+ str(response.text))
			#print("******************")
			mec_status_read_cb( jsonstr=response.json() )
		else:
			print("Failure code:"+ str(response.status_code))
	else:
		data = mec_read_example("example_mec_status.json")
		mec_status_read_cb(data)
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
#if demo == 0:
#mec = VenusMeter('mec_tcp_50','tcp REST',50,'1234567','Mec Meter', '1.0','0.1' )
read_settings()
print("Using " + setting_url + " user: " + setting_user)
#else:
#mec = VenusMeter('mec_tcp_50','DEMO File',50,'1234567','Mec Meter', '1.0','0.1' )
mec_read_status(setting_url) # first read

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
