# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""
create train or eval dataset.
"""
import os
import numpy as np

from mindspore import Tensor
from mindspore.train.model import Model
import mindspore.common.dtype as mstype
import mindspore.dataset.engine as de
import mindspore.dataset.vision.c_transforms as C
import mindspore.dataset.transforms.c_transforms as C2
import mindspore.dataset.transforms.py_transforms as P  # 使用 transforms.py_transforms

# 定义高斯噪声函数
def add_gaussian_noise(image):
    """
    Add Gaussian noise to an image.
    
    Args:
        image (numpy.ndarray): Input image in HWC format (uint8).
    
    Returns:
        numpy.ndarray: Image with Gaussian noise (uint8).
    """
    std = 5.0  # 噪声标准差，可调整
    noise = np.random.normal(0, std, image.shape).astype(np.float32)
    noisy_image = image.astype(np.float32) + noise
    return np.clip(noisy_image, 0, 255).astype(np.uint8)

# 使用 Compose 包装高斯噪声函数
gaussian_noise_op = P.Compose([add_gaussian_noise])

def create_dataset(dataset_path, do_train, config, repeat_num=5):
    """
    创建训练或评估数据集

    Args:
        dataset_path(string): 数据集路径
        do_train(bool): 是否用于训练
        config(struct): 不同平台的训练和评估配置
        repeat_num(int): 数据集重复次数，默认为1

    Returns:
        dataset
    """
    data_dir = os.path.join(dataset_path, "train" if do_train else "test")
    
    if not os.path.exists(data_dir):
        raise ValueError(f"数据集目录不存在: {data_dir}")

    # 根据平台配置创建数据集
    if config.platform == "Ascend":
        rank_size = int(os.getenv("RANK_SIZE", '1'))
        rank_id = int(os.getenv("RANK_ID", '0'))
        if rank_size == 1:
            ds = de.ImageFolderDataset(data_dir, num_parallel_workers=8, shuffle=do_train)
        else:
            ds = de.ImageFolderDataset(data_dir, num_parallel_workers=8, shuffle=do_train,
                                     num_shards=rank_size, shard_id=rank_id)
    elif config.platform == "GPU":
        if do_train and config.run_distribute:
            from mindspore.communication.management import get_rank, get_group_size
            ds = de.ImageFolderDataset(data_dir, num_parallel_workers=8, shuffle=do_train,
                                     num_shards=get_group_size(), shard_id=get_rank())
        else:
            ds = de.ImageFolderDataset(data_dir, num_parallel_workers=8, shuffle=do_train)
    else:  # CPU
        ds = de.ImageFolderDataset(data_dir, num_parallel_workers=8, shuffle=do_train)

    resize_height = config.image_height
    resize_width = config.image_width
    buffer_size = 1000

    # define map operations
    decode_op = C.Decode()
    resize_crop_op = C.RandomCropDecodeResize(resize_height, scale=(0.08, 1.0), ratio=(0.75, 1.333))
    horizontal_flip_op = C.RandomHorizontalFlip(prob=0.5)
    resize_op = C.Resize((256, 256))
    center_crop = C.CenterCrop(resize_width)
    rescale_op = C.RandomColorAdjust(brightness=0.4, contrast=0.4, saturation=0.4)
    normalize_op = C.Normalize(mean=[0.485 * 255, 0.456 * 255, 0.406 * 255],
                               std=[0.229 * 255, 0.224 * 255, 0.225 * 255])
    change_swap_op = C.HWC2CHW()

    if do_train:
        trans = [resize_crop_op, horizontal_flip_op, rescale_op, normalize_op, change_swap_op]
    else:
        trans = [decode_op, resize_op, center_crop, normalize_op, change_swap_op]

    type_cast_op = C2.TypeCast(mstype.int32)

    # 应用 c_transforms
    ds = ds.map(operations=trans, input_columns="image", num_parallel_workers=8)
    # 仅在训练时应用高斯噪声
    if do_train:
        ds = ds.map(operations=[gaussian_noise_op], input_columns="image", num_parallel_workers=8)
    ds = ds.map(operations=type_cast_op, input_columns="label", num_parallel_workers=8)

    # apply shuffle operations
    ds = ds.shuffle(buffer_size=buffer_size)

    # apply batch operations
    ds = ds.batch(config.batch_size, drop_remainder=True)

    # apply dataset repeat operation
    ds = ds.repeat(repeat_num)

    return ds


def extract_features(net, dataset_path, config):
    features_folder = os.path.abspath(dataset_path) + '_features'
    if not os.path.exists(features_folder):
        os.makedirs(features_folder)
    dataset = create_dataset(dataset_path=dataset_path,
                             do_train=False,
                             config=config)
    step_size = dataset.get_dataset_size()
    if step_size == 0:
        raise ValueError("The step_size of dataset is zero. Check if the images count of train dataset is more \
            than batch_size in config.py")

    model = Model(net)

    for i, data in enumerate(dataset.create_dict_iterator(output_numpy=True)):
        features_path = os.path.join(features_folder, f"feature_{i}.npy")
        label_path = os.path.join(features_folder, f"label_{i}.npy")
        if not os.path.exists(features_path) or not os.path.exists(label_path):
            image = data["image"]
            label = data["label"]
            features = model.predict(Tensor(image))
            np.save(features_path, features.asnumpy())
            np.save(label_path, label)
        print(f"Complete the batch {i+1}/{step_size}")
    return step_size