# Single-view Grape 3D Reconstruction


### Requirements
- Python 3.7
- Pytorch 1.1.0
- Pymesh
- SoftRas
- NMR

### Installation
I followed the insturctions in [docs/installation.md](docs/installation.md) for building the environment.

You can also use [this Dockerfile](Dockerfile) to build your environment. For convenience, a pre-built docker image is provided at [shubhamgoel/birds](https://hub.docker.com/r/shubhamgoel/birds). 

### Training
Please see [docs/training.md](docs/training.md)

### Demo
1. From the `ucmr` directory, download the pretrained model (This is the snapshot of the model trained on WGISD dataset of grapes and with a sphere template shape):
```
wget https://drive.google.com/file/d/1xpfOu8nJBE6spzgKRkZJ5dsOPbKdrp1m/view?usp=sharing && tar -vzxf pretrained_model_grapes_WGISD_sphereTemplate.tar.gz
```
You should see `cachedir/snapshots/Cam/e400_cub_train_cam4/pred_net_latest.pth`

2. Run the demo:
```
python -m src.demo \
    --pred_pose \
    --pretrained_network_path=cachedir/snapshots/Cam/e400_cub_train_cam4/pred_net_latest.pth \
    --img_path demo_data/grape_686.jpg
```
Note: The ` --shape_path ` flag is removed from the demo since the pretrained model is trained on sphere (default template shape when no template shape is given). If you are testing with a specific shape template, here you have to feed the .obj or .npy path as the ` --shape_path `. 


### Citation

```
@inProceedings{ucmrGoel20,
  title={Shape and Viewpoints without Keypoints},
  author = {Shubham Goel and
  Angjoo Kanazawa and
  and Jitendra Malik},
  booktitle={ECCV},
  year={2020}
}
```

### Acknowledgements
Parts of this code were borrowed from [CMR](https://github.com/akanazawa/cmr) and [CSM](https://github.com/nileshkulkarni/csm/).
