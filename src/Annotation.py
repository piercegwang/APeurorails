from PIL import Image, ImageDraw
import sys
image = Image.open("../database/board.jpg")
draw  = ImageDraw.Draw(image)
font  = ImageFont.truetype("../database/arial.ttf", 50, encoding="unic")
draw.text((2005,1581), "X", font=font, fill=(0,0,0,255))
image.show()