# coding=utf-8
# Copyright 2020 The TensorFlow Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""Corrupted MNIST Dataset.

MNISTCorrupted is a dataset generated by adding 15 corruptions to the test
images in the MNIST dataset. This dataset wraps the static, corrupted MNIST
test images uploaded by the original authors.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import numpy as np
import tensorflow.compat.v2 as tf
from tensorflow_datasets.image_classification import mnist
import tensorflow_datasets.public_api as tfds

_DESCRIPTION = """\
MNISTCorrupted is a dataset generated by adding 15 corruptions to the test
images in the MNIST dataset. This dataset wraps the static, corrupted MNIST
test images uploaded by the original authors
"""

_CITATION = """
@article{mu2019mnist,
  title={MNIST-C: A Robustness Benchmark for Computer Vision},
  author={Mu, Norman and Gilmer, Justin},
  journal={arXiv preprint arXiv:1906.02337},
  year={2019}
}
"""

_DOWNLOAD_URL = 'https://zenodo.org/record/3239543/files/mnist_c.zip'
_CORRUPTIONS = [
    'identity',
    'shot_noise',
    'impulse_noise',
    'glass_blur',
    'motion_blur',
    'shear',
    'scale',
    'rotate',
    'brightness',
    'translate',
    'stripe',
    'fog',
    'spatter',
    'dotted_line',
    'zigzag',
    'canny_edges',
]
_DIRNAME = 'mnist_c'
_TRAIN_IMAGES_FILENAME = 'train_images.npy'
_TEST_IMAGES_FILENAME = 'test_images.npy'
_TRAIN_LABELS_FILENAME = 'train_labels.npy'
_TEST_LABELS_FILENAME = 'test_labels.npy'


class MNISTCorruptedConfig(tfds.core.BuilderConfig):
  """BuilderConfig for MNISTcorrupted."""

  @tfds.core.disallow_positional_args
  def __init__(self, corruption_type, **kwargs):
    """Constructor.

    Args:
      corruption_type: string, name of corruption from _CORRUPTIONS.
      **kwargs: keyword arguments forwarded to super.
    """
    super(MNISTCorruptedConfig, self).__init__(**kwargs)
    self.corruption = corruption_type


def _make_builder_configs():
  """Construct a list of BuilderConfigs.

  Construct a list of 15 MNISTCorruptedConfig objects, corresponding to
  the 15 corruption types.

  Returns:
    A list of 15 MNISTCorruptedConfig objects.
  """
  config_list = []
  for corruption in _CORRUPTIONS:
    config_list.append(
        MNISTCorruptedConfig(
            name=corruption,
            version=tfds.core.Version(
                '1.0.0',
                'New split API (https://tensorflow.org/datasets/splits)'),
            description='Corruption method: ' + corruption,
            corruption_type=corruption,
        ))
  return config_list


class MNISTCorrupted(tfds.core.GeneratorBasedBuilder):
  """Corrupted MNIST dataset."""
  BUILDER_CONFIGS = _make_builder_configs()

  def _info(self):
    """Returns basic information of dataset.

    Returns:
      tfds.core.DatasetInfo.
    """
    return tfds.core.DatasetInfo(
        builder=self,
        description=_DESCRIPTION,
        features=tfds.features.FeaturesDict({
            'image':
                tfds.features.Image(shape=mnist.MNIST_IMAGE_SHAPE),
            'label':
                tfds.features.ClassLabel(num_classes=mnist.MNIST_NUM_CLASSES),
        }),
        supervised_keys=('image', 'label'),
        homepage='https://github.com/google-research/mnist-c',
        citation=_CITATION)

  def _split_generators(self, dl_manager):
    """Return the train, test split of MNIST-C.

    Args:
      dl_manager: download manager object.

    Returns:
      train split, test split.
    """
    path = dl_manager.download_and_extract(_DOWNLOAD_URL)
    return [
        tfds.core.SplitGenerator(
            name=tfds.Split.TRAIN,
            gen_kwargs={
                'data_dir': os.path.join(path, _DIRNAME),
                'is_train': True
            }),
        tfds.core.SplitGenerator(
            name=tfds.Split.TEST,
            gen_kwargs={
                'data_dir': os.path.join(path, _DIRNAME),
                'is_train': False
            }),
    ]

  def _generate_examples(self, data_dir, is_train):
    """Generate corrupted MNIST data.

    Apply corruptions to the raw images according to self.corruption_type.

    Args:
      data_dir: root directory of downloaded dataset
      is_train: whether to return train images or test images

    Yields:
      dictionary with image file and label.
    """
    corruption = self.builder_config.corruption

    if is_train:
      images_file = os.path.join(data_dir, corruption, _TRAIN_IMAGES_FILENAME)
      labels_file = os.path.join(data_dir, corruption, _TRAIN_LABELS_FILENAME)
    else:
      images_file = os.path.join(data_dir, corruption, _TEST_IMAGES_FILENAME)
      labels_file = os.path.join(data_dir, corruption, _TEST_LABELS_FILENAME)

    with tf.io.gfile.GFile(labels_file, mode='rb') as f:
      labels = np.load(f)

    with tf.io.gfile.GFile(images_file, mode='rb') as f:
      images = np.load(f)

    for i, (image, label) in enumerate(zip(images, labels)):
      yield i, {
          'image': image,
          'label': label,
      }
