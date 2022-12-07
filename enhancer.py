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
    def __init__(self, processID, queue, lock, manager, n_images, dest_path, brightness, sharpness, contrast):
        multiprocessing.Process.__init__(self)
        self.id = processID
        self.n_images = n_images
        self.brightness = brightness
        self.sharpness = sharpness
        self.contrast = contrast
        self.dest = dest_path
        self.queue = queue
        self.lock = lock
        self.counter = manager
        self.imgs = []

    # Saves the image file to target directory
    def create_img_file(self, src_img, enhanced_img, dest):
        format = 'JPEG' if src_img[1][src_img[1].rfind('.') + 1:] == 'jpg' else src_img[1][src_img[1].rfind('.') + 1:].upper()
        # print(dest + "/" + src_img[1][:src_img[1].rfind('.')] + "_enhanced." + src_img[1][src_img[1].rfind('.') + 1:])
        enhanced_img.save(dest + "/" + src_img[1][:src_img[1].rfind('.')] + "_enhanced." + src_img[1][src_img[1].rfind('.') + 1:], format)
    
    def run(self):
        for _ in range(self.n_images):
            # print("process: ", self.id, "Enhancing Image")
            img = self.queue.get()
            self.imgs.append(img)
            conv_img = img[0].convert("RGB")
            # Enhance brightness by given factor
            bri = ImageEnhance.Brightness(conv_img).enhance(self.brightness)
            con = ImageEnhance.Contrast(bri).enhance(self.contrast)
            sharp = ImageEnhance.Sharpness(con).enhance(self.sharpness)
            self.create_img_file(img, sharp, self.dest)
            self.lock.acquire()
            self.counter.value+=1
            self.lock.release()
        # print("Process", self.id, "Enhanced Images: ", str(self.imgs))

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
            img_copy = img.copy()
            img.close()
            # src_imgs.append([img, img.filename[img.filename.rfind('\\') + 1:]])
            self.queue.put([img_copy, img.filename[img.filename.rfind('\\') + 1:]])
            self.image_list.append([img_copy, img.filename[img.filename.rfind('\\') + 1:]])

        # print("Produced Images: ", str(self.image_list))
        


def write_stats(count, numthreads, dest, run):
    with open('stats.txt', 'w') as f:
        f.write('Statistics:\n')
        f.write(f'Total images enhanced in {run} minute/s with {numthreads} thread/s: {count}\n')
        f.write(f'Output images stored in: {dest}\n')

if __name__ == "__main__":

    run_start = time.time()

    # Parse Arguments
    parser = ArgumentParser()
    parser.add_argument("-s", "--src", type=str, required=True, help="Source Image Folder")
    parser.add_argument("-d","--dest", type=str, required=True, help="Destination Folder")
    parser.add_argument("-tm", "--time",type=int, required=True, help="Image Enhancing Time")
    parser.add_argument("-b", "--brightness", type=float, required=True, help="Image Brightness Ratio")
    parser.add_argument("-sh", "--sharpness", type=float, required=True, help="Image Sharpness Ratio")
    parser.add_argument("-c", "--contrast", type=float, required=True, help="Image Contrast Ratio")
    parser.add_argument("-t", "--threads", default=1, type=int, required=False, help="(Optional) Number of Enhancement Threads")
    args = parser.parse_args()


    # Store Arguments
    src_path = args.src
    dest_path = args.dest
    enhancing_time = args.time
    brightness = args.brightness
    sharpness = args.sharpness
    contrast = args.contrast
    n_threads = args.threads

    # Create Lock
    shared_resource_lock = multiprocessing.Lock()
    print("Lock Initialized")

    # Create Queue
    queue = multiprocessing.Queue()
    print("Queue Initialized")

    # Create Manager
    manager = multiprocessing.Manager()
    shared_resource_counter = manager.Value('i',0)
    print("Manager Initialized")

    count = len([e for e in os.listdir(src_path) if os.path.isfile(os.path.join(src_path, e))])
    print("number of images:", count)
    n_images = int(count/n_threads)
    
    c_threads = []
    
    # start timer on program start
    c_time = time.time()

    p = Producer(src_path, queue)
    p.start()

    for i in range(n_threads):
        if i == n_threads - 1:
            n_images += count - (n_images * n_threads)
        c = Enhancer(i, queue, shared_resource_lock,shared_resource_counter, n_images, dest_path, brightness, sharpness, contrast)
        c_threads.append(c)
        c.start()

    while time.time() - c_time < enhancing_time * 60:
        continue
    else:
        for c in c_threads:
            c.terminate()
        p.terminate()

    p.join()

    for c in c_threads:
        c.join()

    run_time = time.time() - c_time
    write_stats(shared_resource_counter.value, n_threads, dest_path, enhancing_time)
    print("Enhanced Images: ", shared_resource_counter.value)
    print("Execution time: ", run_time, "seconds")
