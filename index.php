<?php
require_once 'inc.php';
define('DEFAULT_DIRECTION', 'horizontal');
define('UPLOAD_IMAGE_PATH', 'uploads/');
$ARRAY_VALID_DIR = array(DEFAULT_DIRECTION, 'vertical', 'circular');#, 'mouse');
#if($_POST or $_FILES){print_r($_POST); print_r($_FILES);exit;}

if(!empty($_POST['dir']) && !empty($_FILES['image']) && $_FILES['image']['error'] == 0) {
    // https://stackoverflow.com/questions/38509334/full-secure-image-upload-script
    $uploaddir = UPLOAD_IMAGE_PATH;
    #print_r($_POST);print_r($_FILES);

    $direction = $_POST['dir'];

	$img_ext = '';
	if(isset($_FILES['image']) and isset($_FILES['image']['type']) and strpos($_FILES['image']['type'], 'image/')!==0){
		$err_msg = ('Please upload VALID image file.');
	}else{

    /* Generates random filename and extension */
    function tempnam_sfx($path, $suffix, $prefix){
        do {
            if(substr($path, -1)!=='/'){$path.='/';}
            $file = $path.$prefix.'_'.mt_rand().$suffix;
            $fp = @fopen($file, 'x');
        } while(!$fp);

        fclose($fp);
        return $file;
    }
    function imgfilename_for_python_monitor($direction, $img_ext, $path, $suffix){
      global$ARRAY_VALID_DIR;
      if(!in_array($direction, $ARRAY_VALID_DIR)){
        $direction = DEFAULT_DIRECTION;
      }
      return tempnam_sfx($path,$suffix, $direction.'_'.strtolower($img_ext));
    }
    function get_mp4_file_abs_path($uploaded_img_fileabspath){
      return $uploaded_img_fileabspath.'.mp4'; # <-- After discussed with Python developer
    }

    /* Process image with GD library */
    $verifyimg = getimagesize($_FILES['image']['tmp_name']);

    /* Make sure the MIME type is an image */
    $pattern = "#^(image/)[^\s\n<]+$#i";

    if(!preg_match($pattern, $verifyimg['mime'])){
        die("Only image files are allowed!");
    }

    /* Rename both the image and the extension */
    $ary_img_name_split = explode('.', $_FILES['image']['name']);
    $img_ext = $ary_img_name_split[count($ary_img_name_split)-1];
    $uploadfile = imgfilename_for_python_monitor($direction, $img_ext, $uploaddir, ".img");

    /* Upload the file to a secure directory with the new name and extension */
    if (move_uploaded_file($_FILES['image']['tmp_name'], $uploadfile)) {

       $abs_uploadfile = __DIR__  . '/' . $uploadfile;
       #echo 'absolute uploaded image path: '.($abs_uploadfile);#debug
       $abs_mp4file = get_mp4_file_abs_path($abs_uploadfile);

       $py_output = '';
       $MAX_N = 10;$n=0;
       while(true){
          if($py_output or $n>=$MAX_N){break;}
          if(file_exists($abs_mp4file)){
            $py_output=$abs_mp4file;
          }else{
            sleep(1);
          }
       }

       #save_local_file($uploadfile);

       #db_save($uploadfile); 
       
    } else {
        $err_msg = ("Image upload failed!");
    }

	}//end of $err_msg 'Please upload VALID image file
}
?>
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
<link rel="shortcut icon" type="image/x-icon" href=favicon.ico />
  <title>Upload Page</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href=vendors/bootstrap-3.3.7/css/bootstrap.min.css />
<script src=vendors/jquery-3.2.1.min.js></script>
<script src=vendors/bootstrap-3.3.7/js/bootstrap.min.js></script>
<script src=vendors/bootstrap-3.3.7/js/bootstrap-filestyle.min.js></script>
<style>
ul,ol{padding:0}
li{list-style:none}
.glyphicon.spinning{
animation: spin 1s infinite linear;
-webkit-animation: spin2 1s infinite linear;
}
@keyframes spin {
    from { transform: scale(1) rotate(0deg); }
    to { transform: scale(1) rotate(360deg); }
}
@-webkit-keyframes spin2 {
    from { -webkit-transform: rotate(0deg); }
    to { -webkit-transform: rotate(360deg); }
}
#typebox button{text-transform:capitalize}
  
  h1{font-size:24px}
}
</style>
</head>
<body>
<div class=container>
<div class=row>
<div class="col-lg-8 col-lg-offset-2">
<h1 class="page-header">Gaze Manipulation Demo</h1>
<ul>
<li>Supported image extensions: <code>.png</code>, <code>.jpg</code>, <code>.jpeg</code></li>
<?php /*
<li>Maximum file size: <tt>300kB</tt>.</li>
<li>Maximum image dimension: <tt>400px</tt>. Will be resized if exeeds the limit.</li>
<li>Minimum image dimensions <i>(after resize)</i>: <tt>200x25px</tt>.</li>
*/?>
</ul>
<?php if(isset($err_msg) and $err_msg){
echo '<div class="alert alert-danger">
  <strong>Error!</strong> '.$err_msg.strpos($_FILES['image']['type'], 'image/').'
</div>';
	}?>
<form id="submit-form" class="form-inline" method="post" enctype="multipart/form-data">
<div class="form-group" style="margin:0;padding:0">
<div class="input-group">
<input type="file" name="image" class="filestyle" data-icon="false" data-buttonBefore="true">
</div>
</div>
<div style="border:1px solid #ccc;padding:12px;margin:12px 0 0" id=typebox>
<div style="font-weight:bold;margin:0 0 10px">Types</div>
<?php foreach($ARRAY_VALID_DIR as $k=>$v){ ?>
<button class="btn btn-default btn-dir" type="submit" name="dir" value="<?php echo$v?>"><?php echo $v=='mouse' ? 'cursor' :$v?></button>
<?php } ?>
</div>
</form>

<div style=height:16px></div>

<div id="status-progress" class="alert alert-info" role="alert" style="display: none;"><span class="glyphicon glyphicon-refresh spinning"></span> <b>Wait for it...</b>
</div>

<script>
$('#submit-form').submit(function(){
  $('#status-progress').css('display','');
});
</script>

<?php if(isset($py_output) and $py_output){ ?>
<div id="output" class="panel panel-success" style="">
<div class="panel-heading"><b>Result</b></div>
<div class="panel-body" style="overflow-x: scroll;">
<?php
#$GAZE_OUTPUT_PATH = GAZE_PYTHON_OUTPUT_FOLDER . '/';
list($tmp, $path) = explode(UPLOAD_IMAGE_PATH, $py_output);
$src = UPLOAD_IMAGE_PATH. $path;
?>
<video style="max-width:98%;width:500px;height:500px" autoplay loop controls><source src="<?php echo $src?>" type="video/mp4">Your browser does not support the video tag with MP4.</video>
<div style=height:30px></div>
</div><?php #.panel-body?>
</div><?php #.panel?>
<?php } ?>

</div><?php #.col-lg?>
</div><?php #.row?>
</div><?php #.container?>
