FROM ubuntu:18.04

# Turn off some questions asked during installation, to avoid infinte stall
ARG DEBIAN_FRONTEND=noninteractive

# Update system
RUN apt-get update -y &&\
    apt-get install php -y &&\
    apt-get install apache2 -y &&\
    apt-get install php-mysql -y &&\
    apt-get install wget -y &&\
    apt-get install systemd -y &&\
    apt-get install vim -y &&\
    apt-get install sudo -y

RUN rm -f /var/www/html/index.html

# Changing the max upload size limit to allow the upload of files
RUN echo 'upload_max_filesize = 10M--post_max_size = 10M' | sed 's/--/\n/g' | cat >> /etc/php/7.2/cli/php.ini
RUN echo 'upload_max_filesize = 10M--post_max_size = 10M' | sed 's/--/\n/g' | cat >> /etc/php/7.2/apache2/php.ini

# Change Work Directory
WORKDIR /

# This will allow www-data to use sudo find
# That will come in handy in order to escalate our privilege
RUN echo "www-data ALL=(ALL) NOPASSWD: /usr/bin/find"

# CMD ["/bin/bash", "-c", "chmod 777 ./setup_lxc.sh && ./setup_lxc.sh"]
CMD ["apache2ctl", "-D", "FOREGROUND"]
