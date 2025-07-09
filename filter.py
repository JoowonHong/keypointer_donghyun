import os

from tqdm import tqdm

ROOT = os.getcwd()


def main():

    path = "./data/part5/"  # 경로 변경
    frames_dir = os.path.join(path, "frame")
    labels_dir = os.path.join(path, "gt")

    new_frames_dir = os.path.join(path, "new_frame")
    new_labels_dir = os.path.join(path, "new_gt")
    if not os.path.exists(new_frames_dir):
        os.mkdir(new_frames_dir)
    if not os.path.exists(new_labels_dir):
        os.mkdir(new_labels_dir)

    # 깍두기 제거
    if os.path.isfile(os.path.join(labels_dir, "except.txt")):
        except_file = os.path.join(labels_dir, "except.txt")

        with open(except_file, "r") as f:
            items = f.readlines()
            items = [item.split(".txt")[0] for item in items]

        for frame_name in os.listdir(frames_dir):
            frame = os.path.join(frames_dir, frame_name)

            for item in items:
                if item in frame_name:
                    os.system(f"rm {frame}")

        for label_name in os.listdir(labels_dir):
            label = os.path.join(labels_dir, label_name)

            if label_name == "except.txt":
                continue

            for item in items:
                if item in label_name:
                    os.system(f"rm {label}")

        os.system(f"rm {except_file}")

    # 사용가능 프레임
    for label_name in tqdm(os.listdir(labels_dir)):  # 240427_BRAX001_1714222937432535.txt
        label_ = os.path.join(labels_dir, label_name)
        frame_ = label_name.replace(".txt", ".jpg")  # 240427_BRAX001_1714222937432535.jpg

        for frame_name in os.listdir(frames_dir):
            if frame_ in frame_name:
                os.system(f"cp {os.path.join(frames_dir, frame_name)} {os.path.join(new_frames_dir)}/")
                os.system(f"cp {os.path.join(labels_dir, label_name)} {os.path.join(new_labels_dir)}/")

    # 프레임, 라벨 매칭 여부 확인
    new_frames = [i.split(".")[0] for i in os.listdir(new_frames_dir)]
    new_labels = [i.split(".")[0] for i in os.listdir(new_labels_dir)]
    new_frames = set([i.split(".")[0] for i in os.listdir(new_frames_dir)])
    new_labels = set([i.split(".")[0] for i in os.listdir(new_labels_dir)])
    if new_frames == new_labels:
        print("End of Process")
    else:
        raise Exception("Files not match")


if __name__ == "__main__":
    main()
