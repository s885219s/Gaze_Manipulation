import pickle
import sys
import os
import dlib
import glob
import math
from skimage import io
from skimage.transform import rescale, resize, downscale_local_mean
import numpy as np

def read_training_data(file_path):
	# x.keys()
	#'x_train_L':[len = 441] 		; data['x_train_L'][i], int16, (41, 51, 3)
	#'x_train_R':[len = 441]		; data['x_train_R'][i], int16, (41, 51, 3)
	#'y_train_L':[len = 441]		; data['y_train_L'][i], int16, (41, 51, 3)
	#'y_train_R':[len = 441]		; data['y_train_R'][i], int16, (41, 51, 3)	
	#'feature_point_R':[len = 441]		; data['feature_point_R'][i], int16, (41, 51, 14)
	#'feature_point_L':[len = 441]		; data['feature_point_L'][i], int16, (41, 51, 14)
	#'v_delta:[len = 441]			; data['v_delta'][i], int
	#'h_delta:[len = 441]			; data['h_delta'][i], int
	#'x_train_file_name':[len = 441]	; data['x_train_file_name'][i], str
	#'y_train_file_name':[len = 441]	; data['y_train_file_name'][i], str
	f = open(file_path, 'rb')
	data = pickle.load(f)
	f.close()
	return data

def read_dataset(dirs_path, pose):
#     print(data.keys())
    x_train_L = []
    y_train_L = []
    x_train_R = []
    y_train_R = []
    feature_point_R = []
    feature_point_L = []
    v_delta = []
    h_delta = []
    dirs = [d for d in os.listdir(dirs_path) if os.path.isdir(os.path.join(dirs_path, d))]
    for d in dirs:
        data = read_training_data(dirs_path + d + str('/') + pose + str('/') + d + str('_') + pose)
        if d == dirs[0]:
            x_train_L = np.array(data["x_train_L"])
            y_train_L = np.array(data["y_train_L"])
            x_train_R = np.array(data["x_train_R"])
            y_train_R = np.array(data["y_train_R"])
            feature_point_R = np.array(data["feature_point_R"])
            feature_point_L = np.array(data["feature_point_L"])
            v_delta = np.array(data["v_delta"])
            h_delta = np.array(data["h_delta"])
        else:
            x_train_L = np.vstack((x_train_L, np.array(data["x_train_L"])))
            y_train_L = np.vstack((y_train_L, np.array(data["y_train_L"])))
            x_train_R = np.vstack((x_train_L, np.array(data["x_train_R"])))
            y_train_R = np.vstack((y_train_L, np.array(data["y_train_R"])))
            feature_point_R = np.vstack((feature_point_R, np.array(data["feature_point_R"])))
            feature_point_L = np.vstack((feature_point_L, np.array(data["feature_point_L"])))
            v_delta = np.hstack((v_delta, np.array(data["v_delta"])))
            h_delta = np.hstack((h_delta, np.array(data["h_delta"])))
      
        angle_dif = np.hstack((v_delta.reshape(-1,1), h_delta.reshape(-1,1)))
    return x_train_L/255, y_train_L/255, x_train_R/255, y_train_R/255, feature_point_R/1.0, feature_point_L/1.0, angle_dif/1.0

def input2data(predictor_path, faces_folder_path):
    # usage
    # R_img, L_img, R_feature_point_layer, L_feature_point_layer = input2data("sp_full_ver.dat","./0001_2m_0P_0V_0H.jpg")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)
    right_eye_index = [0, 1, 6, 7, 8, 9, 10]
    left_eye_index = [11, 12, 13, 2, 3, 4, 5]
    grace_ratio = 1.5
    feature_point_num = 7
    #for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
    print("Processing file: {}".format(faces_folder_path))
    img = io.imread(faces_folder_path)
    dets = detector(img, 1)
    print("Number of faces detected: {}".format(len(dets)))
    for k, d in enumerate(dets):
        shape = predictor(img, d)
        right_eye_coord_global = np.zeros((feature_point_num,2))
        left_eye_coord_global = np.zeros((feature_point_num,2))
        right_eye_coord_local = np.zeros((feature_point_num,2))
        left_eye_coord_local = np.zeros((feature_point_num,2))
        for i in range (0, len (right_eye_index) ):
            #print("0,"+ str(i) + "," + str(shape.part(right_eye_index[i]).x) + "," + str(shape.part(right_eye_index[i]).y))
            right_eye_coord_global[i][0] = shape.part(right_eye_index[i]).x
            right_eye_coord_global[i][1] = shape.part(right_eye_index[i]).y
        for i in range (0, len(left_eye_index) ):
            #print("1,"+ str(i) + "," + str(shape.part(left_eye_index[i]).x) + "," + str(shape.part(left_eye_index[i]).y))
            left_eye_coord_global[i][0] = shape.part(left_eye_index[i]).x
            left_eye_coord_global[i][1] = shape.part(left_eye_index[i]).y
        grace_width = 5
        grace_height = 4
        R_xmin = right_eye_coord_global[0,0]
        R_xmax = right_eye_coord_global[3,0]
        R_ymin = right_eye_coord_global[0,1]
        R_ymax = right_eye_coord_global[3,1]
        #CR = int(math.sqrt((R_xmax-R_xmin)*(R_ymax-R_ymin))+.5)
        #R_CRd5= int(grace_ratio*CR)
        #R_CRd4= int(grace_ratio*CR*0.8 + 0.5)
        R_Xcen = int((R_xmax+R_xmin)/2 + 0.5)
        R_Ycen = int((R_ymax+R_ymin)/2 + 0.5)
        R_width = int((R_xmax - R_xmin)/2) + grace_width
        R_height = int(0.8 * R_width + 0.5) + grace_height

        R_new_origin_x = R_Xcen-R_width
        R_new_origin_y = R_Ycen-R_height
        R_img = img[(R_Ycen-R_height):(R_Ycen+R_height),(R_Xcen-R_width):(R_Xcen+R_width)]
        R_img = resize(R_img,(41,51), mode='reflect')
        #text_file = open("test_R.txt", "w")
        for i in range(0,feature_point_num):
            right_eye_coord_local[i,0] = int( (right_eye_coord_global[i,0] - R_new_origin_x) * 50 / (2 * R_width) )
            right_eye_coord_local[i,1] = int( (right_eye_coord_global[i,1] - R_new_origin_y) * 40 / (2 * R_height) )
            #text_file.write("%d,%d\n" % (right_eye_coord_local[i,0], right_eye_coord_local[i,1]))
        #text_file.close()
        L_xmin = left_eye_coord_global[3,0]
        L_xmax = left_eye_coord_global[0,0]
        L_ymin = left_eye_coord_global[3,1]
        L_ymax = left_eye_coord_global[0,1]
        #CR = int(math.sqrt((R_xmax-R_xmin)*(R_ymax-R_ymin))+.5)
        #L_CRd5 = int(grace_ratio*CR)
        #L_CRd4 = int(grace_ratio*CR*0.8 + 0.5)
        L_Xcen = int((L_xmax+L_xmin)/2 + 0.5)
        L_Ycen = int((L_ymax+L_ymin)/2 + 0.5)
        L_width = int((L_xmax - L_xmin)/2 + 0.5) + grace_width
        L_height = int(0.8 * L_width + 0.5) + grace_height

        L_new_origin_x = L_Xcen-L_width
        L_new_origin_y = L_Ycen-L_height
        L_img = img[(L_Ycen-L_height):(L_Ycen+L_height),(L_Xcen-L_width):(L_Xcen+L_width)]
        L_img = resize(L_img,(41,51), mode='reflect')
        #print(L_img.shape)
        #text_file = open("test_L.txt", "w")
        for i in range(0,feature_point_num):
            left_eye_coord_local[i,0] = int( (left_eye_coord_global[i,0] - L_new_origin_x) * 50 / (2 * L_width) )
            left_eye_coord_local[i,1] = int( (left_eye_coord_global[i,1] - L_new_origin_y) * 40 / (2 * L_height) )
            #text_file.write("%d,%d\n" % (left_eye_coord_local[i,0], left_eye_coord_local[i,1]))
        #text_file.close()
        L_feature_point_layer = np.zeros((41,51,feature_point_num*2),"int8")
        R_feature_point_layer = np.zeros((41,51,feature_point_num*2),"int8")
        #print(right_eye_coord_local)
        #print(left_eye_coord_local)
        for i in range(0,feature_point_num):
            # x_distance
            for j in range (0,51):
                L_feature_point_layer[:,j,i*2] = j - left_eye_coord_local[i,0]
                R_feature_point_layer[:,j,i*2] = j - right_eye_coord_local[i,0]
            # y_distance
            for j in range (0,41):
                L_feature_point_layer[j,:,i*2+1] = j - left_eye_coord_local[i,1]
                R_feature_point_layer[j,:,i*2+1] = j - right_eye_coord_local[i,1]

        # we only proccess first detected face in the image
        break
    return R_Xcen, R_Ycen, R_width, R_height, L_Xcen, L_Ycen, L_width, L_height, R_img, L_img, R_feature_point_layer, L_feature_point_layer

