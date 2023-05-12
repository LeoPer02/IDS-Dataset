# importing all the functions 
# from http.server module
from http.server import *
import sys
import os
from urllib.parse import urlparse
import subprocess
import signal
import argparse

# This server was design to be used personally and does not count with security checks
# You could easily crash the server, however it developed only to automate some processes
print('''
Make sure you are root (not sudo) and that you're in the same directory as the server
''')

epilog ='''
This server is responsible for starting/stopping the logging of syscalls from the implemented attacks
You can also define your own module to be executed instead of ours /ebriareospf/briareospf-master/syscall_exit_tracer.py
In order to run this script make sure in the working directory there is a folder 'data' with write permissions and that your module
writes to the file ./data/sys_exit.txt

If your using our module, just place this file inside the module working directory and the data folder will alreaby be there'''

parser = argparse.ArgumentParser(epilog=epilog)

parser.add_argument("-s", "--module-start", action="store", help='Allows you to define the script that will start your module. Keep in mind that the execution will be made in the following way bash (your_module) -p pid1,pid2,...,pidn. If not defined, our module will be used')

parser.add_argument("-e", "--module-end", action="store",help='''Allows you to define the script that will stop your module. You do not need necessarily to define this flag (In case your module_start stops by itself), althought it is recommended since if you chain attacks it would be better to make sure that the previous instance of the module was terminated''')

parser.add_argument("-p", "--port", action="store", help='''Defines the port in which the server runs on''')

parser.add_argument("-d", "--dataset", action="store", help="Defines the folder where to store the logging of the attacks, by default is /")

arguments = parser.parse_args()

# find commands may take a while
print('Setting up server, please wait a bit before proceeding')

port = 5555
module_start = ''
module_end = ''
module_location = os.popen('find / -name syscall_exit_tracer.py 2>/dev/null').read()[:-1] # Remove \n


# Find commands returned
print('You can now proceed with the attacks')
script_dir = os.popen('pwd').read()[:-1] # Remove \n
dataset = '/'

if script_dir[len(script_dir)-1] != '/':
	script_dir += '/'

if arguments.dataset:
	dataset = arguments.dataset
	if dataset[len(dataset) -1] != '/':
		dataset = dataset + '/'

# Get server port
if arguments.port:
	port = int(arguments.port)

# Get module_start
if arguments.module_start:
	module_start = arguments.module_start
	# Only get module_end if module_start was defined
	if arguments.module_end:
		module_end = arguments.module_end
        

print('[DEBBUBG] Script_Dir: {s}	module_location: {m}	dataset: {d}'.format(s=script_dir, m=module_location, d=dataset))
# Checking if necessary files exist
# If they dont, create them
for name in ['LXD', 'FTP', 'Docker', 'SSH', 'FileInclusion', 'ReverseShell', 'Meterpreter']:
    if not os.path.exists('./data/' + name + 'count.txt'):
        f = open('./data/' + name + 'count.txt', 'w')
        f.write('0')
        f.close()

if not os.path.exists('./data/sys_exit.txt'):
        f = open('./data/' + name + 'count.txt', 'x')
        f.close()

class Auditing(BaseHTTPRequestHandler):

    # creating a function for Get Request
	def do_GET(self):
		if '/start' in self.path:
			query = urlparse(self.path).query
			query_components = dict(qc.split("=") for qc in query.split("&"))
			exploit = query_components["exploit"]
			print(query_components)

			# Empty the sys_exit file
			p = subprocess.Popen('echo "" | tr -d \'\n\' | cat > ./data/sys_exit.txt', shell=True)
			exploit_count = open(script_dir + '/data/' + exploit + 'count.txt', 'r')
			count = int(exploit_count.read()) + 1
			exploit_count.close()
            
            		# For each of the attacks get the pids to be traced
			if exploit == 'LXD':
				pid = os.popen('''ps aux | grep www-data | grep "sh -i" | awk '{print $2 }' ''').read().split('\n')
			elif exploit == 'Docker':
				pid = os.popen('''get_docker_pid=$(docker ps | grep docker_wordpress | awk '{ print $1 }') && docker top $get_docker_pid | awk '{print $2 }' | tail +2''').read().split('\n')
			elif exploit == 'SSH':
				pid = os.popen('''ps aux | grep sshd | awk '{ print $2 }' ''').read().split('\n')
			elif exploit == 'FTP':
				pid = os.popen(''' ps aux | grep ftp | awk '{ print $2 }' ''').read().split('\n')
			elif exploit == 'FileInclusion' or exploit == 'ReverseShell':
				pid = os.popen('''ps aux | grep apache2 | awk '{ print $2 }' ''').read().split('\n')
			elif exploit == 'Meterpreter':
				pid = os.popen('''ps aux | grep shell.bin | awk '{print $2 }' ''').read().split('\n')
			else:
				return
		    
		    # No process was found
			if len(pid) <= 1:
				return

			pid = pid[:-1] # Remove last element cause its an empty string	
			args = pid[0]
			for i in range(1, len(pid)):
				args += ',' + pid[i]

			# Execute module with the pids collected
			if module_start != '':
				subprocess.Popen('bash ' + module_start + ' -p ' + args, shell=True)
			else:
				subprocess.Popen('python3 ' + module_location +' -p ' + args, shell=True)
		            
			# Clear audit file and implement rules to filter output
			p2 = subprocess.Popen('bash ./search_pid.sh {pid}'.format(pid=args), shell = True)
		    
		elif '/stop' in self.path:
			query = urlparse(self.path).query
            
			# Kill module
			if module_start != '' and module_end != '':
				subprocess.Popen('bash ' + module_end, shell=True)
			else:
				os.popen('''pkill -9 -f syscall_exit_tracer.py ''')
            
            
			query_components = dict(qc.split("=") for qc in query.split("&"))
			exploit = query_components["exploit"]
			
			# Get the current value of tests
			exploit_count = open(script_dir + '/data/' + exploit + 'count.txt', 'r')
			count = int(exploit_count.read())
			exploit_count.close()
			
			# One digit number will be of the form 01/02/03/04.../09 so that when the File System orders the files it does not put 11 before 2
			# Since we won't get to the 100's there's no need for more than one 0
			if count <= 9 and count >= 0:
				str_count = '0' + str(count)
			else:
				str_count = str(count)
				
			# Copy the contents of sys_exit.txt to the dataset
			p = subprocess.Popen('cp ./data/sys_exit.txt ' + dataset + exploit + str_count + '.txt', shell=True)

			# Stop audit
			p2 = subprocess.Popen('service auditd stop', shell = True)
            
			# Increase the counter
			exploit_count = open(script_dir + '/data/' + exploit + 'count.txt', 'w')
			exploit_count.write(str(count+1))
			exploit_count.close()
            
			# Create the audit result file
			audit_result = open(dataset + 'audit_' + exploit + str_count + '.txt', 'w')
			audit_result.close()
            
			# Write the result from the search to the result file
			p = subprocess.Popen('ausearch -ts recent -te now -m SYSCALL > ' + dataset + 'audit_' + exploit + str_count + '.txt', shell=True)
			

		# Success Response --> 200
		self.send_response(200)
		  
		self.end_headers()

  
  
# this is the object which take port 
# number and the server-name
# for running the server
port = HTTPServer(('', port), Auditing)
  
# this is used for running our 
# server as long as we wish
# i.e. forever
port.serve_forever()
