from GenerateMaster import *

def addAlbum(imageFolder, masterPageFolder, collectionName, albumName):
  masterName = masterPageFolder.split('/')[-1]
  generateAlbum(imageFolder, albumName, f"{masterPageFolder}/{collectionName}", masterName, collectionName)
  reloadCollection(f"{masterPageFolder}/{collectionName}", masterName, True)
  reloadMaster(masterPageFolder, False)

if __name__ == "__main__":
  arguments = sys.argv
  documentation = """
Use this to add an album to a hierarchy of html pages.
Usage: python3 AddAlbum.py iamge_folder master_folder collection_name [album_name]

iamge_folder is the folder of the album you want to add.

master_folder is the name of the outermost folder containing the gallery.

collection_name is the name of the collection the album should be added to.

album_name is the name of the album to be added. It defaults to the name of the folder containing the images.

EXAMPLE:
Photos
|--index.html
|--First-Collection
|  |--index.html
|  |--First-Album
|  |  |--index.html
|  |  |--001
|  |  |  |--index.html
|  |  |  |--First-Album-large.jpg
|  |  |  |--First-Album-small.jpg
|  |  |--002 [...]
|  |  |--003 [...]
|  |  |--004 [...]
|  |--Second-Album [...]
|--Second-Collection [...]
New-Album
|--image1.jpg
|--image2.jpg
|--image3.jpg
|--image4.jpg
|--image5.jpg
|--image6.jpg

After running 'python3 AddAlbum.py New-Album Photos First-Collection' an album containing the photos from New-Album will be generated and added to First-Collection:
Photos
|--index.html
|--First-Collection
|  |--index.html
|  |--First-Album
|  |  |--index.html
|  |  |--001
|  |  |  |--index.html
|  |  |  |--First-Album-large.jpg
|  |  |  |--First-Album-small.jpg
|  |  |--002 [...]
|  |  |--003 [...]
|  |  |--004 [...]
|  |--Second-Album [...]
|  |--\033[92mNew-Album [...]\033[0m
|--Second-Collection [...]
  """
  if arguments[-1] == '-h':
    print(documentation)
  elif len(arguments) == 4:
    album_name = arguments[1].split('/')[-1]
    addAlbum(arguments[1], arguments[2], arguments[3], album_name)
  elif len(arguments) == 5:
    addAlbum(arguments[1], arguments[2], arguments[3], arguments[4])
  else:
    print("""Incorrect number of arguments.
Usage: 'python3 AddAlbum.py image_folder master_folder collection_name album_name'
Run 'python3 AddAlbum.py -h' for more information""")