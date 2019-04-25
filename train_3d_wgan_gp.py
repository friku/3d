from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import utils
import traceback
import numpy as np
import tensorflow as tf
import models_64x64 as models
import time

""" param """
epoch = 100
batch_size = 64
lr = 0.0002
z_dim = 500
n_critic = 5
gpu_id = 3
sample_batch_size = 10

''' data '''
#utils.mkdir('./data/mnist/')
#data.mnist_download('./data/mnist')
#imgs, _, _ = data.mnist_load('./data/mnist')
#imgs.shape = imgs.shape + (1,)
#data_pool = utils.MemoryData({'img': imgs}, batch_size)

data = np.load("3dDataIntFake.npy")*2-1
def fn(data,batch_size):
    random = np.random.randint(0,data.shape[0],batch_size)
    sample_data = data[random]
    return sample_data


""" graphs """
with tf.device('/gpu:%d' % gpu_id):
    ''' models '''
    generator = models.generator3d
    discriminator = models.discriminator_wgan_gp_3d

    ''' graph '''
    # inputs
    real = tf.placeholder(tf.float32, shape=[None,32, 32, 32, 1])
    z = tf.placeholder(tf.float32, shape=[None, z_dim])

    # generate
    fake = generator(z, reuse=False)

    # dicriminate
    r_logit = discriminator(real, reuse=False)
    f_logit = discriminator(fake)

    # losses
    def gradient_penalty(real, fake, f):
        def interpolate(a, b):
            shape = tf.concat((tf.shape(a)[0:1], tf.tile([1], [a.shape.ndims - 1])), axis=0)
            alpha = tf.random_uniform(shape=shape, minval=0., maxval=1.)
            inter = a + alpha * (b - a)
            inter.set_shape(a.get_shape().as_list())
            return inter

        x = interpolate(real, fake)
        print(x)
        pred = f(x)
        gradients = tf.gradients(pred, x)[0]
        print(gradients)
        slopes = tf.sqrt(tf.reduce_sum(tf.square(gradients), reduction_indices=list(range(1, x.shape.ndims))))
        gp = tf.reduce_mean((slopes - 1.)**2)
        return gp

    wd = tf.reduce_mean(r_logit) - tf.reduce_mean(f_logit)
    gp = gradient_penalty(real, fake, discriminator)
    d_loss = -wd + gp * 10.0
    g_loss = -tf.reduce_mean(f_logit)

    # otpims
    d_var = utils.trainable_variables('discriminator')
    g_var = utils.trainable_variables('generator')
    d_step = tf.train.AdamOptimizer(learning_rate=lr, beta1=0.5).minimize(d_loss, var_list=d_var)
    g_step = tf.train.AdamOptimizer(learning_rate=lr, beta1=0.5).minimize(g_loss, var_list=g_var)

    # summaries
    d_summary = utils.summary({wd: 'wd', gp: 'gp'})
    g_summary = utils.summary({g_loss: 'g_loss'})

    # sample
    f_sample = generator(z, training=False)


""" train """
''' init '''
# session
sess = utils.session()
# iteration counter
it_cnt, update_cnt = utils.counter()
# saver
saver = tf.train.Saver(max_to_keep=5)
# summary writer
summary_writer = tf.summary.FileWriter('./summaries/3dganFakeSlim', sess.graph)

''' initialization '''
ckpt_dir = './checkpoints/3dganFakeSlim'
utils.mkdir(ckpt_dir + '/')
if not utils.load_checkpoint(ckpt_dir, sess):
    sess.run(tf.global_variables_initializer())

''' train '''
try:
    z_ipt_sample = np.random.normal(size=[sample_batch_size, z_dim])

    batch_epoch = 10000 // (batch_size * n_critic)
    max_it = epoch * batch_epoch
    for it in range(sess.run(it_cnt), max_it):
        start = time.time()
        sess.run(update_cnt)

        # which epoch
        epoch = it // batch_epoch
        it_epoch = it % batch_epoch + 1

        # train D
        for i in range(n_critic):
            # batch data
            real_ipt = fn(data,batch_size)
            z_ipt = np.random.normal(size=[batch_size, z_dim])
            d_summary_opt, _ = sess.run([d_summary, d_step], feed_dict={real: real_ipt, z: z_ipt})
        summary_writer.add_summary(d_summary_opt, it)

        # train G
        z_ipt = np.random.normal(size=[batch_size, z_dim])
        g_summary_opt, _ = sess.run([g_summary, g_step], feed_dict={z: z_ipt})
        summary_writer.add_summary(g_summary_opt, it)

        # display
        if it % 1 == 0:
            elapsed_time = time.time() - start
            print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
            print("Epoch: (%3d) (%5d/%5d)" % (epoch, it_epoch, batch_epoch))

        # save
        if (it + 1) % 1000 == 0:
            save_path = saver.save(sess, '%s/Epoch_(%d)_(%dof%d).ckpt' % (ckpt_dir, epoch, it_epoch, batch_epoch))
            print('Model saved in file: % s' % save_path)

        # sample
        if (it + 1) % 100 == 0:
            
            f_sample_opt = sess.run(f_sample, feed_dict={z: z_ipt_sample})
            f_sample_opt = (f_sample_opt+1)*0.5
            f_sample_opt = np.round(f_sample_opt, decimals=0)

            save_dir = './sample_images_while_training/3dganFakeSlim1'
            utils.mkdir(save_dir + '/')
            utils.saveModel(f_sample_opt,save_dir,sample_batch_size,it)

        # sample
        if (it + 1) % 1 == 0:
#            np.set_printoptions(threshold=np.inf)
#            f_sample_opt = sess.run(real, feed_dict={real: real_ipt})
#            print(f_sample_opt.shape)
#            f_sample_opt = (f_sample_opt+1)*0.5
#            f_sample_opt = np.round(f_sample_opt, decimals=0)
            output_data = np.load("3dDataIntFake.npy")
#            np.savetxt("./data.txt",output_data[0,:,:,:,0])
            save_dir = './sample_images_while_training/3dganFakeSlim1'
            utils.mkdir(save_dir + '/')
            utils.saveModel(output_data,save_dir,100,it)
            
            utils.LoadModel("/home/fujimoto/3dgan/src/sample_images_while_training/3dDataIntFake/0_0.binvox")
            break
            

except Exception:
    traceback.print_exc()
finally:
    print(" [*] Close main session!")
    sess.close()
