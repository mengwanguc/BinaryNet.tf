from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime
import math
import time
from progress.bar import Bar

import numpy as np
import tensorflow as tf
from data import get_data_provider
import time

def evaluate(model, dataset,
        batch_size=128,
        checkpoint_dir='./checkpoint'):
    with tf.Graph().as_default() as g:
        data = get_data_provider(dataset, training=False)
        with tf.device('/gpu:0'):
            x, yt = data.generate_batches(batch_size)
            is_training = tf.placeholder(tf.bool,[],name='is_training')

            # Build the Graph that computes the logits predictions
            y = model(x, is_training=False)

        # Calculate predictions.
#        loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(labels=yt, logits=y))
#        accuracy = tf.reduce_mean(tf.cast(tf.nn.in_top_k(y,yt,1), tf.float32))

        # Restore the moving average version of the learned variables for eval.
        #variable_averages = tf.train.ExponentialMovingAverage(
        #    MOVING_AVERAGE_DECAY)
        #variables_to_restore = variable_averages.variables_to_restore()
        saver = tf.train.Saver()#variables_to_restore)


        # Configure options for session
        gpu_options = tf.GPUOptions(allow_growth=True)
        sess = tf.Session(
                config=tf.ConfigProto(
                            log_device_placement=False,
                            allow_soft_placement=True,
                            gpu_options=gpu_options,
                            )
                        )
        ckpt = tf.train.get_checkpoint_state(checkpoint_dir+'/')
        if ckpt and ckpt.model_checkpoint_path:
        # Restores from checkpoint
            saver.restore(sess, ckpt.model_checkpoint_path)
        else:
            print('No checkpoint file found')
            return

         # Start the queue runners.
        coord = tf.train.Coordinator()
        try:
            threads = []
            for qr in tf.get_collection(tf.GraphKeys.QUEUE_RUNNERS):
             threads.extend(qr.create_threads(sess, coord=coord, daemon=True,
                                       start=True))

            num_batches = int(math.ceil(data.size[0] / batch_size))
            total_acc = 0  # Counts the number of correct predictions per batch.
            total_loss = 0 # Sum the loss of predictions per batch.
            step = 0
            bar = Bar('Evaluating', max=num_batches,suffix='%(percent)d%% eta: %(eta)ds')
            begin_time = time.time()
            while step < num_batches and not coord.should_stop():
         #     acc_val, loss_val = sess.run([accuracy, loss])
              pred = sess.run([y])
         #     total_acc += acc_val
         #     total_loss += loss_val
              step += 1
              bar.next()
            bar.finish()

            end_time = time.time()

            # Compute precision and loss
          #  total_acc /= num_batches
          #  total_loss /= num_batches
            total_time = end_time - begin_time
            avg_time = total_time / num_batches
#            print('Test num: %d  Accuracy: %.3f  Loss: %.3f  Total Time: %.3f  avg time: %.3f' %
#                  (num_batches, total_acc, total_loss, total_time, avg_time))
            print('Test num: %d  Total Time: %.3f  avg time: %.3f' %
                  (num_batches, total_time, avg_time))



        except Exception as e:  # pylint: disable=broad-except
            coord.request_stop(e)

        coord.request_stop()
        coord.join(threads)
        return pred

def main(argv=None):  # pylint: disable=unused-argument
  evaluate()


if __name__ == '__main__':
  FLAGS = tf.app.flags.FLAGS
  tf.app.flags.DEFINE_string('checkpoint_dir', './results/model',
                             """Directory where to read model checkpoints.""")
  tf.app.flags.DEFINE_string('dataset', 'cifar10',
                             """Name of dataset used.""")
  tf.app.flags.DEFINE_string('model_name', 'model',
                             """Name of loaded model.""")

  FLAGS.log_dir = FLAGS.checkpoint_dir+'/log/'
      # Build the summary operation based on the TF collection of Summaries.
      # summary_op = tf.merge_all_summaries()

      # summary_writer = tf.train.SummaryWriter(log_dir)
          # summary = tf.Summary()
          # summary.ParseFromString(sess.run(summary_op))
          # summary.value.add(tag='accuracy/test', simple_value=precision)
          # summary_writer.add_summary(summary, global_step)

  tf.app.run()
