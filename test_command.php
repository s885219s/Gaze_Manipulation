<?php
if($_SERVER['REMOTE_ADDR']!='140.109.22.22'){exit;}

# http://eeepage.info/php-system-exec-passthru/

#try system AND exec
$a = passthru('/usr/bin/python3 /opt/lampp/htdocs/gaze_manipulation/_call_me_by_php---lasdF8wer2aLsdkfj.py image_path=/opt/lampp/htdocs/gaze_manipulation/uploads/2030165644.img direction=scroll');
echo'<hr>';
print_r($a);

