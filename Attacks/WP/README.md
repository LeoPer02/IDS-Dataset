# Afterwards explain the exploit and mention the author of the exploit itself
## Modify configuration to add the root base directory to the webserver
## Allow user to define if the the webserver is using HTTPS instead of HTTP (not forget to add those changes to rev_shell_handler and requests)


# Important  Note, in order for the LXD privilege escalation to work, the user needs access to the unix.socket, that can be achieved by chmod 0666 /var/lib/lxd/unix.socket

# Mention that the exploits migh have been slightly modified in order to be easier to combine them with the rest of the script
