import os

def main():
    root = './tennis_actions_v1'

    train_classes = {}
    with open(os.path.join(root, 'train_list_videos.txt'), 'r') as f:
        lines = f.readlines()
        for l in lines:
            p, c  = l.split(' ')
            c = int(c.split('\n')[0])

            if c not in list(train_classes.keys()):
                train_classes[c] = 1
            else:
                train_classes[c] += 1


    val_classes = {}
    with open(os.path.join(root, 'val_list_videos.txt'), 'r') as f:
        lines = f.readlines()
        for l in lines:
            p, c  = l.split(' ')
            c = int(c.split('\n')[0])

            if c not in list(val_classes.keys()):
                val_classes[c] = 1
            else:
                val_classes[c] += 1

    print(dict(sorted(train_classes.items())))
    print(dict(sorted(val_classes.items())))

    print(sum(train_classes.values()))
    print(sum(val_classes.values()))


if __name__=='__main__':
    main()