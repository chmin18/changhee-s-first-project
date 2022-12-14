# 수정됐다 이 부분
# CNN code from EE488 [Week10]
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import torch.nn.functional as F
# from torchsummary import summary
from tqdm import tqdm
# from sklearn.preprocessing import StandardScaler
import time
# import matplotlib.pyplot as plt

import scipy.io as sio
from torch.utils.data import DataLoader, Dataset
import numpy as np

# Convolutional layer can be defined by torch.nn.Conv2d
# CNN needs number of input channel / number of output channel / size of kernel


################### Data loading
arr = sio.loadmat('traindata.mat')
train_data = arr['I']
print(torch.FloatTensor(train_data).shape)
train_labels = arr['label']
test_data = arr['I']
test_labels = arr['label']

################### Dataset
class MyDataset(Dataset):
    def __init__(self, x_data, y_data):
        self.x_data = torch.FloatTensor(x_data)
        self.x_data = self.x_data.permute(2,0,1).unsqueeze(1)
        self.y_data = torch.LongTensor(y_data)
        self.y_data = self.y_data.permute(1,0)
        self.len = self.y_data.shape[0]

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.len

trainset = MyDataset(train_data, train_labels)
testset = MyDataset(test_data, test_labels)

trainloader = DataLoader(trainset, batch_size=10, shuffle=True)
testloader = DataLoader(testset, batch_size=10, shuffle=False)

# Check the format
# print(trainset[0][0].size())
# dataiter = iter(trainloader)
# images, labels = dataiter.next()
# print(images.size())

#################### CNN Implementation
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=32, kernel_size=(5,5))
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=32, kernel_size=(5,5))
        self.pool2 = nn.AvgPool2d(kernel_size=2, stride=2)
        self.conv3 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=(5,5))
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(in_features=75264, out_features=2)

    def forward(self, x):
        batchsize = x.size(0)
        x = self.conv1(x)
        x = self.pool1(F.relu(x))
        x = self.conv2(x)
        x = self.pool2(F.relu(x))
        x = self.conv3(x)
        x = self.pool3(F.relu(x))
        x = x.view(batchsize, -1)
        out = self.fc1(x)
        return out

def train(model, n_epoch, loader, optimizer, criterion, device="cpu"):
    model.train()
    for epoch in tqdm(range(n_epoch)):
        running_loss = 0.0
        for i, data in enumerate(loader, 0):
            images, labels = data
            images = images.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()

            outputs = model(images)
            loss = criterion(input=outputs, target=labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        print('Epoch {}, loss = {:.3f}'.format(epoch, running_loss/len(loader)))
    print('Training Finished')

cnn_model = CNN()
optimizer = optim.SGD(params = cnn_model.parameters(), lr=0.001, momentum=0.9)
criterion = nn.CrossEntropyLoss()
train(model=cnn_model, n_epoch=1, loader=trainloader, optimizer=optimizer, criterion=criterion)



# # Functions for visualizing features of CNN.
# def vis_feat(f1, f2, inp):
#     l = [f1, f2]
#     fig, axes = plt.subplots(11, 8, figsize=(12.5, 12.5))
#     plt.subplots_adjust(left = 0, bottome = 0, right = 1, top = 1, wspace = 0, hspace = 0.1)
#     ax = axes[0,0]
#     ax.imshow(inp[0], cmap='gray_r')
#     ax.set_title('Original image')    
#     ax.axis('off') 

#     for i in range(7):
#         ax = axes[0,i+1]
#         ax.axis('off')  

#     for i in range(32):
#         r = 2 + i // 8
#         c = i % 8
#         ax = axes[r, c]             
#         ax.imshow(f1[i], cmap='gray_r')
#         if i == 0:
#             ax.set_title('Output from conv1')      
#         ax.axis('off')
#         if i < 8:
#             ax = axes[1, i]
#             ax.axis('off')

#     for i in range(32):
#         r = 7 + i // 8
#         c = i % 8
#         ax = axes[r, c]             
#         ax.imshow(f2[i], cmap='gray_r')
#         if i == 0:
#             ax.set_title('Output from conv2')      
#         ax.axis('off')
#         if i < 8:
#             ax = axes[6, i]
#             ax.axis('off')

#     plt.xticks([]), plt.yticks([])
#     plt.show()

# def vis(model, loader):
#     with torch.no_grad():
#         for i, data in enumerate(loader, 0):
#             images, labels = data
#             f1 = model.conv1(images)
#             f2 = model.conv2(model.pool(F.relu(f1)))

#             vis_feat(f1[0], f2[0], images[0])
#             break


