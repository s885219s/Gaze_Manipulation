import tensorflow as tf

def repeat(x, num_repeats):
    ones = tf.ones((1, num_repeats), dtype='int32')
    x = tf.reshape(x, shape=(-1,1))
    x = tf.matmul(x, ones)
    return tf.reshape(x, [-1])

def interpolate(image, x, y, output_size):
    batch_size = tf.shape(image)[0]
    height = tf.shape(image)[1]
    width = tf.shape(image)[2]
    num_channels = tf.shape(image)[3]

    x = tf.cast(x , dtype='float32')
    y = tf.cast(y , dtype='float32')

    height_float = tf.cast(height, dtype='float32')
    width_float = tf.cast(width, dtype='float32')

    output_height = output_size[0]
    output_width  = output_size[1]

    x = .5*(x + 1.0)*(width_float)
    y = .5*(y + 1.0)*(height_float)

    x0 = tf.cast(tf.floor(x), 'int32')
    x1 = x0 + 1
    y0 = tf.cast(tf.floor(y), 'int32')
    y1 = y0 + 1

    max_y = tf.cast(height - 1, dtype='int32')
    max_x = tf.cast(width - 1,  dtype='int32')
    zero = tf.zeros([], dtype='int32')

    x0 = tf.clip_by_value(x0, zero, max_x)
    x1 = tf.clip_by_value(x1, zero, max_x)
    y0 = tf.clip_by_value(y0, zero, max_y)
    y1 = tf.clip_by_value(y1, zero, max_y)

    flat_image_dimensions = width*height
    pixels_batch = tf.range(batch_size)*flat_image_dimensions
    flat_output_dimensions = output_height*output_width
    base = repeat(pixels_batch, flat_output_dimensions)
    base_y0 = base + y0*width
    base_y1 = base + y1*width
    indices_a = base_y0 + x0
    indices_b = base_y1 + x0
    indices_c = base_y0 + x1
    indices_d = base_y1 + x1

    flat_image = tf.reshape(image, shape=(-1, num_channels))
    flat_image = tf.cast(flat_image, dtype='float32')
    pixel_values_a = tf.gather(flat_image, indices_a)
    pixel_values_b = tf.gather(flat_image, indices_b)
    pixel_values_c = tf.gather(flat_image, indices_c)
    pixel_values_d = tf.gather(flat_image, indices_d)

    x0 = tf.cast(x0, 'float32')
    x1 = tf.cast(x1, 'float32')
    y0 = tf.cast(y0, 'float32')
    y1 = tf.cast(y1, 'float32')

    area_a = tf.expand_dims(((x1 - x) * (y1 - y)), 1)
    area_b = tf.expand_dims(((x1 - x) * (y - y0)), 1)
    area_c = tf.expand_dims(((x - x0) * (y1 - y)), 1)
    area_d = tf.expand_dims(((x - x0) * (y - y0)), 1)
    output = tf.add_n([area_a*pixel_values_a,
                       area_b*pixel_values_b,
                       area_c*pixel_values_c,
                       area_d*pixel_values_d])
    return output

def meshgrid(height, width):
    x_linspace = tf.linspace(-1., 1., width)
    y_linspace = tf.linspace(-1., 1., height)
    x_coordinates, y_coordinates = tf.meshgrid(x_linspace, y_linspace)
    x_coordinates = tf.reshape(x_coordinates, [-1])
    y_coordinates = tf.reshape(y_coordinates, [-1])
    indices_grid = tf.concat([x_coordinates, y_coordinates], 0)
    return indices_grid

def apply_transformation(flows, input_shape):
    batch_size = tf.shape(input_shape)[0]
    height = tf.shape(input_shape)[1]
    width = tf.shape(input_shape)[2]
    num_channels = tf.shape(input_shape)[3]
    output_size = (height, width)

    # affine_transformation = tf.reshape(affine_transformation, shape=(batch_size,2,3))
    flows = tf.transpose(flows, [0, 3, 1, 2])
    flows = tf.reshape(flows, shape=(batch_size,2,-1))

    flows = tf.cast(flows, 'float32')

    width = tf.cast(width, dtype='float32')
    height = tf.cast(height, dtype='float32')
    output_height = output_size[0]
    output_width = output_size[1]
    indices_grid = meshgrid(output_height, output_width)

    indices_grid = tf.tile(indices_grid, tf.stack([batch_size]))
    # indices_grid = tf.reshape(indices_grid, (batch_size, 3, -1))
    indices_grid = tf.reshape(indices_grid, (batch_size, 2, -1))

    # transformed_grid = tf.matmul(affine_transformation, indices_grid)
    transformed_grid = tf.add(flows, indices_grid)
    x_s = tf.slice(transformed_grid, [0, 0, 0], [-1, 1, -1])
    y_s = tf.slice(transformed_grid, [0, 1, 0], [-1, 1, -1])
    x_s_flatten = tf.reshape(x_s, [-1])
    y_s_flatten = tf.reshape(y_s, [-1])

    transformed_image = interpolate(input_shape,
                                            x_s_flatten,
                                            y_s_flatten,
                                            output_size)

    transformed_image = tf.reshape(transformed_image, shape=(batch_size,
                                                            output_height,
                                                            output_width,
                                                            num_channels))
    return transformed_image

def trans_angle(inputs, height, width):
    batch_size = tf.shape(inputs)[0]
    feature_dims = tf.shape(inputs)[1]
    data = tf.transpose(inputs, perm=[1,0]) 
    data = tf.tile(data,tf.constant([height*width,1]))
    data = tf.transpose(data, perm=[1,0]) 
    ret = tf.reshape(data, [batch_size,height,width,feature_dims])
    return ret

def spatial_softmax_across_pixels(inputs):
    inputs = tf.cast(inputs, dtype = tf.float32)
    batch_size = tf.shape(inputs)[0]
    height = tf.shape(inputs)[1]
    width = tf.shape(inputs)[2]
    channels = tf.shape(inputs)[3]
    inputs = tf.reshape(tf.transpose(inputs, [0, 3, 1, 2]), [batch_size * channels, height * width])
    softmax_inputs = tf.nn.softmax(inputs)
    ret = tf.transpose(tf.reshape(softmax_inputs, [batch_size, channels, height, width]), [0, 2, 3, 1])
    return ret

def spatial_softmax_across_channels(inputs):
    inputs = tf.cast(inputs, dtype = tf.float32)
    batch_size = tf.shape(inputs)[0]
    height = tf.shape(inputs)[1]
    width = tf.shape(inputs)[2]
    channels = tf.shape(inputs)[3]
    inputs = tf.reshape(inputs, [batch_size*height*width, channels])
    softmax_inputs = tf.nn.softmax(inputs)
    ret = tf.reshape(softmax_inputs, [batch_size, height, width, channels])
    return ret

def apply_light_weight(batch_img, light_weight):
    # perfrom softmax
    light_weight = spatial_softmax_across_channels(light_weight)
    
    img_wgts, pal_wgts = tf.expand_dims(light_weight[...,0],3), tf.expand_dims(light_weight[...,1],3)
    img_wgts = tf.concat([img_wgts, img_wgts, img_wgts], axis = 3)
    pal_wgts = tf.concat([pal_wgts, pal_wgts, pal_wgts], axis = 3)
    
    palette = tf.ones(tf.shape(batch_img), dtype = tf.float32)
    
    ret = tf.add(tf.multiply(batch_img, img_wgts), tf.multiply(palette, pal_wgts))
    return ret