import os
import sys
import time
import shutil
import atexit
from datetime import datetime
import hpmap
import numpy as np
import pylab as plt

sys.path.append(os.path.dirname(os.getcwd()))

#imgpath = '/home/gb/irc_ctrl/latest'
imgpath = './'



@atexit.register
def goodbye():
    print ('hpmap_latest.py is stopped.')


def main():
    print ('hpmap_latest.py is started.')
    while 1:
        try:
            try:
                hpmap.main()
            except (TypeError, ValueError, IndexError) as e:
                print("error:", e)

            try:
                shutil.copy2(imgpath+'Moll.png', '/var/www/html/image')
                os.system(f'convert {imgpath}/Orth.png -trim {imgpath}/Orth.png')
                shutil.copy2(imgpath+'Orth.png', '/var/www/html/image')
                os.system(f"stat -c %y {imgpath}/Orth.png > time_orth.txt")
                shutil.copy2(imgpath+'time_orth.txt', '/var/www/html/image')
            except PermissionError:
                print ("Cannot copy the files due to the permission error...")
                continue
                
            time.sleep(5)
        except KeyboardInterrupt:
            exit(0)


if __name__=='__main__':
    main()

