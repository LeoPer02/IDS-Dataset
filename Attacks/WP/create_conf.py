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
		
		## VICTIM PROTOCOL
		v_secure = True
		print('[?] Does the victim use HTTPS? (y|n)')
		ans = input();
		if ans == "n" or ans == "N":
			v_secure = False
			
		 
		## VICTIM PORT
		print('[?] Victim port: (Port used for accesing the webserver, default: 80)')
		f = True
		while f:
			v_port = int(input())
			if v_port < 0 or v_port > 65536:
				print('Please enter a port between 0 and 65536')
			else:
				f = False
	
		## EXPLOIT TO USE
		print('[?] Which of the following exploit do you wish to use?')
		print('''
		[1] LXD container privilege escalation exploit.
		[2] Meterpreter shell.
		[3] Docker Escape
		[4] SSH Bruteforce
		... (More to be implemented)
		''') 
		exp = '0'
		# Represents the different exploit available
		l = ['1', '2', '3', '4']
		while exp not in l:
			exp = input()
		v_ssh_user = ""
		v_ssh_port = 22
		g_default_ssh = True
		g_ssh = False
		g_wordlist = "/usr/share/wordlists/rockyou.txt"
		if exp == '4':
			n=input('[?] Do you know the username on the ssh service? (y|n) ')
			if n == 'Y' or n == 'y':
				v_ssh_user=input('[?] SSH user: ')
				g_ssh = True
			
			n=input('''[?] Which password wordlist do you want to use to bruteforce?\n    Press Enter to use default, /usr/share/wordlists/rockyou.txt\n    Keep in mind, the file will be used to both username (if not provided) and password\n''')
			if n != '':
				while not os.path.exists(n):
					print('[-] That file does not exist, please insert a new one or Enter to use default /usr/share/wordlists/rockyou.txt')
					n = input()
					if n == '':
						break
				if os.path.exists(n):
					g_wordlist = n
			n = input('[?] Is the ssh port the default one, 22? (y|n)\n')
			if n != 'Y' and n != 'y':
				f = True
				while f:
					v_ssh_port = int(input())
					if v_ssh_port <= 0 or v_ssh_port >= 65536:
						print('Please enter a port between 0 and 65536')
					else:
						f = False
						g_default_ssh = False
						
		
		print('''
		########################################################################
		#								       #
		#		SYSCALL LOGGING SERVER CONFIGURATION!                  #		  
		#								       #
		#		During development a server responsible                #
		#		for starting and stopping the logging                  #
		#		of syscalls was implemented.			       #
		#		 						       #
		#		This server was programmed to received GET             #
		#		requests with the form:                                #
		#		{ip}:{port}/start?exploit={exploit}&pid={pid}          #
		#		{ip}:{port}/stop?exploit={exploit}&pid={pid}	       #
		#								       #
		#		Therefore, this script was developed in order to       #
		# 		communicate with such server.                          #
		#                                                                      #
		#		Do you wish to activate this feature and configure     #
		#		the ip and port of the server? (y|n)                   #
		#                                                                      #
		########################################################################
		''')
		n = input()
		g_active = False
		g_host = ""
		g_port = ""
		g_exp = exp
		if n == 'Y' or n == 'y':
			g_active = True
			print('[?] What\'s the ip/host of the server?')
			g_host = input()
			print('[?] What\' the port of the server?')
			g_port = input()
			print('[*] Quick reminder:')
			print('In order to start the logging we will access {ip}:{port}/start?exploit=exploit_name&pid=rev_shell_pid'.format(ip=g_host, port=g_port))
			print('And to stop the logging we will access {ip}:{port}/stop?exploit=exploit_name&pid=rev_shell_pid'.format(ip=g_host, port=g_port))
	else:
		config_object.read("config.ini")
		attacker_info = config_object["ATTACKERINFO"]
		victim_info = config_object["VICTIMINFO"]
		general_info = config_object["GENERALINFO"]
		a_ip = attacker_info['ip']
		a_port = random.randint(1024, 65536)
		# Making sure the random port is not in use
		while check_port(a_ip, a_port):
			a_port = random.randint(1024, 65536)
		v_ip = victim_info['ip']
		v_port = victim_info['port']
		v_secure = victim_info['secure']
		v_ssh_user = victim_info['ssh_user']
		v_ssh_port = victim_info['ssh_port']
		exp = general_info['exploit']
		g_active = general_info['active']
		g_host = general_info['host']
		if general_info['port'] != '':
			g_port = int(general_info['port'])
		else:
			g_port = 0
		g_exp = int(general_info['exploit'])
		g_ssh = general_info['has_ssh_user']
		g_wordlist = general_info['wordlist']
		g_default_ssh = general_info['default_ssh']
		
	
	 
	config_object["ATTACKERINFO"] = {
	    "ip": a_ip,
	    "port": a_port
	}

	config_object["VICTIMINFO"] = {
	    "ip": v_ip,
	    "port": v_port,
	    "secure": v_secure,
	    "ssh_user": v_ssh_user,
	    "ssh_port": v_ssh_port
	}
	config_object["GENERALINFO"] = {
	    "exploit": g_exp,
	    "host": g_host,
	    "port": g_port,
	    "active": g_active,
	    "has_ssh_user": g_ssh,
	    "wordlist": g_wordlist,
	    "default_ssh": g_default_ssh
	 
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
