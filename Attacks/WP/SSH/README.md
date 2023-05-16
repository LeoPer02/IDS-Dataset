# **SSH Bruteforce**

## **Explaining the attack**
---

## **Table of Contents**

* **[Explaining the Attack](#explaining-the-attack)**
* **[How to Use](#how-to-use)**
  * **[Repeat Mode](#for-repeat-mode)** 

<br/>

## **Explaining the Attack**

Bruteforce attacks are usually only used by amateurs bad actors or experienced ones when running out of options, this is due to the high footprint that these attacks cause. However, they are still widely used, and so we considered them an important type of attack to study.

We can easily find tools that help on this types of attacks, however, the one we went with was [Hydra](https://www.kali.org/tools/hydra/) since not only is one of the most popular but also it already comes with the base Kali OS.

## **How to use**
---
<br/>

This exploit can be ran in **repeat** mode.

From the **/path/to/project/IDS-Dataset/Attacks/WP** folder,

<br/>

### **Configurations:**

If you built the victim machine from scratch using our script you can use the following settings for the SSH Brute force attack:

``` Shell
sudo python3 main.py -c # To start the configuration process

Attacker ip: # Check the ip address with ' ifconfig '
Victim ip: # Check the ip address with ' ifconfig '
Exploit: 5
Has username for ssh service: y # Recommended to speed the process
Username: {name_of_your_user}
Which wordlist: /IDS-Dataset/Attacks/WP/t.txt # See Note below
SSH default port: y
Activate auditing: y # Make sure the server is on, check Aux README for information
```

> **📝 _NOTE:_** In the configuration above we mention the username, this should be the username you used to create the VM, if you're unsure open a shell and use `whoami`. After that we mention the use of the `/IDS-Dataset/Attacks/WP/t.txt` file. This file contains a bunch of letters 'a' and the last value should be replaced by the password you used for the mentioned username. This is because bruteforce takes a while, and using the `t.txt` file you will be able to gather enough system calls to define a bruteforce attack without wasting to much time. 

<br/>


### **For Repeat mode:**
``` Shell
sudo python3 main.py -r {number_times} # Don't forget to configure the config.ini on the 1st attack
```

