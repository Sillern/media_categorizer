import os
from datetime import datetime, date, time

import pyexiv2
import hashlib
import stat
import shutil
import mov

input_path = "/home/content/foto_almost_sorted"
output_path = "/home/content/foto/"

dateformat = "%Y/%m_%B/%d"
valid_extensions = [".mov", ".mp4", ".avi", ".jpg", ".nef"]

def has_same_content(files):
  if len(files) == 1:
    return True

  filehash = None
  for filepath in files:
    if not os.path.isfile(filepath):
      return False

    f = open(filepath, "rb")
    current_hash = hashlib.sha1(f.read()).hexdigest()
    f.close()

    if filehash == None:
      filehash = current_hash

    elif filehash != current_hash:
      return False

  return True
      
def mkdir_p(path):
  if os.path.exists( path ):
    return
  os.makedirs( path )

def get_creation_time_exif( filename, dateformat):

  metadata = pyexiv2.ImageMetadata(filename)
  try:
    metadata.read()
  except IOError:
    return None

  datetags = [
      "Exif.Image.DateTime",
      "Xmp.video.DateTimeOriginal",
      "Exif.Photo.DateTimeOriginal"
      ]

  for datetag in datetags:
    try:
      return datetime.strptime(metadata[datetag].raw_value, "%Y:%m:%d %H:%M:%S").strftime(dateformat)
    except KeyError:
      continue

  for exif_key in metadata.exif_keys:
    print exif_key, metadata[exif_key]

  try:
    # mac time
    seconds = int(metadata["Xmp.video.DateUTC"].raw_value) - 2082844800
    if seconds == 0:
      return None

    creation_date = datetime.utcfromtimestamp(seconds)
    return creation_date.strftime(dateformat)
  except KeyError:
    return None

  return None

def get_creation_time(filename, dateformat):
  _,extension = os.path.splitext(filename)

  if extension.lower() in valid_extensions:
    return get_creation_time_exif(filename, dateformat)

  return None

def get_output_path(extension):
  output_paths = {
      ".mov": "film",
      ".avi": "film",
      ".mp4": "film",
      ".jpg": "",
      ".nef": "raw"
      }

  if extension.lower() in output_paths.keys():
    return os.path.join(output_path, output_paths[extension.lower()])

for root, dirs, files in os.walk(input_path):
  for filename in files:
    current_file =  os.path.join(root, filename)
    _,extension = os.path.splitext(filename)

    if extension.lower() in valid_extensions:
      folder = get_creation_time(current_file, dateformat)

      if folder == None:
        print "Unable to get creation time", current_file
        continue

      output_folder = os.path.join( get_output_path(extension), folder )

      mkdir_p( output_folder )
      
      destination_file = os.path.join( output_folder, filename )

      if os.path.isfile( destination_file ):
        if has_same_content( [current_file, destination_file] ):
          print "duplicate file, removing:", current_file 
          os.remove(current_file)
        else:
          print "! Check files:", current_file, destination_file

      else:
        print "renaming:", current_file, destination_file
        shutil.move( current_file, destination_file ) 
    else:
      pass
      #print "Unknown filetype:", current_file

