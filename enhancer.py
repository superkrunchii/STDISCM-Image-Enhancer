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
    def __init__(self, processID, queue, n_images, dest_path, brightness, sharpness, contrast):
        multiprocessing.Process.__init__(self)
        self.id = processID
        self.n_images = n_images
        self.brightness = brightness
        self.sharpness = sharpness
        self.contrast = contrast
        self.dest = dest_path
        self.queue = queue
        self.imgs = []

    # Saves the image file to target directory
    def create_img_file(self, src_img, enhanced_img, dest):
        format = 'JPEG' if src_img[1][src_img[1].rfind('.') + 1:] == 'jpg' else src_img[1][src_img[1].rfind('.') + 1:].upper()
        # print(dest + "/" + src_img[1][:src_img[1].rfind('.')] + "_enhanced." + src_img[1][src_img[1].rfind('.') + 1:])
        enhanced_img.save(dest + "/" + src_img[1][:src_img[1].rfind('.')] + "_enhanced." + src_img[1][src_img[1].rfind('.') + 1:], format)
    
    def run(self):
        for _ in range(self.n_images):
            print("process: ", self.id, "Enhancing Image")
            img = self.queue.get()
            self.imgs.append(img)
            conv_img = img[0].convert("RGB")
            # Enhance brightness by given factor
            bri = ImageEnhance.Brightness(conv_img).enhance(self.brightness)
            con = ImageEnhance.Contrast(bri).enhance(self.contrast)
            sharp = ImageEnhance.Sharpness(con).enhance(self.sharpness)
            self.create_img_file(img, sharp, self.dest)
        print("Process", self.id, "Enhanced Images: ", str(self.imgs))

class Producer(multiprocessing.Process):
    def __init__ (self, src_path, queue):
        multiprocessing.Process.__init__(self)
        self.image_list = []
        self.queue = queue
        self.src = src_path
        self.valid_formats = [".jpg", ".gif", ".png"]
    def run(self):
        for f in os.listdir(self.src):
            ext = os.path.splitext(f)[1]
            if ext.lower() not in self.valid_formats:
                continue
            img = Image.open(os.path.join(self.src, f))
            # src_imgs.append([img, img.filename[img.filename.rfind('\\') + 1:]])
            self.queue.put([img, img.filename[img.filename.rfind('\\') + 1:]])
            self.image_list.append([img, img.filename[img.filename.rfind('\\') + 1:]])
        print("Produced Images: ", str(self.image_list))
        


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

    count = len([e for e in os.listdir(src_path) if os.path.isfile(os.path.join(src_path, e))])
    print("number of images:", count)
    n_images = int(count/n_threads)
    
    c_threads = []
    
    p = Producer(src_path, queue)
    p.start()


    for i in range(n_threads):
        if i == n_threads - 1:
            n_images += count - (n_images * n_threads)
        c = Enhancer(i, queue, n_images, dest_path, brightness, sharpness, contrast)
        c_threads.append(c)
        c.start()
    p.join()
    
    for c in c_threads:
        c.join(5) 

    end = time.time()

    run_time = end - start
    print("Execution time: ", run_time, "seconds")
