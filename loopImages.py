import os
import skvideo.io
import numpy as np
from wand.image import Image
# import cv2

def ex_dim(input_array):
    new_array = np.expand_dims(input_array, axis=0)
    return new_array

def images2mp4(userImage_path,img_path,R_Xcen,R_Ycen,R_width,R_height,L_Xcen,L_Ycen,L_width,L_height):
    outputMp4 = userImage_path + 'output.mp4'
    outputGif = userImage_path + 'output.gif'
    resizeImagesMp4 = []
    resizeImagesGif = []
    reverseGif = []
    reverseMp4 = []
    eyeR = []
    eyeL = []

    for f in os.listdir(userImage_path):
        if f.startswith('eye_R'):
            eyeR.append(f)
        elif f.startswith('eye_L'):
            eyeL.append(f)

    with Image(filename=img_path) as bg:
        bg.format = 'png'
        for count, eye in enumerate(zip(eyeR, eyeL), 1):
            # print(count,eye[0],eye[1])
            with Image(filename=userImage_path+str(eye[0])) as imgR:
                reR = imgR.clone()
                reR.resize(96, 76)
                bg.composite(reR, left=R_Xcen - R_width, top=R_Ycen - R_height)
            with Image(filename=userImage_path+str(eye[1])) as imgL:
                reL = imgL.clone()
                reL.resize(96, 76)
                bg.composite(reL, left=L_Xcen - L_width, top=L_Ycen - L_height)
            resGif = bg.clone()
            resGif.resize(600, 400)
            resGif.save(filename=userImage_path+'frame'+str(count)+'.png')
            # resizeImagesGif.append(resGif)

            # convert to opencv
            # mp4Buffer = np.asarray(bytearray(resGif.make_blob()), dtype=np.uint8)
            # encodeImg = cv2.imdecode(mp4Buffer, cv2.IMREAD_UNCHANGED)
            # resMp4 = cv2.cvtColor(encodeImg, cv2.COLOR_RGB2BGR)
            # resizeImagesMp4.append(resMp4)

        # lastImage = resizeImagesMp4[-1]
        # resizeImagesMp4.append(lastImage)

        # print(type(resizeImagesGif[0]),type(resizeImagesMp4[0]))

        # reverseGif = list(reversed(resizeImagesGif))
        # del reverseGif[-1]
        # resizeImagesGif.extend(reverseGif)
        # del resizeImagesGif[-1]

        # reverseMp4 = list(reversed(resizeImagesMp4))
        # del reverseMp4[0]
        # resizeImagesMp4.extend(reverseMp4)

        # with Image() as gif:
        #     for i in resizeImagesGif:
        #         with i as seq:
        #             gif.sequence.append(seq)
        #     for i in range(len(resizeImagesGif)):
        #         with gif.sequence[i] as frame:
        #             frame.delay = 20
        #     gif.type = 'optimize'
        #     gif.save(filename=outputGif)
    for f in os.listdir(userImage_path):
        if f.startswith('frame'):
            frame = skvideo.io.vread(userImage_path+f)
            resizeImagesMp4.append(frame)

    reverseMp4 = list(reversed(resizeImagesMp4))
    del reverseMp4[0]
    resizeImagesMp4.extend(reverseMp4)


    writer = skvideo.io.FFmpegWriter(outputMp4,
                                     inputdict={
                                         '-r': '5'
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

    return outputMp4