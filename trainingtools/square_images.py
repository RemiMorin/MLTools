import sys, getopt
from PIL import Image
import glob
import os
import shutil
import xml.etree.ElementTree as ET
from xml.dom import minidom


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    reparsed = minidom.parseString(ET.tostring(elem, 'utf-8'))
    return reparsed.toprettyxml(indent="  ")

def write_xml(out_folder, image_path, boxes, width, height, depth):
    found = False
    root = ET.Element('annotation')
    ET.SubElement(root, 'folder').text = os.path.dirname(image_path)
    ET.SubElement(root, 'filename').text = os.path.basename(image_path)
    ET.SubElement(root, 'path').text = image_path
    ET.SubElement(ET.SubElement(root, 'source'), 'database').text = 'Unknown'
    sizeElement = ET.SubElement(root, 'size')
    ET.SubElement(sizeElement, 'width').text = str(width)
    ET.SubElement(sizeElement, 'height').text = str(height)
    ET.SubElement(sizeElement, 'depth').text = str(depth)
    ET.SubElement(root, 'segmented').text = '0'
    for box in boxes:
        objectElement = ET.SubElement(root, 'object')
        ET.SubElement(objectElement, 'name').text = 'bird'
        ET.SubElement(objectElement, 'pose').text = 'Unspecified'
        ET.SubElement(objectElement, 'truncated').text = '0'
        ET.SubElement(objectElement, 'difficult').text = '0'
        bndboxElement = ET.SubElement(objectElement, 'bndbox')
        ET.SubElement(bndboxElement, 'xmin').text = str(int(box[0]))
        ET.SubElement(bndboxElement, 'ymin').text = str(int(box[1]))
        ET.SubElement(bndboxElement, 'xmax').text = str(int(box[2]))
        ET.SubElement(bndboxElement, 'ymax').text = str(int(box[3]))

    image_name, ext = os.path.splitext(os.path.basename(image_path))
    with open(os.path.join(out_folder, image_name + ".xml"), "w") as f:
        f.write(prettify(root))


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

    image_files = glob.glob(os.path.join(folder, "*.[jJ][pP][gG]"))

    output_dir = os.path.join(folder, "cropped")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir, ignore_errors=True)

    os.makedirs(output_dir)

    for image_file in image_files:
        #to follow what is going on...
        print(image_file)
        #determine output files
        image_name, ext = os.path.splitext(os.path.basename(image_file))
        xml_file = os.path.join(folder, image_name + '.xml')
        out_image_file = os.path.join(output_dir, os.path.basename(image_file))

        #read image find small side
        img = Image.open(image_file)
        width, height = img.size
        small_side = min(width, height)

        #read xml
        tree = ET.parse(xml_file)
        root = tree.getroot()
        boxes = []
        for member in root.findall('object'):
            boxes.append([
                int(member.find('bndbox')[0].text) - int((width - small_side) / 2),
                int(member.find('bndbox')[1].text) - int((height - small_side) / 2),
                int(member.find('bndbox')[2].text) - int((width - small_side) / 2),
                int(member.find('bndbox')[3].text) - int((height - small_side) / 2)
                     ])

        minx = int((width - small_side) / 2)
        miny = int((height - small_side) / 2)
        maxx = small_side + int((width - small_side) / 2)
        maxy = small_side + int((height - small_side) / 2)

        minx_box = small_side;
        maxx_box = 0;
        miny_box = small_side;
        maxy_box = 0;

        for box in boxes:
            if box[0] < minx_box:
                minx_box = box[0];
            if box[1] < miny_box:
                miny_box = box[1];
            if box[2] > maxx_box:
                maxx_box = box[2];
            if box[3] > maxy_box:
                maxy_box = box[3];

        #if we can fit the bounding box into a square
        if maxx_box - minx_box < small_side and maxy_box - miny_box < small_side:

            translation_x = 0
            translation_y = 0

            if minx_box < 0:
                translation_x = minx_box
            if maxx_box > small_side:
                translation_x = maxx_box - small_side
            if miny_box < 0:
                translation_y = miny_box
            if maxy_box > small_side:
                translation_y = maxy_box - small_side

            for box in boxes:
                box[0] -= translation_x
                box[1] -= translation_y
                box[2] -= translation_x
                box[3] -= translation_y

            minx += translation_x
            miny += translation_y
            maxx += translation_x
            maxy += translation_y

            write_xml(output_dir,out_image_file,boxes,small_side,small_side,3)
            img2 = img.crop((minx,miny,maxx,maxy))
            img2.save(out_image_file)
        else:
            print("--------skipping " + image_name)



if __name__ == "__main__":
    main(sys.argv[1:])
