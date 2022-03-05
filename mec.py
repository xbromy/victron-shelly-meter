#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#vi: set autoindent noexpandtab tabstop=4 shiftwidth=4

import requests
from requests.auth import HTTPBasicAuth
import json
try:
	from ConfigParser import SafeConfigParser
except:
	from configparser import SafeConfigParser
from venus_meter import VenusMeter

from dbus.mainloop.glib import DBusGMainLoop
import gobject
try:
	import gobject
	from gobject import idle_add
except:
	from gi.repository import GObject as gobject
	from gi.repository.GObject import idle_add#

import dbus
import dbus.service
import inspect
import pprint
import os
import sys
import threading
import time
# Import datetime class from datetime module
from datetime import datetime

class DevState:
	WaitForDevice = 0
	Connect = 1
	Connected = 2

class DevStatistics:
	connection_ok = 0
	connection_ko = 0
	parse_error = 0
	last_connection_errors = 0 # reset every ok read
	last_time = 0
	reconnect = 0

class Mec:
	ip = []
	url = []
	urlstate = []
	user = []
	password = []
	stats = DevStatistics
	intervall = []
	max_retries = 10

global demo
demo = 1
global mec_is_init
mec_is_init = 0
global dev_state
dev_state = DevState.WaitForDevice

def push_statistics() :
	global mec

	mec.set('/stats/connection_ok', Mec.stats.connection_ok)
	mec.set('/stats/connection_error', Mec.stats.connection_ko)
	mec.set('/stats/last_connection_errors', Mec.stats.last_connection_errors)
	mec.set('/stats/parse_error', Mec.stats.parse_error)
	mec.set('/stats/reconnect', Mec.stats.reconnect)


def read_settings() :
	parser = SafeConfigParser()
	parser.read('mec.ini')

	Mec.ip = parser.get('MEC', 'ip')
	Mec.url = parser.get('MEC', 'url')
	Mec.statusurl = parser.get('MEC', 'statusurl')
	Mec.user = parser.get('MEC', 'username')
	Mec.password = parser.get('MEC', 'password')
	Mec.intervall = float(parser.get('MEC', 'intervall'))

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

	time = datetime.now() #data['TIME'] 

	VoltageL1 = 0
	CurrentL1 = 0
	PowerL1 = 0
	ForwardL1 = 0
	ReverseL1 = 0
	VoltageL2 = 0
	CurrentL2 = 0
	PowerL2 = 0
	ForwardL2 = 0
	ReverseL2 = 0
	VoltageL3 = 0
	CurrentL3 = 0
	PowerL3 = 0
	ForwardL3 = 0
	ReverseL3 = 0
	
	
      
      
	#L1
	URLL1 = "http://192.168.3.15/emeter/2"
	meter_rL1 = requests.get(url = URLL1, timeout=1)
	meter_data_L1 = meter_rL1.json()
	

	VoltageL1 = float(meter_data_L1['voltage'])
	CurrentL1 = float(meter_data_L1['current'])
	PowerL1 = float(meter_data_L1['power'])

	ForwardL1 = float(meter_data_L1['total'])
	ReverseL1 = float(meter_data_L1['total_returned'])

	meter_rL1.close

	#L2
	URLL2 = "http://192.168.3.15/emeter/1"
	meter_rL2 = requests.get(url = URLL2, timeout=1)
	meter_data_L2 = meter_rL2.json()


	VoltageL2 = float(meter_data_L2['voltage'])
	CurrentL2 = float(meter_data_L2['current'])
	PowerL2 = float(meter_data_L2['power'])

	ForwardL2 = float(meter_data_L2['total'])
	ReverseL2 = float(meter_data_L2['total_returned'])

	meter_rL2.close

	#L3
	URLL3 = "http://192.168.3.15/emeter/0"
	meter_rL3 = requests.get(url = URLL3, timeout=1)
	meter_data_L3 = meter_rL3.json()

	VoltageL3 = float(meter_data_L3['voltage'])
	CurrentL3 = float(meter_data_L3['current'])
	PowerL3 = float(meter_data_L3['power'])

	ForwardL3 = float(meter_data_L3['total'])
	ReverseL3 = float(meter_data_L3['total_returned'])

	meter_rL3.close

	#total
	Power = float(PowerL1+PowerL2+PowerL3)
	Current = float(CurrentL1+CurrentL2+CurrentL3)
	Forward = float(ForwardL1+ForwardL2+ForwardL3)
	Reverse = float(ReverseL1+ReverseL2+ReverseL3)

	if Mec.stats.last_time == time:
		mec.inc('/stats/repeated_values')
		mec.inc('/stats/last_repeated_values')
		print('got repeated value')
	else:
		Mec.stats.last_time = time
		mec.set('/stats/last_repeated_values', 0)

		mec.set('/Ac/Power', (Power))
		mec.set('/Ac/Current', (Current), 1)
		mec.set('/Ac/Voltage', (VoltageL1))
		mec.set('/Ac/L1/Current', (CurrentL1), 1)
		mec.set('/Ac/L1/Voltage', (VoltageL1))
		mec.set('/Ac/L1/Power', (PowerL1))
		mec.set('/Ac/L2/Current', (CurrentL2), 1)
		mec.set('/Ac/L2/Voltage', (VoltageL2))
		mec.set('/Ac/L2/Power', (PowerL2))
		mec.set('/Ac/L3/Current', (CurrentL3), 1)
		mec.set('/Ac/L3/Voltage', (VoltageL3))
		mec.set('/Ac/L3/Power', (PowerL3))

		mec.set('/Ac/L1/Energy/Forward', (float(ForwardL1)/1000), 2)
		mec.set('/Ac/L1/Energy/Reverse', (float(ReverseL1)/1000), 2)
		mec.set('/Ac/L2/Energy/Forward', (float(ForwardL2)/1000), 2)
		mec.set('/Ac/L2/Energy/Reverse', (float(ReverseL2)/1000), 2)
		mec.set('/Ac/L3/Energy/Forward', (float(ForwardL3)/1000), 2)
		mec.set('/Ac/L3/Energy/Reverse', (float(ReverseL3)/1000), 2)

		mec.set('/Ac/Energy/Forward', (float(ForwardL1+ForwardL2+ForwardL3)/1000), 2)
		mec.set('/Ac/Energy/Reverse', (float(ReverseL1+ReverseL2+ReverseL3)/1000), 2)

		powertotal = Power
		print("++++++++++")
		print("POWER Phase A: " + str(PowerL1) + "W")
		print("POWER Phase B: " + str(PowerL2) + "W")
		print("POWER Phase C: " + str(PowerL3) + "W")
		print("POWER Total: " + str(Power) + "W")
		print("Time: " + str(time) + "ms")
		print("MEC Status: " + str(1911))

		#Mec.stats.parse_error += 1

def mec_data_read_cb( jsonstr ) :
	mec_parse_data ( jsonstr )
	return

def mec_status_read_cb( jsonstr, init) :
	global mec
	if init:
		mec = VenusMeter('mec_tcp_50','tcp:' + Mec.ip, 50,'0',  str(jsonstr['hardware']), str(jsonstr['software']),'0.1')
	return

def mec_read_data() :
	global demo

	err = 0
	if demo == 1:
		try:
			#response = requests.get( Mec.url, verify=False, auth=HTTPBasicAuth(Mec.user, Mec.password), timeout=2)
			# For successful API call, response code will be 200 (OK)
			#if(response.ok):
				#print("code:"+ str(response.status_code))
				#print("******************")
				#print("headers:"+ str(response.headers))
				#print("******************")
				#print("content text:"+ str(response.text))
				#print("******************")
			Mec.stats.connection_ok += 1
			if Mec.stats.last_connection_errors > 0:
				Mec.stats.last_connection_errors = 0
			
			data = mec_read_example("example_mec_data.json")
			mec_data_read_cb( data )
			return 0
		except (requests.exceptions.HTTPError, requests.exceptions.RequestException):
			print('Error reading from ' + Mec.url)
			Mec.stats.connection_ko += 1
			Mec.stats.last_connection_errors += 1
			return 1
	else:
		data = mec_read_example("example_mec_data.json")
		Mec.stats.connection_ok += 1
		mec_data_read_cb(data)
		return 0
	return 0

def mec_read_status(init) :
	global demo

	if demo == 0:
		try:
			response = requests.get( Mec.statusurl ) # no auth an status read
		except requests.exceptions.HTTPError:
			print('Http Error reading from ' + Mec.statusurl)
			return 1
		except requests.exceptions.RequestException:
			print('Request Error reading from ' + Mec.statusurl)
			return 1

		# For successful API call, response code will be 200 (OK)
		if(response.ok):
			#print("code:"+ str(response.status_code))
			#print("******************")
			#print("headers:"+ str(response.headers))
			#print("******************")
			#print("content text:"+ str(response.text))
			#print("******************")
			mec_status_read_cb( jsonstr=response.json(), init=init )
			return 0
		else:
			print("Failure code:"+ str(response.status_code))
			return 1
	else:
		data = mec_read_example("example_mec_status.json")
		mec_status_read_cb(data, init)
		return 0
	return 0

def mec_update_cyclic(run_event) :
	global dev_state, mec

	while run_event.is_set():
		print("Thread: doing")
		if dev_state >= DevState.Connected:
			push_statistics()
			intervall = mec.get('/Mgmt/intervall')
		else:
			intervall = Mec.intervall

		if Mec.stats.last_connection_errors > Mec.max_retries:
			print('Lost connection to mec, reset')
			dev_state = DevState.Connect
			Mec.stats.last_connection_errors = 0
			Mec.stats.reconnect += 1
			mec.set('/Connected', 0)
			mec.invalidate()

		if dev_state == DevState.WaitForDevice:
			if mec_read_status(init=1) == 0:
				dev_state = DevState.Connect
		elif dev_state == DevState.Connect:
			if mec_read_status(init=0) == 0:
				dev_state = DevState.Connected
				mec.validate()
				mec.set('/Connected', 1)
		elif dev_state == DevState.Connected:
			mec_read_data()
		else:
			dev_state = DevState.WaitForDevice

		time.sleep(intervall)
	return

DBusGMainLoop(set_as_default=True)
read_settings()
print("Using " + Mec.url + " user: " + Mec.user)

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
