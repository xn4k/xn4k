#!/usr/bin/env python3
"""Convert a black-and-white portrait to a Unicode Braille dot portrait.

Braille characters are text glyphs (2x4 dot matrix), NOT embedded photo pixels.
The user's original photo is processed locally and is not uploaded to GitHub.

Usage: pip install pillow && python scripts/make_portrait.py my-photo.jpg
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps
ROOT = Path(__file__).resolve().parents[1]
img = Image.open(sys.argv[1]).convert('L')
# The supplied 483x647 portrait: tightly crop head, face, neck and shoulders.
if img.size == (483,647):
    img=img.crop((68,35,305,315))
else:
    img=ImageOps.fit(img,(237,280),method=Image.Resampling.LANCZOS,centering=(.5,.33))
img=img.resize((118,212),Image.Resampling.LANCZOS)
# Knock out the bright studio backdrop and retain shadow/highlight details.
img=img.point(lambda p:int(min(255,max(0,(p-15)*255/(169-15)))))
img=img.convert('1',dither=Image.Dither.FLOYDSTEINBERG)
dots=[(0,0,1),(0,1,2),(0,2,3),(0,3,7),(1,0,4),(1,1,5),(1,2,6),(1,3,8)]
rows=[]
for y in range(0,img.height,4):
    chars=[]
    for x in range(0,img.width,2):
        bits=0
        for dx,dy,i in dots:
            if img.getpixel((x+dx,y+dy))<128:bits |= 1<<(i-1)
        chars.append(chr(0x2800+bits))
    rows.append(''.join(chars))
( ROOT/'assets'/'portrait-braille.txt' ).write_text('\n'.join(rows)+'\n',encoding='utf-8')
print('Saved',ROOT/'assets'/'portrait-braille.txt')
