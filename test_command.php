<?php
if($_SERVER['REMOTE_ADDR']!='140.109.22.127'){exit;}

# http://eeepage.info/php-system-exec-passthru/

#try system AND exec
$a = system('source /home/uchen/py3env/bin/activate && /home/uchen/py3env/bin/python3.4 /var/www/gaze_manipulation/main.py image_path=/var/www/gaze_manipulation/uploads/1315787051.img direction=shift');
echo'<hr>';
print_r($a);

