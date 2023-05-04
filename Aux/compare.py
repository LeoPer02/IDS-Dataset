import re, sys, os

##
# If you are able to change from name of the syscall to the actual number
# a possible and better option, would be to try to find the tuple within
# the other list, that way we can know if all the calls were registered
#


if os.geteuid() != 0:
	print('You need to run this script as root')
	sys.exit()

if(len(sys.argv) != 3):
	sys.exit('Wrong number of arguments\nUsage: python3 '+ sys.argv[0] +' module_file audit_file')

module_list = []
all_pids = set()

with open(sys.argv[1], 'r') as module:
	module_line = module.readline()
	lines = module_line.split(' ')
	lines[:] = (value for value in lines if value != '' and value != '\n')
	pid = lines[0]	
	syscall = lines[len(lines)-1]
	#print(syscall)
	if syscall[0] == 'b':
		syscall=syscall[2:-1]
	else:
		syscall=syscall[:-3]
	#print(pid, syscall)
	module_line = module.readline()
	module_list = [(pid, syscall)]

	all_pids.add(pid)
	while module_line:
		lines = module_line.split(' ')
		lines[:] = (value for value in lines if value != '' and value != '\n')
		pid = lines[0]	
		syscall = lines[len(lines)-1]
		if syscall[0] == 'b':
			syscall=syscall[2:-1]
		else:
			syscall=syscall[0:-3]
		#print(pid, syscall)
		module_list.append((pid, syscall))
		module_line = module.readline()
		all_pids.add(pid)

audit_list = []
for i in all_pids:
	cmd = '''cat ''' + sys.argv[2] + ''' | grep pid=''' + i + ''' | awk '{ print $4 }' | cut -d '=' -f2'''
	p = os.popen('''cat ''' + sys.argv[2] + ''' | grep pid=''' +i +''' | awk '{ print $4 }' | cut -d '=' -f2''').read().split('\n')
	p[:] = (value for value in p if value.isdigit())
	for v in p:
		audit_list.append((i, v))

f = open('differences.txt', 'w')
f.write('Module Entrys: {0: <{fill}} Audit Entrys: {1: <{fill}}\n'.format(len(module_list), len(audit_list), fill=16))
# Both have elements
for i in range(0, max(len(module_list), len(audit_list))):

	if len(module_list) != 0 and len(audit_list) != 0:
		module_pid, module_sys = module_list[0]
		i = 0
		audit_pid = -1
		audit_syscall = '?'
		
		for i in range(0, len(audit_list)):
			if audit_list[i][0] == module_pid:
				audit_pid, audit_sys = audit_list[i]
				break
		if audit_pid == -1:
			f.write('Pid: {0: <{fill}} Module: {1: <{fill}} Audit: NOT_FILTERED\n'.format(module_pid, module_sys, fill=16))
		else:
			f.write('Pid: {0: <{fill}} Module: {1: <{fill}} Audit: {audit_sys}\n'.format(module_pid, module_sys, audit_sys=audit_sys, fill=16))
		del module_list[0]
		del audit_list[i]

	elif len(module_list) != 0 and len(audit_list) == 0:
		module_pid, module_sys = module_list[0]
		f.write('Pid: {0: <{fill}} Module: {1: <{fill}} Audit: NOT_FILTERED\n'.format(module_pid, module_sys, fill=16))
		del module_list[0]
		
	elif len(module_list) == 0 and len(audit_list) != 0:
		audit_pid, audit_sys = audit_list[0]
		f.write('Pid: {0: <{fill}} Module: {1: <{fill}} Audit: {audit_sys}\n'.format(audit_pid,'NOT_FILTERED', audit_sys=audit_sys, fill=16))
		del audit_list[0]
		
	else:
		break
f.close()
