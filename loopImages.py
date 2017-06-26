import os
import skvideo.io
import numpy as np
from PIL import Image
import glob

def ex_dim(input_array):
    new_array = np.expand_dims(input_array, axis=0)
    return new_array

def images2mp4(userImage_path,img_path,R_Xcen,R_Ycen,R_width,R_height,L_Xcen,L_Ycen,L_width,L_height):
    outputMp4 = userImage_path + 'output.mp4'
    resizeImages = []
    resizeImagesMp4 = []
    reverseMp4 = []
    eyeR = []
    eyeL = []


    for f in sorted(glob.glob(userImage_path+'eyeR_*.png'), key = os.path.getmtime):
        eyeR.append(f)
    for f in sorted(glob.glob(userImage_path+'eyeL_*.png'), key = os.path.getmtime):
        eyeL.append(f)

    resMp4 = Image.open(img_path)
    for count, eye in enumerate(zip(eyeR, eyeL), 1):
        reR = Image.open(eye[0])
        reR = reR.resize(((R_width*2), (R_height*2)))
        reR = reR.crop((10, 8, R_width * 2 - 12, R_height * 2 - 10))
        resMp4.paste(reR, (R_Xcen - R_width + 10, R_Ycen - R_height+8))
        reL = Image.open(eye[1])
        reL = reL.resize((L_width*2, L_height*2))
        reL = reL.crop((10, 8, L_width * 2 - 12, L_height * 2 - 10))
        resMp4.paste(reL, (L_Xcen - L_width + 10, L_Ycen - L_height+8))
        if resMp4.width > 1000 or resMp4.height > 1000:
            resMp4.resize((int(resMp4.width/2), int(resMp4.height/2)))
        elif resMp4.width > 2000 or resMp4.height > 2000:
            resMp4.resize((int(resMp4.width) / 4, int(resMp4.height / 4)))
        img = np.asarray(resMp4, dtype=np.uint8)
        img.setflags(write=1)
        resizeImagesMp4.append(img)

    reverseMp4 = list(reversed(resizeImagesMp4))
    del reverseMp4[0]
    resizeImagesMp4.extend(reverseMp4)

    writer = skvideo.io.FFmpegWriter(outputMp4,
                                     inputdict={
                                         '-r': '24'
                                     },
                                     outputdict={
                                         '-vcodec': 'libx264',
                                         '-b': '30000000'
                                     })
    for i in resizeImagesMp4:
        writer.writeFrame(i)
    writer.close()

    for f in os.listdir(userImage_path):
        if not f.startswith('output'):
            os.remove(userImage_path+f)
    os.remove(img_path)

    return outputMp4
