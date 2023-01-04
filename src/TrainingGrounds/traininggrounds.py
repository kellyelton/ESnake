import tkinter as tk
from level1 import Level1


def main():
    window = tk.Tk()
    window.title('Training Grounds - Level 1')
    window.resizable(False, False)
    window.tk.call('tk', 'scaling', 4.0)
    game = Level1(
        window,
        width=800,
        height=800,
        cell_size=25,
        speed=1,
        food_count=3,
        bot_count=3,
        bot_view_distance=4,
        train_epochs=500
    )
    game.play()
    window.mainloop()


if __name__ == '__main__':
    main()
