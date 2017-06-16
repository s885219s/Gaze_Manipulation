<?php
#http://www.doubleservice.com/2011/01/php-application-env-setting/

set_time_limit(0);
/*
ini_set('error_reporting', E_ALL | E_STRICT);
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
*/

define('_DIR_', __DIR__.'/');
#define('CALL_PY_FILE', '_call_me_by_php---lasdF8wer2aLsdkfj.py');
define('CALL_PY_FILE', 'main.py');
define('GAZE_PYTHON_OUTPUT_FOLDER', 'pyoutput');
define('WEB_URL', '/gaze_manipulation/');
define('IS_DEVELOPER', $_SERVER['REMOTE_ADDR']=='140.109.22.127');

function get_python_result($uploaded_image_path, $direction){
  $DEBUG=0 && IS_DEVELOPER;
  # source..
  /*
  $cmd_prepare = 'source /home/uchen/py3env/bin/activate'; 
  if($DEBUG){
    echo$cmd_prepare."<br>";
  }else{
  $command = escapeshellcmd($cmd_prepare);
  shell_exec($command);
  }*/

  # execute...
  $cmd = 'source /home/uchen/py3env/bin/activate && /home/uchen/py3env/bin/python3.4 ' . _DIR_ . CALL_PY_FILE . ' image_path='.$uploaded_image_path . ' direction='.$direction;
  #debug
  if($DEBUG){
    echo$cmd."<br>";
    die('----------debug--------------');
  }else{
  file_put_contents(_DIR_.'_pycmd.log.php', $cmd."\n", FILE_APPEND | LOCK_EX);
  $output = exec($cmd);
  }
  return $output;
}

function save_local_file($uploadfile){
  $img_type = $_FILES['image']['type'];
  $img_name = $_FILES['image']['name'];
  $a = array($img_type, $uploadfile, $img_name);
  $s = "\n" . implode('`',$a);
  return file_put_contents(_DIR_.'_record.php', $s, FILE_APPEND | LOCK_EX);
}

function db_save($uploadfile){
 /* Setup a database connection with PDO */
        // start of DB
        if(!file_exists('config.for.dev.php')){
          return;
        }
        require_once 'config.for.dev.php';
        // Set DSN
        $dsn = 'mysql:host='.$dbhost.';dbname='.$dbname;

        // Set options
        $options = array(
            PDO::ATTR_PERSISTENT    => true,
            PDO::ATTR_ERRMODE       => PDO::ERRMODE_EXCEPTION
        );

        try {
            $db = new PDO($dsn, $dbuser, $dbpass, $options);
        } catch(PDOException $e){
            die("Error!: " . $e->getMessage());
        }

        /* Setup query */
        $query = 'INSERT INTO uploads (name, original_name, mime_type) VALUES (:name, :oriname, :mime)';

        /* Prepare query */
        $stmt = $db->prepare($query);

        /* Bind parameters */
        $stmt->bindParam(':name', basename($uploadfile));
        $stmt->bindParam(':oriname', basename($_FILES['image']['name']));
        $stmt->bindParam(':mime', $_FILES['image']['type']);

        /* Execute query */
        try {
            $stmt->execute();
        } catch(PDOException $e){
            // Remove the uploaded file
            unlink($uploadfile);

            die("Error!: " . $e->getMessage());
        }

}
