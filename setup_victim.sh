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

# Avoid Interactive querys
export DEBIAN_FRONTEND=noninteractive

# NOTE: The normal output will be removed to avoid clogging the user terminal, any error will terminate the script

# Inverted so that there's no need to ! $quiet in the echo's calls
quiet=true

# Using our module by deafult
module=true


# BCC already have bcc installed
bcc=false

# Getting the current directory
wd=$(pwd)

while getopts 'hqmb' OPTION; do
        case "$OPTION" in
                h)
                        echo -e "\n${BOLD}This Script will setup the victim machine as close as possible to the one used during development${END}"
                        echo -e "${BOLD}If any type of interaction is required, the user will be prompted, otherwise the script should run interely by itself${END}"
                        echo -e "${BOLD}Make sure you execute this script from folder where it came from when cloning the repository${END}"
                        echo -e "${BOLD}Bellow you will be able to see the options to execute this script, it is recommended that you the default settings${END}"
                        echo -e "${BOLD}However, you might change the settings to suit your objectives, just keep in mind that some changes in the overall project might need to be altered if you do so${END}"
                        # Show options
                        echo -e "\n\n\t${BLUE_BOLD}-q\t\t\tQuiet mode, does not print the progress\n${END}"
                        echo -e "\t${BLUE_BOLD}-m\t\t\tDisable default module, doesn't install our module\n${END}"
                        echo -e "\t${BLUE_BOLD}-b\t\t\tSkip BCC installation, only use if you already have bcc in your system${END}"
                        echo ""
                        exit 0
                        ;;

                q)
                        quiet=false
                        ;;
                m)
                        module=false
                        ;;
                b)
                        bcc=true
                        ;;

        esac
done

$quiet && echo -e "${GREEN_BOLD}Settings:${END}"
$quiet && echo -e "\n\t${BOLD}Install our module:\t\t$module${END}"
$quiet && echo -e "\t${BOLD}Skip BCC Installation:\t\t$bcc${END}"

# General Info
$quiet && echo -e "${BOLD}\n[*] Build tested with Ubuntu 18.04 ${UNDERLINE}${BLUE}https://releases.ubuntu.com/18.04/${END}"

# Remove files meant for the attacker machine
$quiet && echo -en "\n\n${BOLD}[*] Removing files meant for the attacker machine${END}"
rm -drf $wd/Attacks 1>/dev/null 2>/dev/null
if [ -f $wd/setup_attacker.sh ]; then
        rm -f setup_attacker.sh
fi
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

# Update the system
$quiet && echo -en "${BOLD}[*] Updating System${END}"

apt-get update 1>/dev/null
apt-get install snap -y 1>/dev/null
apt-get install net-tools -y 1>/dev/null

$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

# Installing our module (by default, can be disabled)
if [ $module ]; then

        # A lot of the following commands write to the stderr, therefore I'm hiding it
        # Give the chance for the user to skip bcc installation
        if [ $bcc ]; then
                # Get BCC dependecies
                $quiet && echo -en "${BOLD}[*] Installing BCC dependecies${END}"
                apt-get -y install bison build-essential cmake flex git libedit-dev \
                libllvm6.0 llvm-6.0-dev libclang-6.0-dev python zlib1g-dev libelf-dev libfl-dev python3-distutils 1>/dev/null 2>/dev/null
                $quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

                cd /

                # Installing BCC from source
                $quiet && echo -en "${BOLD}[*] Installing BCC from source, forcing version v0.24.0, since newer ones were not compatible. This might take a while${END}"
                git clone https://github.com/iovisor/bcc.git --branch v0.24.0 1>/dev/null 2>/dev/null
                mkdir bcc/build 1>/dev/null 2>/dev/null
                cd bcc/build 1>/dev/null 2>/dev/null
                cmake .. 1>/dev/null 2>/dev/null
                make 1>/dev/null 2>/dev/null
                make install 1>/dev/null 2>/dev/null
                cmake -DPYTHON_CMD=python3 .. 1>/dev/null 2>/dev/null
                pushd src/python/ 1>/dev/null 2>/dev/null
                make 1>/dev/null 2>/dev/null
                make install 1>/dev/null 2>/dev/null
                popd 1>/dev/null 2>/dev/null
                $quiet && echo -e "${GREEN_BOLD}  [✓]${END}"
        fi

        # Check if the user already has the module
        if [ ! -d /ebriareospf/ ]; then
                # Installing our module
                $quiet && echo -en "${BOLD}[*] Installing our module${END}"
                cd /
                git clone https://github.com/fonsow/ebriareospf.git 1>/dev/null 2>/dev/null
                $quiet && echo -e "${GREEN_BOLD}  [✓]${END}"
        fi
fi

# Install wordpress 
$quiet && echo -en "${BOLD}[*] Installing wordpress dependecies${END}"
apt install apache2 \
                 curl \
                 ghostscript \
                 libapache2-mod-php \
                 mysql-server \
                 php \
                 php-bcmath \
                 php-curl \
                 php-imagick \
                 php-intl \
                 php-json \
                 php-mbstring \
                 php-mysql \
                 php-xml \
                 php-zip -y 1>/dev/null 2>/dev/null

$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

$quiet && echo -en "${BOLD}[*] Installing latest wordpress${END}"
if [ ! -d /srv/www ]; then
        mkdir -p /srv/www
else
        rm -drf /srv/www
        mkdir -p /srv/www
fi
chown www-data: /srv/www
curl https://wordpress.org/latest.tar.gz --output tmp_file.tar.gz 1>/dev/null 2>/dev/null
sudo -u www-data tar zxf tmp_file.tar.gz -C /srv/www
rm tmp_file.tar.gz

$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

$quiet && echo -en "${BOLD}[*] Configuring Apache2${END}"
if [ ! -f /etc/apache2/sites-available/wordpress.conf ]; then
        mv $wd/wordpress.conf /etc/apache2/sites-available/wordpress.conf
fi
a2ensite wordpress 1>/dev/null 2>/dev/null
a2enmod rewrite 1>/dev/null 2>/dev/null
a2dissite 000-default 1>/dev/null 2>/dev/null
service apache2 reload 1>/dev/null 2>/dev/null

$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

$quiet && echo -en "${BOLD}[*] Configuring Database${END}"
mysql < $wd/conf.sql
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

$quiet && echo -en "${BOLD}[*] Configuring Wordpress${END}"
sudo -u www-data cp /srv/www/wordpress/wp-config-sample.php /srv/www/wordpress/wp-config.php
sudo -u www-data sed -i 's/database_name_here/wpdb/' /srv/www/wordpress/wp-config.php
sudo -u www-data sed -i 's/username_here/wpuser/' /srv/www/wordpress/wp-config.php
sudo -u www-data sed -i 's/password_here/wppass/' /srv/www/wordpress/wp-config.php
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

echo -en "${BOLD}[*] Adding wp-file-manager plugin${END}"
if [ -d /srv/www/wordpress/wp-content/plugins ]; then
        rm -drf /srv/www/wordpress/wp-content/plugins
fi
cp -R $wd/Docker/plugins /srv/www/wordpress/wp-content/plugins
chown www-data:www-data /srv/www/wordpress/wp-content/plugins -R
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

# Installing LXD
$quiet && echo -en "${BOLD}[*] Installing LXD" 
apt install lxd -y 1>/dev/null 2>/dev/null
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"


# Initialize LXD with default settings
$quiet && echo -en "${BOLD}[*] Initializing LXD${END}"
lxd init --auto 1>/dev/null 2>/dev/null
$quiet && echo -e "${GREEN_BOLD}  [✓] ${END}"


# Install auditd
$quiet && echo -en "${BOLD}[*] Installing Auditd${END}"
apt-get install auditd -y 1>/dev/null 2>/dev/null
service auditd start
$quiet && echo -e "${GREEN_BOLD}  [✓] ${END}"

# Download Docker

$quiet && echo -en "${BOLD}[*] Installing Docker dependecies ${END}"

# Installing dependecies
apt install apt-transport-https ca-certificates curl software-properties-common 1>/dev/null  2>/dev/null -y

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable" 1>/dev/null

$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"


# Install docker itself
$quiet && echo -en "${BOLD}[*] Installing Docker${END}"
apt install docker-ce -y 1>/dev/null 2>/dev/null

$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

# Checking if it can run the hello-world container
$quiet && echo -en "${BOLD}[*] Checking if Docker is working${END}"
docker run hello-world 1>/dev/null 2>/dev/null

$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"


# Composing docker-compose

$quiet && echo -en "${BOLD}[*] Installing Docker-compose${END}"
apt-get install docker-compose -y 1>/dev/null 2>/dev/null
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

$quiet && echo -en "${BOLD}[*] Building Containers${END}"
cd $wd/Docker

# Stops all containers
docker stop $(docker ps -a -q) 1>/dev/null 2>/dev/null
# Prunes all stopped containers
docker container prune -f 1>/dev/null 2>/dev/null

docker-compose -f ./docker-compose.yml 1>/dev/null 2>/dev/null build

chown -R www-data:www-data /srv/www/wordpress/wp-content/plugins
chown -R www-data:www-data /var/www

nohup docker-compose up &
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

cd $wd

# Installing SSH
$quiet && echo -en "${BOLD}[*] Installing OpenSSH Server${END}"
apt-get install openssh-server -y 1>/dev/null 2>/dev/null
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

# Starting SSH Server
$quiet && echo -en "${BOLD}[*] Starting SSH Server${END}"
systemctl enable ssh 1>/dev/null 2>/dev/null
systemctl start ssh 1>/dev/null 2>/dev/null
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"


# Installing FTP server
$quiet && echo -en "${BOLD}[*] Installing FTP Server${END}"
apt install vsftpd -y 1>/dev/null 2>/dev/null
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

# Starting FTP server
$quiet && echo -en "${BOLD}[*] Installing FTP Server${END}"
systemctl enable --now vsftpd 1>/dev/null 2>/dev/null
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

# Opening ports in firewall just in case
$quiet && echo -en "${BOLD}[*] Allowing FTP through firewall${END}"
ufw allow 20/tcp 1>/dev/null 2>/dev/ull
ufw allow 21/tcp 1>/dev/null 2>/dev/null
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

# Allow URL include in php apache2 (Allow remote file inclusion)
$quiet && echo -en "${BOLD}[*] Allowing PHP URL include${END}"
sed 's/allow_url_include = Off/allow_url_include = On/g' /etc/php/7.2/apache2/php.ini > out.txt && cat out.txt | cat > /etc/php/7.2/apache2/php.ini && rm out.txt
systemctl restart apache2
$quiet && echo -e "${GREEN_BOLD}  [✓]${END}"

# Adding RFI (Remote File Inclusion) endpoint
if [ -f $wd/Aux/file_inclusion.php ]; then
        $quiet && echo -en "${BOLD}[*] Adding RFI endpoint${END}"
        mv $wd/Aux/file_inclusion.php /srv/www/wordpress/file_inclusion.php
        chown www-data:www-data /srv/www/wordpress/file_inclusion.php
        $quiet && echo -e "${GREEN_BOLD}  [✓]${END}"
fi

# Checking if data folder in our module exists
if [ $module ]; then
        if [ ! -d /ebriareospf/briareospf-master/data ]; then
                mkdir /ebriareospf/briareospf-master/data
                touch /ebriareospf/briareospf-master/data/sys_exit.txt
        fi

        # Copy Aux files
        if [ -f $wd/Aux/server.py ]; then
                mv $wd/Aux/server.py /ebriareospf/briareospf-master/server.py
        fi

        if [ -f $wd/Aux/search_pid.sh ]; then
                mv $wd/Aux/search_pid.sh /ebriareospf/briareospf-master/search_pid.sh
        fi

        if [ -f $wd/Aux/overhead.sh ]; then
                mv $wd/Aux/overhead.sh /ebriareospf/briareospf-master/overhead.sh
        fi

        if [ -f $wd/Aux/side_by_side.py ]; then
                mv $wd/Aux/side_by_side.py /ebriareospf/briareospf-master/side_by_side.py
        fi
else
        echo -e "${YELLOW_BOLD}Since you're not using our module, we will keep all the auxiliary files on the Aux folder${END}"
        echo -e "${YELLOW_BOLD}We recommend that you move them to your module folder${END}"
fi

# Change permissions of unix socket
chmod 0666 /var/lib/lxd/unix.socket

# DONE
echo -e "${GREEN_BOLD}\n\n[*] Done configuring the machine! ${END}"

echo -e "${GREEN_BOLD}[***] Before doing anything make sure to start the containers, you can do so with:\n\n\tcd $wd/Docker/ && docker-compose up\n${END}"
echo -e "${YELLOW_BOLD}[*] You should now configure the wordpress websites (both in the host and in the docker)${END}"
echo -e "${YELLOW_BOLD}[*] To do so, on your browser access:\n\thttp://localhost:80\t(Host)\n\thttp://localhost:8080\t(Docker)${END}"
echo -e "${YELLOW_BOLD}[*] Don't forget to go to Dashboard -> Plugins and activate the wp-file-manager (Host and Docker) plugin, as it is required for the attacks${END}"

exit 0

# TO DO:
# Confirm if the bcc installations is working with the server
# Recommend user to update before executing, to avoid having lock


