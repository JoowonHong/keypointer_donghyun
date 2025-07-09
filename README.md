## Tennis ball Keypointer

### Install
```shell
conda create -n keypointer python==3.9.5 -y
conda activate keypointer
```

상기 내용 적용 안되는 경우, 기본적으로 defaults 채널만 사용하고 있는 경우일 수 있으며 추가적인 채널을 추가하면 문제를 해결할 수 있음.
```shell
conda config --add channels conda-forge
conda install -c conda-forge python=3.9.5
conda create -n keypointer -c conda-forge python=3.9.5
conda activate keypointer
```

### Setup
Tool
```shell
git clone git@github.com:PXScope/pxcast-keypointer.git
cd pxcast-keypointer
pip install opencv-python PyQt5==5.15.10
```

### Run
```shell
python keypointer.py

# 1. Click the frame directory          (./240427/BRAX001/part1/frame)
# 2. Click the ground truth directory   (./240427/BRAX001/part1/gt)
```

### Commands
```shell

# Ctrl+O : Open frame directory
# Ctrl+K : Open ground truth directory

# A : Return to the previous frame
# S : Save the ground truth
# D : Go to the next frame
# E : Except the frame
# X : Initialize the point to null

# I : Position up
# J : Position Left
# K : Position down
# L : Position right
```
