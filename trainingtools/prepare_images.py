import sys, getopt
from PIL import Image
import glob
import os
import shutil
from resizeimage import resizeimage
import xml.etree.ElementTree as ET
import pandas as pd


def createClean(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder)


def separateTestTrain(i, train, test):
    if i % 10 == 0:
        return test
    return train


def main(argv):
    folder = './'
    action = 'diff'
    try:
        opts, args = getopt.getopt(argv, "f:s:")
    except getopt.GetoptError as  err:
        print('main.py -f <folder> -a <action> -size <size>')
        print(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt in "-f":
            folder = arg
        elif opt in "-a":
            action = arg
        elif opt in "-s":
            size = int(arg)

    image_files = glob.glob(os.path.join(folder, "*.[jJ][pP][gG]"))

    output_dir_train = os.path.join(folder, "train")
    output_dir_test = os.path.join(folder, "test")
    createClean(output_dir_train)
    createClean(output_dir_test)
    i = 0
    xml_list = []
    xml_test_list = []
    for image_file in image_files:
        with open(image_file, 'r+b') as f:
            with Image.open(f) as image:
                print(image_file)
                width, height = image.size
                if(width < height):
                    ratio = int(width / size)
                else:
                    ratio = int(height / size)
                cover = resizeimage.resize_cover(image, [width / ratio, height / ratio])
                cover.save(
                    os.path.join(separateTestTrain(i, output_dir_train, output_dir_test), os.path.basename(image_file)),
                    image.format)

                image_name, ext = os.path.splitext(os.path.basename(image_file))
                # open related XML
                xml_file = os.path.join(folder, image_name + '.xml')
                tree = ET.parse(xml_file)
                root = tree.getroot()
                for member in root.findall('object'):
                    value = (root.find('filename').text,
                             int(int(root.find('size')[0].text) / ratio),
                             int(int(root.find('size')[1].text) / ratio),
                             member[0].text,
                             int(int(member.find('bndbox')[0].text) / ratio),
                             int(int(member.find('bndbox')[1].text) / ratio),
                             int(int(member.find('bndbox')[2].text) / ratio),
                             int(int(member.find('bndbox')[3].text) / ratio)
                             )
                    separateTestTrain(i, xml_list, xml_test_list).append(value)
        i += 1
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    xml_df.to_csv(os.path.join(output_dir_train, 'train_labels.csv'), index=None)
    xml_df = pd.DataFrame(xml_test_list, columns=column_name)
    xml_df.to_csv(os.path.join(output_dir_test, 'test_labels.csv'), index=None)


if __name__ == "__main__":
    main(sys.argv[1:])
