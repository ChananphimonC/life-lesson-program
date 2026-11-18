"""Contact sheet of frames: python contact.py out.png cols frame1.png frame2.png ..."""
import sys
from PIL import Image
out, cols, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
ims = [Image.open(f).resize((640, 360)) for f in files]
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 640 + (cols + 1) * 8, rows * 360 + (rows + 1) * 8), (30, 30, 30))
for i, im in enumerate(ims):
    sheet.paste(im, (8 + (i % cols) * 648, 8 + (i // cols) * 368))
sheet.save(out)
