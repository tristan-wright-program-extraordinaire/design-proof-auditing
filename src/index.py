import os
import shutil
import webview
from zipfile import ZipFile
import zoho_api
import ArtClasses as ac
import base64
import requests
import json
import time


class Api:
    def __init__(self, token_path):
        self.zoho_api = zoho_api.Zoho(token_path)
        self.zoho = ac.Zoho()
        self.artist = ac.Designer()
        self.syn = ac.Synology(
            self.artist.URL_ADDRESS, self.artist.USERNAME, self.artist.PASSWORD
        )
        self.apple = ac.AppleScript()
        self.currentFiles = {}
        self.mainFiles = {}
        self.invoices = []

    def fullscreen(self):
        webview.windows[0].toggle_fullscreen()

    def save_content(self, content):
        filename = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG)
        if not filename:
            return

        with open(filename, "w") as f:
            f.write(content)

    def ls(self):
        return os.listdir(".")

    def find_file(self):
        filename = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG)
        if filename:
            webview.windows[0].evaluate_js(f"window.pywebview.state.setLoading(true)")
        self.currentFiles = {}
        self.mainFiles = {}
        self.invoices = []
        self.unzip_geoshot(filename)
        self.zoho_api.getDataFromInvoices(self.invoices)
        print(self.zoho_api.data)
        self.create_react_object()
        print(self.currentFiles)
        webview.windows[0].evaluate_js(
            f"window.pywebview.state.setImportedFiles({self.currentFiles})"
        )

    def download_files(self, download_list):
        global guiFolder
        fileList = []
        attachmentPath = os.path.join(guiFolder, "static", "attachments")
        # attachmentPath = str(os.getcwd()) + "/gui/static/attachments/"
        if not os.path.exists(attachmentPath):
            os.mkdir(attachmentPath)
        for download in download_list:
            self.zoho_api.download_attachment(
                "Deals",
                int(download["deal_id"]),
                int(download["attachment_id"]),
                attachmentPath,
            )
            fileList.append(f"/static/attachments/{download['attachment_name']}")
        print(f"Files List: {', '.join(fileList)}")
        webview.windows[0].evaluate_js(
            f"window.pywebview.state.setDownloadAttachments({fileList})"
        )

    def unzip_geoshot(self, filename):
        global guiFolder
        noPrintFiles = []
        self.clear_files()
        unzipPath = os.path.join(guiFolder, "static", "geoshot")
        with ZipFile(str(filename[0]), "r") as zObject:
            zObject.extractall(unzipPath)
            zObject.close()
        rootFolder = [
            f"static/geoshot/{x}"
            for x in os.listdir(unzipPath)
            if not x == "__MACOSX" and not x == ".DS_Store"
        ][0]
        rootFolderPath = os.path.join(guiFolder, rootFolder)
        dealFolders = os.listdir(rootFolderPath)
        for folder in dealFolders:
            if not folder == "__MACOSX" and not folder == ".DS_Store" and not folder == "PDF":
                thisFolderPath = f"{rootFolderPath}/{folder}"
                print(thisFolderPath)
                fileList = os.listdir(thisFolderPath)
                printFile = self.find_print_file(fileList)
                attachmentPath = self.find_attachment_path(fileList)
                indesignFile = self.find_indesign_file(fileList)
                print(indesignFile)
                print(printFile)
                if not printFile == "False":
                    reactFilePath = f"/{rootFolder}/{folder}/{printFile}"
                    invoice = represents_int(str(folder).split("-")[0])
                    print(invoice)
                    if not invoice == "False":
                        self.invoices.append(invoice)
                        if not attachmentPath == "False":
                            attachmentPath = f"/{rootFolder}/{folder}/{attachmentPath}"
                        invoiceObj = {
                            "attachment_path": attachmentPath,
                            "indesign_file": indesignFile,
                            "proof_file": printFile,
                            "path": reactFilePath,
                            "status": "Accept",
                            "approval_type": "Normal"
                        }
                        self.currentFiles[str(invoice)] = invoiceObj
                elif not indesignFile == "False":
                    invoice = represents_int(str(indesignFile).split("-")[0])
                    indesign_path = f"{thisFolderPath}/{indesignFile}"
                    noPrintFiles.append({
                        "indesign_file": indesign_path,
                        "invoice": invoice,
                        "path": thisFolderPath
                    })
        if len(noPrintFiles) > 0:
            webview.windows[0].evaluate_js(
                f"window.pywebview.state.setMissingFiles({noPrintFiles})"
            )

    def create_react_object(self):
        global guiFolder
        print([x for x in self.zoho_api.data])
        for invoice in self.zoho_api.data:
            currDeal = self.zoho_api.data[invoice]
            print(invoice)
            print(currDeal)
            print(currDeal["nas_name"])
            self.currentFiles[str(invoice)]["special_instructions"] = str(currDeal["special_instructions"])
            self.currentFiles[str(invoice)]["deal_name"] = currDeal["deal_name"]
            self.currentFiles[str(invoice)]["deal_id"] = currDeal["deal_id"]
            self.currentFiles[str(invoice)]["invoice"] = invoice
            self.currentFiles[str(invoice)]["stage"] = currDeal["stage"]
            self.currentFiles[str(invoice)]["product_type"] = currDeal["product_type"]
            self.currentFiles[str(invoice)]["ad_size"] = currDeal["ad_size"][0]
            self.currentFiles[str(invoice)]["nas_name"] = currDeal["nas_name"]
            self.currentFiles[str(invoice)]["print_job_id"] = currDeal["print_job_id"]
            self.currentFiles[str(invoice)]["contact_email"] = currDeal["contact_email"]
            if "attachments" in currDeal:
                self.currentFiles[str(invoice)]["attachments"] = [
                    {
                        "id": x["id"],
                        "name": x["File_Name"],
                        "hash": self.zoho_api.data[invoice]["md5_hashes"][i],
                    }
                    for i, x in enumerate(self.zoho_api.data[invoice]["attachments"])
                ]
                if self.currentFiles[invoice]["attachment_path"] != "False":
                    linksPath = os.path.join(
                        guiFolder,
                        remove_leading_slash(
                            self.currentFiles[invoice]["attachment_path"]
                        ),
                    )
                    geo_links = os.listdir(linksPath)
                    print(geo_links)
                    for attachment in geo_links:
                        hash = self.zoho_api.compareHashes(
                            f"{linksPath}/{attachment}",
                            self.zoho_api.data[invoice]["md5_hashes"],
                        )
                        if hash:
                            for x in self.currentFiles[str(invoice)]["attachments"]:
                                if hash == x["hash"]:
                                    x["geo_file"] = (
                                        f"{self.currentFiles[invoice]['attachment_path']}/{attachment}"
                                    )
            else:
                self.currentFiles[invoice]["attachments"] = []

    def find_print_file(self, files):
        for file in files:
            if "p1.pdf" in str(file).lower():
                return file
        return "False"

    def find_indesign_file(self, files):
        for file in files:
            if ".indd" in str(file).lower():
                return file
        return "False"

    def find_attachment_path(self, files):
        for dir in files:
            if str(dir).lower() == "links":
                return dir
        return "False"

    def clear_files(self):
        global guiFolder
        folderPath = os.path.join(guiFolder, "static", "geoshot")
        try:
            files = os.listdir(folderPath)
            for file in files:
                file_path = os.path.join(folderPath, file)
                shutil.rmtree(file_path)
            print("All folders deleted successfully.")
        except OSError:
            print("Error occurred while deleting folders.")

    def submit_files(self, allFiles):
        global guiFolder
        webview.windows[0].evaluate_js(f"window.pywebview.state.setLoading(true)")
        tempNasList = []
        tempFixable = []
        tempApprovalList = []
        tempBrokenList = []
        tempDuplicate = []
        for x in allFiles:
            currFile = allFiles[x]

            ### Create Geoshot Objects For All Files
            self.mainFiles[currFile['deal_id']] = ac.Geoshot(
                deal_name = currFile['deal_name'],
                deal_id = currFile['deal_id'],
                invoice = currFile['invoice'],
                stage = currFile['stage'],
                product_type = currFile['product_type'],
                ad_size = currFile['ad_size'],
                nas_name = currFile['nas_name'],
                react_folder_path = os.path.join(guiFolder,remove_leading_slash(os.path.dirname(currFile['path']))),
                nas_course_path = os.path.join("Volumes",remove_leading_slash(self.artist.DEAL_FOLDER),currFile['nas_name']),
                indesign_file_name = currFile['indesign_file'],
                proof_file_name = currFile['proof_file'],
                print_job_id = currFile['print_job_id'],
                contact_email = currFile['contact_email'],
                status = currFile['status'],
                approval_type = currFile['approval_type']
            )

            ######## CREATE THE REACT LISTS ########

            if currFile["status"] == "Reject":
                ### If Rejected
                tempBrokenList.append(
                    {"deal_id": currFile["deal_id"], "deal_name": currFile["deal_name"]}
                )
            else:
                ### If file is going to be moved into the NAS
                tempApprovalList.append(
                    {"deal_id": currFile["deal_id"], "deal_name": currFile["deal_name"],"approval_type": currFile["approval_type"]}
                )
                try:
                    ### Try to place the file in the NAS
                    self.mainFiles[currFile['deal_id']].placeInNas(
                        self.syn, False
                    )
                except ValueError as err:
                    ## Course Not In Nas
                    tempNasList.append(
                        {
                            "deal_id": currFile["deal_id"],
                            "deal_name": currFile["deal_name"],
                            "nas_name": currFile["nas_name"],
                            "path": currFile["path"],
                        }
                    )
                except FileExistsError as err:
                    ## File Already Exists
                    tempDuplicate.append(
                        {
                            "deal_id": currFile["deal_id"],
                            "deal_name": currFile["deal_name"],
                            "path": str(err),
                        }
                    )
                if currFile["status"] == "Fix":
                    ## Deals To Fix Then Send
                    tempFixable.append(
                        {
                            "deal_id": currFile["deal_id"],
                            "deal_name": currFile["deal_name"],
                        }
                    )
        webview.windows[0].evaluate_js(
            f"window.pywebview.state.setFixableFiles({tempFixable})"
        )
        if len(tempNasList) > 0:
            for i, deal in enumerate(tempNasList):
                thisDeal = ac.Deal_From_Zoho(self.zoho,deal["deal_id"])
                tempNasList[i][
                    "nas_name"
                ] = f"{thisDeal.course_name} - {thisDeal.course_abbrev}"
                tempNasList[i]["course_id"] = thisDeal.course_id
            webview.windows[0].evaluate_js(
                f"window.pywebview.state.setFindNasFolders({tempNasList})"
            )
        webview.windows[0].evaluate_js(
            f"window.pywebview.state.setApproved({tempApprovalList})"
        )
        webview.windows[0].evaluate_js(
            f"window.pywebview.state.setRejected({tempBrokenList})"
        )
        webview.windows[0].evaluate_js(
            f"window.pywebview.state.setDuplicateFiles({tempDuplicate})"
        )
        webview.windows[0].evaluate_js(f"window.pywebview.state.setLoading(false)")

    def submit_nas(self, tempNasList):
        for deal in tempNasList:
            self.zoho.updateNasName(deal["course_id"], deal["nas_name"])
            thisFile = self.mainFiles[deal['deal_id']]
            thisFile.nas_name = deal["nas_name"]
            thisFile.nas_course_path = os.path.join("/Volumes",remove_leading_slash(self.artist.DEAL_FOLDER),deal['nas_name'])
            thisFile.createNasPaths()
            try:
                thisFile.placeInNas(
                    self.syn, True
                )
            except:
                #################################################################
                #################################################################
                ################# CREATE ERROR SOLUTION HERE ####################
                #################################################################
                #################################################################
                print(f"Wasn't Able To Place {deal['deal_name']}")
        webview.windows[0].evaluate_js(f"window.pywebview.state.setFindNasFolders([])")

    def send_emails(self):
        rejectedEmails = []
        normalFilesCount = len(list(filter(lambda x: self.mainFiles[x].approval_type == "Normal" and not self.mainFiles[x].status == "Reject", self.mainFiles)))
        rushedFilesCount = len(list(filter(lambda x: self.mainFiles[x].approval_type == "Rushed" and not self.mainFiles[x].status == "Reject", self.mainFiles)))
        abdFilesCount = len(list(filter(lambda x: self.mainFiles[x].approval_type == "ABD" and not self.mainFiles[x].status == "Reject", self.mainFiles)))
        loadingPercentObj = {
            "loading": "True",
            "Normal": {
                "total": normalFilesCount,
                "count": 0,
                "percentage": (normalFilesCount / (normalFilesCount + rushedFilesCount + abdFilesCount)) * 100
            },
            "Rushed": {
                "total": rushedFilesCount,
                "count": 0,
                "percentage": (rushedFilesCount / (normalFilesCount + rushedFilesCount + abdFilesCount)) * 100
            },
            "ABD": {
                "total": abdFilesCount,
                "count": 0,
                "percentage": (abdFilesCount / (normalFilesCount + rushedFilesCount + abdFilesCount)) * 100
            }
        }
        emptyObj = {}
        webview.windows[0].evaluate_js(
            f"window.pywebview.state.setEmailLoadingPercentage({loadingPercentObj})"
        )
        webview.windows[0].evaluate_js(
            f"window.pywebview.state.setErrorDetails({emptyObj})"
        )
        webview.windows[0].evaluate_js(
            f"window.pywebview.state.setSuccessDetails({emptyObj})"
        )
        for proof in self.mainFiles:
            thisProof = self.mainFiles[proof]
            if not thisProof.status == "Reject":
                if thisProof.status == "Fix":
                    files = os.listdir("/" + thisProof.nas_folder_path)
                    for file in files:
                        if "p2.pdf" in str(file).lower():
                            thisProof.proof_file_name = file
                            thisProof.proof_file_path = os.path.join(thisProof.nas_folder_path,file)
                    # Check to see if there is a different proof
                thisProof.attachment_id = self.zoho_api.upload_attachment("Deals",int(proof),"/" + thisProof.proof_file_path)
                
                url = "*****PROPRIETARY INFO *****"

                params = {
                    "auth_type": "*****PROPRIETARY INFO *****",
                    "*****PROPRIETARY INFO *****": "*****PROPRIETARY INFO *****",
                    "id": proof,
                    "attachment_id": thisProof.attachment_id,
                    "email": thisProof.contact_email,
                    "approval_type": thisProof.approval_type
                }
                headers = {"Content-Type":"application/JSON"}

                if thisProof.attachment_id:
                    response = requests.post(url,params=params, headers=headers)
                    responseJson = response.json()
                    print(responseJson)
                    if not thisProof.approval_type == "ABD":
                        errorBlock = json.loads(responseJson["details"]["output"])["data"][0]
                        responseCode = errorBlock["code"]
                        if not responseCode == "SUCCESS":
                            rejectedEmails.append({
                                "deal_id": proof,
                                "deal_name": thisProof.deal_name,
                                "code": responseCode,
                                "error": str(list(errorBlock["details"].keys())[0])
                            })
                else:
                    rejectedEmails.append({
                        "deal_id": proof,
                        "deal_name": thisProof.deal_name,
                        "code": "FAILURE",
                        "error": "Couldn't Upload Attachment"
                    })
                loadingPercentObj[thisProof.approval_type]["count"] += 1
                webview.windows[0].evaluate_js(
                    f"window.pywebview.state.setEmailLoadingPercentage({loadingPercentObj})"
                )
        loadingPercentObj = {"loading": "False"}
        webview.windows[0].evaluate_js(
            f"window.pywebview.state.setEmailLoadingPercentage({loadingPercentObj})"
        )
        webview.windows[0].evaluate_js(
            f"window.pywebview.state.setRejectedEmails({rejectedEmails})"
        )
                                
    def send_email(self, deal_id):
        thisProof = self.mainFiles[deal_id]

        if not thisProof.attachment_id:
            thisProof.attachment_id = self.zoho_api.upload_attachment("Deals",int(deal_id),"/" + thisProof.proof_file_path)
        
        url = "*****PROPRIETARY INFO *****"

        params = {
            "auth_type": "*****PROPRIETARY INFO *****",
            "*****PROPRIETARY INFO *****": "*****PROPRIETARY INFO *****",
            "attachment_id": thisProof.attachment_id,
            "id": deal_id,
            "approval_type": thisProof.approval_type
        }
        headers = {"Content-Type":"application/JSON"}

        if thisProof.attachment_id:
            response = requests.post(url,params=params, headers=headers)
            responseJson = response.json()
            errorBlock = json.loads(responseJson["details"]["output"])["data"][0]
            responseCode = errorBlock["code"]
            if not responseCode == "SUCCESS":
                errorObj = {
                    'message_id': responseJson["details"]["id"],
                    'code': responseCode,
                    'invoice': thisProof.invoice,
                    'error': str(list(errorBlock["details"].keys())[0])
                }
                webview.windows[0].evaluate_js(
                    f"window.pywebview.state.setErrorDetails({errorObj})"
                )
            else:
                successObj = {
                    'message_id': responseJson["details"]["id"],
                    'invoice': thisProof.invoice,
                }
                webview.windows[0].evaluate_js(
                    f"window.pywebview.state.setSuccessDetails({successObj})"
                )
        else:
            errorObj = {
                'message_id': deal_id,
                'code': "FAILURE",
                'invoice': thisProof.invoice,
                'error': "Couldn't Upload Attachment"
            }
            webview.windows[0].evaluate_js(
                f"window.pywebview.state.setErrorDetails({errorObj})"
            )

    def open_zoho(self, deal_id):
        self.apple.openUrl(f"*****PROPRIETARY INFO *****")

    def open_print_job_zoho(self, print_job_id):
        print(f"*****PROPRIETARY INFO *****")
        self.apple.openUrl(f"*****PROPRIETARY INFO *****")

    def open_indesign(self, deal_id):
        self.apple.openIndesignFile(f"/{self.mainFiles[deal_id].indesign_file_path}")

    def open_indesign_missing(self,path):
        self.apple.openIndesignFile(path)

    def open_finder_fixable(self, deal_id):
        self.apple.openFinder(f"/{self.mainFiles[deal_id].nas_folder_path}")

    def open_finder_approved(self, deal_id):
        self.apple.openFinder(f"/{self.mainFiles[deal_id].nas_folder_path}")

    def open_finder_duplicate(self, deal_id, path):
        self.apple.openFinder(f"/{self.mainFiles[deal_id].nas_folder_path}")
        self.apple.openFinder(f"/{self.mainFiles[deal_id].react_folder_path}")

    def open_finder_missing(self,path):
        self.apple.openFinder(path)

    def open_drawer(self):
        webview.windows[0].resize(width=1450, height=832)
        webview.windows[0].evaluate_js(f"window.pywebview.state.setDrawerOpen(true)")

    def close_drawer(self):
        webview.windows[0].resize(width=1200, height=832)
        webview.windows[0].evaluate_js(f"window.pywebview.state.setDrawerOpen(false)")


def get_entrypoint():
    def exists(path):
        return os.path.exists(os.path.join(os.path.dirname(__file__), path))

    if exists("../gui/index.html"):  # unfrozen development
        print("1")
        return "../gui/index.html"

    if exists("../Resources/gui/index.html"):  # frozen py2app
        print("2")
        return "../Resources/gui/index.html"

    if exists("./gui/index.html"):
        print("3")
        return "./gui/index.html"

    raise Exception("No index.html found")


def represents_int(s):
    try:
        int(s)
    except ValueError:
        print(s)
        return "False"
    else:
        return int(s)


def remove_leading_slash(path):
    return "/".join(path.split("/")[1:])


entry = get_entrypoint()
guiFolder = os.path.join(os.path.dirname(__file__), os.path.dirname(entry))
# token_storage_path = os.path.join(guiFolder, "static", "python_sdk_tokens.txt")
token_storage_path = os.path.join(os.path.dirname(__file__),"../Resources/python_sdk_tokens.txt")

if not os.path.exists(token_storage_path):
    token_storage_path = "./python_sdk_tokens.txt"

if __name__ == "__main__":
    attachmentPath = os.path.join(guiFolder, "static", "attachment")
    if not os.path.exists(attachmentPath):
        os.mkdir(attachmentPath)
    window = webview.create_window(
        "pywebview-react boilerplate",
        entry,
        js_api=Api(token_storage_path),
        width=1200,
        height=832,
    )
    webview.start(http_server=True, debug=True)