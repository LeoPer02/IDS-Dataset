# **Docker Containers**

<br/>

## **Table of Contents**

* **[Explaining the Containers](#explaining-the-containers)**
* **[Security Options](#security-options)**
  * **[Capabilities](#capabilities)**
  * **[Apparmor](#apparmor)** 
* **[Troubleshooting](#troubleshooting)**
  * **[Unable to remove network "has active endpoints"](#unable-to-remove-network-has-active-endpoints)**
<br/>

## **Explaining the Containers**

<br/>

`docker-compose.yml` is the main file, responsible for building both containers, wordpress and db.

The db container is a simple mysql container which will host the database service used by wordpress. 
This way we can separate responsibilities which in addition to making it more modular and simple, allows us to more easily pin point problems rising from building the containers.

As for the wordpress container we build the Dockerfile, which uses the official wordpress image but adds some extra commands:

* `COPY init.sh /usr/local/bin/dockerInit`: Copy the init.sh file and add it to the bin folder, to be accessible from the PATH.
* `RUN chmod +x /usr/local/bin/dockerInit`: Give that file executable permission.
* `RUN dockerInit`: Execute the file

The init.sh file consists of the following:

``` Bash
#!/usr/bin/env bash
apt-get update
apt-get install sudo -y
echo "www-data ALL=(ALL) NOPASSWD: /usr/bin/find" | cat >> /etc/sudoers
chown -R www-data:www-data /var/www/html/wp-content/

```

This script, will update the system, install the `sudo` command and give the the www-data user the ability to use `sudo find` command (Used for privilege escalation).
It will also try to change the ownership of the plugins folder and contents.

<br/>

## **Security Options**

Two important options that were utilized:
``` yml
cap_add:
    - SYS_ADMIN
```
and
``` yml
security_opt:
    - apparmor:unconfined
```

This settings are the core reason why the Docker Escape attack is possible. More information in the actual payload used in the DockerEscape Folder's README.

<br/>

### **Capabilities**

[Capabilities](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux_atomic_host/7/html/container_security_guide/linux_capabilities_and_seccomp) can be seen as a way to break up privileges to processes running as root into smaller groups. That way we can more easily control the permissions of the processes.

Docker allows the addition of capabilities to it's containers with the command `--cap-add` and using this, a developer can control the permissions this container has within the system.

The problem is when the container has too much permissions. In that situation, it might be possible, within a container created for isolation, for an attacker to break that isolation.
In our case, the capability `SYS_ADMIN` was added. This capability, in addition to many other commands, allows the use of `mount`. This command is the one which will allow us to break isolation.

<br/>

### **Apparmor**

Linux [Apparmor](https://ubuntu.com/server/docs/security-apparmor), in a nutshell, is a security module that confines programs to a set of files and capabilities.

We can use this security module to restrict the capabilities a process has access to, this way we have a more concise control over the permissions of the process running in our system.

When creating a docker container this feature is used by default, however, as mentioned above, it restricts the capabilities one has access to, being `SYS_ADMIN` one of them.
This renders the `cap_add:` options we just used completely useless, so to fix that, we add `security_opt: apparmor=unconfined` which disables the default docker apparmor profile, allowing the mount capability to the container.

<br/>

## **Troubleshooting**

<br/>

### **_Unable to remove network "has active endpoints":_**
A possible workaround for this problem is the execution of 
``` Bash
sudo aa-remove
```






