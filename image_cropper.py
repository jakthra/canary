

import configargparse
from PIL import Image
from dotmap import DotMap
import os
import glob
from tkinter import filedialog
from tkinter import Tk
import itertools as it


def multiple_file_types(*patterns):
    return it.chain.from_iterable(glob.iglob(pattern) for pattern in patterns)

def run(args):
  args = DotMap(args)

  # Run without attendence
  if args.gui:
    root = Tk()
    root.geometry("400x400")
    root.withdraw()
    folder_selected = filedialog.askdirectory()
  else:
    folder_selected = args.input_folder

  # Check outpout folder exist, if not, make it
  if not os.path.isdir(args.output_folder):
    os.mkdir(args.output_folder)

  print(f'Processing images from: {folder_selected} to: {args.output_folder}')
  for file in multiple_file_types(os.path.join(folder_selected,'*.jpg'), os.path.join(folder_selected,'*.jpeg')):
    # Get image name
    image_name = os.path.basename(file)
    image_name_end = image_name.split('.')
    image_name_final = image_name_end[0] + "_" + str(args.output_resolution[0]) + "x" + str(args.output_resolution[1]) + "." + image_name_end[1]

    

    # load image from input folder
    im = Image.open(file)
    im = crop_and_resize(args, im, image_name)

    # Save image
    image_path = os.path.join(args.output_folder, image_name_final)
    print(image_path)
    im.save(image_path, dpi=(args.output_dpi,args.output_dpi))

    # Optimize file size
    reduce_file_size(args, image_path)
  print('Done!')
    
def crop_and_resize(args, im, image_name):
  # Crop and resize image by computing new aspect ratio of desired resolution args.output_resolution
  im_aspect_ratio = im.size[0]/im.size[1]
  im_desired_aspect_ratio = args.output_resolution[0]/args.output_resolution[1]
  if args.verbose:
    print('Image: {}'.format(image_name))
    print("Original size: {}".format(im.size))
    print("Original aspect ratio: {}".format(im_aspect_ratio))
    print("Desired resolution: {}".format(args.output_resolution))
    print("Desired aspect ratio: {}".format(im_desired_aspect_ratio))

  # Compute aspect ratio for new image size
  if im_desired_aspect_ratio > im_aspect_ratio:
    # Compute new height
    # aspect ratio = width/height
    new_height = im.size[0]/im_desired_aspect_ratio
    im = im.crop((0,0, im.size[0], new_height))
  else:
    new_width = im.size[1]*im_desired_aspect_ratio
    im = im.crop((0,0, new_width, im.size[1]))

  if args.verbose:
    print("New aspect ratio: {}".format(im.size[0]/im.size[1]))
  im = im.resize(args.output_resolution)

  return im
  


def reduce_file_size(args, image_path):
  # Reduce image size to args.output_max_file_size target
  quality = 100
  file_size = os.path.getsize(image_path)
  image = Image.open(image_path)
  while file_size/(1024*1024)> args.output_max_file_size:
    if args.verbose:
      print(f'Reducing quality to {quality}, file-size: {file_size/(1024*1024)} -> target: {args.output_max_file_size}')
    image.save(image_path, optimize=True, quality=quality)
    file_size = os.path.getsize(image_path)
    quality -= 5
    if quality < 5:
      break;
    image = Image.open(image_path)

if __name__=='__main__':
  p = configargparse.ArgParser(default_config_files=['settings.cfg'])
  p.add('-i', '--input_folder')
  p.add('-d', '--output_dpi', type=int)
  p.add('-r', '--output_resolution', type=int,  nargs='+')
  p.add('-s', '--output_max_file_size', type=float)
  p.add('-o', '--output_folder')
  p.add('-v', '--verbose', action='store_true', default=False)
  p.add('-g', '--gui', action='store_true', default=False)

  run(vars(p.parse_args()))