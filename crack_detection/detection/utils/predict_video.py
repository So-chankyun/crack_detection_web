import os
import cv2
import numpy as np
from PIL import Image

from crack_detection.detection.model.network.unet_model import UNet
from crack_detection.detection.model import test

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as tr

# MODEL PATH
detection_folder = './crack_detection/detection'
MODEL_PATH = os.path.join(detection_folder,'Unet(50k using data, epoch15).pth')
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def merge_img(frame, pred):
    re_frm = cv2.resize(frame, dsize=(640, 384), interpolation=cv2.INTER_CUBIC)
    add_mask = re_frm.copy()
    pred = pred.reshape((384,640)).shape
    # print(add_mask.shape)
    # print(pred.reshape((384,640)).shape)
    add_mask[pred !=0 ]=[0,255,0]

    return add_mask

'''
* Description *
  - 저장된 비디오를 예측하여 다시 저장한다.

* Process *
  1. Load model
  2. Load Data
  3. Predict
  4. circulate 2~3 process
'''
def make_video(video_path,save_path,frame=15.0):
    width  = 640
    height = 384
    frame_thred = 1.1

    capture = cv2.VideoCapture(video_path)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH,width) # 일단은 고정된 사이즈로 가자
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT,height)

    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter(save_path, fourcc, frame, (int(width), int(height)))

    count = 0
    max_ratio, avg_ratio = 0.0, 0.0

    while cv2.waitKey(33) < 0:
        count+=1
        ret, frame = capture.read()
        if not ret:
            print("프레임을 수신할 수 없습니다. 종료 중 ...")
            break

        pred_img = np.asarray(test.predict(frame,'video'))
        # 예측 진행. tensor -> image-> array, 시간 소요가 너무 오래 걸리면 이를 수정할 필요가 있다.
        convert_img = merge_img(frame, pred_img)
        CRPF = np.round((pred_img.reshape(-1).sum()/(width*height))*100, 2)

        # max_ratio = CRPF if CRPF > max_ratio else max_ratio
        # avg_ratio = (avg_ratio*(count-1)+CRPF)/count

        """
        ########### args.frame_thred 이상이 됐을 때 캡처 (추가 예정) ###########
        """

        font=cv2.FONT_HERSHEY_SIMPLEX
        color = (50,50,165) if CRPF > frame_thred else (50,165,50)

        CRPF_img = cv2.putText(convert_img, 'Crack Ratio : {:.2f} {}'.format(CRPF, "%"), (5, 20), font, .6, color, 2)

        out.write(CRPF_img)


    capture.release()
    out.release()