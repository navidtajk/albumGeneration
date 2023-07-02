from GenerateCollection import *

def collectionThumb(collectionTitle, numAlbums, numPhotos, albumTitle):
    return (f"\t\t<td style=\"text-align:center\" valign='top' width='20%'>\n"
            f"\t\t\t<a class='clear' href='{collectionTitle}/index.html'>\n"
            f"\t\t\t\t<img src='{collectionTitle}/{albumTitle}/001/{albumTitle}-small.jpg' border='0' width='150' height='100'/><br/>\n"
            f"\t\t\t\t{collectionTitle}\n"
            f"\t\t\t</a>\n"
            f"\t\t\t<p style=\"font-size: 75%; margin-top: 0;\">{numAlbums} album{'s' if numAlbums != 1 else ''}, {numPhotos} image{'s' if numPhotos != 1 else ''}</p>"
            f"\t\t</td>\n")

def reloadMaster(masterPageFolder: str, reloadCollections: str = True):
  masterName = masterPageFolder.split('/')[-1]
  files = os.scandir(masterPageFolder)
  folders = list(filter(lambda x: x.is_dir(), files))
  thumbnailHTML = ""
  for index, file in enumerate(folders):
    previousTitle = folders[index - 1].name.replace(' ', '_')
    currentTitle = folders[index].name.replace(' ', '_')
    if index == len(folders) - 1:
      nextTitle = folders[0].name.replace(' ', '_')
    else:
      nextTitle = folders[index + 1].name.replace(' ', '_')
    if reloadCollections:
      numAlbums, numPhotos, firstAlbum = reloadCollection(file.path, masterName)
    else:
      numAlbums, numPhotos, firstAlbum = getCollectionStats(f"{masterPageFolder}/{currentTitle}")
    if index % 5 == 0:
      if index != 0:
        thumbnailHTML += "\t\t</tr>\n"
      thumbnailHTML += "\t\t<tr>\n"
    thumbnailHTML += collectionThumb(currentTitle, numAlbums, numPhotos, firstAlbum)
    collectionPagePath = f"{masterPageFolder}/{currentTitle}/index.html"
    with open(collectionPagePath, "r") as f:
      collectionPageContents = f.read()
    collectionPageContents = (
      collectionPageContents
        .replace("PREVIOUS", previousTitle)
        .replace("NEXT", nextTitle)
    )
    with open(collectionPagePath, "w") as f:
      f.write(collectionPageContents)
  with open("GeneralPageTemplate.html") as f:
      masterPageContents = f.read()
  with open("MasterPageTemplate.html", "r") as f:
    innerContent = f.read()
  masterPageContents = (
    masterPageContents
      .replace("INNER_CONTENT", innerContent)
      .replace("THUMBNAILS", thumbnailHTML)
      .replace("CURRENT", masterName)
      .replace("FIRST_COLLECTION", folders[0].name.replace(' ', '_'))
  )
  masterPagePath = f"{masterPageFolder}/index.html"
  with open(masterPagePath, "w") as f:
    f.write(masterPageContents)

def generateMaster(collectionFolder, masterName, destination):
  files = os.scandir(collectionFolder)
  folders = list(filter(lambda x: x.is_dir(), files))

  os.mkdir(f"{destination}/{masterName}")
  for index, file in enumerate(folders):
    current_title = folders[index].name.replace(' ', '_')
    generateCollection(file.path, current_title, f"{destination}/{masterName}", masterName)
  return reloadMaster(f"{destination}/{masterName}")
  
if __name__ == "__main__":
  arguments = sys.argv
  documentation = """
Use this to generate a hierarchy of html pages to view a set of images.
Usage: python3 GenerateMaster.py collection_folder page_name [destination]

collection_folder is the path to a folder of folders of images. Child pages of the collection will be named by their corresponding folder (replacing spaces with dashes).

page_name is the name of the outermost folder.

destination is the parent directory of the outermost folder. It defaults to the current directory.

EXAMPLE:
All_Images
|--First Collection
|  |--First Album
|  |  |--image1.jpg
|  |  |--image2.jpg
|  |  |--image3.jpg
|  |  |--image4.jpg
|  |--Second Album
|  |  |--photo1.jpg
|  |  |--photo2.jpg
|  |  |--photo3.jpg
|  |  |--photo4.jpg
|--Second Collection
|  |--First Album
|  |  |--image1.jpg
|  |  |--image2.jpg
|  |  |--image3.jpg
|  |  |--image4.jpg
|  |--Second Album
|  |  |--photo1.jpg
|  |  |--photo2.jpg
|  |  |--photo3.jpg
|  |  |--photo4.jpg
|  |--Third Album
|  |  |--photo1.jpg
|  |  |--photo2.jpg
|  |  |--photo3.jpg

After running 'python3 ./All_Images Photos .' there will be a new directory, './Photos'
For each image, a numbered folder is generated contining an index page for viewing the image, the full-size image, and a thumbnail.
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
"""
  if arguments[-1] == '-h':
    print(documentation)
  elif len(arguments) == 3:
    generateMaster(arguments[1], arguments[2], '.')
  elif len(arguments) == 4:
    generateMaster(arguments[1], arguments[2], arguments[3])
  else:
    print("""Incorrect number of arguments.
Usage: 'python3 GenerateMaster.py collection_folder page_name [destination]'
Run 'python3 GenerateMaster.py -h' for more information""")