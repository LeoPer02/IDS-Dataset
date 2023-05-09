import sys, re, os


if(len(sys.argv) != 3):
	sys.exit('Wrong number of arguments\nUsage: python3 '+ sys.argv[0] +' module_file audit_file')

module_list = []
audit_list = []

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
		syscall=syscall[:-2]
	#print(pid, syscall)
	module_line = module.readline()
	if syscall == '4294967295':
		syscall = 'UNKNOWN'
	module_list = [(pid, syscall)]

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
		if syscall == '4294967295':
			syscall = 'UNKNOWN'
		module_list.append((pid, syscall))
		module_line = module.readline()

p = os.popen('cat ' + sys.argv[2] + ' | grep type=SYSCALL').read().split('\n')
p = p[:-1]
for i in p:
	sys = re.compile(r'^syscall=[0-9]+')
	p = re.compile(r'^pid=[0-9]+')
	syscall = ''
	pid = ''
	entry = i.split(' ')
	for e in entry:
		if sys.search(e):
			syscall = e
		elif p.search(e):
			pid = e
		if pid != '' and syscall != '':
			break
	if pid != '' and syscall != '':
		audit_list.append((pid, syscall))
	pid = ''
	syscall = ''

m = len(module_list)
a = len(audit_list)

print('{0: <53} {1: <53}\n'.format('Module', 'Audit'))
for i in range(0, max(a, m)):
	if i < a and i < m:
		print('pid={0: <{fill}} syscall={1: <{fill}} {2: <{fill}} {3: <{fill}}'.format(module_list[i][0], module_list[i][1], audit_list[i][0], audit_list[i][1], fill = 20))
	elif i < a and i >= m:
		print('pid={0: <{fill}} syscall={0: <{fill}} {1: <{fill}} {2: <{fill}}'.format('?', audit_list[i][0], audit_list[i][1], fill = 20))
	else:
		print('pid={0: <{fill}} syscall={1: <{fill}} pid={2: <{fill}} syscall={2: <{fill}}'.format(module_list[i][0], module_list[i][1], '?', fill = 20))

