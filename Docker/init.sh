#!/usr/bin/env bash
apt-get update
apt-get install sudo -y
echo "www-data ALL=(ALL) NOPASSWD: /usr/bin/find" | cat >> /etc/sudoers
chown -R www-data:www-data /var/www/html/wp-content/