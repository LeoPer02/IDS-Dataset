import create_conf
import os
import sys
import requests
import errno
import socket

from exploit_LXD import exploit_LXD
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
	
	match int(general_info['exploit']):
		case 1:
			exploit_LXD()
		case default:
			sys.exit('Something went wrong :(\nExploit chosen is not valid')
	
if __name__ == '__main__':
	main()
