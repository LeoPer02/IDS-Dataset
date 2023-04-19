<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the
 * installation. You don't have to use the web site, you can
 * copy this file to "wp-config.php" and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * MySQL settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://codex.wordpress.org/Editing_wp-config.php
 *
 * @package WordPress
 */

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define('DB_NAME', getenv('WORDPRESS_DB_NAME'));

/** MySQL database username */
define('DB_USER', getenv('WORDPRESS_DB_USER'));

/** MySQL database password */
define('DB_PASSWORD', getenv('WORDPRESS_DB_PASSWORD'));

/** MySQL hostname */
define('DB_HOST', getenv('WORDPRESS_DB_HOST'));

/** Database Charset to use in creating database tables. */
define('DB_CHARSET', 'utf8');

/** The Database Collate type. Don't change this if in doubt. */
define('DB_COLLATE', '');

/**#@+
 * Authentication Unique Keys and Salts.
 *
 * Change these to different unique phrases!
 * You can generate these using the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}
 * You can change these at any point in time to invalidate all existing cookies. This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define('AUTH_KEY',         '{57K6%.(]6>*,7lB/doK|~fP1SmX7N0]ZU^qca(bMd/xJn4+mS]#Mo%n^8vGmO5:');
define('SECURE_AUTH_KEY',  '+0wa~#9`Lb63|e}DtkF8wFs%_w-yqR)8UUM ucKE(l,e>}rw|fY]dK[zG7C~va-_');
define('LOGGED_IN_KEY',    '9x#_{E@w@t[$Zb4w58)-!d-~/%?+4^-=y`l.4cnuM`?A6`DQ{ k-U>Ds9GLq|jj4');
define('NONCE_KEY',        '+:<G]=C_3ExyH_q?!.1sZ1b?h8!K#B/1h$zFFdRP}GP^m]JYP6D-gGBrl?3}>#BF');
define('AUTH_SALT',        '&|f0<?x)UHP|EA,hSE_4M @BfI>f@<=CxFPE,|MiFoN=Ue2s+7RhZRc|.#S#w[+6');
define('SECURE_AUTH_SALT', 'XEo12vcUtw5R-w[Iw|(@pcyo& a5St2;PrBD>+FF3}4=@XsW)[Yo86KkWV^JE!Hn');
define('LOGGED_IN_SALT',   'Pk1*Swx0B*,b1B>aAXGRX<Bn1<vsoXg?%WQ(vy1;BvN+^1LS;u=Rf>Od;+RLq<>,');
define('NONCE_SALT',       'iOexK0U27hbqP VT<|R!6fA0y.)A2!7T|!_7r#L!cb<!B)*zOujC(}Nt?D.{f(=G');

/**#@-*/

/**
 * WordPress Database Table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix  = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the Codex.
 *
 * @link https://codex.wordpress.org/Debugging_in_WordPress
 */
define('WP_DEBUG', false);

/* That's all, stop editing! Happy blogging. */

/** Absolute path to the WordPress directory. */
if ( !defined('ABSPATH') )
	define('ABSPATH', dirname(__FILE__) . '/');

/** Sets up WordPress vars and included files. */
require_once(ABSPATH . 'wp-settings.php');
define( 'WP_AUTO_UPDATE_CORE', false );
define('AUTOMATIC_UPDATER_DISABLED',true);
define(‘FS_METHOD’, ‘ftpext’);
define(‘FTP_BASE’, ‘/home/vagrant/ftp/’);
define(‘FTP_USER’, ‘vagrant’);
define(‘FTP_PASS’, ‘vagrant’);
define(‘FTP_HOST’, ‘localhost’);
define(‘FTP_SSL’, false);


