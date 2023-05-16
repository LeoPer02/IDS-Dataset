# **LXD Root File System mount**

## **Table of Contents**

* **[Explaining the Attack](#explaining-the-attack)**
* **[How to Use](#how-to-use)**
  * **[Configurations](#configurations)**
  * **[Interactive Mode](#for-interactive-mode)**
  * **[Repeat Mode](#for-repeat-mode)** 
* **[Troubleshooting](#troubleshooting)**
  * **[Error: Get http://unix.socket/1.0: dial unix /var/lib/lxd/unix.socket: connect: permission denied:](#error-get-httpunixsocket10-dial-unix-varliblxdunixsocket-connect-permission-denied)**
  * **[Using sequential repeat mode LXD attacks throws error on the lxc container:](using-sequential-repeat-mode-LXD-attacks-throws-error-on-the-lxc-container)**  
<br/>


## **Explaining the attack**

> **📝 _NOTE:_** As mentioned on the project explanation, this attack uses the Wp File Manager vulnerability as an entry point to the victim system.



Here we will take advantage of a misconfiguration on the www-data user (low-privileged), where it has the ability to manage LXC Containers.

The way this attacks is performed is as follows:
- Get a compiled image to use on the LXC container. Done in the attacker machine using the commands ```wget https://raw.githubusercontent.com/saghul/lxd-alpine-builder/master/build-alpine && bash build-alpine```.
- This compile image is then transferred to the victim system through the reverse shell obtained with the Wp File Manager.
- Once on the victim machine, we run the [exploit](https://www.exploit-db.com/exploits/46978) which can be summarize as:
    * Importing the compile image into the LXD container created (privesc)
    * Starting the container as [privileged](https://linuxcontainers.org/lxc/security/#privileged-containers)
    * Mount the root of the file system of the host onto the container
    * Opening a shell into the container
- Doing all this will grants the attacker root permissions inside a container whose file system is a carbon copy of the victim's one.

<br/>

## **How to use**

---
<br/>

This exploit can be ran in **interactive** and **repeat** mode.

From the **/path/to/project/IDS-Dataset/Attacks/WP** folder,

<br/>

### **Configurations:**

If you built the victim machine from scratch using our script you can use the following settings for the LXD attack:

``` Shell
sudo python3 main.py -c # To start the configuration process

Attacker ip: # Check the ip address with ' ifconfig '
Victim ip: # Check the ip address with ' ifconfig '
Exploit: 1
HTTPS: n
Victim Port: 80
Activate auditing: y # Make sure the server is on, check Aux README for information
```
<br/>

### **For interactive mode:**
``` Shell
sudo python3 main.py # Don't forget to configure the config.ini on the 1st attack
```

This will start the attack against the targeted machine.
> **📝 _TIP:_** If the attack seems to be frozen, generally after the message `Creating privesc` try pressing Enter a couple of times and that should flush the buffer if it doesn't on it's own.


<br/>

### **For Repeat mode:**
``` Shell
sudo python3 main.py -r {number_times}
```

Keep in mind that this command will start and attack based on the information stored in config.ini, if one exists, otherwise before the attack will prompt you to the information required.

If you want to run the attack in **repeat mode but firstly change the config.**
``` Shell
sudo python3 main.py -c -r {number_times}
``` 

<br/>

## **Troubleshooting**
---

### **Error: Get `http://unix.socket/1.0`: dial unix /var/lib/lxd/unix.socket: connect: permission denied:** 
This error might happen after each boot, this is caused by a lack of permissions from the www-data user to use the lxd/unix.socket.

During development we added the user to the lxd group to try to fix the issue but with no luck, however the work around we found was:
``` Shell
chmod 0666 /var/lib/lxd/unix.socket
```
This should fix your error, just keep in mind that in the next boot you might need to use this workaround again. 

<br/>

### **Using sequential repeat mode LXD attacks throws error on the lxc container:**
The error you're getting most likely is due to the victim machine not having enough time to cleanup.

After the attack is done we erase the created image and container to simulate the attacker trying to hide its tracks, however this process takes it's time.

The repeat mode is constructed in a way so that we only cleanup the tracks once all the attacks are over. So if you're using repeat mode attacks back to back you might get into the situation where you're trying to create the container but it still exists (but it's being deleted, which will cause an error).

For that, instead of:

 ``` Shell
 sudo python3 main.py -r 5 && sudo python3 main.py -r 10
 ``` 
 use: 
 ```
 sudo python3 main.py -r 15
 ```

 Which has the exact same effect but avoids the error mentioned above.
