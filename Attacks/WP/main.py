import create_conf
import os
import sys
import requests
import errno
import socket
import argparse

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


from initial_access import wp_file_manager
from datetime import datetime
from configparser import ConfigParser 	

epilog ="This script was created in order to automate the exploitation and logging of the syscalls produced by the attacks"

parser = argparse.ArgumentParser(epilog=epilog)
parser.add_argument("-c", "--config", action="store_true", help='''	Allows you to only configure the exploit and not run it. Althougth if combined with -r will prompt the configuration before running the attacks''')

parser.add_argument("-r", "--repeat", action="store",
		    help='''	This options allows you to repeat the same exploit multiple times, the configuration used will be the one
		    found inside config.ini on the working directory, if not found, it will request you to fill it out. You can also configure them before the execution with the -c or --config flag\n''')

arguments = parser.parse_args()

	
if arguments.config:
	create_conf.gen_config(True)
	if not arguments.repeat:
		sys.exit()


if arguments.repeat:
	if not os.path.exists('./config.ini'):
		print(color.YELLOW + '[-]'+ color.END+ ' Configuration file not found')
		create_conf.gen_config(True)
	else:
		# Just randomize the port but keep the other changes
		# This way we avoid the TIME_WAIT of each port we use
		create_conf.gen_config(False)

if os.geteuid() != 0:
		exit(color.RED + "[-]" + color.END + " You need root privileges to run this script")	  	  
	
def main():

	flag = False

	config_object = ConfigParser()

	if arguments.repeat == None:
		print(color.GREEN + '[+]' + color.END + ' Executing exploit...')
		print(color.YELLOW + '[?] Do you wish to continue?' + color.END + color.BOLD + ' (y|n)' + color.END )
		ans = input()

	# Don't ask to configure if the script is in repeat mode
	if arguments.repeat == None:
		if os.path.exists('./config.ini'):			  
			print(color.GREEN + '[+]' + color.END + ' Config file detected')
			print(color.YELLOW + '[?] Do you wish to modify the configuration file?' + color.END + color.BOLD + ' (y|n)' + color.END)
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
	l = [1,2,3,4,5,6,7]
	if int(general_info['exploit']) in l:
		wp_file_manager(victim_info, attacker_info, general_info, general_info['exploit'], arguments)
	else:
		sys.exit(color.RED + "Something went wrong, invalid exploit" + color.END)
	
if __name__ == '__main__':
	main()
