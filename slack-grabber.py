#!/usr/bin/python
import pyautogui as pag
import numpy as np
import time
import cv2
import os

idle_coords = (10,10)
conversation_region = (334, 179, 1580, 750)
bottom_region = (334, 800, 1580, 100)
center_coords = (1000, 500)

out_dir = 'tien_josiah_slacks'
prefix  = 'conv_window_'
suffix  = '.png'

def page_down():
    bottom_img = pag.screenshot(region=bottom_region)
    bottom_arr = np.array(bottom_img)

    for _ in range(10):
        new_conv_img = pag.screenshot(region=conversation_region)
        new_conv_arr = np.array(new_conv_img)

        match_results = cv2.matchTemplate(bottom_arr, new_conv_arr, cv2.TM_SQDIFF_NORMED)
        _, _, min_loc, _ = cv2.minMaxLoc(match_results)
        if min_loc[1] < 100:
            break
        
        step_amount = max( min_loc[1] // 75, 1)
        pag.moveTo(center_coords)
        pag.scroll( -step_amount )
        pag.moveTo(idle_coords)
        time.sleep(1)
    else:
        print('Failed to moved bottom to top while paging down. Returning anyway.')


def get_img_diff(img1, img2):
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    return np.sum(arr1 - arr2)

def get_start_index():
    existing_fnames = os.listdir(out_dir)
    existing_fnames.sort()
    last_ind_str = existing_fnames[-1][len(prefix):-len(suffix)]
    return int(last_ind_str) + 1


if __name__ == '__main__':
    n = get_start_index()
    last_img = None
    critical_img_diff = 1
    while True:
        img = pag.screenshot(region=conversation_region)
        if last_img == None or get_img_diff(img, last_img) > critical_img_diff:
            out_num = str(n).zfill(4)
            img.save( f'{out_dir}/{prefix}{out_num}{suffix}' )
            if last_img != None:
                print(get_img_diff(img, last_img))
            last_img = img
            n += 1
        else:
            break
        page_down()
        time.sleep(3)

