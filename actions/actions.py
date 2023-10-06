# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions



from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, EventType , UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import FormValidationAction
from rasa_sdk.events import Restarted
from rasa_sdk.events import FollowupAction
from rasa_sdk.events import UserUttered
from rasa_sdk.types import DomainDict
import requests
import xml.etree.ElementTree as ET
import webbrowser
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.utils import simpleSplit
import re
import datetime
from datetime import datetime
import xmltodict


class ActionGreet(Action):
    def name(self) -> str:
        return "action_greet"

    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(response="utter_greet")
        return []#SlotSet("greeted", True)
        
class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        # Handle fallback when the bot doesn't understand
        dispatcher.utter_message("I'm sorry, I didn't understand that. Can you please rephrase?")
        return [UserUtteranceReverted()]
    
class ActionHandleNetworkList(Action):
    def name(self) -> Text:
        return "action_handle_network_list"
    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        # Prepare the buttons for user selection
        buttons = [
                    {"title": "Hospital Name & Pin Code", "payload": "/hospital_name"},
                    {"title": "Pin Code", "payload": "/pin_code"}
                ]

        # Generate the button message to prompt user for selection
        dispatcher.utter_message(
            text="Please select an option to get details",
            buttons=buttons
        )

        return []

class ActionAskInsurerId(Action):
    def name(self) -> Text:
        return "action_ask_insurer_id"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        # Prepare the list of Indian states as buttons for user selection
        insurer_info = tracker.get_slot("insurer")
 
        if insurer_info:
            # Generate buttons using the insurer names from the dictionary
            buttons = [
                {"title": insurer_name, "payload": f"/insurer_id{{\"insurer_id\": \"{str(insurer_id)}\"}}"}
                for insurer_name, insurer_id in insurer_info.items()
            ]

            # Generate the button message to prompt the user for insurer selection
            dispatcher.utter_message(
                text="Please select your insurance from the options below:",
                buttons=buttons
            )
        else:
            dispatcher.utter_message(text="No insurer information available.")

        return [SlotSet("requested_slot", "insurer_id")]

class ActionAskHospital(Action):
    def name(self) -> Text:
        return "action_ask_hospital"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:


        dispatcher.utter_message(text="Please enter the hospital name:")

        return [SlotSet("requested_slot", "hospital")]

class ActionAskPin(Action):
    def name(self) -> Text:
        return "action_ask_pin"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:


        dispatcher.utter_message(text="Please provide your 6 digit PIN Code:")

        return [SlotSet("requested_slot", "pin")]

class ValidateNetworkListForm1(FormValidationAction):
    def name(self) -> Text:
        return "validate_network_list_form1"
    
    async def validate_insurer_id(
        self, 
        slot_value: Any, 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        # Get the insurer information from the tracker
        insurer_info = tracker.get_slot("insurer")

        # Validate if the provided insurer_id is in the insurer_info dictionary
        if slot_value in insurer_info.values():
            # The insurer_id is valid
            return {"insurer_id": slot_value}
        else:
            # The insurer_id is not valid, utter a validation message
            dispatcher.utter_message(text="Invalid insurer selected. Please select a valid insurer.")
            return {"insurer_id": None}


    async def validate_hospital(
        self, 
        slot_value: Any, 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
    # async def validate_policy_number(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        hospital = slot_value
        if hospital is not None:
            return {"hospital": hospital}
        else:
            dispatcher.utter_message(text="Please provide correct hospital name")
            return {"hospital": None}
   
    async def validate_pin(
        self, 
        slot_value: Any, 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        # dispatcher.utter_message(text=f"pin is {slot_value}")
        if not slot_value:
            # If slot is empty, ask for the PIN again
            return await self.ask_pin(dispatcher)
        
        if len(slot_value) == 6 and slot_value.isdigit():
            return {"pin": slot_value}
        else:
            return await self.ask_pin(dispatcher)
        
    async def ask_pin(self, dispatcher: CollectingDispatcher) -> Dict[Text, Any]:
        dispatcher.utter_message(text="Please provide your 6 digit PIN Code:")
        return {"pin": None}
    
class ValidateNetworkListForm2(FormValidationAction):
    def name(self) -> Text:
        return "validate_network_list_form2"
    
    async def validate_insurer_id(
        self, 
        slot_value: Any, 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        # Get the insurer information from the tracker
        insurer_info = tracker.get_slot("insurer")

        # Validate if the provided insurer_id is in the insurer_info dictionary
        if slot_value in insurer_info.values():
            # The insurer_id is valid
            return {"insurer_id": slot_value}
        else:
            # The insurer_id is not valid, utter a validation message
            dispatcher.utter_message(text="Invalid insurer selected. Please select a valid insurer.")
            return {"insurer_id": None}


    async def validate_pin(
        self, 
        slot_value: Any, 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        # dispatcher.utter_message(text=f"pin is {slot_value}")
        if not slot_value:
            # If slot is empty, ask for the PIN again
            return await self.ask_pin(dispatcher)
        
        if len(slot_value) == 6 and slot_value.isdigit():
            return {"pin": slot_value}
        else:
            return await self.ask_pin(dispatcher)
        
    async def ask_pin(self, dispatcher: CollectingDispatcher) -> Dict[Text, Any]:
        dispatcher.utter_message(text="Please provide your 6 digit PIN Code:")
        return {"pin": None}
  
class ActionFetchNetworks(Action):
    def name(self) -> Text:

        return "action_fetch_networks"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        insurer_id = tracker.get_slot("insurer_id")
        pin = tracker.get_slot("pin")
        hospital=tracker.get_slot("hospital")
        api_url = "https://testtips.vidalhealthtpa.com:7443/vidalwhatsappservice/WhatAppChatbot/hospitalDetails"
        # Define the payload to send to the API
        # Define headers with the required parameters
        payload = {}
        if hospital is None or hospital.strip() == "":
            headers = {
            'insId': insurer_id,
            'pinCode': pin,
            'Authorization': 'Basic VmlkYWxCb3Q6Qm90VWF0JDMxMg==',
            'hospitalName': '' }

            response = requests.request("POST", api_url, headers=headers, data=payload)
            if response.status_code == 400:
                dispatcher.utter_message(text="Error: Bad Request, please try again.")
                dispatcher.utter_message(text=response.content)
            elif response.status_code == 200:
                root = ET.fromstring(response.text)
                # Extract hospital names
                hospital_names = [hospital.find("HOSPITAL_NAME").text for hospital in root.findall(".//hospitals")]

                if not hospital_names:
                    # If the list is empty, send a message indicating no hospitals found
                    dispatcher.utter_message(text="No hospitals found for the given criteria. Please try again")
                else:
                    # Generate buttons for hospital names
                    buttons = []
                    for hospital_name in hospital_names:
                        payload = f"/show_hospital_details{{\"hosp_dtl\": \"{hospital_name}\"}}"
                        buttons.append({"title": hospital_name, "payload": payload})
                    
                    # Send a message with the hospital name buttons
                    dispatcher.utter_button_message("Please select a hospital:", buttons=buttons)
                    return [SlotSet("xml_response_network", response.text)]

            else:
                dispatcher.utter_message(text="Error fetching hospital details. Please try again.")
        else:
            headers = {
            'insId': insurer_id,
            'pinCode': pin,
            'Authorization': 'Basic VmlkYWxCb3Q6Qm90VWF0JDMxMg==',
            'hospitalName': hospital }

        # Call the API to fetch hospitals
            response = requests.request("POST", api_url, headers=headers, data=payload)
            if response.status_code == 400:
                dispatcher.utter_message(text="Error: Bad Request, please try again.")
                dispatcher.utter_message(text=response.content)
            elif response.status_code == 200:
                root = ET.fromstring(response.text)
                # Extract hospital names
                hospitals = root.findall(".//hospitals")
                
                if not hospitals:
                    # If the list is empty, send a message indicating no hospitals found
                    dispatcher.utter_message(text="No hospitals found for the given criteria. Please try again")
                else:
                    message = ""
                    for hospital in hospitals:
                        name = hospital.find("HOSPITAL_NAME").text
                        state = hospital.find("STATE_NAME").text
                        city = hospital.find("CITY_DESCRIPTION").text
                        address = hospital.find("ADDRESS").text
                        contact = hospital.find("CONTACT_NUMBER").text
                        # email = hospital.find("EMAIL_ID").text
                        latitude = hospital.find("LATITUDE").text
                        longitude = hospital.find("LONGITUDE").text

                        # Formatting the message to be dispatched
                        message += f"Hospital Name: {name}\n"
                        message += f"Address: {address}, {city}, {state}\n"
                        message += f"Contact Number: {contact}\n"
                        # message += f"Email ID: {email}\n"
                        message += f"Latitude: {latitude}\n"
                        message += f"Longitude: {longitude}\n"
                        
                    dispatcher.utter_message(text=message)

                # return [SlotSet("xml_response_network", response.text)]

            else:
                dispatcher.utter_message(text="Error fetching hospital details. Please try again.")

        dispatcher.utter_message(text="Download full list of Network hospitals : https://tips.vidalhealthtpa.com/vidalhealth/HospNetwork.htm")
        return [SlotSet("insurer_id", None),SlotSet("hospital", None),SlotSet("pin", None)]

class ActionShowHospitalDetails(Action):
    def name(self) -> Text:
        return "action_show_hospital_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        hospital_name = next(tracker.get_latest_entity_values("hosp_dtl"), None)
        root = ET.fromstring(tracker.get_slot("xml_response_network"))
        # dispatcher.utter_message(text=f"hospital_name: {hospital_name}")
        # dispatcher.utter_message(text=tracker.get_slot("xml_response"))
        if hospital_name and root:
            # root = ET.fromstring(xml_response)
        # Find the hospital with the selected name
            hospital_element = None
            for hosp in root.findall(".//hospitals"):
                # dispatcher.utter_message(text="hi")
                name = hosp.find("HOSPITAL_NAME").text
                # dispatcher.utter_message(text=f"name: {name}")
                if name == hospital_name:
                    hospital_element = hosp
                    break
            
            if hospital_element is not None:
                # Extract hospital details
                        name = hospital_element.find("HOSPITAL_NAME").text
                        state = hospital_element.find("STATE_NAME").text
                        city = hospital_element.find("CITY_DESCRIPTION").text
                        address = hospital_element.find("ADDRESS").text
                        contact = hospital_element.find("CONTACT_NUMBER").text
                        # email = hospital_element.find("EMAIL_ID").text
                        latitude = hospital_element.find("LATITUDE").text
                        longitude = hospital_element.find("LONGITUDE").text

                        # Formatting the message to be dispatched
                        message = ""

                        # Formatting the message to be dispatched
                        message += f"Hospital Name: {name}\n"
                        message += f"Address: {address}, {city}, {state}\n"
                        message += f"Contact Number: {contact}\n"
                        # message += f"Email ID: {email}\n"
                        message += f"Latitude: {latitude}\n"
                        message += f"Longitude: {longitude}\n"
                        dispatcher.utter_message(text=message)

            else:
                dispatcher.utter_message("Hospital not found.")
        else:
            dispatcher.utter_message("Hospital or Response Empty. Try Again.")
        dispatcher.utter_message(text="Download full list of Network hospitals : https://tips.vidalhealthtpa.com/vidalhealth/HospNetwork.htm")
        return [SlotSet("insurer_id", None),SlotSet("hospital", None),SlotSet("pin", None),SlotSet("xml_response_network", None)]

       
class ActionHandleVerification(Action):
    def name(self) -> Text:
        return "action_handle_verification"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        # Add any additional logic or API calls related to Option 1 handling
        verification= tracker.get_slot("verification_status")
        if(verification==False):
            dispatcher.utter_message(response="utter_verification")

        else:
            root = ET.fromstring(tracker.get_slot("xml_response"))
            option_type = tracker.get_slot("option_type")
            if option_type == "ecard":
                dependent_elements = root.findall(".//emp_dependent_list/dependent")
                if dependent_elements:
                    buttons = []
                    seen_names = set()  # A set to keep track of names we've already added
                    for dependent in dependent_elements:
                        name = dependent.find("name").text
                        if name not in seen_names:  # Check if we've already added this name
                            payload = f"/show_dependent_details{{\"dependent_name\": \"{name}\"}}"
                            buttons.append({"title": name, "payload": payload})
                            seen_names.add(name)  # Add the name to the seen_names set
                            
                    dispatcher.utter_button_message("Select a member to view details:", buttons=buttons)
                else:
                    dispatcher.utter_message(text="No members found.")


            elif option_type == "claim_status":

                claims = root.findall(".//paclaim_list/paclaim[claim_type='Re-imbursement']")
                if claims:
                    transaction_count = 0  # To keep track of the transaction number

                    for claim_element in claims:
                        if transaction_count == 5:
                            break

                        claim_number = claim_element.find("claim_number").text or "NA"
                        
                        # Extracting all the necessary details and replacing None with 'NA'
                        received_date = claim_element.find("received_date").text or "NA"
                        claimant_name = claim_element.find("claimant_name").text or "NA"
                        doa = claim_element.find("doa").text or "NA"
                        dod = claim_element.find("dod").text or "NA"
                        hosp_name = claim_element.find("hosp_name").text or "NA"
                        claim_amount = claim_element.find("claim_amount").text or "NA"
                        approved_amount = claim_element.find("approved_amount").text or "NA"
                        claim_status = claim_element.find("status").text or "NA"
                        letter_link = claim_element.find("letter_link").text or "NA"

                        # Creating the detailed message
                        details_message = f"""
                            Claim Number: {claim_number}
                            Received Date: {received_date}
                            Patient Name: {claimant_name}
                            Date of Admission: {doa}
                            Date of Discharge: {dod}
                            Hospital Name: {hosp_name}
                            Claim Amount: {claim_amount}
                            Approved Amount: {approved_amount}
                            Claim Status: {claim_status}
                            """

                        # Append letter link if available, else show 'NA'
                        if letter_link != "NA":
                            details_message += f"Download Letter: {letter_link} "
                        else:
                            details_message += "Download Letter: NA "
                        details_message += "\n\n"
                        # Send the detailed message using the dispatcher
                        dispatcher.utter_message(text=details_message)

                        # Increase the transaction count
                        transaction_count += 1
                else:
                    dispatcher.utter_message(text="No Re-imbursement claims found.")

            elif option_type == "cashless_status":
                claims = root.findall(".//paclaim_list/paclaim[claim_type='Cashless']")
                if claims:
                    transaction_count = 0  # To keep track of the transaction number

                    for claim_element in claims:
                        if transaction_count == 5:
                            break

                        claim_number = claim_element.find("claim_number").text or "NA"
                        
                        # Extracting all the necessary details and replacing None with 'NA'
                        received_date = claim_element.find("received_date").text or "NA"
                        claimant_name = claim_element.find("claimant_name").text or "NA"
                        doa = claim_element.find("doa").text or "NA"
                        dod = claim_element.find("dod").text or "NA"
                        hosp_name = claim_element.find("hosp_name").text or "NA"
                        claim_amount = claim_element.find("claim_amount").text or "NA"
                        approved_amount = claim_element.find("approved_amount").text or "NA"
                        claim_status = claim_element.find("status").text or "NA"
                        letter_link = claim_element.find("letter_link").text or "NA"

                        # Creating the detailed message
                        details_message = f"""
                            Claim Number: {claim_number}
                            Received Date: {received_date}
                            Patient Name: {claimant_name}
                            Date of Admission: {doa}
                            Date of Discharge: {dod}
                            Hospital Name: {hosp_name}
                            Claim Amount: {claim_amount}
                            Approved Amount: {approved_amount}
                            Cashless Status: {claim_status}
                            """

                        # Append letter link if available, else show 'NA'
                        if letter_link != "NA":
                            details_message += f"Download Letter: {letter_link}"
                        else:
                            details_message += "Download Letter: NA"
                        details_message += "\n\n"
                        # Send the detailed message using the dispatcher
                        dispatcher.utter_message(text=details_message)

                        # Increase the transaction count
                        transaction_count += 1
                else:
                    dispatcher.utter_message(text="No Cashless claims found.")

        
           
            elif option_type == "network_list":
                # Call ActionHandleNetworkList by returning a FollowupAction event
                return [FollowupAction("action_handle_network_list")]
        return []

class ActionShowDependentDetails(Action):
    def name(self) -> Text:
        return "action_show_dependent_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        dependent_name = next(tracker.get_latest_entity_values("dependent_name"), None)
        xml_response = tracker.get_slot("xml_response")  # Assuming the XML response is stored in a slot
        
        if dependent_name and xml_response:
            root = ET.fromstring(xml_response)

            matching_dependents = root.findall(".//emp_dependent_list/dependent[name='{}']".format(dependent_name))
            
            if matching_dependents:
                for dependent_element in matching_dependents:
                    policy_number = dependent_element.find("policy_number").text or "NA"
                    age = dependent_element.find("age").text or "NA"
                    gender = dependent_element.find("gender").text or "NA"
                    relship = dependent_element.find("relship").text or "NA"
                    coverage_type = dependent_element.find("coverage_type").text or "NA"
                    ecard_link = dependent_element.find("ecard_link").text or "NA"

                    details_message = f"Details of {dependent_name}:\n"
                    details_message += f"Coverage Type: {coverage_type}\n"
                    details_message += f"Policy Number: {policy_number}\n"
                    details_message += f"Age: {age}\n"
                    details_message += f"Gender: {gender}\n"
                    details_message += f"Relationship: {relship}\n"
                    details_message += f"Download E-Card: {ecard_link}\n\n\n"  # Added a newline for separation

                    dispatcher.utter_message(details_message)
            else:
                dispatcher.utter_message(text="Member not found.")
        else:
            dispatcher.utter_message(text="Member name or XML response not available.")
        
        return []



class ActionHandleRetail(Action):
    def name(self) -> Text:
        return "action_handle_retail"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        # Add any additional logic or API calls related to Option 1 handling
        dispatcher.utter_message(response="utter_retail")
        
        return []
    
class ActionHandleCorporate(Action):
    def name(self) -> Text:
        return "action_handle_corporate"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        # Add any additional logic or API calls related to Option 1 handling
        dispatcher.utter_message(response="utter_corporate")
        return []

class ActionHandleMobile(Action):
    def name(self) -> Text:
        return "action_handle_mobile"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        # Add any additional logic or API calls related to Option 1 handling
        dispatcher.utter_message("Verification via mobile number:")
        return [] #{"verification_type": "mobile"}

class ActionAskMobile(Action):
    def name(self) -> Text:
        return "action_ask_mobile"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(text="Please provide your 10 digit registered mobile number:")
        return []

class ActionAskOtp(Action):
    def name(self) -> Text:
        return "action_ask_otp"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        mobile_number = tracker.get_slot("mobile")
        policy_type = tracker.get_slot("policy_type")

        if not mobile_number or not policy_type:
            dispatcher.utter_message(text="Mobile number or policy type is not provided.")
            return [Restarted()]

        url = "https://testtips.vidalhealthtpa.com:7443/vidalwhatsappservice/WhatAppChatbot/validateMobile"

        payload = {}
        headers = {
        'mobileNo': mobile_number,
        'policyType': policy_type,
        'Authorization': 'Basic VmlkYWxCb3Q6Qm90VWF0JDMxMg=='
        }

# print(response.text)
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            # dispatcher.utter_message(text=f"response:\n\n{response}")
            if response.status_code == 200:
                try:

                    dispatcher.utter_message("Please enter the OTP you received.")

                # Set the slot to expect OTP
                    return [SlotSet("requested_slot", "otp")]
                    
                except ET.ParseError:
                    # If XML parsing fails, try to parse it as JSON
                    response_data = response.json()
                    if 'status' in response_data and 'message' in response_data:
                        dispatcher.utter_message(text=f"Mobile number validation failed. Please try other verification methods.")
                    else:
                        dispatcher.utter_message(text="Unknown error occurred. Please try again later.")

            else:
                dispatcher.utter_message(text=f"Mobile number validation failed. Please try other verification methods.")
                

        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred while validating the mobile number. Please try again")
        dispatcher.utter_message(text="Unable to fetch the details with provided Mobile number")    
        return [SlotSet("otp", None),SlotSet("mobile", None),FollowupAction("action_handle_mobile")]

class ValidateMobileForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_mobile_form"

    async def validate_mobile(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        # if tracker.get_intent_of_latest_message() == "mobile":
        mobile = slot_value
    
    # Checking if the mobile number is valid (10 digits)
        if len(mobile) == 10 and mobile.isdigit():
            return {"mobile": mobile}
        else:
            dispatcher.utter_message(text="Incorrect format. ")
            
            return {"mobile": None}
        
    async def validate_otp(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
         
        otp = slot_value
        if len(otp) != 6 or not otp.isdigit():
            dispatcher.utter_message(text="Incorrect format")
            return {"otp": None}
        
        mobile_number = tracker.get_slot("mobile")
        policy_type = tracker.get_slot("policy_type")

        # Call another API to verify the OTP
        otp_url = "https://testtips.vidalhealthtpa.com:7443/vidalwhatsappservice/WhatAppChatbot/validateMobileOTP"

        payload = {}
        headers = {
        'mobileNo': mobile_number,
        'Otp': otp,
        'policyType': policy_type,
        'Authorization': 'Basic VmlkYWxCb3Q6Qm90VWF0JDMxMg=='
        }
        # dispatcher.utter_message(text=f"url:\n\n{otp_url}, payload:\n\n{headers}")

        response_otp = requests.request("POST", otp_url, headers=headers, data=payload)

        if response_otp.status_code == 200:
            # Parse the XML response
            
            root = ET.fromstring(response_otp.text)
            remarks = root.find(".//remarks")
            # dispatcher.utter_message(text=response_otp.text)

            if remarks is not None and remarks.text == 'Valid':
                dispatcher.utter_message(text="OTP validation successful. You can proceed.")
                option_type = tracker.get_slot("option_type")
                insurer_code = {}  # Create an empty dictionary to store insurer information
                for dependent in root.findall(".//emp_dependent_list/dependent"):
                    insurance_id = dependent.find("insurance_id").text
                    insurance_name = dependent.find("insurance_name").text
                    insurer_code[insurance_name] = insurance_id
                # dispatcher.utter_message(text=f"insurer_code: {insurer_code}")
                if option_type == "ecard":
                    dependent_elements = root.findall(".//emp_dependent_list/dependent")
                    if dependent_elements:
                        buttons = []
                        seen_names = set()  # A set to keep track of names we've already added
                        for dependent in dependent_elements:
                            name = dependent.find("name").text
                            if name not in seen_names:  # Check if we've already added this name
                                payload = f"/show_dependent_details{{\"dependent_name\": \"{name}\"}}"
                                buttons.append({"title": name, "payload": payload})
                                seen_names.add(name)  # Add the name to the seen_names set
                                
                        dispatcher.utter_button_message("Select a member to view details:", buttons=buttons)
                    else:
                        dispatcher.utter_message(text="No members found.")

                elif option_type == "claim_status":

                    claims = root.findall(".//paclaim_list/paclaim[claim_type='Re-imbursement']")
                    if claims:
                        transaction_count = 0  # To keep track of the transaction number

                        for claim_element in claims:
                            if transaction_count == 5:
                                break

                            claim_number = claim_element.find("claim_number").text or "NA"
                            
                            # Extracting all the necessary details and replacing None with 'NA'
                            received_date = claim_element.find("received_date").text or "NA"
                            claimant_name = claim_element.find("claimant_name").text or "NA"
                            doa = claim_element.find("doa").text or "NA"
                            dod = claim_element.find("dod").text or "NA"
                            hosp_name = claim_element.find("hosp_name").text or "NA"
                            claim_amount = claim_element.find("claim_amount").text or "NA"
                            approved_amount = claim_element.find("approved_amount").text or "NA"
                            claim_status = claim_element.find("status").text or "NA"
                            letter_link = claim_element.find("letter_link").text or "NA"

                            # Creating the detailed message
                            details_message = f"""
                                Claim Number: {claim_number}
                                Received Date: {received_date}
                                Patient Name: {claimant_name}
                                Date of Admission: {doa}
                                Date of Discharge: {dod}
                                Hospital Name: {hosp_name}
                                Claim Amount: {claim_amount}
                                Approved Amount: {approved_amount}
                                Claim Status: {claim_status}
                                """

                            # Append letter link if available, else show 'NA'
                            if letter_link != "NA":
                                details_message += f"Download Letter: {letter_link} "
                            else:
                                details_message += "Download Letter: NA "
                            details_message += "\n\n"
                            # Send the detailed message using the dispatcher
                            dispatcher.utter_message(text=details_message)

                            # Increase the transaction count
                            transaction_count += 1
                    else:
                        dispatcher.utter_message(text="No Re-imbursement claims found.")

                elif option_type == "cashless_status":
                    claims = root.findall(".//paclaim_list/paclaim[claim_type='Cashless']")
                    if claims:
                        transaction_count = 0  # To keep track of the transaction number

                        for claim_element in claims:
                            if transaction_count == 5:
                                break


                            claim_number = claim_element.find("claim_number").text or "NA"
                            
                            # Extracting all the necessary details and replacing None with 'NA'
                            received_date = claim_element.find("received_date").text or "NA"
                            claimant_name = claim_element.find("claimant_name").text or "NA"
                            doa = claim_element.find("doa").text or "NA"
                            dod = claim_element.find("dod").text or "NA"
                            hosp_name = claim_element.find("hosp_name").text or "NA"
                            claim_amount = claim_element.find("claim_amount").text or "NA"
                            approved_amount = claim_element.find("approved_amount").text or "NA"
                            claim_status = claim_element.find("status").text or "NA"
                            letter_link = claim_element.find("letter_link").text or "NA"

                            # Creating the detailed message
                            details_message = f"""
                                Claim Number: {claim_number}
                                Received Date: {received_date}
                                Patient Name: {claimant_name}
                                Date of Admission: {doa}
                                Date of Discharge: {dod}
                                Hospital Name: {hosp_name}
                                Claim Amount: {claim_amount}
                                Approved Amount: {approved_amount}
                                Cashless Status: {claim_status}
                                """

                            # Append letter link if available, else show 'NA'
                            if letter_link != "NA":
                                details_message += f"Download Letter: {letter_link} "
                            else:
                                details_message += "Download Letter: NA "
                            details_message += "\n\n"
                            # Send the detailed message using the dispatcher
                            dispatcher.utter_message(text=details_message)

                            # Increase the transaction count
                            transaction_count += 1
                    else:
                        dispatcher.utter_message(text="No Cashless claims found.")

        
                elif option_type == "network_list":
                # Call ActionHandleNetworkList by returning a FollowupAction event
                    action_handle_network_list = ActionHandleNetworkList()
                    action_handle_network_list.run(dispatcher, tracker, domain)
                    # return {"otp": otp, "xml_response": response_otp.text, "verification_status": True, "insurer": insurer_code}


                return  {"otp": otp, "xml_response": response_otp.text, "verification_status": True, "insurer": insurer_code}
            else:
                dispatcher.utter_message(text="OTP validation failed. Please enter correct OTP")
                return {"otp": None}
        else:
            # Handle error response
            dispatcher.utter_message(text="Error in OTP validation request. Please try again.")
        # return {"otp": None}
        if policy_type == "RTL":
            action_handle_retail = ActionHandleRetail()
            action_handle_retail.run(dispatcher, tracker, domain)
            return {"otp": None,"mobile": None,"verification_type": None}
        else:
            action_handle_corporate = ActionHandleCorporate()
            action_handle_corporate.run(dispatcher, tracker, domain)
            return {"otp": None,"mobile": None,"verification_type": None}

    
class ActionHandlePolicyDetails(Action):
    def name(self) -> Text:
        return "action_handle_policy_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        # Add any additional logic or API calls related to Option 1 handling
        dispatcher.utter_message("Verification via policy details.")
        return []

    
class ActionHandleEmployeeDetails(Action):
    def name(self) -> Text:
        return "action_handle_employee_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        # Add any additional logic or API calls related to Option 1 handling
        dispatcher.utter_message("Verification via employee details.")
        return []
    
class ActionAskDOB(Action):
    def name(self) -> Text:
        return "action_ask_dob"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(text="Please provide your date of birth in the format (DD/MM/YYYY):")
        return []
    
class ActionAskPolicyNumber(Action):
    def name(self) -> Text:
        return "action_ask_policy_number"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(text="Please provide your policy number:")
        return []
 
class ActionAskEmployeeNumber(Action):
    def name(self) -> Text:
        return "action_ask_employee_number"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(text="Please provide your employee number:")
        return []

class ActionAskCorporateName(Action):
    def name(self) -> Text:
        return "action_ask_corporate_name"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(text="Please provide your corporate name:")
        return []

class ValidatePolicyDetailsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_policy_details_form"

    async def validate_dob(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        
        dob = slot_value
        pattern = re.compile(r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$')
        if pattern.match(dob):
            dd, mm, yyyy = map(int, dob.split('/'))
            try:
                datetime(yyyy, mm, dd)
                return {"dob": dob}
            except ValueError:
                dispatcher.utter_message("Incorrect format")
                return {"dob": None}
        else:
            dispatcher.utter_message("Incorrect format")
            return {"dob": None}
        
    async def validate_policy_number(
        self, 
        slot_value: Any, 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
    # async def validate_policy_number(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        policy_number = slot_value
        if policy_number is not None:
            return {"policy_number": policy_number}
        else:
            return await self.ask_policy_number(dispatcher)
        
    async def ask_policy_number(self, dispatcher: CollectingDispatcher) -> Dict[Text, Any]:
        dispatcher.utter_message(text="Incorrect format")
        return {"policy_number": None}

class ValidateEmployeeDetailsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_employee_details_form"

    # async def validate_dob(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
    async def validate_dob(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        
        dob = slot_value
        pattern = re.compile(r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$')
        if pattern.match(dob):
            dd, mm, yyyy = map(int, dob.split('/'))
            try:
                datetime(yyyy, mm, dd)
                return {"dob": dob}
            except ValueError:
                dispatcher.utter_message("Incorrect format")
                return {"dob": None}
        else:
            dispatcher.utter_message("Incorrect format")
            return {"dob": None}
        
    async def validate_corporate_name(
        self, 
        slot_value: Any, 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:

        if slot_value is not None:
            return {"corporate_name": slot_value}
        else:
            dispatcher.utter_message(text="Incorrect format")
            return {"corporate_name": None}
        
    async def validate_employee_number(
        self, 
        slot_value: Any, 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:

    #     if slot_value is not None:
    #         return {"id_number": slot_value}
    #     else:
    #         return await self.ask_employee_number(dispatcher)
    # async def validate_employee_number(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        employee_number = slot_value
        if employee_number is not None:
            return {"employee_number": employee_number}    
        else:
            return await self.ask_employee_number(dispatcher)
        
    async def ask_employee_number(self, dispatcher: CollectingDispatcher) -> Dict[Text, Any]:
        dispatcher.utter_message(text="Incorrect format")
        return {"employee_number": None}

class ActionVerify(Action):
    def name(self) -> Text:
        return "action_verify"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        verification_type=tracker.get_slot("verification_type")
        policy_type=tracker.get_slot("policy_type")
        option_type=tracker.get_slot("option_type")

        if verification_type == "policy_details" :

            policy_type = tracker.get_slot("policy_type")
            policy_number = tracker.get_slot("policy_number")
            dob = tracker.get_slot("dob")
            url = "https://testtips.vidalhealthtpa.com:7443/vidalwhatsappservice/WhatAppChatbot/verificationDtls"

            payload = {}
            headers = {
            'policyType': policy_type,
            'policyNO' : policy_number,
            'empNO': '',
            'corpName': '',
            'dob': dob,
            'Authorization': 'Basic VmlkYWxCb3Q6Qm90VWF0JDMxMg=='
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
            # Parse the XML response
                root = ET.fromstring(response.text)
                # tracker.slots["xml_response"] = response.text
                if not root.find(".//emp_dependent_list/dependent") and not root.find(".//paclaim_list/paclaim"):
                    dispatcher.utter_message(text="Verification failed")
                                    
                    
                    return [SlotSet("policy_number", None),SlotSet("dob", None),SlotSet("verification_type", None), FollowupAction("action_handle_retail") ]
                    
                dispatcher.utter_message(text="Verification successfully completed")    
                insurer_code = {}  # Create an empty dictionary to store insurer information
                for dependent in root.findall(".//emp_dependent_list/dependent"):
                    insurance_id = dependent.find("insurance_id").text
                    insurance_name = dependent.find("insurance_name").text
                    insurer_code[insurance_name] = insurance_id             
                if option_type == "ecard":
                    dependent_elements = root.findall(".//emp_dependent_list/dependent")
                    if dependent_elements:
                        buttons = []
                        seen_names = set()  # A set to keep track of names we've already added
                        for dependent in dependent_elements:
                            name = dependent.find("name").text
                            if name not in seen_names:  # Check if we've already added this name
                                payload = f"/show_dependent_details{{\"dependent_name\": \"{name}\"}}"
                                buttons.append({"title": name, "payload": payload})
                                seen_names.add(name)  # Add the name to the seen_names set
                                
                        dispatcher.utter_button_message("Select a member to view details:", buttons=buttons)
                    else:
                        dispatcher.utter_message(text="No members found.")

                elif option_type == "claim_status":

                    claims = root.findall(".//paclaim_list/paclaim[claim_type='Re-imbursement']")
                    if claims:
                        transaction_count = 0  # To keep track of the transaction number

                        for claim_element in claims:
                            if transaction_count == 5:
                                break

                            claim_number = claim_element.find("claim_number").text or "NA"
                            
                            # Extracting all the necessary details and replacing None with 'NA'
                            received_date = claim_element.find("received_date").text or "NA"
                            claimant_name = claim_element.find("claimant_name").text or "NA"
                            doa = claim_element.find("doa").text or "NA"
                            dod = claim_element.find("dod").text or "NA"
                            hosp_name = claim_element.find("hosp_name").text or "NA"
                            claim_amount = claim_element.find("claim_amount").text or "NA"
                            approved_amount = claim_element.find("approved_amount").text or "NA"
                            claim_status = claim_element.find("status").text or "NA"
                            letter_link = claim_element.find("letter_link").text or "NA"

                            # Creating the detailed message
                            details_message = f"""
                                Claim Number: {claim_number}
                                Received Date: {received_date}
                                Patient Name: {claimant_name}
                                Date of Admission: {doa}
                                Date of Discharge: {dod}
                                Hospital Name: {hosp_name}
                                Claim Amount: {claim_amount}
                                Approved Amount: {approved_amount}
                                Claim Status: {claim_status}
                                """

                            # Append letter link if available, else show 'NA'
                            if letter_link != "NA":
                                details_message += f"Download Letter: {letter_link} "
                            else:
                                details_message += "Download Letter: NA "
                            details_message += "\n\n"
                            # Send the detailed message using the dispatcher
                            dispatcher.utter_message(text=details_message)

                            # Increase the transaction count
                            transaction_count += 1
                    else:
                        dispatcher.utter_message(text="No Re-imbursement claims found.")

                elif option_type == "cashless_status":
                    claims = root.findall(".//paclaim_list/paclaim[claim_type='Cashless']")
                    if claims:
                        transaction_count = 0  # To keep track of the transaction number

                        for claim_element in claims:
                            if transaction_count == 5:
                                break

                            claim_number = claim_element.find("claim_number").text or "NA"
                            
                            # Extracting all the necessary details and replacing None with 'NA'
                            received_date = claim_element.find("received_date").text or "NA"
                            claimant_name = claim_element.find("claimant_name").text or "NA"
                            doa = claim_element.find("doa").text or "NA"
                            dod = claim_element.find("dod").text or "NA"
                            hosp_name = claim_element.find("hosp_name").text or "NA"
                            claim_amount = claim_element.find("claim_amount").text or "NA"
                            approved_amount = claim_element.find("approved_amount").text or "NA"
                            claim_status = claim_element.find("status").text or "NA"
                            letter_link = claim_element.find("letter_link").text or "NA"

                            # Creating the detailed message
                            details_message = f"""
                                Claim Number: {claim_number}
                                Received Date: {received_date}
                                Patient Name: {claimant_name}
                                Date of Admission: {doa}
                                Date of Discharge: {dod}
                                Hospital Name: {hosp_name}
                                Claim Amount: {claim_amount}
                                Approved Amount: {approved_amount}
                                Cashless Status: {claim_status}
                                """

                            # Append letter link if available, else show 'NA'
                            if letter_link != "NA":
                                details_message += f"Download Letter: {letter_link}"
                            else:
                                details_message += "Download Letter: NA "
                            details_message += "\n\n"
                            # Send the detailed message using the dispatcher
                            dispatcher.utter_message(text=details_message)

                            # Increase the transaction count
                            transaction_count += 1
                    else:
                        dispatcher.utter_message(text="No Cashless claims found.")

            
                elif option_type == "network_list":
                    return [SlotSet("xml_response", response.text), SlotSet("insurer", insurer_code), SlotSet("verification_status", True), FollowupAction("action_handle_network_list")]
            
                return [SlotSet("xml_response", response.text), SlotSet("insurer", insurer_code), SlotSet("verification_status", True)]
            else:
                dispatcher.utter_message(text="Error: Unknown, please try again.")
                
            return [SlotSet("policy_number", None),SlotSet("dob", None),SlotSet("verification_type", None), FollowupAction("action_handle_retail") ]

        elif verification_type == "employee_details":

            policy_type = tracker.get_slot("policy_type")
            corporate_name = tracker.get_slot("corporate_name")
            employee_number = tracker.get_slot("employee_number")
            dob = tracker.get_slot("dob")
            url = "https://testtips.vidalhealthtpa.com:7443/vidalwhatsappservice/WhatAppChatbot/verificationDtls"

            payload = {}
            headers = {
            'policyType': policy_type,
            'policyNO' : '',
            'empNO': employee_number,
            'corpName': corporate_name,
            'dob': dob,
            'Authorization': 'Basic VmlkYWxCb3Q6Qm90VWF0JDMxMg=='
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
            # Parse the XML response
                root = ET.fromstring(response.text)
                # dispatcher.utter_message(text=f"response: {response.text}")
                dependent_element = root.find(".//emp_dependent_list/dependent")
                paclaim_element = root.find(".//paclaim_list/paclaim")
                
                if not dependent_element and not paclaim_element:
                    dispatcher.utter_message(text="Verification failed")
                # tracker.slots["xml_response"] = response.text
                # if not root.find(".//emp_dependent_list/dependent") and not root.find(".//paclaim_list/paclaim"):
                    # dispatcher.utter_message(text="Verification failed")
                    return [SlotSet("corporate_name", None),SlotSet("employee_number", None),SlotSet("dob", None),SlotSet("verification_type", None), FollowupAction("action_handle_corporate") ]

                dispatcher.utter_message(text="Verification successfully completed")                
                insurer_code = {}  # Create an empty dictionary to store insurer information
                for dependent in root.findall(".//emp_dependent_list/dependent"):
                    insurance_id = dependent.find("insurance_id").text
                    insurance_name = dependent.find("insurance_name").text
                    insurer_code[insurance_name] = insurance_id

                if option_type == "ecard":
                    dependent_elements = root.findall(".//emp_dependent_list/dependent")
                    if dependent_elements:
                        buttons = []
                        seen_names = set()  # A set to keep track of names we've already added
                        for dependent in dependent_elements:
                            name = dependent.find("name").text
                            if name not in seen_names:  # Check if we've already added this name
                                payload = f"/show_dependent_details{{\"dependent_name\": \"{name}\"}}"
                                buttons.append({"title": name, "payload": payload})
                                seen_names.add(name)  # Add the name to the seen_names set
                                
                        dispatcher.utter_button_message("Select a member to view details:", buttons=buttons)
                    else:
                        dispatcher.utter_message(text="No members found.")

                elif option_type == "claim_status":

                    claims = root.findall(".//paclaim_list/paclaim[claim_type='Re-imbursement']")
                    if claims:
                        transaction_count = 0  # To keep track of the transaction number

                        for claim_element in claims:
                            if transaction_count == 5:
                                break

                            claim_number = claim_element.find("claim_number").text or "NA"
                            
                            # Extracting all the necessary details and replacing None with 'NA'
                            received_date = claim_element.find("received_date").text or "NA"
                            claimant_name = claim_element.find("claimant_name").text or "NA"
                            doa = claim_element.find("doa").text or "NA"
                            dod = claim_element.find("dod").text or "NA"
                            hosp_name = claim_element.find("hosp_name").text or "NA"
                            claim_amount = claim_element.find("claim_amount").text or "NA"
                            approved_amount = claim_element.find("approved_amount").text or "NA"
                            claim_status = claim_element.find("status").text or "NA"
                            letter_link = claim_element.find("letter_link").text or "NA"

                            # Creating the detailed message
                            details_message = f"""
                                Claim Number: {claim_number}
                                Received Date: {received_date}
                                Patient Name: {claimant_name}
                                Date of Admission: {doa}
                                Date of Discharge: {dod}
                                Hospital Name: {hosp_name}
                                Claim Amount: {claim_amount}
                                Approved Amount: {approved_amount}
                                Claim Status: {claim_status}
                                """

                            # Append letter link if available, else show 'NA'
                            if letter_link != "NA":
                                details_message += f"Download Letter: {letter_link} "
                            else:
                                details_message += "Download Letter: NA "
                            details_message += "\n\n"
                            # Send the detailed message using the dispatcher
                            dispatcher.utter_message(text=details_message)

                            # Increase the transaction count
                            transaction_count += 1
                    else:
                        dispatcher.utter_message(text="No Re-imbursement claims found.")

                elif option_type == "cashless_status":
                    claims = root.findall(".//paclaim_list/paclaim[claim_type='Cashless']")
                    if claims:
                        transaction_count = 0  # To keep track of the transaction number

                        for claim_element in claims:
                            if transaction_count == 5:
                                break

                            claim_number = claim_element.find("claim_number").text or "NA"
                            
                            # Extracting all the necessary details and replacing None with 'NA'
                            received_date = claim_element.find("received_date").text or "NA"
                            claimant_name = claim_element.find("claimant_name").text or "NA"
                            doa = claim_element.find("doa").text or "NA"
                            dod = claim_element.find("dod").text or "NA"
                            hosp_name = claim_element.find("hosp_name").text or "NA"
                            claim_amount = claim_element.find("claim_amount").text or "NA"
                            approved_amount = claim_element.find("approved_amount").text or "NA"
                            claim_status = claim_element.find("status").text or "NA"
                            letter_link = claim_element.find("letter_link").text or "NA"

                            # Creating the detailed message
                            details_message = f"""
                                Claim Number: {claim_number}
                                Received Date: {received_date}
                                Patient Name: {claimant_name}
                                Date of Admission: {doa}
                                Date of Discharge: {dod}
                                Hospital Name: {hosp_name}
                                Claim Amount: {claim_amount}
                                Approved Amount: {approved_amount}
                                Cashless Status: {claim_status}
                                """

                            # Append letter link if available, else show 'NA'
                            if letter_link != "NA":
                                details_message += f"Download Letter: {letter_link}"
                            else:
                                details_message += "Download Letter: NA "
                            details_message += "\n\n"
                            # Send the detailed message using the dispatcher
                            dispatcher.utter_message(text=details_message)

                            # Increase the transaction count
                            transaction_count += 1
                    else:
                        dispatcher.utter_message(text="No Cashless claims found.")

            
                elif option_type == "network_list":
                    return [SlotSet("xml_response", response.text), SlotSet("insurer", insurer_code), SlotSet("verification_status", True), FollowupAction("action_handle_network_list")]
            
                return [SlotSet("xml_response", response.text), SlotSet("insurer", insurer_code), SlotSet("verification_status", True)]
            else:
                dispatcher.utter_message(text="Error: Unknown, please try again")

            return [SlotSet("corporate_name", None),SlotSet("employee_number", None),SlotSet("dob", None),SlotSet("verification_type", None), FollowupAction("action_handle_corporate") ]

        return [Restarted()]
    

class ActionHandleClaimIntimation(Action):
    def name(self) -> Text:
        return "action_handle_claim_intimation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        # Add any additional logic or API calls related to Option 2 handling
        # dispatcher.utter_message("You selected Claim Intimation.")
        url = "https://tips.vidalhealthtpa.com/vidalhealth/loginClmIntimation.htm"



        # Respond to the user
        dispatcher.utter_message(text=f"{url} for Claim Intimation" )

        return []
    
class ActionHandleClaimProcess(Action):
    def name(self) -> Text:
        return "action_handle_claim_process"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        # Add any additional logic or API calls related to Option 2 handling
        # dispatcher.utter_message("You selected Claim Process.")
        url = "https://www.vidalhealthtpa.com/home/Claim-Guide"


        # Respond to the user
        dispatcher.utter_message(text=f"{url} for Claim Process" )

        return []

class ActionHandleBranches(Action):
    def name(self) -> Text:
        return "action_handle_branches"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        # Add any additional logic or API calls related to Option 2 handling
        # dispatcher.utter_message("You selected Branches.")
        url = "https://www.vidalhealthtpa.com/home/About/Branches.html"


        # Respond to the user
        dispatcher.utter_message(text=f"{url} for Branches" )

        return []    

class ActionHandleDownload(Action):
    def name(self) -> Text:
        return "action_handle_download"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        # Add any additional logic or API calls related to Option 2 handling
        # dispatcher.utter_message("You selected Download. ")
        url = "https://www.vidalhealthtpa.com/home/Forms.html"

        webbrowser.open(url)
        dispatcher.utter_message(text=f"{url} for Downloads" )
        # dispatcher.utter_message(text=url)

        return []
 
    

# INSURERS = [ 'NATIONAL INSURANCE COMPANY LTD', 'ORIENTAL INSURANCE COMPANY LIMITED', 'ORIENTAL INSURANCE CO', 'NEW INDIA ASSURANCE COMPANY LTD', 'NEW INDIA COMPANY GJ', 'NEW INDIA COMPANY NP', 'NEW INDIA COMPANY TG', 'NEW INSURANCE COMPANY', 'NEW INSURANCE COMPANY LTD', 'UNION INSURANCE COMPANY', 'UNITED INDIA INSURANCE COMPANY LTD']

# # A list of Indian states (you can add more if needed)
# INDIAN_STATES = ['Andaman and Nicobar Islands', 'Andhrapradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chandigarh', 'Chhattisgarh', 'DDSR', 'Dadra and Nagar Haveli', 'Daman and Diu', 'Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Lakshadweep', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Orissa', 'Pondicherry', 'Punjab', 'QQQQ', 'REW R DSFE', 'Rajasthan', 'Sikkim', 'Tamilnadu', 'Telangana', 'Tripura', 'Unknown', 'Uttar Pradesh', 'Uttaranchal', 'West Bengal', 'a', 'aa', 'aaq', 'd', 'dfdfd', 'dfdfdk', 'dfsds', 'dsd', 'ere', 'nnnn', 'test 1', 'test state']

# # Specify the path to the JSON file you previously saved
# input_file_path = 'state_data.json'

# # Read the data from the JSON file
# with open(input_file_path, 'r') as json_file:
#     CITIES_BY_STATE = json.load(json_file)

# class ActionAskInsurer(Action):
#     def name(self) -> Text:
#         return "action_ask_insurer"

#     def run(
#         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     ) -> List[EventType]:
#         # Prepare the list of Indian states as buttons for user selection
#         buttons = []
#         for insurer in INSURERS:
#             buttons.append({"title": insurer, "payload": f"/inform_insurer{{\"insurer\": \"{insurer}\"}}"})

#         # Generate the button message to prompt user for selection
#         dispatcher.utter_message(
#             text="Please select your insurance from the options below:",
#             buttons=buttons
#         )


#         return []

# class ActionAskState(Action):
#     def name(self) -> Text:
#         return "action_ask_state"
    
#     # def run(
#     #     self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     # ) -> List[EventType]:
#     #     # Get the list of Indian states
#     #     indian_states = INDIAN_STATES

#     #     # Generate a comma-separated list of state names
#     #     state_list = ", ".join(indian_states)

#     #     # Generate the message to prompt the user to select a state
#     #     dispatcher.utter_message(text=f"Please select your state from the following list: {state_list}")

#     #     return []
    # def run(
    #     self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    # ) -> List[EventType]:
    #     # Prepare the list of Indian states as buttons for user selection
    #     buttons = []
    #     for state in INDIAN_STATES:
    #         buttons.append({"title": state, "payload": f"/inform{{\"state\": \"{state}\"}}"})

    #     # Generate the button message to prompt user for selection
    #     dispatcher.utter_message(
    #         text="Please select your state from the options below:",
    #         buttons=buttons
    #     )

    #     return []
    
# class ActionAskCities(Action):
#     def name(self) -> Text:
#         return "action_ask_city"

#     def run(
#         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     ) -> List[Dict[Text, Any]]:
#         # Get the selected state from the user's input
#         selected_state = tracker.get_slot("state")

#         # Check if the selected state is in the CITIES_BY_STATE dictionary
#         if selected_state in CITIES_BY_STATE:
#             cities = CITIES_BY_STATE[selected_state]
#             # Generate the button message to prompt user for city selection
#             buttons = [{"title": city, "payload": f"/inform{{\"city\": \"{city}\"}}"} for city in cities]
#             dispatcher.utter_message(
#                 text=f"Please select a city in {selected_state} from the options below:",
#                 buttons=buttons
#             )
#         else:
#             dispatcher.utter_message("Invalid state selected. Please choose a valid state.")

#         return []




            # Extract emp_dependent_list data and print it
                # for dependent in root.findall(".//emp_dependent_list/dependent"):
                #     abbrevation_code = dependent.find("abbrevation_code").text
                #     # tracker.slots["insurer"] = abbrevation_code
                #     policy_number = dependent.find("policy_number").text
                #     enrollment_id = dependent.find("enrollment_id").text
                #     name = dependent.find("name").text
                #     age = dependent.find("age").text
                #     gender = dependent.find("gender").text
                #     relship = dependent.find("relship").text
                #     ecard_link = dependent.find("ecard_link").text

                #     details = (
                #         f"Policy Number: {policy_number}\n"
                #         f"Enrollment ID: {enrollment_id}\n"
                #         f"Name: {name}\n"
                #         f"Age: {age}\n"
                #         f"Gender: {gender}\n"
                #         f"Relationship: {relship}\n"
                #         f"Ecard Link: {ecard_link}\n"
                #     )

                #     dispatcher.utter_message(text=details)