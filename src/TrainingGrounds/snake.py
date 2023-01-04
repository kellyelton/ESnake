import random


class Snake:
    def __init__(self, canvas, cell_size, start_pos, color):
        self.canvas = canvas
        self.cell_size = cell_size
        self.color = color
        self.initial_position = [start_pos]
        self.position = self.initial_position
        self.direction = random.choice(['left', 'right', 'up', 'down'])
        self.segments = [self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size, x * self.cell_size + self.cell_size, y * self.cell_size + self.cell_size, fill='white') for x, y in self.position]
        self.head = self.position[-1]
        self.is_paused = False
        self.score = 0

    def pause(self):
        self.is_paused = True

    def move(self):
        x, y = self.head
        if self.direction == 'left':
            x -= 1
        elif self.direction == 'right':
            x += 1
        elif self.direction == 'up':
            y -= 1
        elif self.direction == 'down':
            y += 1
        self.position = self.position[1:] + [(x, y)]
        self.head = self.position[-1]
        for segment, position in zip(self.segments, self.position):
            self.canvas.coords(segment, position[0] * self.cell_size, position[1] * self.cell_size, position[0] * self.cell_size + self.cell_size, position[1] * self.cell_size + self.cell_size)

    def add_segment(self):
        x, y = self.position[0]
        if self.direction == 'left':
            x += 1
        elif self.direction == 'right':
            x -= 1
        elif self.direction == 'up':
            y += 1
        elif self.direction == 'down':
            y -= 1
        self.position = [(x, y)] + self.position
        self.segments.insert(0, self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size, x * self.cell_size + self.cell_size, y * self.cell_size + self.cell_size, fill=self.color))

    def change_direction(self, direction, unpause=False):
        if direction is None: return
        if direction == self.direction: return

        if unpause and self.is_paused:
            self.is_paused = False

        if direction == 'left' and self.direction != 'right':
            self.direction = direction
        elif direction == 'right' and self.direction != 'left':
            self.direction = direction
        elif direction == 'up' and self.direction != 'down':
            self.direction = direction
        elif direction == 'down' and self.direction != 'up':
            self.direction = direction

    def check_collision(self, level):
        x, y = self.head

        x = x * self.cell_size
        y = y * self.cell_size

        # check if colliding with wall
        if x < 0 or x > level.width - 1 or y < 0 or y > level.height - 1:
            return True

        # check if colliding with itself
        if self.head in self.position[:-1]:
            return True

        if self is not level.snake:
            if self.head in level.snake.position:
                return True
        else:
            if self.head in level.snake.position[:-1]:
                return True

        # check if colliding with any bots
        for bot in level.bots:
            bot_snake = bot[0]
            if bot_snake is self: continue
            if self.head in bot_snake.position:
                return True

        return False
