# Rasa_Chatbot
Building rasa chatbot for Vidal Health
Guide:
1. Installation Process:
Rasa Open Source:
pip install rasa 
2. Training Process:
Once you've set up your NLU training data and dialogue stories:
rasa train 
This command will train a model using your NLU data and stories and save the trained model in the models/ directory.
3. API Call Process for Website Integration:
To integrate Rasa with a website, you would typically run Rasa as a server and communicate with it via REST API.
Starting the Rasa Server:
rasa run -m models --enable-api --cors "*" 
•	-m models: Specifies the directory where your trained model is stored.
•	--enable-api: Enables API mode.
•	--cors "*": Allows any domain to access the API, which is necessary for website integration.
Now, your Rasa chatbot will be accessible at http://localhost:5005/webhooks/rest/webhook. You can POST a message in this format:
{ "message": "Hello, Rasa!" } 
And receive a response from the Rasa server.
For website integration, you'd typically use JavaScript on the client side to make these API calls and display the chatbot's responses. Several frontend chatbot widget libraries, such as Botpress or Rasa-Webchat, can be used to provide a GUI for chatbot interactions on the website.
4. Running Custom Actions:
If your bot uses custom actions, you'll need to run a separate action server alongside the Rasa server.
Start the action server with:
rasa run actions 
By default, Rasa will search for custom actions in a file named actions.py. If your actions are defined elsewhere, ensure that the endpoints.yml file is correctly pointing to your custom action server.
5. Debugging Process:
Rasa Shell:
For testing and debugging, you can use the Rasa shell:
rasa shell --debug 
The --debug flag provides detailed logs of the conversation. This can be invaluable for understanding how Rasa is interpreting messages and predicting responses.
Logs:
Always keep an eye on the logs (console outputs) when running Rasa. They provide crucial insights into how the bot is functioning, including any issues with custom actions, mispredictions, and more.
In Conclusion:
After training the model and starting the server, integrating Rasa with a website revolves around making the appropriate API calls and managing responses. Debugging requires understanding Rasa's internal operations, and tools like the --debug flag can be immensely beneficial. If you utilize custom actions, it's essential to run and monitor the action server to ensure smooth bot operations.

Company Requirements Description:
Below is a detailed breakdown of the various functionalities and processes the chatbot is designed to handle:
________________________________________
1. Network List:
Purpose: To provide information on hospitals based on specific criteria.
Workflow:
•	The chatbot initiates by asking the user for verification.
•	Upon successful verification:
•	If both hospital name and pin are provided:
•	The bot provides specific details about the hospital, such as its address and contact information.
•	If only the pin is provided:
•	The bot presents a list of hospitals available in that area.
•	The user can then select a specific hospital from the list to view its details.
________________________________________
2. E-Card:
Purpose: To allow users to view E-Cards of members.
Workflow:
•	The chatbot starts by verifying the user.
•	Once verified:
•	It displays a list of members under the verified user.
•	The user can select a member from the list.
•	Upon selection, the bot provides the eCard of the chosen member.
________________________________________
3. Cashless Status:
Purpose: To provide information on a user's cashless history.
Workflow:
•	The chatbot begins with a verification step.
•	Post successful verification:
•	The bot provides details of the last five claims made by the user.
________________________________________
4. Claim Status:
Purpose: Similar to the cashless status but might provide different or more detailed information regarding the claims.
Workflow:
•	Starts with user verification.
•	Once verified, the chatbot provides details about the user's claims.
________________________________________
5. Downloads & Branches:
Purpose: To guide users to relevant pages or resources.
Workflow:
•	For specific queries related to downloads or branches:
•	The chatbot provides direct links to the website or redirects users to the respective pages.
________________________________________
6. Claim Intimation & Claim Process:
Current Status: At the moment, for claim intimation and claim process, users are redirected to specific pages on the website.
Future Development:
•	Both functionalities will incorporate a verification step.
•	The exact workflow for "Claim Intimation" and "Claim Process" is pending and will be decided in the future.
________________________________________
7. Verification:
Purpose: To ensure that the user is authorized to access specific information or perform certain tasks.
Methods:
•	Retail Verification:
•	Mobile & OTP:
•	Users provide their registered mobile number.
•	They receive an OTP for verification.
•	Policy Details:
•	Users need to provide their date of birth (DOB) and policy number.
•	Corporate Verification:
•	Mobile Verification:
•	Similar to the retail mobile verification process.
•	Employee Details:
•	Users need to provide their employee number, DOB, and corporate name.
________________________________________
