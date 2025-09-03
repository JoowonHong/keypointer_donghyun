import os

def main():
    root = './persons'

    for p in os.listdir(root):
        cmd = f'mkdir {os.path.join(root, p)}_labels'
        print(cmd)

        os.system(cmd)


if __name__=='__main__':
    main()