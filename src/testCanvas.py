from tkinter import Tk, Canvas, Frame, BOTH, NW
from PIL import Image, ImageTk


class Board(Frame):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.master.title("")
        self.pack(fill=BOTH, expand=1)

        self.img = Image.open("../database/board.jpg")
        self.board = ImageTk.PhotoImage(self.img)

        canvas = Canvas(self, width=self.img.size[0],
                        height=self.img.size[1])
        canvas.create_image(10, 10, anchor="nw", image=self.board)
        canvas.pack(fill=BOTH, expand=1)


def main():
    root = Tk()
    ex = Board()
    root.mainloop()


if __name__ == '__main__':
    main()