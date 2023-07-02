import os
import shutil
import sys
from wand.image import Image

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
validExtensions = set(['bpg', 'bmp,', 'bm', 'bmp3', 'cmyk', 'cmyka', 'gif', 'heic', 'jpeg', 'jpg', 'png', 'png8', 'png00', 'png24', 'png32', 'png48', 'png64', 'ppm', 'ps', 'psd', 'svg', 'tiff', 'tif', 'webp', 'tga', 'nef', 'cr2'])
def generateThumbnails(imageFile: str, saveDirectory, smallImageName: str, largeImageName: str, originalImageName: str, smallWidth: int, smallHeight: int, largeHeight: int):
  """Generates a small and medium version of the given image with the specified dimensions, and saved at the specified location. Returns a tuple containing the location of the original image and date information for the image (if it exists)."""
  with Image(filename=imageFile) as image:
    originalImageFilename = ""
    imageAspectRatio = image.width / image.height
    if image.height > largeHeight:
      image.resize(width=int(largeHeight*imageAspectRatio), height=largeHeight)
      originalImageFilename = f"{originalImageName}.{image.format.lower()}"
      shutil.copy2(imageFile, f"{saveDirectory}/{originalImageFilename}")
      image.format = 'JPEG'
      image.save(filename=f"{saveDirectory}/{largeImageName}.jpg")
    else:
      originalImageFilename = f"{largeImageName}.jpg"
      if image.format == 'JPEG':
        shutil.copy2(imageFile, f"{saveDirectory}/{originalImageFilename}")
      else:
        image.format = 'JPEG'
        image.save(filename=f"{saveDirectory}/{originalImageFilename}")
    
    finalAspectRatio = smallWidth / smallHeight
    if imageAspectRatio == finalAspectRatio:
      image.resize(width=smallWidth, height=smallHeight)
    elif imageAspectRatio < finalAspectRatio:
      image.resize(width=smallWidth, height=int(smallWidth/imageAspectRatio))
      barHeight = int((image.height - smallHeight) / 2)
      image.crop(top=barHeight, bottom=barHeight + smallHeight)
    else:
      image.resize(width=int(smallHeight*imageAspectRatio), height=smallHeight)
      barWidth = int((image.width - smallWidth) / 2)
      image.crop(left=barWidth, right=barWidth + smallWidth)
    image.save(filename=f"{saveDirectory}/{smallImageName}.jpg")
    return originalImageFilename, image.metadata.get('exif:DateTimeOriginal')

def processDateString(dateString: str):
  nums = list(map(int, dateString.split(':')))
  return nums[0], nums[1] - 1, nums[2]

def readableDateString(dateString):
  if dateString == "":
    return ""
  year, month, day = processDateString(dateString)
  return f"{day} {months[month]} {year}"

def makeDateRange(dateString1, dateString2):
  if dateString1 == "":
    return ""
  year1, month1, day1 = processDateString(dateString1)
  year2, month2, day2 = processDateString(dateString2)
  if year1 != year2:
    return f"{day1} {months[month1]} {year1}-{day2} {months[month2]} {year2}"
  if month1 != month2:
    return f"{day1} {months[month1]}-{day2} {months[month2]} {year1}"
  if day1 != day2:
    return f"{day1}-{day2} {months[month2]} {year1}"
  return f"{day1} {months[month1]} {year1}"

def imageThumb(imageTitle, albumName):
  return (f"\t\t<td style=\"text-align:center\" valign='top' width='20%'>\n"
        f"\t\t\t<a class='clear' href='{imageTitle}/index.html'>\n"
        f"\t\t\t\t<img src='{imageTitle}/{albumName}-small.jpg' border='0' width='150' height='100'/><br/>\n"
        f"\t\t\t\t{imageTitle}\n"
        f"\t\t\t</a>\n"
        f"\t\t</td>\n")

def getAlbumStats(albumFolder: str):
  """Returns a tuple containing the number of images in the album, the start date, and the end date. The same return values as calling reloadAlbum, but without changin any files"""
  files = os.listdir(albumFolder)
  albumName = albumFolder.split('/')[-1]
  # Subtract 1 because of index.html
  maxIndex = len(files) - 1
  startDate = ""
  endDate = ""
  for index in range(1, maxIndex + 1):
    currentIndex = format(index, '03d')
    with Image(filename=f"{albumFolder}/{currentIndex}/{albumName}-large.jpg") as img:
      dateString = img.metadata.get('exif:DateTimeOriginal')
    if dateString is None:
      pass
    else:
      if startDate == "":
        startDate = dateString
        endDate = dateString
      else:
        if dateString > endDate:
          endDate = dateString
        elif dateString < startDate:
          startDate = dateString
  return maxIndex, startDate, endDate

def reloadAlbum(albumFolder: str, collectionName: str, masterName: str):
  """'Reloads' the album, regenerating the page for the album based on the existing subfolders. Returns a tuple containing the number of images in the album, the start date for the photos, and the end date"""
  files = os.scandir(albumFolder)
  
  albumName = albumFolder.split('/')[-1]
  thumbnailHTML = "<tr>\n"
  # Subtract 1 because of index.html
  maxIndex = len(list(filter(lambda x: x.is_dir(), files)))
  startDate = ""
  endDate = ""
  for index in range(1, maxIndex + 1):
    previousIndex = format(index - 1, '03d')
    currentIndex = format(index, '03d')
    nextIndex = format(index + 1, '03d')
    if index == 1:
      previousIndex = format(maxIndex, '03d')
    elif index == maxIndex:
       nextIndex = "001"
    thumbnailHTML += imageThumb(currentIndex, albumName)
    if index % 5 == 0:
      thumbnailHTML += "\t\t</tr>\n"
      if index != maxIndex:
        thumbnailHTML += "\t\t<tr>\n"
    with Image(filename=f"{albumFolder}/{currentIndex}/{albumName}-large.jpg") as img:
      dateString = img.metadata.get('exif:DateTimeOriginal')
    if dateString is None:
      pass
    else:
      dateString = dateString.split(' ')[0]
      if startDate == "":
        startDate = dateString
        endDate = dateString
      else:
        if dateString > endDate:
          endDate = dateString
        elif dateString < startDate:
          startDate = dateString
    imagePagePath = f"{albumFolder}/{currentIndex}/index.html"
    with open(imagePagePath, "r") as f:
      imagePageContents = f.read()
    imagePageContents = (
      imagePageContents
        .replace("NEXT", nextIndex)
        .replace("PREVIOUS", previousIndex)
    )
    with open(imagePagePath, "w") as f:
      f.write(imagePageContents)
  with open(f"GeneralPageTemplate.html", "r") as f:
    albumPageContents = f.read()
  with open(f"AlbumPageTemplate.html", "r") as f:
    innerContents = f.read()
  header = ""
  headerPath = f"{albumFolder}/header.txt"
  if os.path.exists(headerPath):
    with open(headerPath) as f:
      header = f.read()
  albumPageContents = (
    albumPageContents
      .replace("INNER_CONTENT", innerContents)
      .replace("THUMBNAILS", thumbnailHTML)
      .replace("CURRENT", albumName)
      .replace("MASTER_NAME", masterName)
      .replace("COLLECTION_NAME", collectionName)
      .replace("HEADER", header)
  )

  with open(f"{albumFolder}/index.html", "w") as f:
    f.write(albumPageContents)
  return maxIndex, startDate, endDate

def validImage(file: os.DirEntry) -> bool:
  # skip over hidden files and folders
  if file.name[0] == '.' or not file.is_file:
    return False
  extension = file.name.split('.')[-1].lower()
  return extension in validExtensions

def generateAlbum(imageFolder, albumName, destination, masterName, collectionName):
  # get list of all files in current directory
  os.scandir(imageFolder)
  files = os.scandir(imageFolder)
  # filter only for files that end in '.jpg'
  jpgFiles = list(map(lambda x: x.name, filter(validImage, files)))
  os.mkdir(f"{destination}/{albumName}")
  maxIndex = len(jpgFiles)
  print(jpgFiles)
  for index, filename in enumerate(jpgFiles):
    index += 1
    previousIndex = format(index - 1, '03d')
    currentIndex = format(index, '03d')
    nextIndex = format(index + 1, '03d')
    if index == 1:
      previousIndex = format(maxIndex, '03d')
    elif index == maxIndex:
      nextIndex = "001"
    os.mkdir(f"{destination}/{albumName}/{currentIndex}")
    # shutil.copy2(f"{imageFolder}/{filename}", f"{destination}/{albumName}/{currentIndex}/{albumName}-large.jpg")
    origialImageName, dateString = generateThumbnails(f"{imageFolder}/{filename}", f"{destination}/{albumName}/{currentIndex}", f"{albumName}-small", f"{albumName}-large", f"{albumName}-original", 150, 100, 600)
    if dateString is None:
      dateString = ""
    else:
      dateString = dateString.split(' ')[0]
    with open(f"GeneralPageTemplate.html", "r") as f:
      imagePageContents = f.read()
    with open(f"ImagePageTemplate.html", "r") as f:
      innterContents = f.read()
    imagePageContents = (
      imagePageContents
        .replace("INNER_CONTENT", innterContents)
        .replace("PREVIOUS", previousIndex)
        .replace("CURRENT", currentIndex)
        .replace("NEXT", nextIndex)
        .replace("MASTER_NAME", masterName)
        .replace("COLLECTION_NAME", collectionName)
        .replace("ALBUM_NAME", albumName)
        .replace("DATE_STRING",  readableDateString(dateString))
        .replace("ORIGINAL_IMAGE", origialImageName)
    )
    with open(f"{destination}/{albumName}/{currentIndex}/index.html", "w") as f:
      f.write(imagePageContents)
  headerPath = f"{imageFolder}/header.txt"
  if os.path.exists(headerPath):
    with open(headerPath) as f:
      shutil.copy2(headerPath, f"{destination}/{albumName}/header.txt")
  return reloadAlbum(f"{destination}/{albumName}", collectionName, masterName)

if __name__ == "__main__":
  generateAlbum("/Users/Navid/CleanPhotos/Research/Yi_Figures", "Test", ".", "dd", "dd")