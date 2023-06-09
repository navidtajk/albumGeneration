import os
import shutil
import sys
from wand.image import Image

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def generateThumbnail(imageFile: str, saveFile: str, width: int, height: int):
  """Generates a small version of the given image with the specified dimensions, and saved at the specified location. Also returns date information for the image."""
  with Image(filename=imageFile) as img:
    imageAspectRatio = img.width / img.height
    finalAspectRatio = width / height
    if imageAspectRatio == finalAspectRatio:
      img.resize(width=width, height=height)
    elif imageAspectRatio < finalAspectRatio:
      img.resize(width=width, height=int(width/imageAspectRatio))
      barHeight = int((img.height - height) / 2)
      img.crop(top=barHeight, bottom=barHeight + height)
    else:
      img.resize(width=int(height*imageAspectRatio), height=height)
      barWidth = int((img.width - width) / 2)
      img.crop(left=barWidth, right=barWidth + width)
    img.save(filename=saveFile)
    return img.metadata.get('exif:DateTimeOriginal')

def processDateString(dateString: str):
  nums = list(map(int, dateString.split(':')))
  return nums[0], nums[1], nums[2]

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
  files = os.listdir(albumFolder)
  albumName = albumFolder.split('/')[-1]
  thumbnailHTML = "<tr>\n"
  # Subtract 1 because of index.html
  maxIndex = len(files) - 1
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
    # write updated file contents back to file
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
  albumPageContents = (
    albumPageContents
      .replace("INNER_CONTENT", innerContents)
      .replace("THUMBNAILS", thumbnailHTML)
      .replace("CURRENT", albumName)
      .replace("MASTER_NAME", masterName)
      .replace("COLLECTION_NAME", collectionName)
  )

  with open(f"{albumFolder}/index.html", "w") as f:
    f.write(albumPageContents)
  return len(files), startDate, endDate

def generateAlbum(imageFolder, albumName, destination, masterName, collectionName):
  # get list of all files in current directory
  files = os.listdir(imageFolder)
  # filter only for files that end in '.jpg'
  jpg_files = list(filter(lambda x: x.endswith(".jpg") or x.endswith("JPG"), files))
  os.mkdir(f"{destination}/{albumName}")
  maxIndex = len(jpg_files)
  for index, file_name in enumerate(jpg_files):
    index += 1
    previousIndex = format(index - 1, '03d')
    currentIndex = format(index, '03d')
    nextIndex = format(index + 1, '03d')
    if index == 1:
      previousIndex = format(maxIndex, '03d')
    elif index == maxIndex:
      nextIndex = "001"
    os.mkdir(f"{destination}/{albumName}/{currentIndex}")
    shutil.copy2(f"{imageFolder}/{file_name}", f"{destination}/{albumName}/{currentIndex}/{albumName}-large.jpg")
    dateString = generateThumbnail(f"{imageFolder}/{file_name}", f"{destination}/{albumName}/{currentIndex}/{albumName}-small.jpg", 150, 100)
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
    )
    with open(f"{destination}/{albumName}/{currentIndex}/index.html", "w") as f:
      f.write(imagePageContents)
  return reloadAlbum(f"{destination}/{albumName}", collectionName, masterName)

if __name__ == "__main__":
  generateAlbum("Open Houses/2023 Open House", "2023 Open House", ".", "dd", "dd")