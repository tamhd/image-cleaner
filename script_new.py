#!/usr/bin/env python
import sys
import glob
from scipy.misc import imread
from scipy.linalg import norm
from scipy import sum, average
from PIL import Image
import numpy as np
from scipy.misc import imsave
import scipy.misc
import imagehash


def img_extensions():
    """ return all extensions being considered 
        i.e. jpg, jpeg, png
    """
    return [".JPG"]


def to_grayscale(arr):
    "If arr is a color image (3D array), convert it to grayscale (2D array)."
    if len(arr.shape) == 3:
        return average(arr, -1)  # average over the last axis (color channels)
    else:
        return arr


def normalize(arr):
    rng = arr.max()-arr.min()
    if rng == 0:
        rng = 1
    amin = arr.min()
    return (arr-amin)*255/rng


def img_resize(infile, size):
    """ resize images to a thumbnail
    """
    try:
        infile.thumbnail(size, Image.ANTIALIAS)
    except:
        print("cannot create thumbnail for '%s'" % infile)
    return infile


def img_compare(file1, file2):
    """ main function to compare images
    """
    # read image
    img1 = Image.open(file1)
    img2 = Image.open(file2)

    # resize 
    size = 128, 128
    img1_res = img_resize(img1, size)
    img2_res = img_resize(img2, size)

    img1_res.save("img_1.thumbnail", "JPEG")
    img2_res.save("img_2.thumbnail", "JPEG")

    # convert to gray scale
    img1_grayscale = img1_res.convert('LA')
    img1_grayscale.save("img_1_grayscale.png")

    img2_grayscale = img2_res.convert('LA')
    img2_grayscale.save("img_2_grayscale.png")

    # normalise
    img1_norm = normalize(np.array(img1_grayscale.getdata()).astype(float))
    img2_norm = normalize(np.array(img2_grayscale.getdata()).astype(float))

    try:
        # compare two images
        diff = img1_norm - img2_norm
        m_norm = sum(abs(diff))  # Manhattan norm
        z_norm = norm(diff.ravel(), 0)  # Zero norm

        # print("Manhattan norm:", m_norm, "/ per pixel:", m_norm/img1_norm.size)
        # print("Zero norm:", z_norm, "/ per pixel:", z_norm*1.0/img1_norm.size)

        return m_norm/img1_norm.size, float(z_norm) / img1_norm.size
    except:
        return 100, 100

if __name__ == "__main__":
    img_dir = sys.argv[1]
    print("Hash the directory {}".format(img_dir))
    img_hashes = list()
    img_paths = sorted(glob.glob("{dir}/*{ext}".format(dir=img_dir, ext=".JPG"))[:100])
    for curr_file in img_paths:
        print(curr_file)
        phash = imagehash.dhash(Image.open(curr_file))
        img_hashes.append(phash)
    
    print("Start Comparison")
    prev_file, prev_hash = None, None
    for (curr_file, curr_hash) in zip(img_paths, img_hashes):
        if prev_file: 
            diff = curr_hash - prev_hash
            if diff < 20: 
                print("Similar:")
                print(prev_file)
                print(curr_file)
                print(diff)
        prev_file, prev_hash = curr_file, curr_hash

