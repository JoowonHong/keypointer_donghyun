## Tennis ball Keypointer

### Install
```shell
conda create -n keypointer python==3.10.* -y
conda activate keypointer
```

### Setup
Tool
```shell
cd keypointer
pip install opencv-python PyQt5==5.15.10

# image resources 
pyrcc5 resources.qrc -o resources_rc.py

```

### Run
```shell
python keypointer.py

# 1. Click the frame directory          (./donghae_a_01/part0/images)
# 2. Click the ground truth directory   (./donghae_a_01/part0/labels)
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
# V : Paste the previous points for current image

# I : Position up
# J : Position Left
# K : Position down
# L : Position right
```
