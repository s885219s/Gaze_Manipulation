<?php
require_once 'inc.php';

if(!empty($_POST['submit']) && !empty($_FILES['image']) && $_FILES['image']['error'] == 0) {
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

       $abs_uploadfile = __DIR__ . $uploadfile;
       $output = get_python_result($abs_uploadfile);

       save_local_file($uploadfile);

       db_save($uploadfile); 
       
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
</head>
<body>
<h1>Please upload image:</h1>
<form method="post" enctype="multipart/form-data">
<input name="image" type="file" />
<input name="submit" type="submit" value="Upload" />
</form>
