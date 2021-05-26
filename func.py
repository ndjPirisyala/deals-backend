from PIL import Image, ImageDraw, ImageFont
import urllib.request, time, random
from config import alpha

basewidth = 900

def resize(image:str, old_price:str, price:str, currency:str):
    img1 = Image.new('RGBA', (2000, 2000), (255, 255, 255, 255))
    img = Image.open(urllib.request.urlopen(image))
    print(img.size)
    if img.size[0] < img.size[1]:
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    else:
        hpercent = (basewidth / float(img.size[1]))
        wsize = int((float(img.size[0]) * float(hpercent)))
        img = img.resize((wsize, basewidth), Image.ANTIALIAS)
    bg_w, bg_h = img1.size
    img_w, img_h = img.size

    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    img1.paste(img, offset)
    draw = ImageDraw.Draw(img1) 
    font = ImageFont.truetype("BPtypewriteDamagedStrikethroughItalics.ttf", 140)
    font2 = ImageFont.truetype("LiberationSans-Bold.ttf", 180)
    if not old_price == -1.0:
        draw.text((bg_w - 1100, bg_h - 300),f"{currency}{old_price}",(112,128,144),font=font, stroke_width=4, stroke_fill='black')
    draw.text((bg_w - 800, bg_h - 200),f"{currency}{price}",(255,140,0),font=font2,  stroke_width=4, stroke_fill='black')
    draw = ImageDraw.Draw(img1) 
    draw.line((0,bg_h-400, 0,bg_h), fill=(250,250,0,250), width=60)
    draw.line((30,bg_h-550, 30,bg_h-30), fill=(50,250,50,250), width=30)
    draw.line((0,bg_w, 700,bg_w), fill=(250,250,0,250), width=60)
    draw.line((45,bg_w-40, 800,bg_w-40), fill=(50,250,50,250), width=20)
    draw.line((bg_w-500,0, bg_w,0), fill=(250,0,250,250), width=60)
    draw.line((bg_w-600,30, bg_w,30), fill=(50,250,50,250), width=30)
    draw.line((bg_w,0, bg_w,600), fill=(250,0,250,250), width=60)
    draw.line((bg_w-40,45, bg_w-40,500), fill=(50,250,50,250), width=20)
    img1.save("a.png")

# resize(image="https://images-na.ssl-images-amazon.com/images/I/61QTyA4sD1L._AC_SL1200_.jpg", old_price="12", price='30', currency="$")




