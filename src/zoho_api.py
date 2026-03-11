import os
from zohocrmsdk.src.com.zoho.api.authenticator import OAuthToken
from zohocrmsdk.src.com.zoho.crm.api import Initializer
from zohocrmsdk.src.com.zoho.api.authenticator.store import FileStore
from zohocrmsdk.src.com.zoho.crm.api.attachments import (
    AttachmentsOperations,
    FileBodyWrapper,
    APIException,
    ActionWrapper,
    SuccessResponse
)
from zohocrmsdk.src.com.zoho.crm.api.util import StreamWrapper
from zohocrmsdk.src.com.zoho.crm.api.dc import USDataCenter
import requests
import base64
import hashlib


class Zoho:
    def __init__(self,fileStorePath):
        self.data = {}
        environment = USDataCenter.PRODUCTION()
        token = OAuthToken(
            client_id="*****PROPRIETARY INFO *****",
            client_secret="*****PROPRIETARY INFO *****",
            grant_token="*****PROPRIETARY INFO *****",
        )
        store = FileStore(file_path=fileStorePath)
        Initializer.initialize(environment=environment, token=token, store=store)
        print("Initialized")
        self.attachments_operations = AttachmentsOperations()

    def getDataFromInvoices(self,invoices):
        ZOHO_URL = "*****PROPRIETARY INFO *****"
        print(",".join([str(x) for x in invoices]))
        parameters = {
            "auth_type": "*****PROPRIETARY INFO *****",
            "*****PROPRIETARY INFO *****": "*****PROPRIETARY INFO *****",
            "invoices": ",".join([str(x) for x in invoices]),
        }
        zoho_response = requests.get(ZOHO_URL, params=parameters)
        self.data = zoho_response.json()

    def download_attachment(self, module_api_name, record_id, attachment_id, destination_folder):
        response = self.attachments_operations.get_attachment(
            attachment_id,
            record_id,
            module_api_name,
        )
        if response is not None:
            print("Status Code: " + str(response.get_status_code()))
            if response.get_status_code() in [204, 304]:
                print(
                    "No Content"
                    if response.get_status_code() == 204
                    else "Not Modified"
                )
                return
            response_object = response.get_object()
            if response_object is not None:
                if isinstance(response_object, FileBodyWrapper):
                    stream_wrapper = response_object.get_file()
                    # Construct the file name by joining the destinationFolder and the name from StreamWrapper instance
                    file_name = os.path.join(
                        destination_folder, stream_wrapper.get_name()
                    )
                    print(file_name)
                    # Open the destination file where the file needs to be written in 'wb' mode
                    with open(file_name, "wb") as f:
                        for chunk in stream_wrapper.get_stream():
                            f.write(chunk)
                        f.close()
                elif isinstance(response_object, APIException):
                    print("Status: " + response_object.get_status().get_value())
                    print("Code: " + response_object.get_code().get_value())
                    print("Details")
                    details = response_object.get_details()
                    for key, value in details.items():
                        print(key + " : " + str(value))
                    print("Message: " + response_object.get_message())

    def upload_attachment(self, module_api_name, record_id, absolute_file_path):
        try:
            file_body_wrapper = FileBodyWrapper()
            stream_wrapper = StreamWrapper(file_path=absolute_file_path)
            file_body_wrapper.set_file(stream_wrapper)
            response = self.attachments_operations.upload_attachments(record_id, module_api_name, file_body_wrapper)
        except:
            print("Couldn't Find File To Attach: " + str(record_id))
            return False

        if response is not None:
            print('Status Code: ' + str(response.get_status_code()))
            response_object = response.get_object()
            if response_object is not None:
                if isinstance(response_object, ActionWrapper):
                    action_response_list = response_object.get_data()
                    for action_response in action_response_list:
                        if isinstance(action_response, SuccessResponse):
                            print("Status: " + action_response.get_status().get_value())
                            print("Code: " + action_response.get_code().get_value())
                            print("Details")
                            details = action_response.get_details()
                            for key, value in details.items():
                                print(key + ' : ' + str(value))
                            print("Message: " + action_response.get_message())
                            return details['id']
                        elif isinstance(action_response, APIException):
                            print("Status: " + action_response.get_status().get_value())
                            print("Code: " + action_response.get_code().get_value())
                            print("Details")
                            details = action_response.get_details()
                            for key, value in details.items():
                                print(key + ' : ' + str(value))
                            print("Message: " + action_response.get_message())
                elif isinstance(response_object, APIException):
                    print("Status: " + response_object.get_status().get_value())
                    print("Code: " + response_object.get_code().get_value())
                    print("Details")
                    details = response_object.get_details()
                    for key, value in details.items():
                        print(key + ' : ' + str(value))
                    print("Message: " + response_object.get_message())
        return False

 

    def compareHashes(self,imagePath,hashList):
        with open(imagePath, "rb") as image_file:
            input_string = base64.b64encode(image_file.read())
            md5hash = hashlib.md5(input_string).hexdigest()
            for hash in hashList:
                if md5hash == hash:
                    return hash
            return False