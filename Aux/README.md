# **Auxiliary Scripts**

## **Table of Contents**

* **[Server](#server)**
  * **[How to Use Server](#how-to-use-server)**
  * **[Usage examples Server](#usage-examples-server)**
* **[Overhead](#overhead)**
  * **[How to Use Overhead](#how-to-use-overhead)**
  * **[Usage examples Overhead](#usage-examples-overhead)**
* **[Compare](#compare)**
  * **[How to Use Compare](#how-to-use-compare)**
* **[Side by Side](#side_by_side)**
  * **[How to Use Side by Side](#how-to-use-side_by_side)**
* **[Search Pid](#search-pid)**
* **[File Inclusion](#file-inclusion)**

<br/>

## **Server**

This script is responsible for creating a server that will listen for 1 of 2 requests:
* **/start?exploit={name_of_exploit}:** This GET request warns the server that the attack will begin shortly, and so the server, based on the name of the exploit, grabs the necessary PIDs to audit, and starts both auditing modules over those PIDs.
  
* **/stop?exploit={name_of_exploit}:** This GET request tells the server that the attack as ended, that way the server stops the auditing modules, grabs the output of both measurements and places them on the designated folder with the correct name, i.e. "Docker01.txt" and "audit_Docker01.txt".

If you're using [our](https://github.com/fonsow/ebriareospf/tree/main/briareospf-master) module it's recommended that you execute the server as `root` and not with `sudo` as this was a cause of many problems during development.

<br/>

### **How to Use Server**

Quick rundown of the flags:
* **-p {port}:** Defines the port in which the server is to listen. *_Default = 5555_*
* **-d {folder}:** Defines the dataset folder, i.e. where the files are to be saved. *_Default = /_*
* **-s {bash_script}:** Allows the user to use their own module to audit the system calls, if this value is provided, instead of starting our module the server will execute: `bash {bash_script} PIDs`. *_Default = ''_*
* **-e {bash_script}:** Defines the script used to stop the user own auditing module, can be omitted if the module stops by itself. *_Default = ''_*
* **-h** Will display the help menu


### **Usage Examples Server**

Here are some examples of execution of the Server script:

``` Bash
# su root
python3 server.py -p 4444 -d /home/wpuser/dataset/
```
Listens on port `4444`, stores the output in `/home/wpuser/dataset/` and user our module

<br/>

``` Bash
# su root
python3 server.py -p 7878 -d /home/wpuserp/dataset/ -s ./start_module.sh -e ./end_module.sh
```
Listens on `7878`, stores the output in `/home/wpuser/dataset/`, does not use our module and so starts the user module with `start_module.sh` and stops it with `./stop_module.sh`.

<br/>

``` Bash
# su root
python3 server.py -s ./start_module_stops_alone.sh
```
Listens on `5555`, stores the output in `/`, does not use our module and so starts the user module with `start_module.sh` and since no end module script was provided, is assumed that the user module stops on it's own.

## **Overhead**

This script is responsible for comparing the execution time between modules.
In order to do that it will execute a bunch the following commands:

``` Bash
while [ $counter -le 500 ]
	do
		# This cycle will generate multiple read/write syscalls
		let counter=counter+1
		echo "çfweuohfisadnbfkjghsgayirtyaioury793" | cat > ./random_file_.txt
		cat ./random_file_.txt > ./random_file_.txt
		rm ./random_file_.txt
	done
```

The user can define how many iterations the script will do, that is, how many times it will run the commands above. By default that value is 5, however, the bigger the value the most accurate will be the average calculated but it also translates into a lot more time waiting.

We mentioned above the average, this values is calculated in 2 ways, using the command `time` and the command `date +%s.%N`. 

The usage of time is simple, we place the commands to executed inside a function, lets call it `exec_cmd` and executed `time exec_cmd`. With `date` we registered the time right before and after the beginning of the execution and then got the difference.

**Why use 2 types of measurement?** If one fails, we have the other or if one, for some reason, returns an absurd value, we can use the other one as reference.

This script executes 3 measurements:
* **Time it takes with no auditing**
* **Time it takes with only auditd**
* **Time it takes with only our/yours module**

### **How to use Overhead**

<br/>

Quick rundown of the flags:

* **-h** Displays the help menu.
* **-f {file}:** Defines the file in which the result is to be saved. *_Default = '/Overhead_Logging.txt_*
* **-r {number_iterations}:** Defines the number of time each measurement will be performed. *_Default = 5_*
* **-s {module_start}:** Defines the script that starts your module. *_Default = ''_*
* **-e {module_end}:** Defines the script that stops your module. Can be omitted if the module stops by himself but not recommended, because if the module takes a lot of time to do so it might influence sequential measurements. *_Default = ''_*
* **-m {our_module_path}:** Defines where the folder where our module is stored (not the executable but it's working directory). *_Default = "/ebriareospf/briareospf-master/"_*

<br/>

### **Usage Examples Overhead**

Here are some examples of execution of the overhead script:

``` Bash
# su root
bash overhead.sh -f /home/wpuser/first_exec.txt -r 10 -m /ebriareospf/briareospf-master/
```
Execute each measurement `10` times, with our module in `/ebriareospf/briareospf-master/` and store the result in `/home/wpuser/first_exec.txt`.

<br/>

``` Bash
# su root
bash overhead.sh -f /home/wpuser/first_exec.txt -r 3 -s ./start_module.sh -e ./end_module.sh
```
Execute each measurement `3` times with the user module by starting with `./start_module.sh` and ending with `./end_module` storing the result in `/home/wpuser/first_exec.txt`.

<br/>

``` Bash
# su root
bash overhead.sh -r 10
```
Execute each measurement `10` times with our module in `/ebriareospf/briareospf-master/` and store the results in `/Overhead_Logging.txt`.

<br/>

``` Bash
# su root
bash overhead.sh
```
Execute each measurement `5` times with our module in `"/ebriareospf/briareospf-master/"` and store the results in `/Overhead_Logging.txt`.

<br/>

## **Compare**

This script will take the result from our module and compare it to the auditd in the following way:
* Go line by line and grab the PID and System call.
* Store that information in a list of tuples `(PID, SYSCALL_M)`.
* If the PID collected never appeared before, add it to the set of PIDs.
* Once done, start iterating through auditd output and once you find an entry with a PID which is in the PID set, add it to a list as tuple `(PID, SYSCALL_A)`.
* Once also done, start iterating through both list and:
  * If both out module and auditd have an entry with PID `x` print `Pid x  Module SYSCALL_M Audit SYSCALL_A`
  * If only our module as an entry with PID `x` then print `Pid x  Module SYSCALL_M  Audit NOT_FILTERED`
  * If only audit has an entry with PID `x` then print `Pid x  Module NOT_FILTERED  Audit SYSCALL_A`

This will compare the system calls gathered by both audit modules but only for the PIDs that our module detected. The results we are trying to get here are, if we take the PIDs that both captured, did they catch the exact same system calls? The order was the same?

### **How to Use Compare**

This script does not use flags, to use it execute the following command:

``` Bash
sudo python3 compare.py our_module_file.txt auditd_file.txt 
```
This will write to `./differences.txt`.

If you want to redirect the output:

``` Bash
sudo python3 compare.py our_module_file.txt auditd_file.txt && mv ./differences.txt {file_to_redirect}
```

<br/>

## **Side_by_side**

This script will create an output file which compares, side by side, the entries of our module with the auditd's entries. Contrary to the [Compare](#compare) script, we want to study the global differences on the auditing performed by both modules, for that we print, side by side, the entries collected by both modules.

The output can have one of the following formats:

``` 
Module                  Audit
pid=x   syscall=y       pid=i   sycall=j
```

```
Module                  Audit
pid=?   syscall=?       pid=i   sycall=j
```

```
Module                  Audit
pid=x   syscall=y       pid=?   sycall=?
```

The `?` here meaning that no more entries were registered by the module.

<br/>

### **How to Use Side_by_Side**
<br/>

This script does not use flags, to use it execute the following command:

``` Bash
sudo python3 side_by_side.py our_module_file.txt auditd_file.txt 
```
This will write to the `stdio`.

If you want to redirect the output:

``` Bash
sudo python3 side_by_side.py our_module_file.txt auditd_file.txt > {file_to_redirect}
```

<br/>

## **Search Pid**

This script is only used to add the rules to auditd when the server receives a request to start the auditing, however if you wish to use it:

``` Bash
sudo bash search_pid.sh pid_1,pid_2,pid_3,...,pid_n
```

To check if the rules were set:

``` Bash
auditctl -l
```
<br/>

## **File Inclusion**

This is the vulnerable web page file that will be moved to the correct folder once the `setup_victim.sh` script is executed or deleted when executing the `setup_attacker.sh` script.

<br/>
