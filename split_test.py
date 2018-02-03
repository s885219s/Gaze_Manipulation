import glob
from PIL import Image


while True:
    img_list = glob.glob(root + "/uploads/*.img")
        
        if img_list :
            img_path = sorted(img_list, key=os.path.getmtime)[0]
            str = img_path.split(str="_",_)
            print(str)
            # resize_image = Image.open(img_path)
            # re_width, re_height = resize_image.size
            # if re_width>re_height and re_width>500 :
            #     resize_image = resize_image.resize((500, int(re_height*500/re_width)),Image.BICUBIC)
            # elif re_height>re_width and re_height>500 :
            # 	resize_image = resize_image.resize((int(re_width*500/re_height),500),Image.BICUBIC)
            # resize_image.save(img_path)
            # resize_image.save(img_path + '.jpg')