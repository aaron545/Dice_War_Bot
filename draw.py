from PIL import Image, ImageDraw, ImageFont

class Draw:
  
  @staticmethod
  def getBlankImage(size, color=(240, 240, 240)):
    return Image.new('RGB', size, color)

  @staticmethod
  def addImage(img, added_img, xy):
    img_copy = img.copy()
    img_copy.paste(added_img, xy, added_img)
    return img_copy

  # x or y == -1: center
  @staticmethod
  def addText(img, xy, text, fontSize, fontType="arial.ttf", color=(0, 0, 0)):
    img_copy = img.copy()
    w, h = img.size
    x, y = xy
    draw = ImageDraw.Draw(img_copy)

    font = ImageFont.truetype(fontType, fontSize)
    font_w, font_h = draw.textsize(text, font)
    text_x = x if x != -1 else (w-font_w)//2
    text_y = y if y != -1 else (h-font_h)//2

    draw.text(
      (text_x, text_y),  # Coordinates
      text,  # Text
      color,  # Color
      font = font
    )
    return img_copy