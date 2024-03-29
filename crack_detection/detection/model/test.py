import os
from PIL import Image
from crack_detection.detection.model.network.unet_model import UNet
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as tr

detection_folder = './crack_detection/detection'
MODEL_PATH = os.path.join(detection_folder,'Unet(50k using data, epoch15).pth')
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 1. Load model
def load_model():
    model = UNet(n_channels=3,n_classes=2,bilinear=True)
    model.load_state_dict(torch.load(MODEL_PATH))
    model.to(DEVICE)
    model.eval()

    return model

# 2. Data load and transforms
def load_data(path,data_type,size):
    # load image
    if data_type == 'image':
        img = Image.open(path).convert('RGB')
    elif data_type == 'video':
        img = Image.fromarray(path)

    img = img.resize(size)
    tensor_img = tr.ToTensor()(img).unsqueeze(0)

    return tensor_img

# 3. prediction
def predict(path,data_type,model,size):
    pred = model(load_data(path,data_type,size).to(DEVICE))
    pred = torch.argmax(F.softmax(pred,dim=1),dim=1).squeeze(0).float().cpu()

    return pred









