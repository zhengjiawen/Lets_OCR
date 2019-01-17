#coding=utf-8
import torch
import torch.nn.functional as F


class Vgg_16(torch.nn.Module):

    def __init__(self):
        super(Vgg_16, self).__init__()
        self.convolution1 = torch.nn.Conv2d(1, 64, 3, padding=1)
        self.pooling1 = torch.nn.MaxPool2d(2, stride=2)
        self.convolution2 = torch.nn.Conv2d(64, 128, 3, padding=1)
        self.pooling2 = torch.nn.MaxPool2d(2, stride=2)
        self.convolution3 = torch.nn.Conv2d(128, 256, 3, padding=1)
        self.convolution4 = torch.nn.Conv2d(256, 256, 3, padding=1)
        self.pooling3 = torch.nn.MaxPool2d((1, 2), stride=(2, 1)) #notice stride of the non-square pooling
        self.convolution5 = torch.nn.Conv2d(256, 512, 3, padding=1)
        self.BatchNorm1 = torch.nn.BatchNorm2d(512)
        self.convolution6 = torch.nn.Conv2d(512, 512, 3, padding=1)
        self.BatchNorm2 = torch.nn.BatchNorm2d(512)
        self.pooling4 = torch.nn.MaxPool2d((1, 2), stride=(2, 1))
        self.convolution7 = torch.nn.Conv2d(512, 512, 2)

    def forward(self, x):
        x = F.relu(self.convolution1(x), inplace=True)
        x = self.pooling1(x)
        x = F.relu(self.convolution2(x), inplace=True)
        x = self.pooling2(x)
        x = F.relu(self.convolution3(x), inplace=True)
        x = F.relu(self.convolution4(x), inplace=True)
        x = self.pooling3(x)
        x = self.convolution5(x)
        x = F.relu(self.BatchNorm1(x), inplace=True)
        x = self.convolution6(x)
        x = F.relu(self.BatchNorm2(x), inplace=True)
        x = self.pooling4(x)
        x = F.relu(self.convolution7(x), inplace=True)
        return x


class RNN(torch.nn.Module):
    def __init__(self, class_num, hidden_unit):
        super(RNN, self).__init__()
        self.Bidirectional_LSTM1 = torch.nn.LSTM(512, hidden_unit, bidirectional=True)
        self.embedding1 = torch.nn.Linear(hidden_unit * 2, 512)
        self.Bidirectional_LSTM2 = torch.nn.LSTM(512, hidden_unit, bidirectional=True)
        self.embedding2 = torch.nn.Linear(hidden_unit * 2, class_num)

    def forward(self, x):
        x = self.Bidirectional_LSTM1(x)
        s, b, l = x[0].size()
        x = self.embedding1(x[0].view(s * b, l))
        x = x.view(s, b, -1)
        x = self.Bidirectional_LSTM2(x)
        s, b, l = x[0].size()
        x = self.embedding2(x[0].view(s * b, l))
        x = x.view(s, b, -1)
        return x


class CRNN(torch.nn.Module):
    def __init__(self, class_num, hidden_unit=256):
        super(CRNN, self).__init__()
        self.cnn = torch.nn.Sequential()
        self.cnn.add_module('vgg_16', Vgg_16())
        self.rnn = torch.nn.Sequential()
        self.rnn.add_module('rnn', RNN(class_num, hidden_unit))

    def forward(self, x):
        x = self.cnn(x)
        assert x.shape[2] == 1
        x = x.squeeze(2)
        x = x.transpose(0, 2)
        x = x.transpose(1, 2)
        x = self.rnn(x)
        return x
