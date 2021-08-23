#!/usr/bin/python
import numpy as np
import cv2
import sys
import os

from numpy.lib.function_base import insert

def get_sorted_png_paths(image_dir):
    image_fnames = [ fname for fname in os.listdir(image_dir) if fname[-4:] == '.png' ]
    image_fnames.sort()
    return [ os.path.join(image_dir, fname) for fname in image_fnames ]

def find_insert_row(img, frame, start_row, min_check_rows=32, ignore_rows=33):
    last_error = None
    for check_rows in range(min_check_rows, img.shape[0]-ignore_rows-1):
        img_region = img[ignore_rows:ignore_rows+check_rows,:,:]
        frame_region = frame[start_row-check_rows:start_row]
        error = np.sum(np.abs((img_region - frame_region)))
        if last_error != None and error < last_error / 2:
            return check_rows + ignore_rows
        last_error = error
    else:
        raise Exception('Failed to find match.')


def robust_find_insert_row(img, frame, start_row, min_check_rows=32, ignore_rows=33):
    lowest_error_per_row = None
    best_check_rows = None
    for check_rows in range(min_check_rows, img.shape[0]-ignore_rows-1):
        img_region = img[ignore_rows:ignore_rows+check_rows,:,:]
        frame_region = frame[start_row-check_rows:start_row]
        error_per_row = np.sum(np.abs((img_region - frame_region))) / check_rows
        if lowest_error_per_row == None or error_per_row < lowest_error_per_row:
            lowest_error_per_row = error_per_row
            best_check_rows = check_rows
        return best_check_rows + ignore_rows
    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: ./sticher.py <image-dir>')
        exit()

    image_dir = sys.argv[1]
    sorted_png_paths = get_sorted_png_paths(image_dir)

    first_img = cv2.imread( sorted_png_paths[0] )
    img_rows, img_cols, img_channels = first_img.shape
    
    big_frame = np.zeros((img_rows*len(sorted_png_paths), img_cols, img_channels), first_img.dtype)
    big_frame[:img_rows, :, :] = first_img
    
    img_count = len(sorted_png_paths)
    last_row = img_rows-1
    for i, img_path in enumerate(sorted_png_paths[1:]):
        print(f'> {i+1}/{img_count} ', end='\r')
        img = cv2.imread(img_path)
        insert_row = robust_find_insert_row(img, big_frame, last_row)
        
        big_frame[last_row:last_row+img_rows-insert_row, :, :] = img[insert_row:,:,:]
        last_row = last_row+img_rows-insert_row
        cv2.imwrite('big.png', big_frame[:last_row])
    
    print(f'Done.   ')