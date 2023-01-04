import tkinter as tk
import random
from snake import Snake
from food import Food
from botnet import BotNet
from datarecorder import DataRecorder
from botnettrainer import BotNetTrainer


class Level1:
    def __init__(self, window, width, height, cell_size, speed, food_count, bot_count, bot_view_distance, train_epochs):
        self.food_count = food_count
        self.bot_count = bot_count
        self.bot_view_distance = bot_view_distance
        self.window = window
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.train_epochs = train_epochs
        self.vwidth = self.width // self.cell_size
        self.vheight = self.height // self.cell_size
        self.speed = speed
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg='black')
        self.canvas.pack()
        self.window.update()
        self.canvas.focus_set()
        x_length = (self.bot_view_distance * 2) ** 2 + 2
        y_length = 2
        self.foods = []
        self.bots = []

        if not hasattr(self, 'data_recorder'):
            self.data_recorder = DataRecorder(self.bot_view_distance)

        self.snake_color = 'white'
        self.bot_color = 'blue'
        # bright green, slighly transparent
        self.food_color = '#6631FF31'

        snake_start_pos = self.get_random_position()
        bot_start_pos = self.get_random_position()
        self.snake = Snake(self.canvas, self.cell_size, snake_start_pos, self.snake_color)
        self.snake.pause()
        for i in range(self.bot_count):
            bot_start_pos = self.get_random_position()
            bot_trainer = BotNetTrainer('data.csv', x_length, y_length, self.train_epochs)
            bot_trainer.load_and_train()
            bot_snake = Snake(self.canvas, self.cell_size, bot_start_pos, self.bot_color)
            bot_net = BotNet(self.canvas, self.cell_size, bot_snake, bot_trainer.model, self.bot_view_distance)
            bot = (bot_snake, bot_net, bot_trainer, 0)
            self.bots.append(bot)
            
        for i in range(self.food_count):
            food_start_pos = self.get_random_position()
            self.foods.append(Food(self.canvas, self.cell_size, food_start_pos))

        self.score = 0
        self.best_bot_score = 0
        self.is_game_over = False
        self.score_text = self.canvas.create_text(10, 10, text=f'Score: {self.score}', anchor='nw', font=('Arial', 14), fill='white')
        self.best_bot_score_text = self.canvas.create_text(10, 70, text=f'Best Bot Score: {self.best_bot_score}', anchor='nw', font=('Arial', 14), fill='white')

        self.window.bind('<Left>', lambda event: self.snake.change_direction('left', unpause=True))
        self.window.bind('<Right>', lambda event: self.snake.change_direction('right', unpause=True))
        self.window.bind('<Up>', lambda event: self.snake.change_direction('up', unpause=True))
        self.window.bind('<Down>', lambda event: self.snake.change_direction('down', unpause=True))

        # space bar pauses player movement
        self.window.bind('<space>', lambda event: self.snake.pause())

    def play(self):
        self.update_player()
        self.update_bots()

        if not self.is_game_over:
            self.window.after(self.speed, self.play)

    def update_player(self):
        if self.snake.is_paused:
            return
        original_direction = self.snake.direction
        original_position = self.snake.head
        self.snake.move()
        new_direction = self.snake.direction
        new_position = self.snake.head

        # if snake head is on any foods, add segment and move food
        food_index = None
        for i, food in enumerate(self.foods):
            head_x = self.snake.head[0]
            head_y = self.snake.head[1]
            food_x = food.position[0]
            food_y = food.position[1]

            if head_x == food_x and head_y == food_y:
                food_index = i
                break

        if food_index is not None:
            self.score += 1
            self.canvas.itemconfigure(self.score_text, text=f'Score: {self.score}')
            self.snake.add_segment()
            new_food_location = self.get_random_position()
            self.foods[food_index].move(new_food_location)
            self.data_recorder.record_move(self, original_position, new_position, original_direction, new_direction, False, True)
        elif self.snake.check_collision(self):
            self.data_recorder.record_move(self, original_position, new_position, original_direction, new_direction, True, False)
            self.game_over()
        else:
            self.data_recorder.record_move(self, original_position, new_position, original_direction, new_direction, False, False)

    def update_bots(self):
        for bot_index, bot in enumerate(self.bots):
            bot_snake, bot_net, bot_trainer, best_score = bot

            bot_net.update(self)

            bot_snake.move()

            # get food index if bot head is on that food
            food_index = None
            for i, food in enumerate(self.foods):
                if bot_snake.head == food.position:
                    food_index = i

            if food_index is not None:
                bot_snake.score += 1

                # if the bot beat it's own high score, update its high score
                if bot_snake.score > best_score:
                    best_score = bot_snake.score
                    self.bots[bot_index] = (bot_snake, bot_net, bot_trainer, best_score)

                    # if the bot beat the best bot score, update the best bot score
                    if bot_snake.score > self.best_bot_score:
                        self.best_bot_score = bot_snake.score
                        self.canvas.itemconfigure(self.best_bot_score_text, text=f'Best Bot Score: {self.best_bot_score}')

                bot_snake.add_segment()
                new_food_location = self.get_random_position()
                self.foods[food_index].move(new_food_location)
            elif bot_snake.check_collision(self):
                # clear bot
                for segment in bot_snake.segments:
                    self.canvas.delete(segment)

                bot_trainer.load_and_train()

                bot_start_pos = self.get_random_position()
                bot_snake = Snake(self.canvas, self.cell_size, bot_start_pos, self.bot_color)
                bot_net.bot = bot_snake

                self.bots[bot_index] = (bot_snake, bot_net, bot_trainer, best_score)

    def game_over(self):
        self.is_game_over = True
        self.window.unbind('<Left>')
        self.window.unbind('<Right>')
        self.window.unbind('<Up>')
        self.window.unbind('<Down>')
        self.canvas.create_text(self.width / 2, self.height / 2, text=f'Game Over! Score: {self.score}', fill='white', font=('Arial', 14))
        self.canvas.create_text(self.width / 2, self.height / 2 + 40, text='Press any key to play again', fill='white', font=('Arial', 14))
        self.window.bind('<Any-KeyPress>', self.restart)

    def restart(self, event):
        self.canvas.delete('all')
        self.data_recorder.clear()
        # remove canvas from window
        self.canvas.pack_forget()
        self.__init__(self.window, self.width, self.height, self.cell_size, self.speed, self.food_count, self.bot_count, self.bot_view_distance, self.train_epochs)
        self.play()

    def at(self, pos):
        # is there any food in this postion?
        for food in self.foods:
            if pos == food.position:
                return food
        
        # is there a snake in this position?
        if pos in self.snake.position:
            return self.snake
        
        # are any of the bots in this position?
        for bot in self.bots:
            bot_snake, bot_net, bot_trainer, best_score = bot
            if pos in bot_snake.position:
                return bot_snake
        
        # Is this the wall?
        if pos[0] < 0 or pos[0] > self.vwidth - 1 or pos[1] < 0 or pos[1] > self.vheight - 1:
            return "wall"
        
        # is this empty?
        return None

    def get_random_position(self):
        EMPTY_RADIUS = 4

        # make sure there's nothing within 10 cell radius of the position
        while True:
            x = random.randint(0, self.vwidth - 1)
            y = random.randint(0, self.vheight - 1)

            # am I colliding with the wall? if so continue
            if x < EMPTY_RADIUS or x > self.vwidth - EMPTY_RADIUS or y < EMPTY_RADIUS or y > self.vheight - EMPTY_RADIUS:
                continue

            # get distance to snake if it exists
            if hasattr(self, 'snake'):
                too_close = False

                for position in self.snake.position:
                    distance_to_snake = abs(x - position[0]) + abs(y - position[1])
                    if distance_to_snake < EMPTY_RADIUS:
                        too_close = True
                        break

                if too_close:
                    continue

            # get distance to bot if it exists
            if hasattr(self, 'bots'):
                too_close = False

                for bot in self.bots:
                    bot_snake, bot_net, bot_trainer, best_score = bot
                    for position in bot_snake.position:
                        distance_to_bot = abs(x - position[0]) + abs(y - position[1])
                        if distance_to_bot < EMPTY_RADIUS:
                            too_close = True
                            break
                    
                    if too_close:
                        break

                if too_close:
                    continue

            # Are any foods within EMPTY_RADIUS cell radius from this position?
            food_close_by = False
            for food in self.foods:
                distance_to_food = abs(x - food.position[0]) + abs(y - food.position[1])
                if distance_to_food < EMPTY_RADIUS:
                    food_close_by = True
                    break

            if food_close_by:
                continue

            break
     
        return x, y
