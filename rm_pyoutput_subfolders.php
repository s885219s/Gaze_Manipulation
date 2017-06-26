<?php
if(strpos($_SERVER['REMOTE_ADDR'],'140.109.')!==0){exit;}

$year = date('Y');
$month= date('m');
foreach(range(1,20)as$before){
	$day= date('d')-$before;
	$path = '/var/www/gaze_manipulation/pyoutput/'.$year.$month.$day.'_*/';
	#echo'<h3>'.$path.'</h3>';#debug
	foreach(glob($path)as$v){
	  $cmd='rm -rf '.$v;
	  $a = system($cmd);
          var_dump($a);
	}
}

echo'<h1>Done, now result is:</h1>';
echo'<pre>';
echo system('ls /var/www/gaze_manipulation/pyoutput/');
