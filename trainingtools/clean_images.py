import sys, getopt
from PIL import Image
import glob
import os
import shutil


def main(argv):
    folder = './'
    action = 'diff'
    try:
        opts, args = getopt.getopt(argv, "f:a:")
    except getopt.GetoptError:
        print('main.py -f <folder> -a <action>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in "-f":
            folder = arg
        elif opt in "-a":
            action = arg

    files = glob.glob(os.path.join(folder,"**", "*([0-9]).[jJ][pP][gG]"),recursive=True)
    files += glob.glob(os.path.join(folder,"**", "*_1.[jJ][pP][gG]"),recursive=True)
    files += glob.glob(os.path.join(folder,"**", "*([0-9]).[xX][mM][lL]"),recursive=True)
    files += glob.glob(os.path.join(folder,"**", "*_1.[xX][mM][lL]"),recursive=True)

    #this is just a special case where our point and shoot name pictures starting with a p
    #since my subject was bird, I can get rid of all irrelevant familly pictures that way!files += glob.glob(os.path.join(folder, "*[pP]*.*"),recursive=True)
    files += glob.glob(os.path.join(folder,"**", "*[pP]*.*"),recursive=True)

    for file in files:
        print (file)
        os.remove(file)


if __name__ == "__main__":
    main(sys.argv[1:])
