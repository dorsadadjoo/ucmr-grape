from __future__ import division, print_function

import json
import os.path as osp

import numpy as np

from absl import app, flags
from torch.utils.data import DataLoader
import os
from . import base as base_data


def first_existing_dir(dir_list):
    for dd in dir_list:
        if osp.isdir(dd):
            return dd
    raise FileNotFoundError

def get_data_root_dir(classname):
    if classname.startswith('shoe'):
        dir_list = [
            '/home/shubham/data/zappos/',
        ]
    elif classname.startswith('tv'):
        dir_list = [
            '/home/shubham/data/tv/',
        ]
    elif classname.startswith('grape'):
        #change made by dorsa:
        current_dir = os.getcwd()
        data_root = "data/grape"
        grape_dir = osp.join(current_dir, data_root) 
        dir_list = [
            grape_dir,
        ]
    else:
        raise ValueError
    return first_existing_dir(dir_list)

def get_img_dir(classname):
    return f'{get_data_root_dir(classname)}/images/'
def get_detections_dir(classname):
    return f'{get_data_root_dir(classname)}/detections/'

#change made by dorsa:
flags.DEFINE_string('grape_img_dir', osp.join(os.getcwd(), 'data/grape/images'), 'Images Directory')
flags.DEFINE_string('grape_detections_dir', osp.join(os.getcwd(), 'data/grape/detections'), 'Detections Directory')
#end change.
curr_path = osp.dirname(osp.abspath(__file__))
# cache_path = osp.join(curr_path, '../../', 'cachedir')
cache_path = '../../cachedir'

flags.DEFINE_string('grape_cache_dir', osp.join(cache_path, 'jsons'), 'CUB Data Directory')
flags.DEFINE_enum('grape_dataset_class', 'grape', ['grape','shoe','shoe5k','tv'], 'json class')
flags.DEFINE_string('grape_file_path', '', '(optional) Expilicty specify JSON file path. If unspecified, it\'s set to cache/class_split.json')


class GrapeDataset(base_data.BaseDataset):

    def __init__(self, opts):
        super().__init__(opts,)
        self.img_dir = opts.grape_img_dir
        # print("self.img_dir: ",  self.img_dir)
        self.detections_dir = opts.grape_detections_dir
        # print("self.detections_dir: " , self.detections_dir)
        self.cache_dir = opts.grape_cache_dir
        # print("self.cache_dir: " ,self.cache_dir)
        self.dataset_class = opts.grape_dataset_class
        # print('self.dataset_class: ', self.dataset_class)

        if self.img_dir == '':
            self.img_dir = get_img_dir(opts.grape_dataset_class)
        if self.detections_dir == '':
            self.detections_dir = get_detections_dir(opts.grape_dataset_class)
       
        # print("self.img_dir: ",  self.img_dir)
        # print("self.detections_dir: " , self.detections_dir)

        if opts.grape_file_path:
            self.grape_anno_path = opts.grape_file_path
        else:
            print("dataset:", opts.grape_dataset_class)
            self.grape_anno_path = f'{get_data_root_dir(opts.grape_dataset_class)}/{opts.grape_dataset_class}_{opts.split}.json'

        if not osp.exists(self.grape_anno_path):
            print('%s doesnt exist!' % self.grape_anno_path)
            import ipdb
            ipdb.set_trace()

        # Load the annotation file.
        print('loading %s' % self.grape_anno_path)
        with open(self.grape_anno_path, 'r') as f:
            self.grape_anno = json.load(f)

        # json_anno expected to be list of dicts, each containing
        # - img_path:        relative img path
        # - detections_path: relative path to .npy/.npz/.mat file containing
        #     - masks:   kxhxw: bool
        #     - boxes:   kx4:   float32
        #     - scores:  k:     float32
        #     - classes: k:     object
        # - index: into .npy/.npz/.mat file
        # - sfmpose: (optional) [s, [trans], [rot_quat]]

        print('%d images' % len(self.grape_anno))

        return

    @staticmethod
    def fetch_detection(detections_path, index):
        detections = np.load(detections_path, allow_pickle=True).item()
        masks = detections['masks']
        boxes = detections['boxes']
        scores = detections['scores']
        classes = detections['classes']
        # np.save("mask.pt",masks)
        mask = masks[index, :, :].astype(np.bool)
        box = boxes[index, :].astype(np.float64)
        # Swap x,y in box
        box = box[[1,0,3,2]]

        try:
            sfmpose = detections['sfmpose']
            sfmpose = sfmpose[index]
        except KeyError:
            sfmpose = [1,[0,0],[1,0,0,0]] # fake [scale, [trans], [rot_quat]]
        sfmpose[0] = np.array(sfmpose[0], dtype=np.float64)
        sfmpose[1] = np.array(sfmpose[1], dtype=np.float64)
        sfmpose[2] = np.array(sfmpose[2], dtype=np.float64)
        return mask, box, sfmpose

    def get_anno(self, index):
        # print("child get anno has been called")
        anno = self.grape_anno[index]

        img_path = osp.join(self.img_dir, anno['img_path'])
        detections_path = osp.join(self.detections_dir, anno['detections_path'])
        

        mask, bbox, sfm_pose = self.fetch_detection(detections_path, anno['index'])
        mask = mask.astype(np.uint8)

        kp = vis = None
        return img_path, mask, bbox, sfm_pose, kp, vis

    def __len__(self):
        return len(self.grape_anno)

def data_loader(opts):
    dset = GrapeDataset(opts)
    # dset = d_set_func(opts, filter_key=filter_key)
    return DataLoader(
        dset,
        batch_size=opts.batch_size,
        shuffle=opts.shuffle_data,
        num_workers=opts.n_data_workers,
        pin_memory=True,
        drop_last=opts.drop_last_batch,
        collate_fn=base_data.collate_fn)

def main(_):
    opts = flags.FLAGS
    dataset = GrapeDataset(opts)
    import matplotlib.pyplot as plt
    for elem in dataset:
        plt.imshow(np.transpose(elem['img'], (1,2,0)))
        plt.show()

if __name__ == "__main__":
    flags.DEFINE_integer('img_size', 256, 'image size')
    app.run(main)
