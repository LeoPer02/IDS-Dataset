#!/bin/bash


# GENERAL INFORMATIOn
# This script executes a lot of instructions and measures the time does instructions take when:
# - There's no auditting of any type
# - When auditd is monitoring the script
# - When our/yours module is monitoring this script
# 1500 instructions will be executed per run, and the number of runs can be controlled by the user, default 5
# After that the time it took for each run and the average are place inside a file, also controled by the user, default /Overhead_Logging.txt
# In order to measure the time we record the time before the execution and after and then subtract both
# This way we lose some precision, however we record up to nanoseconds and calculate with up to 9 decimal digits
# If you want results as precise as possible, use a higher value of runs, however that will come at the cost of time


# Run only as root, or with root privileges
if [ "$EUID" -ne 0 ]
	then echo "You need root privileges to run this script. However if you're running our module use root itself"
	exit
fi

file_path='/Overhead_Logging.txt'
iter=5
module_start=""
module_end=""

if [ $# -eq 0 ]
then
	echo "Invalid number of arguments, if you need help use bash $(basename $0) -h"
	exit 1
fi

while getopts ':hf:i:s:e:' OPTION; do
	case "$OPTION" in
		h)
			echo ""
			echo "script usage: $(basename $0) [-p path/to/folder/] [-h] [-f name_of_file] [-i some_int]" >&2
			echo ""
			echo "-h displays this help information"
			echo "-i defines the number of times each test will be performed, higher number increases accuracy but at the cost of time, default value: 5"
			echo "-f defines file in wich the results will be saved, default '/Overhead_Logging.txt'. This will overwrite whatever is in the file, or create a new one if it doens't exist"
			echo ""
			echo "##################### YOUR OWN MODULE #######################"
			echo "-s defines the script used to stop the module after is has been used, you can omit this step if the script in -e stops by itself" 
			echo "-e defines the script used to inialize the module (in case you want to use your own), for that provide an .sh file that will monitor this process"			
			echo ""
			echo "By default we will execute $HOME/ebriareospf/briareospf-master/syscall_exit_tracer.py"
			exit 0
			;;
		f)
			file_path="$OPTARG"
			;;
		i)	
			iter=$OPTARG
			re='^([1-9]+[0-9]*)$'
			if ! [[ $iter =~ $re ]] ; then
				echo "error: Not a number" >&2; exit 1
			fi
			;;
		s)
			module_start="$OPTARG"
			if [ ! -f $module_start ]; then
				echo "The Module_start script provided does not exist"
				exit 1
			fi
			;;
		e)
			module_end="$OPTARG"
			if [ ! -f $module_end ]; then
				echo "The Module_end script provided does not exist"
				exit 1
			fi
			;;
	esac
done


exec_random(){
	local counter=1
	while [ $counter -le 500 ]
	do
		# This cycle will generate multiple read/write instructions
		let counter=counter+1
		echo "çfweuohfisadnbfkjghsgayirtyaioury793" | cat > ./random_file_.txt
		cat ./random_file_.txt > ./random_file_.txt
		rm ./random_file_.txt
	done
}

take_measurements() {
	local counter=0
	local temp=0
	local sum_time=0
	while [ $counter -lt $iter ]
	do
		start=`date +%s.%N` # Register Start time
		time_temp=$({ time exec_random; } 2> out.time && cat out.time) # Execute the instructions, get its time, redirect it to the temporary file and output it's content
		end=`date +%s.%N` # Register end time

		rm out.time # Remove temporary file
		time=$(echo $time_temp | grep real | awk '{ print $2 }' | cut -d "m" -f2) # Get execution time with 'time'
		temp=$( echo "$end - $start" | bc -l ) # Get execution time with date
		sum_time=$(echo "$sum_time + $temp" | bc -l) # Add to total

		echo "Measure $counter:" | cat >> $file_path
		echo "  With time: $time" | cat >> $file_path
		echo "  With date: $temp" | cat >> $file_path
		echo "" | cat >> $file_path 
		let counter=counter+1
	done
	average=$(echo "scale=9; $sum_time / $iter" | bc)
	echo $average
}

get_no_logging() {
	echo "NO LOGGING" | cat >> $file_path
	echo "==============================" | cat >> $file_path 
	without_logging=$(take_measurements)
	echo "==============================" | cat >> $file_path 
	echo "Average: $without_logging" | cat >> $file_path 
	echo ""  | cat >> $file_path
	#####################################################
	echo "#######################################################"
	echo "  Finished measuring time without any monitoring"
	echo "  $iter runs performed, average of: $without_logging""s"
	echo "#######################################################" 
	echo ""
}

init_audit() {
	service auditd start
	auditctl -D > /dev/null 2>&1
	auditctl -a exit,always -F pid=$(echo $$) -S all -k parent_pid
	# Module for now does not allow filtering by PPID
	# auditctl -a exit,always -F ppid=$(echo $PPID) -S all -k parent_pid
}

cleanup_audit() {
	auditctl -D > /dev/null 2>&1
	service auditd stop
}

get_with_audit() {
	init_audit
	echo "WITH AUDITD" | cat >> $file_path
	echo "==============================" | cat >> $file_path 
	with_audit=$(take_measurements)
	echo "==============================" | cat >> $file_path 
	echo "Average: $with_audit" | cat >> $file_path 
	echo ""  | cat >> $file_path
	cleanup_audit

	#####################################################
	echo "#######################################################"
	echo "  Finished measuring time with audit"
	echo "  $iter runs performed, average of: $with_audit""s"
	echo "#######################################################"
	echo ""
}

init_module() {
	if [[ $module_start == "" ]]; then
		cur_wd=$(pwd)
		# Hardcoded
		cd /home/vagrant/ebriareospf/briareospf-master
		timeout 60 python3 /home/vagrant/ebriareospf/briareospf-master/syscall_exit_tracer.py -p $(echo $$) & > /dev/null 2>&1
		cd $cur_wd
	else
		bash $module_start
	fi
}

clean_module() {
	# Even if provided there's no need to execute a module_end without a module_start
	if [ $module_start != "" ] && [ $module_end != "" ]; then
		bash $module_end
	fi
}

get_with_module() {
	init_module
	echo "WITH MODULE" | cat >> $file_path
	echo "==============================" | cat >> $file_path 
	with_module=$(take_measurements)
	echo "==============================" | cat >> $file_path 
	echo "Average: $with_module" | cat >> $file_path 
	echo ""  | cat >> $file_path

	#####################################################
	echo "#######################################################"
	echo "  Finished measuring time with the module"
	echo "  $iter runs performed, average of: $with_module""s"
	echo "#######################################################" 
	echo ""
}

current_time=$(date)
# Clean file
rm $file_path > /dev/null 2>&1
echo "##########################################" | cat >> $file_path
echo "Sample taken at: " $current_time | cat >> $file_path
echo "" | cat >> $file_path
echo "NOTE:" | cat >> $file_path
echo "The execution time was calculated using 2 different commands 'time' and 'date' but the average is calculate only using the date time" | cat >> $file_path
echo "Within the time calculate by 'date' is also the time execution of the command 'time' is self so that might justify some level of disparity" | cat >> $file_path
echo "However, from our tests, that disparity is usually too small to be considered, so we decided to keep both for matters of validation" | cat >> $file_path
echo "" | cat >> $file_path


service auditd stop

# Get time without any logging system
get_no_logging
get_with_audit
get_with_module

#### TO FILE #############
echo "" | cat >> $file_path
echo "Without any type of logging: $without_logging" | cat >> $file_path
echo "With auditctl: $with_audit" | cat >> $file_path
echo "With our module: $with_module" | cat >> $file_path

#### TO TERMINAL #########
echo ""
echo "Stats:"
echo "Without any type of logging: $without_logging""s"
echo "With auditctl: $with_audit""s"
echo "With our module: $with_module""s"
echo ""
echo ""
echo "Measurements taken"
echo "Please check $file_path in order to see the details of the measurement"


