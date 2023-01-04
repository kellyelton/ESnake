class Food:
    def __init__(self, canvas, cell_size, start_position):
        self.canvas = canvas
        self.cell_size = cell_size
        self.position = start_position
        self.food = self.canvas.create_oval(self.position[0] * self.cell_size, self.position[1] * self.cell_size, self.position[0] * self.cell_size + self.cell_size, self.position[1] * self.cell_size + self.cell_size, fill='red')

    def move(self, new_position):
        self.canvas.delete(self.food)
        self.position = new_position
        self.food = self.canvas.create_oval(self.position[0] * self.cell_size, self.position[1] * self.cell_size, self.position[0] * self.cell_size + self.cell_size, self.position[1] * self.cell_size + self.cell_size, fill='red')