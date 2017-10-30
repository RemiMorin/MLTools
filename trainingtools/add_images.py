import fnmatch
import getopt
import glob
import os
import shutil
from tkinter import *
from tkinter import ttk

import PIL
from PIL import ImageTk
from resizeimage import resizeimage

def createClean(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder)

def button_click_exit_mainloop (event):
    event.widget.quit() # this will cause mainloop to unblock.

def processFile( origine_image_files, destination_basenames,source_folder,destination_folder):
    conflicts = []
    for image_file in origine_image_files:
        image_file_name = os.path.basename(image_file)
        image_name, ext = os.path.splitext(image_file_name)
        if image_file_name.lower() in destination_basenames:
            conflicts.append(image_file)
        else:
            shutil.move(image_file, destination_folder)
            shutil.move(os.path.join(source_folder,image_name + ".xml"), destination_folder)

    return conflicts

def findConflicts(image_name,destination_folder):
    reg_expr = re.compile(fnmatch.translate(image_name), re.IGNORECASE)
    result = []
    for root, dirs, files in os.walk(destination_folder, topdown=True):
        result += [os.path.join(root, j) for j in files if re.match(reg_expr, j)]
    return result

def getConflict(image_name, destination_folder):
    result = findConflicts(image_name,destination_folder)
    if len(result) > 1:
        print ("Note there is more than one conflicting image for " + image_name)
    return result[0]

def getImageName(f):
    image_name, ext = os.path.splitext(os.path.basename(f))
    return image_name

def getResizedImage(image_file):
    return resizeimage.resize_cover(PIL.Image.open(image_file), [500, 500])

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "o:d:")
    except getopt.GetoptError as  err:
        print('main.py -o <originfolder> -d <destinationfolder>')
        print(err)
        sys.exit(2)
    for opt, arg in opts:
        if opt in "-o":
            origin_folder = arg
        elif opt in "-d":
            destination_folder = arg

    if not origin_folder or not destination_folder:
        print ("error both origin and destination is required")
        return

    if not os.path.exists(destination_folder) or not os.path.isdir(destination_folder):
        print("destination path does not exist or is not a folder")
        return

    origine_image_files = glob.glob(os.path.join(origin_folder, "*.[jJ][pP][gG]"))
    destination_image_files = glob.glob(os.path.join(destination_folder, "*.[jJ][pP][gG]"))
    destination_basenames = [os.path.basename(file_name).lower() for file_name in destination_image_files]
    conflicts = processFile(origine_image_files,destination_basenames,origin_folder,destination_folder)

    operationContext = {}

    #method into the scope for variable visibility
    def setContext(image_file):
        operationContext['current_image_file']= image_file
        operationContext['conflicting_image'] = getConflict(os.path.basename(operationContext['current_image_file']), destination_folder)
        operationContext['counter'] = 1
        operationContext['current_image_name'] = getImageName(operationContext['current_image_file'])
        operationContext['current_xml_file'] = os.path.join(origin_folder, operationContext['current_image_name'] + ".xml")

    root = Tk()
    root.title("Add files to folder")
    if not conflicts:
        root.destroy()
        return
    setContext(conflicts.pop())

    def deleteOrigin(*argv):
        os.remove(operationContext['current_image_file'])
        os.remove(operationContext['current_xml_file'])
        nextFile()

    def addOrigin(*argv):
        new_image_name = operationContext['current_image_name'] + "_" + str(operationContext['counter'])
        other_conflict = findConflicts(new_image_name + '.jpg', destination_folder)
        if len(other_conflict):
            operationContext['counter'] += 1
            operationContext['conflicting_image'] = other_conflict[0]
            updateImages()
        else:
            shutil.move(operationContext['current_image_file'],os.path.join( destination_folder,new_image_name + ".jpg"))
            shutil.move(operationContext['current_xml_file'],os.path.join( destination_folder,new_image_name + ".xml"))
            nextFile()

    def nextFile():
        if not conflicts:
            root.destroy()
            return
        setContext(conflicts.pop())
        updateImages()

    def updateImages():
        imagetk = ImageTk.PhotoImage(getResizedImage(operationContext['current_image_file']))
        photo_label_origin.configure(image=imagetk)
        photo_label_origin.image = imagetk

        imagetk = ImageTk.PhotoImage(getResizedImage(operationContext['conflicting_image']))
        photo_label_destination.configure(image=imagetk)
        photo_label_destination.image = imagetk

    imagetk = ImageTk.PhotoImage(getResizedImage(operationContext['current_image_file']))

    photo_label_origin = ttk.Label(root,image=imagetk)
    photo_label_origin.image = imagetk
    photo_label_origin.grid(column=2, row=1)

    imagetk = ImageTk.PhotoImage(getResizedImage(operationContext['conflicting_image']))
    photo_label_destination = ttk.Label(root,image=imagetk)
    photo_label_destination.image = imagetk
    photo_label_destination.grid(column=1, row=1)

    ttk.Button(root, text="Same", command=deleteOrigin).grid(column=1, row=2, sticky=W)
    ttk.Button(root, text="New", command=addOrigin).grid(column=2, row=2, sticky=W)


    root.mainloop()

if __name__ == "__main__":
    main(sys.argv[1:])
