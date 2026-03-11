import os
import json
import requests
import shutil
import urllib.parse
from datetime import datetime
import time
import subprocess
from cryptography.fernet import Fernet
import xml.etree.ElementTree as ET

us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "Virgin Islands, U.S.": "VI",
}
abbrev_to_us_state = dict(map(reversed, us_state_to_abbrev.items()))

TESTING_ENV = False

def state_to_abbrev(state):
    if state in us_state_to_abbrev:
        return us_state_to_abbrev[state]
    else:
        return None

def abbrev_to_state(abbrev):
    if abbrev in abbrev_to_us_state:
        return abbrev_to_us_state[abbrev]
    else:
        return None

class Zoho:
    def __init__(self):
        self.params = {
            "auth_type": "*****PROPRIETARY INFO *****",
            "zapikey": "*****PROPRIETARY INFO *****"
        }
    
    def getDeal(self,deal_id):
        deal_info_params = {
            "dealid": str(deal_id)
        }
        deal_info_params.update(self.params)
        response = requests.get("*****PROPRIETARY INFO *****",params=deal_info_params)
        root = ET.fromstring(response.content)

        return root

    def updateNasName(self,course_id,nas_name):
        nas_name_params = {
            "courseid": str(course_id),
            "nas_name": urllib.parse.quote(str(nas_name))
        }
        nas_name_params.update(self.params)
        if TESTING_ENV:
            print("TESTING TESTING")
            print(f"Didn't submit {nas_name} for id: {course_id}")
            return
        response = requests.get("*****PROPRIETARY INFO *****",params=nas_name_params)
        if response.status_code == 200:
            print(f"Submitted {nas_name} for id: {course_id}")
        else:
            print("ERROR RECEIVED FROM NAS NAME CHANGE SUBMISSION")
        

class Synology:
    def __init__(self,URL_ADDRESS,USERNAME,PASSWORD):
        self.url = f'*****PROPRIETARY INFO *****'
        self.username = USERNAME
        self.password = PASSWORD
        self.login()
    
    def login(self):
        login_params = {
            "api": "SYNO.API.Auth",
            "version": "7",
            "method": "login",
            "account": self.username,
            "passwd": self.password,
            "session": "Core",
            "format": "cookie",
            "enable_syno_token": "yes"
        }
        login_response = requests.get(self.url,login_params)
        print(login_response.json())
        self.params = {
            "_sid": login_response.json()['data']['sid'],
            "SynoToken": login_response.json()['data']['synotoken']
        }
        print("Logged In To Synology")

    # NOT FINISHED YET
    def search(self):
        folder_path = ""
        pattern = ""

        search_params = {
            "api": "SYNO.FileStation.Search",
            "version": "2",
            "method": "start",
            "folder_path": folder_path,
            "recursive": "true",
            "pattern": pattern,
            "limit": "-1"
        }
        search_params.update(self.params)

        task_id = ""

        list_params = {
            "api": "SYNO.FileStation.Search",
            "version": "2",
            "method": "list",
            "additional": "%5B%22real_path%22%2C%22size%22%2C%22owner%22%2C%22time%22%2C%22perm%22%2C%22type%22%5D",
            "taskid": task_id,
            "limit": "-1"
        }
        list_params.update(self.params)

        clean_params = {
            "api": "SYNO.FileStation.Search",
            "version": "2",
            "method": "clean",
            "task_id": task_id
        }
        clean_params.update(self.params)
    
    #Input folder path, output files in path
    def list(self,path):
        encoded_path = f'{urllib.parse.quote(path).replace("/","%2F")}'
        list_request_url = f'*****PROPRIETARY INFO *****'
        print(list_request_url)
        response = requests.get(list_request_url)
        if response.json()['success']:
            return response.json()['data']['files']
        else:
            return False

class Deal:
    def __init__(self,id,invoice,nas_course_path,product_type):
        self.invoice = invoice
        self.id = id
        self.nas_course_path = nas_course_path
        self.product_type = product_type

    def open_zoho(self):
        apples = AppleScript()
        apples.openUrl(f"*****PROPRIETARY INFO *****")
    
    def find(self):
        pass

    def open(self):
        pass
    
    def create(self):
        pass

    def matchProductFolder(self,folders):
        formattedProduct = ("".join(self.product_type.split(" "))).upper()
        for folder in folders:
            formattedFolder = ("".join(folder['name'].split(" "))).upper()
            if formattedProduct == formattedFolder:
                return folder['name']

class Deal_From_Zoho(Deal):
    def __init__(self,zoho,deal_id):
        root = zoho.getDeal(deal_id)
        self.company_name = root.find("company").find("name").text
        self.company_id = root.find("company").find("id").text
        self.invoice = root.find("invoice").text
        self.course_name = root.find("course").find("name").text
        self.course_id = root.find("course").find("id").text
        self.course_state = root.find("course").find("state").text
        self.course_abbrev = state_to_abbrev(root.find("course").find("state").text)
        self.nas_name = root.find("course").find("nas_name").text
        self.state_abrv = root.find("address").find("state_abvr").text
        self.street = root.find("address").find("street").text
        self.city = root.find("address").find("city").text
        self.product_type = root.find("product_type").text
        self.stage = root.find("stage").text
        self.adsize = root.find("adsize").text
        self.phone = root.find("phone").text
        self.location = [x.text for x in root.iter('adlocation')]
        self.placement = [x.text for x in root.iter('adplacement')]
        self.assinvoice = root.find('assinvoice').text
        self.years = root.find('years').text
        self.deal_type = root.find('deal_type').text
        self.id = str(deal_id)

class Advertiser:
    def __init__(self):
        pass

class Product:
    def __init__(self):
        pass

class PrintJob:
    def __init__(self):
        pass

class Geoshot:
    def __init__(self,deal_name,deal_id,invoice,stage,product_type,ad_size,nas_name,react_folder_path,nas_course_path,indesign_file_name,proof_file_name,print_job_id,contact_email,status,approval_type):
        self.deal_name = deal_name
        self.deal_id = deal_id
        self.invoice = invoice
        self.stage = stage
        self.product_type = product_type
        self.ad_size = ad_size
        self.nas_name = nas_name
        self.react_folder_path = react_folder_path
        self.nas_course_path = nas_course_path
        self.indesign_file_name = indesign_file_name
        self.proof_file_name = proof_file_name
        self.print_job_id = print_job_id
        self.contact_email = contact_email
        self.status = status
        self.approval_type = approval_type
        self.nas_folder_name = f"{self.deal_name} - {self.product_type}"
        self.createNasPaths()
        self.deal = Deal(deal_id,invoice,nas_course_path,product_type)
        self.attachment_id = False

    def createNasPaths(self):
        self.nas_folder_path = os.path.join(self.nas_course_path,self.nas_folder_name)
        self.indesign_file_path = os.path.join(self.nas_folder_path,self.indesign_file_name)
        self.proof_file_path = os.path.join(self.nas_folder_path,self.proof_file_name)

    def placeInNas(self,syn,create_course_folder):
        print("/".join(self.nas_course_path.split("/")[1:]))
        dealFolder = syn.list(f'/{"/".join(self.nas_course_path.split("/")[1:])}')
        print(dealFolder)
        if dealFolder or create_course_folder:
            if not dealFolder and not TESTING_ENV and create_course_folder:
                try:
                    os.mkdir(self.nas_course_path)
                except FileExistsError:
                    print("Course Folder Already Exists: " + self.nas_course_path)
                newCoursePath = os.path.join(self.nas_course_path,self.product_type.upper())
                try:
                    os.mkdir(newCoursePath)
                except FileExistsError:
                    print("Product Folder Already Exists: " + newCoursePath)
                self.nas_course_path = newCoursePath
                self.createNasPaths()
                dealFolder = syn.list(f'/{"/".join(self.nas_course_path.split("/")[1:])}')
            else:
                productFolderName = self.deal.matchProductFolder(dealFolder)
                if productFolderName:
                    self.nas_course_path = os.path.join(self.nas_course_path,productFolderName)
                    self.createNasPaths()
            if TESTING_ENV:
                tempLocation = "/Volumes/Art Department/-----FILE REQUESTS-----/Test Apps/Copy Location"
                self.nas_folder_path = os.path.join(tempLocation,self.nas_folder_path)
            try:
                print(self.react_folder_path)
                print(self.nas_folder_path)
                shutil.copytree(self.react_folder_path,f"/{self.nas_folder_path}")
            except FileExistsError:
                raise FileExistsError(self.nas_folder_path)
            print(f"Changed {self.react_folder_path} to this: {self.nas_folder_path}")
        else:
            print("Couldn't Find Course")
            raise ValueError("Couldn't Find Course")
            # return False

class AppleScript:
    def __init__(self):
        pass

    def openFinder(self,path):
        if os.path.isdir(path):
            subprocess.call(["open", path])
        else:
            subprocess.call(["open", os.path.dirname(path)])

    def openIndesignFile(self,fileName):
        ascript = f'tell application "Adobe InDesign 2025" to open "{fileName}"'
        self.asrun(ascript.encode())
    
    def triggerIndesignScript(self,script_name,thePackage):
        userPath = os.path.abspath(os.getcwd())
        print(userPath)
        splitUserPath = str(userPath).split('/')
        userPath2 = ["Library","Preferences","Adobe InDesign","Version 19.0","en_US","Scripts","Scripts Panel"]
        print(splitUserPath)
        joinedPath = os.path.join(str(splitUserPath[1]),str(splitUserPath[2]),*userPath2,f"{script_name}.js")
        filePath = f"/{joinedPath}"
        print(filePath)
        if not os.path.isfile(filePath):
            self.alert("Missing Script")
            return False
        if thePackage:
            ascript = '''
                tell application "System Events"
                    set the clipboard to "''' + str(thePackage) + '''"
                end tell
                tell application "Adobe InDesign 2025"
                    do script "''' + str(filePath) + '''" language javascript
                end tell
                '''
        else:
            ascript = '''
                tell application "Adobe InDesign 2025"
                    do script "''' + str(filePath) + '''" language javascript
                end tell
                '''
        self.asrun(ascript.encode())

    def openUrl(self,url):
        ascript = f'tell application "Google Chrome" to open location "{str(url)}"'
        self.asrun(ascript.encode())
        
    def asrun(self,ascript):
        "Run the given AppleScript and return the standard output and error."

        osa = subprocess.Popen(['osascript', '-'],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        return osa.communicate(ascript)[0]

    def asquote(self,astr):
        "Return the AppleScript equivalent of the given string."
        
        astr = astr.replace('"', '" & quote & "')
        return '"{}"'.format(astr)

    def alert(self,message):
        print(message)

class Designer:
    def __init__(self):
        synologyPath = os.path.expanduser("~/Desktop/StartupFiles/system_files/synology.dfe")

        with open(synologyPath,"rb") as encrypedCred:
            encrypted_data = encrypedCred.read()

        KEY = b'*****PROPRIETARY INFO *****'
        cipher_suite = Fernet(KEY)

        config = json.loads((cipher_suite.decrypt(encrypted_data)).decode())

        self.USERNAME = config['CREDENTIALS']['Username']
        self.PASSWORD = config['CREDENTIALS']['Password']
        self.PORT = config['SERVER']['Port']
        self.IP_ADDRESS = config['SERVER']['Address']
        self.URL_ADDRESS = f"{self.IP_ADDRESS}:{self.PORT}"
        self.DEAL_FOLDER = config['SERVER']['Path']


def find_indesign_file(files):
    for file in files:
        if ".indd" in str(file).lower():
            return file
    return "False"



if __name__ == "__main__":
    artist = Designer()

    syn = Synology(artist.URL_ADDRESS,artist.USERNAME,artist.PASSWORD)
    thisList = syn.list("/Art Department")
    print(thisList)