import os
import sys
import numpy as np
import skvideo.io
import datetime
from random import randint
import tensorflow as tf
import keras
from keras.layers import Input
models_ver = "utils_20170706_V2"
sys.path.append(models_ver)
from load_dataset_server import input2data, read_dataset
from DeepWarp import create_model
from loopImages import ex_dim,images2mp4
from config import get_config
import threading
import os.path
import inspect
import glob
import datetime
import time
import shlex
import subprocess
from PIL import Image
from queue import Queue


def get_image_without_alpha(image): #https://stackoverflow.com/questions/35902302/discarding-alpha-channel-from-images-stored-as-numpy-arrays
    return image[:, :, :3]
def normalize_video_width_and_height(width,height):
    if not width%2:
        if not height%2:
            return width,height
        else:
            return width,height+1
    else:
        if not height%2:
    	    return width+1,height
        else:
            return width+1,height+1

def look_new_images(e,q):
    load_model_input = []
    while True:
        if(not e.is_set()):
            # wake_time = (round((time.time() - start_time),2) % cycle)
            # if base > wake_time:
            #     time.sleep(base - wake_time)
            # else:
            #     time.sleep(cycle + base - wake_time)

            img_list = glob.glob(root + "/uploads/*.img")
            if img_list :
                thread_start_time = time.time()
                print('img list is not empty!')
                date_string = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                path_random = str(randint(0, 10000)).zfill(4)
                userImage_path = os.path.join(dataImage_path, date_string + '_' + path_random + '/')
                os.mkdir(userImage_path)
                img_path = sorted(img_list, key=os.path.getmtime)[0]
                try:
                    os.rename(img_path, userImage_path + os.path.basename(img_path))
                except:
                    print('thread number'+ str(order)+ ': other thread has handled it.')
                    continue
                vid_path = img_path
                img_path = userImage_path + os.path.basename(img_path)
                img_name = os.path.basename(img_path)
                index = img_name.split('_')
                direction = index[0]
                img_format = index[1]
                pure_name = index[2]
                os.rename(img_path, userImage_path + os.path.basename(img_path)[:os.path.basename(img_path).find(".")] + '.' + img_format)
                re_img_path = userImage_path + os.path.basename(img_path)[:os.path.basename(img_path).find(".")] + '.' + img_format

                or_image = Image.open(re_img_path)
                re_image = or_image.copy()
                re_width,re_height = re_image.size
                if re_width>re_height and re_width>500:
                    re_image = re_image.resize(normalize_video_width_and_height(500,int(re_height*500/re_width)),Image.BICUBIC)
                elif re_height>re_width and re_height>500:
                    re_image = re_image.resize(normalize_video_width_and_height(int(re_width*500/re_height),500),Image.BICUBIC)
                else:
                	re_image = re_image.resize(normalize_video_width_and_height(re_width,re_height))
                re_image.save(userImage_path + os.path.basename(re_img_path))
                or_image.save(userImage_path + 'origin_'+os.path.basename(re_img_path))
                os.rename(re_img_path, img_path)

                load_model_input.append(userImage_path)
                load_model_input.append(img_path)
                # print(datetime.datetime.fromtimestamp(os.stat(img_path).st_ctime).strftime('%Y-%m-%d T %H:%M:%S.%f'))
                # img_time = datetime.datetime.fromtimestamp(os.stat(img_path).st_ctime).strftime('%Y-%m-%d T %H:%M:%S.%f')
                eyes_array = get_feature_points(img_path)
                load_model_input.append(eyes_array)
                # direction = os.path.basename(img_path)[:os.path.basename(img_path).find("_")]
                # direction = 'shift'
                load_model_input.append(direction)
                load_model_input.append(vid_path)
                load_model_input.append(thread_start_time)

                q.put(load_model_input)
                e.set()
            else:
                print("waiting for user upload image")
        else:
            print('waiting for gaze manipulation process')
        time.sleep(2)

def load_model(e,q):
    '''setting input dimension'''
    is_cfw_only = True
    model_type = 'cfw_lcm'
    dataset = "columbia_openface_v3"
    if (is_cfw_only):
        model_type = 'cfw'

    conf,_ = get_config()

    '''inputes'''
    input_ef = Input(shape=(conf.height, conf.width, conf.ef_dim), name='Input_ef', dtype=tf.float32)
    input_agl = Input(shape=(conf.agl_dim,), name='Input_agl', dtype=tf.float32)
    input_img = Input(shape=(conf.height, conf.width, conf.channel), name='Input_img', dtype=tf.float32)

    '''create network'''
    model_L = create_model(input_img, input_agl, input_ef, conf, cfw_only=is_cfw_only, is_bias=False)
    model_L.load_weights(models_ver + '/weights/best_' + model_type + '_' + dataset + '_' + 'L' + '.h5')

    model_R = create_model(input_img, input_agl, input_ef, conf, cfw_only=is_cfw_only, is_bias=False)
    model_R.load_weights(models_ver + '/weights/best_' + model_type + '_' + dataset + '_' + 'R' + '.h5')

    while True:
        if(e.is_set()):
            load_model_input = q.get()
            print('get : ' + load_model_input[1])
            try:
                R_Xcen, R_Ycen, R_width, R_height, L_Xcen, L_Ycen, L_width, L_height = predict_gaze_direction(model_L,model_R,load_model_input)
            except:
                os.remove(load_model_input[1])
                print("can not find the eyes")
                load_model_input.clear()
                q.task_done()
                e.clear()
                continue
            convert_images_to_video(load_model_input[0], load_model_input[1], R_Xcen, R_Ycen, R_width, R_height, L_Xcen, L_Ycen, L_width, L_height,load_model_input[3],load_model_input[4])
            print("generate time : {}".format(time.time() - load_model_input[5]))
            load_model_input.clear()
            q.task_done()
            e.clear()

        else:
            print('waiting for looking thread to put image in queue')
            time.sleep(1)


def get_feature_points(img_path):
    print('get feature points')
    eyes_params = subprocess.check_output(['./openface/bin/FaceLandmarkImg', '-f', img_path, '-gaze'], universal_newlines=True)
    eyes_params = shlex.split(eyes_params)
    # print(eyes_params)

    eyes_array = np.zeros((2, 7, 2), dtype=np.int16)
    for i in range(len(eyes_params)):
        eyes_array[int(i / 14)][int((i / 2) % 7)][i % 2] = eyes_params[i]

    return eyes_array

def ex_dim(input_array):
    new_array = np.expand_dims(input_array, axis=0)
    return new_array

def predict_gaze_direction(model_L,model_R,load_model_input):
    print('predict gaze direction')
    userImage_path = load_model_input[0]
    img_path = load_model_input[1]
    eyes_array = load_model_input[2]
    direction = load_model_input[3]
    nframe_per_sec = 15
    # decoded_imgs_L = []
    # decoded_imgs_R = []

    R_Xcen, R_Ycen, R_width, R_height, L_Xcen, L_Ycen, L_width, L_height, R_img, L_img, R_feature_point_layer, L_feature_point_layer = input2data(
        img_path, eyes_array)

    R_img = get_image_without_alpha(R_img)
    L_img = get_image_without_alpha(L_img)


    # img_r = np.uint8(R_img * 255)
    # savenameR = os.path.join(userImage_path, 'test_R.png')
    # skvideo.io.vwrite(savenameR, img_r)
    # img_l = np.uint8(L_img * 255)
    # savenameL = os.path.join(userImage_path, 'test_L.png')
    # skvideo.io.vwrite(savenameL, img_l)

    if direction == 'vertical':
        '''vertical'''
        av = np.expand_dims(np.linspace(-15.0, 15.0, num=nframe_per_sec), 1)
        ah = np.expand_dims(np.linspace(0.0, 0.0, num=nframe_per_sec), 1)
        angle_dif = np.concatenate((av, ah), axis=1)
        x_train_R = np.repeat(np.expand_dims(R_img,0),nframe_per_sec, axis = 0)
        x_train_L = np.repeat(np.expand_dims(L_img, 0), nframe_per_sec, axis=0)
        feature_point_R = np.repeat(np.expand_dims(R_feature_point_layer,0),nframe_per_sec, axis = 0)
        feature_point_L = np.repeat(np.expand_dims(L_feature_point_layer, 0), nframe_per_sec, axis=0)

    elif direction == 'horizontal':
        '''horizontal'''
        av = np.expand_dims(np.linspace(0.0, 0.0, num=nframe_per_sec), 1)
        ah = np.expand_dims(np.linspace(-15.0, 15.0, num=nframe_per_sec), 1)
        angle_dif = np.concatenate((av, ah), axis=1)
        x_train_R = np.repeat(np.expand_dims(R_img,0),nframe_per_sec, axis = 0)
        x_train_L = np.repeat(np.expand_dims(L_img, 0), nframe_per_sec, axis=0)
        feature_point_R = np.repeat(np.expand_dims(R_feature_point_layer, 0), nframe_per_sec, axis = 0)
        feature_point_L = np.repeat(np.expand_dims(L_feature_point_layer, 0), nframe_per_sec, axis=0)
    elif direction == 'circular':
        nframe_per_sec = 2*nframe_per_sec
        theda = np.linspace(0.0, 360.0, num=nframe_per_sec)
        ah = np.expand_dims(15 * np.cos(theda * np.pi / 180), 1)
        av = np.expand_dims(15 * np.sin(theda * np.pi / 180), 1)
        angle_dif = np.concatenate((av, ah), axis=1)
        x_train_R = np.repeat(np.expand_dims(R_img,0),nframe_per_sec, axis = 0)
        x_train_L = np.repeat(np.expand_dims(L_img, 0), nframe_per_sec, axis=0)
        feature_point_R = np.repeat(np.expand_dims(R_feature_point_layer, 0), nframe_per_sec, axis = 0)
        feature_point_L = np.repeat(np.expand_dims(L_feature_point_layer, 0), nframe_per_sec, axis=0)

    elif direction == 'mouse':
        print("not done yet")
        exit()

    # print(feature_point_R.shape)
    decoded_imgs_L = model_L.predict([feature_point_L, angle_dif, x_train_L])
    decoded_imgs_R = model_R.predict([feature_point_R, angle_dif, x_train_R])

    for i in range(nframe_per_sec):
        img_r = np.uint8(decoded_imgs_R[i,...] * 255)
        imgname = 'eyeR_' + str(i).zfill(2) + '.png'
        savename = os.path.join(userImage_path, imgname)
        skvideo.io.vwrite(savename, img_r)
    for i in range(nframe_per_sec):
        img_l = np.uint8(decoded_imgs_L[i,...] * 255)
        imgname = 'eyeL_' + str(i).zfill(2) + '.png'
        savename = os.path.join(userImage_path, imgname)
        skvideo.io.vwrite(savename, img_l)

    return R_Xcen, R_Ycen, R_width, R_height, L_Xcen, L_Ycen, L_width, L_height

def convert_images_to_video(userImage_path,img_path,R_Xcen,R_Ycen,R_width,R_height,L_Xcen,L_Ycen,L_width,L_height,direction,vid_path):
    print('convert images to video')
    outputMp4 = img_path + '.mp4'
    resizeImagesMp4 = []
    eyeR = []
    eyeL = []

    for f in sorted(glob.glob(userImage_path + 'eyeR_*.png'), key=os.path.getmtime):
        eyeR.append(f)
    for f in sorted(glob.glob(userImage_path + 'eyeL_*.png'), key=os.path.getmtime):
        eyeL.append(f)

    resMp4 = Image.open(img_path)
    for count, eye in enumerate(zip(eyeR, eyeL), 1):
        reR = Image.open(eye[0])
        # print(reR.size)
        reR = reR.resize(((R_width * 2), (R_height * 2)),Image.BICUBIC)
        # print(reR.size)
        reR = reR.crop((10, 14, R_width * 2 - 10, R_height * 2 - 16))
        # print(reR.size)
        resMp4.paste(reR, (R_Xcen - R_width + 10, R_Ycen - R_height + 14))
        reL = Image.open(eye[1])
        reL = reL.resize((L_width * 2, L_height * 2),Image.BICUBIC)
        reL = reL.crop((10, 14, L_width * 2 - 10, L_height * 2 - 16))
        resMp4.paste(reL, (L_Xcen - L_width + 10, L_Ycen - L_height + 14))
        img = np.asarray(resMp4, dtype=np.uint8)
        img.setflags(write=1)
        resizeImagesMp4.append(img)

    img2mp4_time = time.time()
    if(direction!='circular'):
        reverseMp4 = list(reversed(resizeImagesMp4))
        del reverseMp4[0]
        resizeImagesMp4.extend(reverseMp4)
        # print(len(resizeImagesMp4))
    else:
        reverseMp4 = list(resizeImagesMp4)
        resizeImagesMp4.extend(reverseMp4)
        # print(len(resizeImagesMp4))
        
    # writer = skvideo.io.FFmpegWriter(outputMp4,
    #                                  inputdict={
    #                                      '-r': '15'
    #                                  },
    #                                  outputdict={
    #                                      '-vcodec': 'libx264',
    #                                      '-b': '30000000'
    #                                  })
    # for i in resizeImagesMp4:
    #     writer.writeFrame(i)
    # writer.close()
    skvideo.io.vwrite(outputMp4,resizeImagesMp4,inputdict={},outputdict={'-r':'15','-pix_fmt': 'yuvj420p'},verbosity=1)
    os.rename(outputMp4 , vid_path + '.mp4')
    for f in os.listdir(userImage_path):
    	if not f.startswith('origin'):
        	os.remove(userImage_path+f)
    # os.remove(img_path)

    # image_txt = open(file_path + '.txt', 'w')
    # image_txt.write(file_path + "\n" + create_time)
    # image_txt.close()
    # os.remove(file_path)
    # return create_time

if __name__ == '__main__':
    root = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    dataImage_path = os.path.join(root, 'pyoutput/')
    if not os.path.isdir(dataImage_path):
        os.mkdir(dataImage_path)
    # start_time = time.time()

    # start_time = float(sys.argv[1])
    # interval_time = float(sys.argv[2])
    # order = int(sys.argv[3])
    # thread_num = int(sys.argv[4])
    # base = order * interval_time
    # cycle = interval_time * thread_num

    q = Queue()
    e = threading.Event()

    t1 = threading.Thread(name='loading_thread', target=load_model, args=(e,q))
    t1.start()
    t2 = threading.Thread(name='looking_thread', target=look_new_images, args=(e,q)) 
    t2.start()
