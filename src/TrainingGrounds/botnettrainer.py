from torch import nn
import torch
import os
import time
import random


class BotNetTrainer:
    def __init__(self, file_name, x_length, y_length, train_epochs=100):
        self.file_name = file_name
        self.x_length = x_length
        self.y_length = y_length
        self.train_epochs = train_epochs
        self.data = []
        self.optimizer = None
        self.best_avg_loss = 1

        self.model = self.create_model(x_length, y_length)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.0001)

        self.loss_function = nn.MSELoss()
    
    def load_and_train(self):
        # load data
        training_data = self.load_data()

        if training_data is None:
            return
    
        # train model
        self.train_model(training_data)
    
    def load_data(self):
        TRAIN_DATA_COUNT = 50

        x_train = []
        y_train = []
        
        # if csv file doesn't exist, return None
        if not os.path.exists(self.file_name):
            return None

        # if length of csv file is less than TRAIN_DATA_COUNT lines, return None
        line_count = 0
        with open(self.file_name, 'r') as f:
            line_count = sum(1 for line in f)
            if line_count < TRAIN_DATA_COUNT:
                return None

            lines_to_skip = random.randint(0, line_count - TRAIN_DATA_COUNT)
            f.seek(0)
            for i in range(lines_to_skip):
                f.readline()

            for i in range(0, 50):
                line = f.readline()
                # skip lines that are just whitespace or empty
                if line.strip() == '':
                    i -= 1
                    continue

                # parse csv line
                line = line.strip().split(',')

                # take first x_length values
                x_train.append([float(x) for x in line[:self.x_length]])
                # take last y_length values
                y_train.append([float(y) for y in line[-self.y_length:]])
        
        return (x_train, y_train)

    def train_model(self, training_data):
        x, y = training_data

        # convert to tensors
        x = torch.tensor(x)
        y = torch.tensor(y)

        start_time = time.time()
        losses = []
        # train model
        for epoch in range(self.train_epochs):
            # forward pass
            y_pred = self.model(x)

            # calculate loss
            loss = self.loss_function(y_pred, y)

            # backpropagation
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            losses.append(loss.item())

        avg_loss = sum(losses) / len(losses)

        if avg_loss < self.best_avg_loss:
            self.best_avg_loss = avg_loss
            print(f'New best average loss: {avg_loss}')
            # save model to standard nn file format
            #file_name = 'model.pt'
            #torch.save(self.model, file_name)
            #print(f'Model saved to {file_name}')

        #print(f'Average loss: {avg_loss} in {epoch_run_time} seconds')
        
        # save model to standard nn file format
        #file_name = 'model.pt'
        #torch.save(self.model, file_name)
        #print(f'Model saved to {file_name}')
        
    def create_model(self, input_size, output_size):
        # create pytorch model
        # output values should be between -1 and 1

        model = nn.Sequential(
            nn.Linear(input_size, input_size // 2 ),
            nn.Linear(input_size // 2, 2),
            nn.Tanh()
        )

        return model

