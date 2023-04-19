from configparser import ConfigParser
import ipaddress
import os
import random
import socket

def gen_config(change):
	config_object = ConfigParser()
	# If the use wants to change the info query him
	# Otherwise just randomize the port and keep the other information
	if change:
		#Get the configparser object
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
		a_port = random.randint(1024, 65536)
		# Making sure the random port is not in use
		while check_port(a_ip, a_port):
			a_port = random.randint(1024, 65536)
		
		
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
	
	else:
		config_object.read("config.ini")
		attacker_info = config_object["ATTACKERINFO"]
		victim_info = config_object["VICTIMINFO"]
		a_ip = attacker_info['ip']
		a_port = random.randint(1024, 65536)
		# Making sure the random port is not in use
		while check_port(a_ip, a_port):
			a_port = random.randint(1024, 65536)
		v_ip = victim_info['ip']
		v_port = victim_info['port']
	
	 
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

def check_port(ip, port):

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		s.bind((ip, port))
	except socket.error as e:
		if e.errno == errno.EADDRINUSE:
			return True
		else:
			# something else raised the socket.error exception
			print(e)
			sys.exit()
	return False

	s.close()
