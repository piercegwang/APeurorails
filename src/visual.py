from PIL import Image, ImageDraw, ImageTk
import tkinter as tk

class Visual:
    LINE_THICKNESS = 2
    CIRCLE_THICKNESS = 2
    RADIUS = 6
    references = {(0, 0): (505, 402),  # Paris
                  (-9, -19): (210, 669),  # Madrid
                  (15, -13): (645, 583),  # Milano
                  (26, -8): (860, 513),  # Wien
                  (17, 5): (820, 330),  # Berlin
                  (10, 20): (827, 117),  # Goteburg
                  (-10, 16): (468, 177),  # Manchester
                  (7, 4): (650, 344),  # Ruhr
                  (-21, -17): (32, 637),  # Lisboa
                  (-14, -25): (81, 749),  # Sevilla
                  (1, -14): (410, 598),  # Toulouse
                  (21, -15): (722, 611),  # Venezia
                  (25, -25): (705, 749),  # Roma
                  (39, -19): (983, 665),  # Beograd
                  (35, -22): (895, 708),  # Sarajevo
                  (28, -15): (836, 611),  # Zagreb
                  (-21, 17): (304, 163),  # Cork
                  (27, 2): (958, 373),  # Lodz
                  (8, 9): (705, 274),  # Bremen
                  (-18, 19): (363, 135),  # Dublin
                  (-17, 22): (402, 93),  # Belfast
                  }
    X_CONST = (16.21, -0.1)
    Y_CONST = (8.0645, 14.03)

    def __init__(self, board_file):
        self.filepath = board_file
        self.board = Image.open(self.filepath)
        self.board = self.board.resize((4096 // 4, 3281 // 4), Image.ANTIALIAS)
        self.draw = ImageDraw.Draw(self.board)

        # Create tkinter window
        self.window = tk.Tk()
        self.tk_img = ImageTk.PhotoImage(self.board)
        self.panel = tk.Label(self.window, image=self.tk_img)
        self.panel.pack(side="bottom", fill="both", expand="yes")

    def draw_path(self, points, color=0):
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            if is_one_step(p2[0] - p1[0], p2[1] - p1[1]):
                p1 = self.coordinates_to_pixels(p1)
                p2 = self.coordinates_to_pixels(p2)
                self.draw.line([p1, p2], fill=color, width=Visual.LINE_THICKNESS)

    def mark_city(self, city_loc, color=0):
        city_loc = self.coordinates_to_pixels(city_loc)
        for i in range(Visual.RADIUS, Visual.RADIUS + Visual.CIRCLE_THICKNESS):
            self.draw.ellipse((city_loc[0] - i, city_loc[1] - i, city_loc[0] + (i - 1), city_loc[1] + (i - 1)),
                              outline=color)
            self.draw.ellipse(
                (city_loc[0] - (i - 1), city_loc[1] - (i - 1), city_loc[0] + (i - 1), city_loc[1] + (i - 1)),
                outline=color)
            self.draw.ellipse((city_loc[0] - i, city_loc[1] - i, city_loc[0] + i, city_loc[1] + i),
                              outline=color)

    def clean(self):
        self.board = Image.open(self.filepath)
        self.board = self.board.resize((4096 // 4, 3281 // 4), Image.ANTIALIAS)
        self.draw = ImageDraw.Draw(self.board)

    def update(self):
        self.tk_img = ImageTk.PhotoImage(self.board)
        self.panel.configure(image=self.tk_img)
        self.window.update()

    def quit(self):
        self.window.quit()

    def coordinates_to_pixels(self, coords):
        def get_closest_reference(coords):
            def distance(p1, p2):
                return abs(p2[1] - p1[1]) + abs(p2[0] - p1[0])

            closest_reference = None
            for r in Visual.references:
                if closest_reference is None or distance(coords, r) < distance(coords, closest_reference):
                    closest_reference = r
            return closest_reference

        ref = get_closest_reference(coords)
        pixel = list(Visual.references[ref])

        delta = (coords[0] - ref[0], coords[1] - ref[1])

        pixel[0] += round(Visual.X_CONST[0] * (delta[0] + 0.5 * delta[1])) + round(Visual.X_CONST[1] * delta[1])
        pixel[1] -= round(Visual.Y_CONST[1] * delta[1])
        # print(ref, pixel)
        return tuple(pixel)