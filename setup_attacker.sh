#!/bin/bash

# Run only as root, or with root privileges
if [ "$EUID" -ne 0 ]
        then echo "You need to be root in order to run this script."
        exit
fi

# Define the colors (Make script more readable)

END="\e[0m"

# Text settings.
BOLD="\e[1m"
UNDERLINE="\e[4m"

# Text color.
RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
BLUE="\e[34m"
MAGENTA="\e[35m"
CYAN="\e[36m"

# Text color with bold font.
RED_BOLD="\e[1;31m"
GREEN_BOLD="\e[1;32m"
YELLOW_BOLD="\e[1;33m"
BLUE_BOLD="\e[1;34m"
MAGENTA_BOLD="\e[1;35m"
CYAN_BOLD="\e[1;36m"

#
# End of Color declaration
#

# exit when any command fails
set -e

# keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting
trap 'echo -e "${RED_BOLD}\"${last_command}\" command failed with exit code $?."; echo -e "Try fixing the error and re-run the script${END}";' ERR

# Using Kali linux
kali=true

# Inverted quiet mode
quiet=true

# Getting current directory
wd=$(pwd)

while getopts 'hkq' OPTION; do
    case "$OPTION" in
        h)
            echo -e "\n${BOLD}This script will setup your attacking machine.${END}"
            echo -e "\n${BOLD}During development Kali Linux was used as the attacking machine, however any Linux Distrubition is expected to work as long as you use the -k flag${END}"
            echo -e "${BLUE_BOLD}-k\t\tIf you're not using Kali Linux${END}"
            echo -e "${BLUE_BOLD}-q\t\tExecute script in quiet mode${END}"
            exit 0
            ;;
        
        k)
            kali=false
            ;;
        
        q)
            quiet=false
            ;;
    esac
done

$quiet && echo -e "${GREEN_BOLD}Settings:${END}"
$quiet && echo -e "\n\t${BOLD}Using Kali Linux:\t\t$kali${END}"

# Updating
$quiet && echo -en "\n\n${BOLD}Updating${END}"
apt update -y 1>/dev/null 2>/dev/null
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

# Install jq
$quiet && echo -en "${BOLD}Installing jq${END}"
apt install jq -y 1>/dev/null 2>/dev/null
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"



if [ ! $kali ]; then
    # If OS is not Kali Linux
    $quiet && echo -en "${BOLD}Installing build-essential${END}"
    apt-get -y install build-essential 1>/dev/null 2>/dev/null
    $quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

    $quiet && echo -en "${BOLD}Installing git${END}"
    apt-get install git -y 1>/dev/null 2>/dev/null
    $quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

    $quiet && echo -en "${BOLD}Installing hydra${END}"
    apt-get install hydra -y 1>/dev/null 2>/dev/null
    $quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

    $quiet && echo -en "${BOLD}Installing curl${END}"
    apt-get install curl -y 1>/dev/null 2>/dev/null
    $quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

    $quiet && echo -en "${BOLD}Installing gzip${END}"
    apt-get install gzip -y 1>/dev/null 2>/dev/null
    $quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

    # Get rockyou.txt wordlist
    if [ ! -d /usr/share/wordlists ]; then
        mkdir /usr/share/wordlists
    fi

    if [ ! -f /usr/share/wordlists/rockyou.txt ]; then
        $quiet && echo -en "${BOLD}Getting Rockyou wordlist${END}"
        curl https://gitlab.com/kalilinux/packages/wordlists/-/raw/kali/master/rockyou.txt.gz?inline=false --output /usr/share/wordlists/rockyou.txt.gz
        cd /usr/share/wordlists
        gzip -d rockyou.txt.gz
        $quiet && echo -e "${GREEN_BOLD}  [✓]${END}"
    fi

    # Installing msfconsole
    $quiet && echo -en "${BOLD}Installing msfconsole${END}"
    cd /
    curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall 2>/dev/null && \
    chmod 755 msfinstall && \
    ./msfinstall 1>/dev/null 2>/dev/null
    # Add / to path so the user is able to invoque msfconsole
    export PATH="/opt/metasploit-framework/bin/:$PATH"
    $quiet && echo -e "${GREEN_BOLD}  [✓]${END}"


fi

# Removing Victim files
$quiet && echo -en "${BOLD}Removing Victim files${END}"
if [ -f $wd/conf.sql ]; then
    rm -f $wd/conf.sql
fi

if [ -f $wd/wordpress.conf ]; then
    rm -f $wd/wordpress.conf
fi

if [ -f $wd/setup_victim.sh ]; then
    rm -f $wd/setup_victim.sh
fi

if [ -d $wd/Aux ]; then
    rm -drf $wd/Aux
fi

if [ -d $wd/Docker ]; then
    rm -drf $wd/Docker
fi
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

$quiet && echo -e "${GREEN_BOLD}[*] DONE${END}"
$quiet && echo -e "${GREEN_BOLD}This machine is now configured!${END}"
exit 0








