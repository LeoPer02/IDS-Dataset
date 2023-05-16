# **Automation Script**

<br/>

## **Table of Contents**

* **[How does it work](#how-does-it-work)**
  * **[Steps](#steps)**
  * **[Modes](#modes)**
* **[How to Use](#how-to-use)**
<br/>

## **How does it work**

<br/>

The script is divided in modules, each one representing a different attack.

This script can be divided in 3 steps and 2 modes:

### **Steps**

<br/>

* **Configuration:** This step will ask the minimum number of questions needed for the execution of the attack, i.e. if the user wants to perform a `FTP Bruteforce` theres no need to ask if the target uses `HTTPS` or `HTTP` and so forth, and then store the answers in a `config.ini` file.
* **Initial Access**: This does not apply to FTP, SSH and FileInclusion because those attacks act as the entry point them selfs, however, for the rest of the attacks, an initial access is required and for that purpose the WP File Manager plugin vulnerability is used to upload a reverse shell to the victim system.
* **Exploitation:** This is the part where the actual attack begins,  either in `interactive` or `repeat` mode.

An extra step is the **Cleanup**, which is used when possible. This step will erase files and other types of traces left behind by the attack, although not near at all to being perfect, it acts as a possible step used by an experience attacker in order to hide his tracks.
 

<br/>

### **Modes**

<br/>

* **Repeat Mode:** In this mode the script will minimize the amount of output displayed to the user and perform the attack, when possible, `n` times, defined by the user. This mode may also modify the exploit in some minor ways, such as only entering the `Cleanup` step once all the attacks concluded, instead of the default cleaning up after every attack. 
* **Interactive Mode:** This mode merely acts only as a non `Repeat Mode`. In some attacks it will allow the user to execute their own commands such as in `LXD` and `Remote File Inclusion`. On the others, it will simply be presented with banners and explanations of what's going on.

<br/>

**_Keep these steps and modes in mind, as they will be used in order to explain how to use the script_**

## **How to use**
---

In this section we will show all the possibilities when it comes to ways of executing this script.

``` Bash
sudo python3 main.py -h
```
Will display the help menu and give more information into the available flags.

<br/>

``` Bash
sudo python3 main.py -c
```
The `-c` flag will start the [Configuration](#steps) step and once done will exit.

<br/>

``` Bash
sudo python3 main.py -r {number_of_executions}
```
The `-r` flag will make the script enter the [Repeat mode](#modes) and check if the configuration file exists, if:
- **YES:** Start the [Initial Access](#steps) step with the current configuration on a loop with `{numer_of_executions}` iterations.
- **NO:** Will start the [Configuration](#steps) step and once done proceed to [Initial Access](#steps) with the same behavior as above.


<br/>

``` Bash
sudo python3 main.py
```
This will start the script in [Interactive Mode](#modes) and if the configuration file exists, ask the user if he wants to change it. If it doesn't exit, it will enter the [Configuration](#steps) step.

<br/>

``` Bash
sudo python3 main.py -c -r {number_of_executions}
```
This will firstly enter the [Configuration](#steps) step, regardless if the config file exists or not, and then, in [Repeat mode](#modes), enter the [Initial Access](#steps).

Use this combination if you want to execute a different attack multiple times.
