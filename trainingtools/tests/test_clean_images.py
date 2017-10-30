import unittest
import clean_images
import os
import glob
import shutil

class TestStringMethods(unittest.TestCase):
    workdir = './test_clean'
    files = ['woop.jpg','woop.xml','woop(1).jpg','woop(2).jpg','woop(123456).jpg','woop(1).xml','woop(2).xml','woop(123456).xml']

    def setUp(self):
        if os.path.exists(self.workdir):
            shutil.rmtree(self.workdir, ignore_errors=True)
        os.makedirs(self.workdir)

        #create files, clean tools does not look at content so create them empty
        for file in self.files:
            open(os.path.join(self.workdir,file), 'a').close()
        pass

    def test_clean_removed(self):
        clean_images.main(['-f' + self.workdir])
        remaining_files = [f for f in os.listdir(self.workdir) if os.path.isfile(os.path.join(self.workdir, f))]
        print(remaining_files)
        self.assertEqual(len(remaining_files),2)
        pass

if __name__ == '__main__':
    unittest.main()