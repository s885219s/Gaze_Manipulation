class model_config(object):
    def __init__(self):
        self.height = 41
        self.width = 51
        self.channel = 3
        self.ef_dim = 14
        self.agl_dim = 2
        self.encoded_agl_dim = 16

def get_config():
    config = model_config()
    return config
    
def create_model(input_img, input_agl, input_ef, conf, cfw_only = False):    
    from keras.models import Model
    from keras.layers import Lambda, Dense, Conv2D, Activation, BatchNormalization, concatenate, add
    from keras.layers.advanced_activations import LeakyReLU
    import tensorflow as tf
    from transformation import apply_transformation, trans_angle, apply_light_weight
    '''inputes'''
    agl_encode = Dense(16)(input_agl)
    agl_encode = Activation('relu')(agl_encode)

    agl_encode = Dense(16)(agl_encode)
    agl_encode = Activation('relu')(agl_encode)

    encoded_agl = Lambda(lambda x: trans_angle(x, conf.height, conf.width),output_shape=(conf.height, conf.width, conf.encoded_agl_dim), name = 'encoded_agl')(agl_encode)

    '''Coarse warping.'''
    input_datas = concatenate([input_img, input_ef, encoded_agl], axis = 3, name = 'input_datas')

    locnet = Lambda(lambda image: tf.image.resize_images(image, (int(conf.height/2+0.5), int(conf.width/2 + 0.5))))(input_datas)

    locnet = Conv2D(16, (5, 5),padding='same')(locnet)
    locnet = BatchNormalization()(locnet)
    locnet = Activation('relu')(locnet)

    locnet = Conv2D(32, (3, 3),padding='same')(locnet)
    locnet = BatchNormalization()(locnet)
    locnet = Activation('relu')(locnet)

    locnet = Conv2D(32, (3, 3),padding='same')(locnet)
    locnet = BatchNormalization()(locnet)
    light_feature_1 = Activation('relu', name = 'light_feature_1')(locnet)

    locnet = Conv2D(32, (1, 1),padding='same')(light_feature_1)
    locnet = BatchNormalization()(locnet)
    locnet = Activation('relu')(locnet)

    locnet = Conv2D(2, (1, 1),padding='same')(locnet)
    locnet = Activation('tanh')(locnet)

    D_c_flow = Lambda(lambda image: tf.image.resize_images(image, (conf.height, conf.width)),output_shape=(conf.height, conf.width, 2), name = 'D_c_flow')(locnet)

    D_c_img = Lambda(lambda x: apply_transformation(flows = x[0], input_shape = x[1]),output_shape = (conf.height, conf.width, conf.channel), name = 'D_c_img')([D_c_flow, input_img])

    '''Fine warping'''
    D_fin_input = concatenate([input_datas, D_c_img, D_c_flow], axis = 3, name = 'D_fin_input')

    locnet2 = Conv2D(16, (5, 5),padding='same')(D_fin_input)
    locnet2 = BatchNormalization()(locnet2)
    locnet2 = Activation('relu')(locnet2)
    # locnet2 = LeakyReLU(alpha=0.02)(locnet2)
    
    locnet2 = Conv2D(32, (3, 3),padding='same')(locnet2)
    locnet2 = BatchNormalization()(locnet2)
    locnet2 = Activation('relu')(locnet2)

    locnet2 = Conv2D(32, (3, 3),padding='same')(locnet2)
    locnet2 = BatchNormalization()(locnet2)
    light_feature_2 = Activation('relu', name = 'light_feature_2')(locnet2)
    # light_feature_2 = LeakyReLU(alpha=0.02, name = 'light_feature_2')(locnet2)

    locnet2 = Conv2D(32, (1, 1),padding='same')(light_feature_2)
    locnet2 = BatchNormalization()(locnet2)
    locnet2 = Activation('relu')(locnet2)

    locnet2 = Conv2D(2, (1, 1),padding='same')(locnet2)
    D_r_flow = Activation('tanh', name = 'D_r_flow')(locnet2)

    D = add([D_c_flow, D_r_flow], name = 'D')

    cfw_img = Lambda(lambda x: apply_transformation(flows = x[0], input_shape = x[1]),output_shape=(conf.height, conf.width, conf.channel), name = 'cfw_img')([D, input_img])

    if(cfw_only):
        model = Model(inputs = [input_ef, input_agl, input_img], outputs=[cfw_img])
        return model
    
    '''lcm'''
    light_feature_1_res = Lambda(lambda image: tf.image.resize_images(image, size=(conf.height, conf.width)),output_shape=(conf.height, conf.width, 32))(light_feature_1)

    light_feature_input = concatenate([light_feature_1_res, light_feature_2], axis = 3, name = 'light_feature_input')
    
    # locnet3 = Conv2D(8, (1, 1),padding='same', use_bias=False)(light_feature_2)
    locnet3 = Conv2D(8, (1, 1),padding='same')(light_feature_input)
    locnet3 = BatchNormalization()(locnet3)
    locnet3 = Activation('relu')(locnet3)

    locnet3 = Conv2D(8, (1, 1),padding='same')(locnet3)
    locnet3 = BatchNormalization()(locnet3)
    locnet3 = Activation('relu')(locnet3)

    locnet3 = Conv2D(2, (3, 3),padding='same')(locnet3)

    res_img = Lambda(lambda x: apply_light_weight(batch_img=x[0], light_weight=x[1]), output_shape=(conf.height, conf.width, conf.channel), name = 'res_img')([cfw_img, locnet3])
    
    model = Model(inputs = [input_ef, input_agl, input_img], outputs=[res_img])
    return model