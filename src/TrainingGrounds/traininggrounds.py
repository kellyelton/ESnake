import tkinter as tk
from level1 import Level1


def main():
    window = tk.Tk()
    window.title('Training Grounds - Level 1')
    window.resizable(False, False)
    window.tk.call('tk', 'scaling', 4.0)
    game = Level1(
        window,
        800,
        800,
        25,
        40,
        20,
        2,
        4,
        10
    )
    game.play()
    window.mainloop()


if __name__ == '__main__':
    main()
