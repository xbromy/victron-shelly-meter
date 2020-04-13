#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#vi: set autoindent noexpandtab tabstop=4 shiftwidth=4

from dbus.mainloop.glib import DBusGMainLoop
import gobject
from gobject import idle_add
import dbus
import dbus.service
import inspect
import pprint
import os
import sys


# velib path
sys.path.insert(1, os.path.join(os.path.dirname(__file__), './velib_python'))
from vedbus import VeDbusService

#def main(argv):
#	global dbusObjects
class VenusMeter :
	def __init__(self, dev, connection, instance, serial, product, firmwarev, pversion) :
		#VERSION = '0.1'

		print(__file__ + " starting up")
	#	instance = 50 + 0

		# Have a mainloop, so we can send/receive asynchronous calls to and from dbus
		#DBusGMainLoop(set_as_default=True)

		#Put ourselves on to the dbus
		dbusservice = VeDbusService('com.victronenergy.grid.' + dev)

		# Most simple and short way to add an object with an initial value of 5.
		#	dbusservice.add_path('/Ac/Power', value=1000, description='Total power', writeable=False)
		#	dbusservice.add_path('/DeviceType', value=1000, description='Total power', writeable=False)
		# Add objects required by ve-api
		dbusservice.add_path('/Mgmt/ProcessName', __file__)
		dbusservice.add_path('/Mgmt/ProcessVersion', pversion)
		dbusservice.add_path('/Mgmt/Connection', connection) # todo
		dbusservice.add_path('/DeviceInstance', instance)
		dbusservice.add_path('/ProductId', 0xFFFF) # 0xB012 ?
		dbusservice.add_path('/ProductName', product)
		#dbusservice.add_path('/CustomName', "PLC Mec meter")
		dbusservice.add_path('/FirmwareVersion', firmwarev)
		dbusservice.add_path('/Serial', serial)
		dbusservice.add_path('/Connected', 1)
		dbusservice.add_path('/ErrorCode', '(0) No Error')

		_kwh = lambda p, v: (str(v) + 'KWh')
		_a = lambda p, v: (str(v) + 'A')
		_w = lambda p, v: (str(v) + 'W')
		_v = lambda p, v: (str(v) + 'V')

		if 0:
			dbusservice.add_path('/Ac/Energy/Forward', 3003, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/Energy/Reverse', 30003, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L1/Current', -2, gettextcallback=_a)
			dbusservice.add_path('/Ac/L1/Energy/Forward', 1000, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L1/Energy/Reverse', 10000, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L1/Power', -2*230, gettextcallback=_w)
			dbusservice.add_path('/Ac/L1/Voltage', 230, gettextcallback=_v)
			dbusservice.add_path('/Ac/L2/Current', 1, gettextcallback=_a)
			dbusservice.add_path('/Ac/L2/Energy/Forward', 1001, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L2/Energy/Reverse', 10001, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L2/Power', 1*230, gettextcallback=_w)
			dbusservice.add_path('/Ac/L2/Voltage', 230, gettextcallback=_v)
			dbusservice.add_path('/Ac/L3/Current', 0.5, gettextcallback=_a)
			dbusservice.add_path('/Ac/L3/Energy/Forward', 1002, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L3/Energy/Reverse', 10002, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L3/Power', 0.5*230, gettextcallback=_w)
			dbusservice.add_path('/Ac/L3/Voltage', 230, gettextcallback=_v)
			dbusservice.add_path('/Ac/Power', 111, gettextcallback=_w)
			dbusservice.add_path('/Ac/Current', (1+2+0.5), gettextcallback=_a)
			dbusservice.add_path('/Ac/Voltage', 230, gettextcallback=_v)
		else:
			dbusservice.add_path('/Ac/Energy/Forward', None, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/Energy/Reverse', None, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L1/Current', None, gettextcallback=_a)
			dbusservice.add_path('/Ac/L1/Energy/Forward', None, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L1/Energy/Reverse', None, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L1/Power', None, gettextcallback=_w)
			dbusservice.add_path('/Ac/L1/Voltage', None, gettextcallback=_v)
			dbusservice.add_path('/Ac/L2/Current', None, gettextcallback=_a)
			dbusservice.add_path('/Ac/L2/Energy/Forward', None, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L2/Energy/Reverse', None, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L2/Power', None, gettextcallback=_w)
			dbusservice.add_path('/Ac/L2/Voltage', None, gettextcallback=_v)
			dbusservice.add_path('/Ac/L3/Current', None, gettextcallback=_a)
			dbusservice.add_path('/Ac/L3/Energy/Forward', None, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L3/Energy/Reverse', None, gettextcallback=_kwh)
			dbusservice.add_path('/Ac/L3/Power', None, gettextcallback=_w)
			dbusservice.add_path('/Ac/L3/Voltage', None, gettextcallback=_v)
			dbusservice.add_path('/Ac/Power', None, gettextcallback=_w)
			dbusservice.add_path('/Ac/Current', None, gettextcallback=_a)
			dbusservice.add_path('/Ac/Voltage', None, gettextcallback=_v)

#	mainloop = gobject.MainLoop()
#	mainloop.run()

#main("")
