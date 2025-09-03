import os
import re
import random
import cv2
import glob
import numpy as np
import subprocess

def letterbox(frame,
              new_shape=(640, 640),
              color=114):

    # if frame.shape[2] == 4:
    #     frame = frame[:, :, :3]  # RGBA → RGB

    shape = frame.shape[:2]  # (h, w)
    
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    elif isinstance(new_shape, str):
        new_shape = tuple(map(int, new_shape.split(",")))
    elif isinstance(new_shape, list):
        new_shape = tuple(new_shape)

    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    ratio = (r, r)

    new_unpad = (int(round(shape[1] * r)), int(round(shape[0] * r)))

    frame_resized = cv2.resize(frame, new_unpad, interpolation=cv2.INTER_LINEAR)

    dw = new_shape[1] - new_unpad[0]  # width padding
    dh = new_shape[0] - new_unpad[1]  # height padding
    dw /= 2
    dh /= 2

    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))

    frame_padded = cv2.copyMakeBorder(frame_resized, top, bottom, left, right, 
                                      cv2.BORDER_CONSTANT, value=color)


    return frame_padded, ratio, (dw, dh)


def natural_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def main():
    
    root_dir = './persons/'

    # outputs
    output_dir = './tennis_actions_v1'
    train_videos = os.path.join(output_dir, 'videos_train')
    train_labels = os.path.join(output_dir, 'train_list_videos.txt')
    val_videos = os.path.join(output_dir, 'videos_val')
    val_labels = os.path.join(output_dir, 'val_list_videos.txt')

    if not os.path.exists(train_videos):
        os.makedirs(train_videos)

    if not os.path.exists(train_labels):
        with open(train_labels, 'w') as f:
            f.write("")

    if not os.path.exists(val_videos):
        os.makedirs(val_videos)

    if not os.path.exists(val_labels):
        with open(val_labels, 'w') as f:
            f.write("")


    # data processing
    frames_dirs = [os.path.join(root_dir,d) for d in os.listdir(root_dir) if '_labels' not in d]

    classify = {}
    for frames_dir in frames_dirs:
        labels_dir = f'{frames_dir}_labels'

        frames_pathes = [os.path.join(frames_dir, c) for c in
                         sorted(os.listdir(frames_dir), key=natural_key)]
        label_pathes = [os.path.join(labels_dir, l) for l in 
                        sorted(os.listdir(labels_dir), key=natural_key)
                        if 'except' not in l]
        except_file = os.path.join(labels_dir, 'except.txt')

        with open(except_file, 'r') as f:
            except_list = [item.split('\n')[0] for item in f.readlines()]
        
        for i, (frames_path, label_path) in enumerate(zip(frames_pathes, label_pathes)):
            frames_name = frames_path.split('/')[-1]
            label_name = label_path.split('/')[-1]

            if frames_name not in label_name:
                raise FileNotFoundError(f'{frames_name} not found in {label_name}')

            if label_name in except_list:
                continue

            with open(label_path, 'r') as f:
                label = f.readline()
                label = int(label.split(' \n')[0])

            if label not in list(classify.keys()):
                classify[label] = [frames_path]
            else:
                classify[label].append(frames_path)


    # data split
    train_ratio = 0.8
    
    train_frames_list = []
    val_frames_list = []
    for c in sorted(list(classify.keys())):
        pathes = classify[c].copy()
        random.shuffle(pathes)

        n = int(len(pathes) * train_ratio)

        train_pathes = [(p, c) for p in pathes[:n]]
        val_pathes = [(p, c) for p in pathes[n:]]

        train_frames_list.extend(train_pathes)
        val_frames_list.extend(val_pathes)


    # data save
    def data_save(frames_list, clip_dir, label_path, fps=30, clip_len=5):
        annos = []
        for t in frames_list:
            f, c = t

            print(f, c)
            
            part, clip_name = f.split('/')[-2:]
            
            temp_name = f'__{part}_{clip_name}.tmp.mp4'
            output_name = f'__{part}_{clip_name}.mp4'

            temp_clip_path = os.path.join(clip_dir, temp_name)
            output_clip_path = os.path.join(clip_dir, output_name)

            # videos
            frames = sorted(glob.glob(os.path.join(f, '*.jpg')), key=natural_key)
            
            if not frames:
                raise FileNotFoundError('No frames found in the folder')

            if len(frames) != fps * clip_len:
                continue

            max_h = max([cv2.imread(f).shape[0] for f in frames])
            max_w = max([cv2.imread(f).shape[1] for f in frames])

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            o = cv2.VideoWriter(temp_clip_path, fourcc, fps, (max_w, max_h))

            for p in frames:
                frame = cv2.imread(p, cv2.IMREAD_COLOR)
                letter_frame, _, _ = letterbox(frame, (max_h, max_w))
                o.write(letter_frame)
            
            o.release()

            # ffmpeg
            subprocess.run([
                "ffmpeg",
                "-y",
                "-i", temp_clip_path,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                output_clip_path
            ], stdout=subprocess.DEVNULL, 
               stderr=subprocess.DEVNULL,
               check=True)
            os.system(f'rm {temp_clip_path}')

            # annotations
            annos.append(f'{output_name} {c}')
        
        random.shuffle(annos)
        with open(label_path, 'w') as f:
            f.write('\n'.join(annos))

        return _

    _ = data_save(train_frames_list, train_videos, train_labels, fps=30, clip_len=5)
    _ = data_save(val_frames_list, val_videos, val_labels, fps=30, clip_len=5)
    

if __name__=='__main__':
    main()