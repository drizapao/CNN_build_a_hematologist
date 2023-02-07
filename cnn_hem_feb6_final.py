

## pre-trained model but with 10 classes (modifying final layer to output a 10-dimensional vector)
import os
from time import time
from tqdm import tqdm
import numpy

import torch
import torch.nn as nn
from torch.nn import Linear, CrossEntropyLoss
from torch.optim import Adam
from torch.utils.data import DataLoader

import torchvision
from torchvision.datasets import ImageFolder
from torchvision.models import resnet50
from torchvision.transforms import transforms


# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

##
tfm = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

##
import torch
from torch.utils.data import Dataset
from torchvision import datasets
from torchvision.transforms import ToTensor
import matplotlib.pyplot as plt


import os
import pandas as pd
from torchvision.io import read_image

class CustomImageDataset(Dataset):
    def __init__(self, annotations_file, img_dir, transform=None, target_transform=None):
        self.img_labels = pd.read_csv(annotations_file)
        self.img_dir = img_dir
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.img_labels)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.img_labels.iloc[idx, 0])
        image = read_image(img_path)
        label = self.img_labels.iloc[idx, 2]
        if self.transform:
            image = self.transform(image)
        if self.target_transform:
            label = self.target_transform(label)
        return image, label

training_data = CustomImageDataset('training_data.csv', 'training_3', tfm)
testing_data = CustomImageDataset('test_label.csv','testing_3', tfm)

len_training_dat = training_data.__len__()
len_test_dat = testing_data.__len__()

from torch.utils.data import DataLoader

train_dataloader = DataLoader(training_data, batch_size=64, shuffle=True, num_workers=1, pin_memory=True)
test_dataloader = DataLoader(testing_data, batch_size=64, shuffle=True, num_workers=1, pin_memory=True)


##
model = resnet50(pretrained=True)
model.fc = nn.Linear(in_features=2048, out_features=10, bias=True)

model = model.to(device)

#Loss function & optimizer

import torch.optim as optim


loss_fn = nn.CrossEntropyLoss()
optimiser = optim.Adam(model.parameters(), lr=0.001)

#freeze pre-trained layers

for param in model.parameters():
  param.requires_grad = True


import numpy as np

for epoch in range(32):
    start = time()
    
    tr_acc = 0
    test_acc = 0
    
    # Train
    model.train()
    
    with tqdm(train_dataloader, unit="batch") as tepoch:
        for xtrain, ytrain in tepoch:
            xtrain, ytrain = xtrain.to(device), ytrain.to(device)
            
            print(xtrain)
            print(xtrain.shape)
            print(xtrain.type())
            print(ytrain)
            print(ytrain.shape)
            print(ytrain.type())

            train_prob = model(xtrain)
            print(train_prob)
            print(train_prob.shape)
            print(train_prob.type())
            
            
            optimiser.zero_grad()

            loss = loss_fn(train_prob, ytrain)
            loss.backward()
            optimiser.step()
            
            # training ends
            
            train_pred = torch.max(train_prob, 1).indices
            tr_acc += int(torch.sum(train_pred == ytrain))
            
        ep_tr_acc = tr_acc / len_training_dat
    
    # Evaluate
    model.eval()
    with torch.no_grad():
        for xtest, ytest in test_dataloader:
            xtest, ytest = xtest.to(device), ytest
            test_prob = model(xtest)
            test_prob = test_prob.cpu()
            
            test_pred = torch.max(test_prob,1).indices
            test_acc += int(torch.sum(test_pred == ytest))
            
        ep_test_acc = test_acc / len_test_dat
    
    end = time()
    duration = (end - start) / 60
    
    print(f"Epoch: {epoch}, Time: {duration}, Loss: {loss}\nTrain_acc: {ep_tr_acc}, Test_acc: {ep_test_acc}")
