# basic_checks_script

This script for manual reviews improves review efficiency by: 

* Programatically checking email age and validity
* Checking public records and producing address verification codes for clients' shipping and billing addresses
* Providing convenient links to search for property valuations and to view properties with google street view
* Indicates multi-unit vs. single-unit properties, to quickly identify missing or invalid unit numbers in case customer verification is required

The results from the script can be output either to a spreadsheet result in batch, or individually as internal comments within review tickets depending on business needs. Spreadsheet results are backed up to a local CSV file for added convenience.  

Tech used: Google OAuth 2.0, Google API client for Python, Zenpy, Python 3.8.5, Selenium

## Ekata Review Instructions

### Setup Instructions:

* Download the script folder 

* Download chromedrive to your mac if not downloaded

* cd into basic_checks_script folder and run command: 
    ```pip3 install -r requirements.txt```

* Configure the .env file with your logins and sheet id
    (press ```CMD + shift + .``` to show hidden files)

NB: Do not change layout of spreadsheet without aligning first

#### Troubleshooting 
Error that mentions chromedriver not on PATH may be because of the 
location of chromedriver in the filesystem. if this happens, try putting 
an instance of the chromedriver file in the basic_checks_script folder


### Run Instructions: 

* Place Order IDs in column A of ekata_review, or for zendesk, order IDs in column A and ticket numbers in column B of ekata_review_zendesk.

* Open terminal and cd into basic_checks_script folder

* Check that the correct variables are set in the .env file (sheet id, passwords, etc.)

* run the command ```python3 basic_checks_sheets.py``` for output to google sheets, or ```python3 basic_checks_zendesk.py``` for output to zendesk internal notes.

* For google sheets - you will be prompted to input a range in this format e.g: ``2 50`` -- this instructs the script to process orders from row 2 to row 50. this is useful if you want to run the script in multiple terminals at once to decrease processing time. 

NB: sheet updates are only posted when the script
finishes, so it is running even if you do not see updates. 
Script may take 30+ minutes to complete, please check the 
terminal output to check for error message if it seems 
to be taking too long. Note as well that not all error messages mean that
the script has crashed. Progress tracker cell (above) may not work as 
expected with multiple instances running

#### Troubleshooting 

HQM login fail can be because VPN is not connected. 
Ekata fail may be because of a captcha pop-up, try logging into ekata 
manually before running the script in that case


### Example of spreadsheet use 

<img width="1035" alt="Screen Shot 2023-04-07 at 8 02 18 PM" src="https://user-images.githubusercontent.com/79812985/230695191-ece462f2-17ac-4f80-a731-83876eca6d4a.png">

### Example of internal note use

<img width="994" alt="Screen Shot 2023-04-07 at 8 06 35 PM" src="https://user-images.githubusercontent.com/79812985/230695233-60800a50-202c-4ea7-abfb-1342fb9079b4.png">



