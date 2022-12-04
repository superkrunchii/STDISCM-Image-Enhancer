from PIL import Image
from PIL import ImageEnhance
import os, os.path
from argparse import ArgumentParser
import multiprocessing
import time

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
# Enhancer Class
class Enhancer(multiprocessing.Process):
    def __init__(self, processID, n_images, src_imgs, dest_path, brightness, sharpness, contrast):
        multiprocessing.Process.__init__(self)
        self.id = processID
        self.n_images = n_images
        self.brightness = brightness
        self.sharpness = sharpness
        self.contrast = contrast
        self.src = src_imgs
        self.dest = dest_path

    # Saves the image file to target directory
    def create_img_file(self, src_img, enhanced_img, dest):
        format = 'JPEG' if src_img[1][src_img[1].rfind('.') + 1:] == 'jpg' else src_img[1][src_img[1].rfind('.') + 1:].upper()
        # print(dest + "/" + src_img[1][:src_img[1].rfind('.')] + "_enhanced." + src_img[1][src_img[1].rfind('.') + 1:])
        enhanced_img.save(dest + "/" + src_img[1][:src_img[1].rfind('.')] + "_enhanced." + src_img[1][src_img[1].rfind('.') + 1:], format)
    
    def run(self):
        for _ in range(self.n_images):
            img = self.src.get()
            conv_img = img[0].convert("RGB")
            # Enhance brightness by given factor
            bri = ImageEnhance.Brightness(conv_img).enhance(2)
            con = ImageEnhance.Contrast(bri).enhance(8.3)
            sharp = ImageEnhance.Sharpness(con).enhance(2.3)
            self.create_img_file(img, sharp, self.dest)

def write_stats():
    pass

if __name__ == "__main__":

    start = time.time()

    # Parse Arguments
    parser = ArgumentParser()
    parser.add_argument("src", type=str)
    parser.add_argument("dest", type=str)
    parser.add_argument("time", type=int)
    parser.add_argument("brightness", type=float)
    parser.add_argument("sharpness", type=float)
    parser.add_argument("contrast", type=float)
    parser.add_argument("threads", default=1, type=int)
    args = parser.parse_args()

    # Store Arguments
    src_path = args.src
    dest_path = args.dest
    enhancing_time = args.time
    brightness = args.brightness
    sharpness = args.sharpness
    contrast = args.contrast
    n_threads = args.threads

    #Create Queue
    queue = multiprocessing.Queue()

    p_threads = []
    count = 0

    # Import source pictures + get filename for organized output
    src_imgs = []
    valid_formats = [".jpg", ".gif", ".png"]
    for f in os.listdir(src_path):
        ext = os.path.splitext(f)[1]
        if ext.lower() not in valid_formats:
            continue
        img = Image.open(os.path.join(src_path, f))
        # src_imgs.append([img, img.filename[img.filename.rfind('\\') + 1:]])
        queue.put([img, img.filename[img.filename.rfind('\\') + 1:]])
        count += 1
    
    
    print("count:", count)
    n_images = count//n_threads
    print("n_images", n_images)

    for i in range(n_threads):
        p = Enhancer(i, n_images, queue, dest_path, brightness, sharpness, contrast)
        p_threads.append(p)
        p.start()

    for p in p_threads:
        p.join() 

    end = time.time()

    run_time = end - start
    print("Execution time: ", run_time, "seconds")
