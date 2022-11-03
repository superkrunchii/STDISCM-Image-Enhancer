from PIL import Image
from PIL import ImageEnhance
import os, os.path

"""
    Input:
    Src dir
    Target dir
    Enhancing time in minutes
    Brightness enhancement factor
    Sharpness enhancement factor
    Contrast enhancement factor
    Num threads

    Output:
    Enhanced images
    txt file of statistics
"""
# Saves the image file to target directory
def create_img_file(src_img, enhanced_img, dest):
    format = 'JPEG' if src_img[1][src_img[1].rfind('.') + 1:] == 'jpg' else src_img[1][src_img[1].rfind('.') + 1:].upper()
    enhanced_img.save(dest + "/" + src_img[1][:src_img[1].rfind('.')] + "_enhanced." + src_img[1][src_img[1].rfind('.') + 1:], format)

# Import source pictures + get filename for organized output
src_imgs = []
src_path = "./src_img"
dest_path = "./target_img"
valid_formats = [".jpg", ".gif", ".png"]
for f in os.listdir(src_path):
    ext = os.path.splitext(f)[1]
    if ext.lower() not in valid_formats:
        continue
    img = Image.open(os.path.join(src_path, f))
    src_imgs.append([img, img.filename[img.filename.rfind('\\') + 1:]])

for img in src_imgs:
    conv_img = img[0].convert("RGB")
    # Enhance brightness by given factor
    bri = ImageEnhance.Brightness(conv_img).enhance(2)
    con = ImageEnhance.Contrast(bri).enhance(8.3)
    sharp = ImageEnhance.Sharpness(con).enhance(2.3)
    create_img_file(img, sharp, dest_path)