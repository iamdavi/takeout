from pathlib import Path
from datetime import datetime
import glob
import os
import json
import time
import re


class TakeoutParser():
    takeoutPath = ''
    jsonsFilesPaths = []
    tmpFolderName = './takeout_ordenado/'
    filesNotFound = []

    def __init__(self):
        self.takeoutPath = self.getTakeoutPath()
        self.takeoutFolders = self.getTakeoutFolders()
        self.parseTakeoutFolders()

    def parseTakeoutFolders(self):
        for takeoutFolder in self.takeoutFolders:
            takeoutIndex = takeoutFolder.name.split('-')[2]
            print(f"Examinando carpeta: 'takeout-...-{takeoutIndex}'")
            # jsonsFiles = takeoutFolder.rglob('*.json')
            # for json in jsonsFiles:
            #     self.parseJson(json)
            # Get remainder files
            self.moveRemainderFiles(takeoutFolder)

    def moveRemainderFiles(self, takeoutFolder: Path):
        extensiones_imagenes = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.svg']
        extensiones_videos = ['*.mp4', '*.avi', '*.mkv', '*.mov', '*.wmv', '*.flv', '*.mpeg']
        patrones = extensiones_imagenes + extensiones_videos
        archivos = []
        for patron in patrones:
            archivos.extend(takeoutFolder.rglob(patron))
        date_regex = re.compile(r"(\d{4})[-_]?(\d{2})[-_]?(\d{2})")
        for archivo in archivos:
            match = date_regex.search(str(archivo.name))
            if match:
                year, month, day = match.groups()
            else:
                # get json file
                jsonPath = Path(str(archivo.parent) + '/' + archivo.name + '.json')
                year, month = self.getDayAndMonthFromJson(jsonPath)

            imagePath = Path(self.tmpFolderName + '/' + year + '/' + month)
            imagePath.mkdir(parents=True, exist_ok=True)
            destination = str(imagePath) + '/' + archivo.name
            archivo.replace(destination)

    def getDayAndMonthFromJson(self, jsonPath):
        json_string = jsonPath.read_text()
        data = json.loads(json_string)
        if (
            not data or 
            not data.get('photoTakenTime', {}).get('timestamp') or 
            not data.get('title')
        ):
            return
        timestamp = int(data['photoTakenTime']['timestamp'])
        # timestamp = time.time()
        dt_object = datetime.fromtimestamp(timestamp)
        year = dt_object.year
        month = "{:02}".format(dt_object.month)
        return (str(year), str(month))

    # def parseJson(self, jsonPath):
    #     json_string = jsonPath.read_text()
    #     data = json.loads(json_string)
    #     if (
    #         not data or 
    #         not data.get('photoTakenTime', {}).get('timestamp') or 
    #         not data.get('title')
    #     ):
    #         return
    #     photoTimestamp = int(data['photoTakenTime']['timestamp'])
    #     relativePath = self.createTree(int(photoTimestamp))
    #     fileToMovePath = Path(str(jsonPath.parent) + '/' + data.get('title'))
    #     destination = str(relativePath) + '/' + data.get('title')
    #     try:
    #         fileToMovePath.replace(destination)
    #     except FileNotFoundError:
    #         return
    #         # self.addFileNotFound(destination)
    #     except Exception as e:
    #         return
    #         # self.addFileNotFound(destination)

    # def createTree(self, timestamp):
    #     timestampDate = datetime.fromtimestamp(timestamp) 
    #     yearMonthDay = str(timestampDate).split(' ')[0].split('-')
    #     yearMonthDay.pop()
    #     imagePath = Path(self.tmpFolderName + '/'.join(yearMonthDay))
    #     imagePath.mkdir(parents=True, exist_ok=True)
    #     return imagePath
    
    def printJson(self, jsonToPrint):
        json_load = json.dumps(jsonToPrint, indent=2)
        print(json_load)

    # def change_creation_time(self, file_path, new_time):
    #     current_time = time.time()
    #     new_time_seconds = time.mktime(new_time.timetuple())
    #     os.utime(file_path.removesuffix('.json'), (current_time, new_time_seconds))

    def getTakeoutFolders(self):
        pattern = re.compile(r'^takeout-.+-\d{3}$')
        directories = [folder for folder in self.takeoutPath.iterdir() if folder.is_dir()]
        matching_directories = [folder for folder in directories if pattern.match(folder.name)]
        return matching_directories

    def getTakeoutPath(self):
        print("""
        Debes introducir la ruta donde se encuentran los archivos 'takeout-XXX...-NNN'
        descargados, de no introducir ninguno, se buscaran dichos archivos en
        la ruta actual.
        """)
        takeoutPath = Path.cwd()
        # takeoutPath = input("Ruta absoluta de 'takeouts': ")
        # if not takeoutPath:
        #     takeoutPath = Path.cwd()
        return Path(takeoutPath)

    def addFileNotFound(self, path):
        self.filesNotFound.append(path)


if __name__ == "__main__":
    parser = TakeoutParser()
