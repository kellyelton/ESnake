import torch
from snake import Snake


class BotNet:
    def __init__(self, canvas, cell_size, bot: Snake, model, view_distance):
        self.canvas = canvas
        self.cell_size = cell_size
        self.bot = bot
        self.model = model
        self.view_distance = view_distance

    def update_model(self, model):
        print('updating model')
        self.model = model

    def update(self, level):
        # get prediction from model
        # input of the model is the a 10 square radious around the bot
        # the outputs (float, float) are the direction

        # get the 10x10 grid around the bot
        grid = []
        for x in range(-self.view_distance, self.view_distance):
            for y in range(-self.view_distance, self.view_distance):
                entity = level.at((self.bot.position[0][0] + x, self.bot.position[0][1] + y))

                grid.append(self.entity_to_float(entity, level))
 
        # inputs are the direction [int, int] and the grid
        direction = self.direction_to_floats(self.bot.direction)

        # combine the direction and grid arrays into tensor
        inputs = direction + grid

        # inputs to tensor
        inputs = torch.tensor(inputs, dtype=torch.float)

        # get the prediction from the model
        prediction = self.model(inputs)

        # convert the prediction to a direction
        direction = self.floats_to_direction(prediction)

        if direction is not None and direction != self.bot.direction:
            #print(f'Changing direction from {self.bot.direction} to {direction}')
            # set the direction of the bot
            self.bot.change_direction(direction)

    @staticmethod
    def direction_to_floats(direction):
        if direction == 'up':
            return [0, -1]
        elif direction == 'right':
            return [1, 0]
        elif direction == 'down':
            return [0, 1]
        elif direction == 'left':
            return [-1, 0]
        else:
            raise Exception(f'Invalid direction {direction}')
    
    @staticmethod
    def floats_to_direction(floats):
        # verify floats are in expected range of [-1, 1]
        if floats[0] < -1 or floats[0] > 1:
            raise Exception(f'Invalid floats value: [{floats[0]}, {floats[1]}]')

        floats = (floats > 0.8).int()

        if floats[0] == 0 and floats[1] == -1:
            return 'up'
        elif floats[0] == 1 and floats[1] == 0:
            return 'right'
        elif floats[0] == 0 and floats[1] == 1:
            return 'down'
        elif floats[0] == -1 and floats[1] == 0:
            return 'left'
        else:
            return None
        #    raise Exception('Invalid direction')

    @staticmethod
    def entity_to_float(entity, level):
        if entity is None:
            return 0
        elif entity is level.snake:
            return -1
        elif entity in level.foods:
            return 1
        else:
            return -1
