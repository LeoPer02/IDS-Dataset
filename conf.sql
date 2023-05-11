CREATE DATABASE IF NOT EXISTS wpdb;
CREATE USER IF NOT EXISTS 'wpuser'@'localhost' IDENTIFIED BY 'wppass';
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP,ALTER ON wpdb.* TO 'wpuser'@'localhost';
FLUSH PRIVILEGES;
