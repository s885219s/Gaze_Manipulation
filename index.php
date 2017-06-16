<?php
require_once 'inc.php';
$ARRAY_VALID_DIR = array('shift', 'scroll', 'mouse');

if(!empty($_POST['submit']) && !empty($_POST['dir']) && !empty($_FILES['image']) && $_FILES['image']['error'] == 0) {
    // https://stackoverflow.com/questions/38509334/full-secure-image-upload-script
    $uploaddir = 'uploads/';
    #print_r($_POST);print_r($_FILES);

    /* Generates random filename and extension */
    function tempnam_sfx($path, $suffix){
        do {
            if(substr($path, -1)!=='/'){$path.='/';}
            $file = $path.mt_rand().$suffix;
            $fp = @fopen($file, 'x');
        } while(!$fp);

        fclose($fp);
        return $file;
    }

    /* Process image with GD library */
    $verifyimg = getimagesize($_FILES['image']['tmp_name']);

    /* Make sure the MIME type is an image */
    $pattern = "#^(image/)[^\s\n<]+$#i";

    if(!preg_match($pattern, $verifyimg['mime'])){
        die("Only image files are allowed!");
    }

    /* Rename both the image and the extension */
    $uploadfile = tempnam_sfx($uploaddir, ".img");

    /* Upload the file to a secure directory with the new name and extension */
    if (move_uploaded_file($_FILES['image']['tmp_name'], $uploadfile)) {

       $abs_uploadfile = __DIR__  . '/' . $uploadfile;
       $direction = $_POST['dir'];
       if(!in_array($direction, $ARRAY_VALID_DIR)){die('INVALID dir');}
       $py_output = get_python_result($abs_uploadfile, $direction);

       #save_local_file($uploadfile);

       #db_save($uploadfile); 
       
    } else {
        die("Image upload failed!");
    }
}
?>
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Upload Page</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<?php
if(isset($py_output) and $py_output){
echo'<h1 style="border-bottom:1px solid #aaa">Result</h1>';
$GAZE_OUTPUT_PATH = GAZE_PYTHON_OUTPUT_FOLDER . '/';
list($tmp, $path) = explode($GAZE_OUTPUT_PATH, $py_output);
$src = WEB_URL . $GAZE_OUTPUT_PATH . $path;
?>
<video width="320" autoplay loop controls><source src="<?php echo $src?>" type="video/mp4">Your browser does not support the video tag with MP4.</video>
<div style=height:30px></div>
<?php } ?>
<h1 style="border-bottom:1px solid #aaa">Upload</h1>
<form method="post" enctype="multipart/form-data">
<h2>Direction:</h2>
<?php foreach($ARRAY_VALID_DIR as$k=>$v){ ?>
<label><input type=radio name=dir value=<?php echo $v?><?php echo $k==0?' checked':''?> /><?php echo$v?></label>
<?php } ?>
<h2>Image:</h2>
<input name="image" type="file" />
<input style="display:block;max-width:280px;width:100%;font-size:18px;height:60px;margin:30px 0 0" name="submit" type="submit" value="Upload!" />
</form>
