from configparser import ConfigParser
import ipaddress
import os

def gen_config():
	#Get the configparser object
	config_object = ConfigParser()
	print('[?] Attacker Ip: (Ip address of the attacking machine)')
	f = True
	a_ip = ""
	## ATTACKER IP
	while f:
		a_ip = input()
		try:
			ip_object = ipaddress.ip_address(a_ip)
			f = False
		except ValueError:
			print('Not a valid ipaddress, reenter a valid one')
	
	## ATTACKER PORT
	print('[?] Attacker port: (Port used for the reverse shell)')
	f = True
	while f:
		a_port = int(input())
		if a_port < 1024 or a_port > 65536:
			print('Please enter a port between 1024 and 65536, that is not in use')
		else:
			f = False
	
	
	## VICTIM IP
	f = True
	v_ip = ""
	print('[?] Victim ip: (Ip of the website you want to attack)')
	while f:
		v_ip = input()
		try:
			ip_object = ipaddress.ip_address(v_ip)
			f = False
		except ValueError:
			print('Not a valid ipaddress, reenter a valid one')
	
	## VICTIM PORT
	print('[?] Victim port: (Port used for accesing the webserver, default: 80)')
	f = True
	while f:
		v_port = int(input())
		if v_port < 0 or v_port > 65536:
			print('Please enter a port between 0 and 65536')
		else:
			f = False
	
	
	
	 
	config_object["ATTACKERINFO"] = {
	    "ip": a_ip,
	    "port": a_port
	}

	config_object["VICTIMINFO"] = {
	    "ip": v_ip,
	    "port": v_port
	}

	if os.path.exists('./config.ini'):
		os.remove('./config.ini')
	#Write the above sections to config.ini file
	with open('config.ini', 'w') as conf:
	    config_object.write(conf)
