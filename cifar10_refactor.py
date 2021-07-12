# -*- coding: utf-8 -*-

import torch
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

if __name__=='__main__':

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # CUDA 기기가 존재한다면, 아래 코드가 CUDA 장치를 출력합니다:

    print(device)

    transform = transforms.Compose(
        [transforms.ToTensor(),
         transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    '''
    여러 transform들을 Compose로 구성
    여기서는 ToTensor와 Normalize를 Compose
    ToTensor: numpy 배열을 pytorch tensor로 변형
    Normalize: 평균과 표준편차 사용해서 이미지 정규화
    Normalize(mean, std, inplace=False)
    inplace=True로 하면 내용이 바뀜, False면 따로 변수에 넣어줘야 함
    '''

    batch_size = 4
    # batch size를 4로 고정

    trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                            download=True, transform=transform)
    '''
    root  : root directory of dataset
    train : if True, 데이터셋을 training set에서 만든다. False면 test set에서
    download: True면 다운로드 해서 root directory에 넣음
    transform: optional, PIL image를 받아서 transformed 버전으로 만드는 function(transform)
    '''

    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size,
                                              shuffle=True, num_workers=2)
    '''
    trainset: dataset
    shuffle: True면 매 epoch마다 shuffle함
    num_workers: data loading 과정에서 얼마나 많은 subprocess들을 사용할지
    '''

    testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                           download=True, transform=transform)


    testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size,
                                             shuffle=False, num_workers=2)


    classes = ('plane', 'car', 'bird', 'cat',
               'deer', 'dog', 'frog', 'horse', 'ship', 'truck')


    class Net(nn.Module):
      #https://guru.tistory.com/70
        def __init__(self):
            super().__init__()
            # 첫번째 2D 합성곱 계층
            # 1개의 입력 채널(이미지)을 받아들이고, 3개의 입력 채널(rgb), 커널사이즈가 5인 6개의 합성곱.
            self.conv1 = nn.Conv2d(3, 6, 5)
            self.pool = nn.MaxPool2d(2, 2)
            #2*2 max pooling
            self.conv2 = nn.Conv2d(6, 16, 5)
            # 첫번째 fully connected layer
            self.fc1 = nn.Linear(16 * 5 * 5, 120)
            #https://deepinsight.tistory.com/86
            #input,output
            #input-> output channel * (dimension of input image 5*5)
            self.fc2 = nn.Linear(120, 84)
            self.fc3 = nn.Linear(84, 10)
            #최종이 10인 이유: class가 10개

        def forward(self, x):
            #계산 그래프(즉, 신경망)에 데이터를 지나가게 하는 forward 함수
            x = self.pool(F.relu(self.conv1(x)))
            #Conv2d->relu->pooling으로 진행
            #pooling: input size 줄이기, overfitting 조절, 특징 더 잘 뽑음
            x = self.pool(F.relu(self.conv2(x)))
            x = torch.flatten(x, 1) # flatten all dimensions except batch
            # start_dim=1으로 x를 압축합니다.
            x = F.relu(self.fc1(x))
            x = F.relu(self.fc2(x))
            x = self.fc3(x)
            return x


    net = Net()
    net = net.to(device)


    criterion = nn.CrossEntropyLoss()
    #Loss function을 CrossEntropyLoss 사용
    #softmax와 cross-entropy 합친 method임
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
    #optimizer로는 SGD(stochastic gradient descent: batch 단위로 Loss function 계산) 사용, learning raet=0.001, momentum=0.9
    #net은 위에서 정의한 model, momentum(관성) 값을 주면 local minimum을 탈출해서 minimum을 찾을 수 있음(local minimum에서 바로 멈추지 않음)

    #학습
    for epoch in range(2):  # loop over the dataset multiple times
    # 2번 반복
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
          #아까 만든 trainloader 이용, 뒤에 0은 label임
            # get the inputs; data is a list of [inputs, labels]
            inputs, labels = data[0].to(device), data[1].to(device)
            # zero the parameter gradients
            optimizer.zero_grad()
            #Pytorch에서는 gradients값들을 추후에 backward를 해줄때 계속 더해주기 때문에 매번 zero로 만들어줘야 함
            # forward + backward + optimize
            outputs = net(inputs)
            #input을 아까 만든 model net에다가 넣음
            loss = criterion(outputs, labels)
            #loss 계산
            loss.backward()
            #loss를 back propagation
            # autograd 를 사용하여 역전파 단계를 계산합니다. 이는 requires_grad=True를 갖는
            # 모든 텐서들에 대한 손실의 변화도를 계산합니다.
            optimizer.step()
            # 가중치 갱신

            # print statistics
            running_loss += loss.item()
            if i % 2000 == 1999:    # print every 2000 mini-batches
                print('[%d, %5d] loss: %.3f' %
                      (epoch + 1, i + 1, running_loss / 2000))
                running_loss = 0.0

    print('Finished Training')

    PATH = './cifar_net.pth'
    torch.save(net.state_dict(), PATH)
    #모델 저장

    correct = 0
    total = 0
    # since we're not training, we don't need to calculate the gradients for our outputs
    with torch.no_grad():
        for data in testloader:
            images, labels = data
            # calculate outputs by running images through the network
            outputs = net(images)
            # the class with the highest energy is what we choose as prediction
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            #.size(0) returns first dimension of label size
            correct += (predicted == labels).sum().item()
            #predicted와 실제 label이 동일한 경우의 합(batch size기 때문에)

    print('Accuracy of the network on the 10000 test images: %d %%' % (
        100 * correct / total))

    # 각 분류(class)에 대한 예측값 계산을 위해 준비
    correct_pred = {classname: 0 for classname in classes}
    total_pred = {classname: 0 for classname in classes}

    # 변화도는 여전히 필요하지 않습니다
    with torch.no_grad():
        for data in testloader:
            images, labels = data
            outputs = net(images)
            _, predictions = torch.max(outputs, 1)
            # 각 분류별로 올바른 예측 수를 모읍니다
            for label, prediction in zip(labels, predictions):
                if label == prediction:
                    correct_pred[classes[label]] += 1
                total_pred[classes[label]] += 1


    # 각 분류별 정확도(accuracy)를 출력합니다
    for classname, correct_count in correct_pred.items():
        accuracy = 100 * float(correct_count) / total_pred[classname]
        print("Accuracy for class {:5s} is: {:.1f} %".format(classname,
                                                       accuracy))