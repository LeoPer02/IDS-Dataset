<?php
$file=$_REQUEST['file'];

echo "File inclusion vulnerability\n";
echo "<br>";
echo "Passed file: $file";

include($file)
?>

