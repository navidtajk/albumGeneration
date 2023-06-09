from GenerateAlbum import *


def albumThumb(albumTitle, numPhotos, dateField):
    return (f"\t\t<td style=\"text-align:center\" valign='top' width='20%'>\n"
            f"\t\t\t<a class='clear' href='{albumTitle}/index.html'>\n"
            f"\t\t\t\t<img src='{albumTitle}/001/{albumTitle}-small.jpg' border='0' width='150' height='100'/><br/>\n"
            f"\t\t\t\t{albumTitle}\n"
            f"\t\t\t</a><br/>\n"
            f"\t\t\t<p style=\"font-size: 75%; margin-top: 0;\">{numPhotos} image{'s' if numPhotos != 1 else ''}<br/>{dateField}</p>\n"
            f"\t\t</td>\n")

def getCollectionStats(collectionPath: str):
  """Returns a tuple containing the number of albums in the collection, the total number of photos, and the first album, respectively"""
  files = os.scandir(collectionPath)
  folders = list(filter(lambda x: x.is_dir(), files))
  folders.sort(key=lambda x: x.name)
  folders.reverse()
  totalPhotos = 0
  for folder in folders:
    totalPhotos += getAlbumStats(folder.path)[0]
  return len(folders), totalPhotos, folders[0].name

def reloadCollection(collectionFolder: str, masterName: str, reloadAlbums: bool = True):
  collectionName = collectionFolder.split("/")[-1]
  totalPhotos = 0
  files = os.scandir(collectionFolder)
  folders = list(filter(lambda x: x.is_dir(), files))
  folders.sort(key=lambda x: x.name)
  folders.reverse()
  thumbnailHTML = ""
  for index in range(0, len(folders)):
    previousTitle = folders[index - 1].name.replace(' ', '-')
    currentTitle = folders[index].name.replace(' ', '-')
    if index == len(folders) - 1:
      nextTitle = folders[0].name.replace(' ', '-')
    else:
      nextTitle = folders[index + 1].name.replace(' ', '-')
    if reloadAlbums:
      numPhotos, startDate, endDate = reloadAlbum(f"{collectionFolder}/{currentTitle}", collectionName, masterName)
    else:
      numPhotos, startDate, endDate = getAlbumStats(f"{collectionFolder}/{currentTitle}")
    totalPhotos += numPhotos
    if index % 5 == 0:
      if index != 0:
        thumbnailHTML += "\t\t</tr>\n"
      thumbnailHTML += "\t\t<tr>\n"
    thumbnailHTML += albumThumb(currentTitle, numPhotos, makeDateRange(startDate, endDate))
    albumPagePath = f"{collectionFolder}/{currentTitle}/index.html"
    with open(albumPagePath, "r") as f:
      albumPageContents = f.read()
    albumPageContents = (
      albumPageContents
        .replace("PREVIOUS", previousTitle)
        .replace("NEXT", nextTitle)
    )
    with open(albumPagePath, "w") as f:
      f.write(albumPageContents)
  with open("GeneralPageTemplate.html", "r") as f:
    collectionPageContents = f.read()
  with open("CollectionPageTemplate.html", "r") as f:
    innerContent = f.read()
  collectionPageContents = (
    collectionPageContents
      .replace("INNER_CONTENT", innerContent)
      .replace("THUMBNAILS", thumbnailHTML)
      .replace("CURRENT", collectionName)
      .replace("FIRST_ALBUM", folders[0].name.replace(' ', '-'))
      .replace("MASTER_NAME", masterName)
  )
  collectionPagePath = f"{collectionFolder}/index.html"
  with open(collectionPagePath, "w") as f:
    f.write(collectionPageContents)
  return len(folders), totalPhotos, folders[0].name.replace(' ', '-')

def generateCollection(collectionFolder, collectionName, destination, masterName):
  # get list of all files in current directory
  files = os.scandir(collectionFolder)
  folders = list(filter(lambda x: x.is_dir(), files))
  folders.sort(key=lambda x: x.name)
  folders.reverse()
  os.mkdir(f"{destination}/{collectionName}")
  for index, file in enumerate(folders):
    currentTitle = folders[index].name.replace(' ', '-')
    generateAlbum(file.path, currentTitle, f"{destination}/{collectionName}", masterName, collectionName)
  return reloadCollection(f"{destination}/{collectionName}", masterName)

if __name__ == "__main__":
  generateCollection("Open Houses", "Open House Albums", ".")