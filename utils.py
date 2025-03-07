import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

def conv_layer_2d(x, filter_shape, stride, trainable=True):
    W = tf.get_variable(
        name='weight',
        shape=filter_shape,
        dtype=tf.float32,
        initializer=tf.contrib.layers.xavier_initializer(),
        trainable=trainable)
    b = tf.get_variable(
        name='bias',
        shape=[filter_shape[-1]],
        dtype=tf.float32,
        initializer=tf.contrib.layers.xavier_initializer(),
        trainable=trainable)
    x = tf.nn.bias_add(tf.nn.conv2d(
        input=x,
        filter=W,
        strides=[1, stride, stride, 1],
        padding='SAME'), b)

    return x

def deconv_layer_2d(x, filter_shape, output_shape, stride, trainable=True):
    x = tf.pad(x, [[0,0], [3,3], [3,3], [0,0]], mode='reflect')
    W = tf.get_variable(
        name='weight',
        shape=filter_shape,
        dtype=tf.float32,
        initializer=tf.contrib.layers.xavier_initializer(),
        trainable=trainable)
    b = tf.get_variable(
        name='bias',
        shape=[output_shape[-1]],
        dtype=tf.float32,
        initializer=tf.contrib.layers.xavier_initializer(),
        trainable=trainable)
    x = tf. nn.bias_add(tf.nn.conv2d_transpose(
        value=x,
        filter=W,
        output_shape=output_shape,
        strides=[1, stride, stride, 1],
        padding='SAME'), b)

    return x[:, 3:-3, 3:-3, :]

def deconv_layer_2d1(x, filter_shape, output_shape, stride, trainable=True):
    x = tf.pad(x, [[0,0], [3,3], [3,3], [0,0]], mode='reflect')
    W = tf.get_variable(
        name='weight',
        shape=filter_shape,
        dtype=tf.float32,
        initializer=tf.contrib.layers.xavier_initializer(),
        trainable=trainable)
    b = tf.get_variable(
        name='bias',
        shape=[output_shape[-1]],
        dtype=tf.float32,
        initializer=tf.contrib.layers.xavier_initializer(),
        trainable=trainable)
    x = tf. nn.bias_add(tf.nn.conv2d_transpose(
        value=x,
        filter=W,
        output_shape=output_shape,
        strides=[1, stride, stride, 1],
        padding='SAME'), b)

    return x[:, 3:-3, 3:-3, :]

def deconv_layer_2d2(x, filter_shape, output_shape, stride, trainable=True):
    x = tf.pad(x, [[0,0], [5,5], [5,5], [0,0]], mode='reflect')
    W = tf.get_variable(
        name='weight',
        shape=filter_shape,
        dtype=tf.float32,
        initializer=tf.contrib.layers.xavier_initializer(),
        trainable=trainable)
    b = tf.get_variable(
        name='bias',
        shape=[output_shape[-1]],
        dtype=tf.float32,
        initializer=tf.contrib.layers.xavier_initializer(),
        trainable=trainable)
    x = tf. nn.bias_add(tf.nn.conv2d_transpose(
        value=x,
        filter=W,
        output_shape=output_shape,
        strides=[1, stride, stride, 1],
        padding='SAME'), b)

    return x[:, 5:-5, 5:-5, :]

def flatten_layer(x):
    input_shape = x.get_shape().as_list()
    dim = input_shape[1] * input_shape[2] * input_shape[3]
    transposed = tf.transpose(x, (0, 3, 1, 2))
    x = tf.reshape(transposed, [-1, dim])

    return x

def dense_layer(x, out_dim, trainable=True):
    in_dim = x.get_shape().as_list()[-1]
    W = tf.get_variable(
        name='weight',
        shape=[in_dim, out_dim],
        dtype=tf.float32,
        initializer=tf.truncated_normal_initializer(stddev=0.02),
        trainable=trainable)
    b = tf.get_variable(
        name='bias',
        shape=[out_dim],
        dtype=tf.float32,
        initializer=tf.constant_initializer(0.0),
        trainable=trainable)
    x = tf.add(tf.matmul(x, W), b)

    return x

def pixel_shuffle_layer(x, r, n_split):
    def PS(x, r):
        N, h, w = tf.shape(x)[0], tf.shape(x)[1], tf.shape(x)[2]
        x = tf.reshape(x, (N, h, w, r, r))
        x = tf.transpose(x, (0, 1, 2, 4, 3))
        x = tf.split(x, h, 1)
        x = tf.concat([tf.squeeze(x_) for x_ in x], 2)
        x = tf.split(x, w, 1)
        x = tf.concat([tf.squeeze(x_) for x_ in x], 2)
        x = tf.reshape(x, (N, h*r, w*r, 1))

    xc = tf.split(x, n_split, 3)
    x = tf.concat([PS(x_, r) for x_ in xc], 3)

    return x

def plot_SR_data(idx, LR, SR, path):

    for i in range(LR.shape[0]):
        vmin0, vmax0 = np.min(SR[i,:,:,0]), np.max(SR[i,:,:,0])
        vmin1, vmax1 = np.min(SR[i,:,:,1]), np.max(SR[i,:,:,1])

        plt.figure(figsize=(12, 12))
        
        plt.subplot(121)
        plt.imshow(LR[i, :, :, 0], vmin=37.042, vmax=83.1, cmap='jet', origin='lower')
        plt.title('LR u Input', fontsize=11)
        #plt.colorbar()
        plt.xticks([], [])
        plt.yticks([], [])
        
        
        ax = plt.subplot(122)
        plt.imshow(SR[i, :, :, 0], vmin=37.042, vmax=83.1, cmap='jet', origin='lower')
        plt.title('MR u Output', fontsize=11)
        #plt.colorbar()
        plt.xticks([], [])
        plt.yticks([], [])   
    

        plt.savefig(path+'/img{0:05d}.png'.format(idx[i]), dpi=200, bbox_inches='tight')
        plt.close()


def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def downscale_image(x, K):
    tf.reset_default_graph()

    if x.ndim == 3:
        x = x.reshape((1, x.shape[0], x.shape[1], x.shape[2]))

    x_in = tf.placeholder(tf.float64, [None, x.shape[1], x.shape[2], x.shape[3]])

    weight = tf.constant(1.0/(2*K**2), shape=[K, K, x.shape[3], x.shape[3]], dtype=tf.float64)
    downscaled = tf.nn.conv2d(x_in, filter=weight, strides=[1, K, K, 1], padding='SAME')

    with tf.Session() as sess:
        ds_out = sess.run(downscaled, feed_dict={x_in: x})

    return ds_out

def generate_TFRecords(filename, data, mode='test', K=None):
    '''
        Generate TFRecords files for model training or testing

        inputs:
            filename - filename for TFRecord (should by type *.tfrecord)
            data     - numpy array of size (N, h, w, c) containing data to be written to TFRecord
            mode    - if 'train', then data contains HR data that is coarsened k times 
                       and both HR and LR data written to TFRecord
                       if 'test', then data contains LR data 
            K        - downscaling factor, must be specified in training mode

        outputs:
            No output, but .tfrecord file written to filename
    '''
    if mode == 'train':
        assert K is not None, 'In training mode, downscaling factor K must be specified'
        data_LR = downscale_image(data, K)

    with tf.python_io.TFRecordWriter(filename) as writer:
        for j in range(data.shape[0]):
            if mode == 'train':
                h_HR, w_HR, c = data[j, ...].shape
                h_LR, w_LR, c = data_LR[j, ...].shape
                features = tf.train.Features(feature={
                                     'index': _int64_feature(j),
                                   'data_LR': _bytes_feature(data_LR[j, ...].tostring()),
                                      'h_LR': _int64_feature(h_LR),
                                      'w_LR': _int64_feature(w_LR),
                                   'data_HR': _bytes_feature(data[j, ...].tostring()),
                                      'h_HR': _int64_feature(h_HR),
                                      'w_HR': _int64_feature(w_HR),
                                         'c': _int64_feature(c)})
            elif mode == 'test':
                h_LR, w_LR, c = data[j, ...].shape
                features = tf.train.Features(feature={
                                     'index': _int64_feature(j),
                                   'data_LR': _bytes_feature(data[j, ...].tostring()),
                                      'h_LR': _int64_feature(h_LR),
                                      'w_LR': _int64_feature(w_LR),
                                         'c': _int64_feature(c)})

            example = tf.train.Example(features=features)
            writer.write(example.SerializeToString()) 
