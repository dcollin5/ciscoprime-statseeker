import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import json

import xml.etree.ElementTree as ET

# Load configuration from the config file
def load_config(filename):
    try:
        with open(filename, "r") as config_file:
            config = json.load(config_file)
            return config["base_url"], config["username"], config["password"], config["ss_server"], config["ss_user"], config["ss_pword"]
    except FileNotFoundError:
        raise Exception("Config file not found")
    except KeyError:
        raise Exception("Config file does not contain 'base_url', 'username', 'password', 'ss_server', 'ss_user', 'ss_pword' fields")

#StatSeeker Request
def do_request(server, query, user, pword, reqData):
    # Run auth request
    headers = { 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded' }
    url = f'https://{server}/ss-auth'
    authData = {'user': user, 'password': pword}
    resp = requests.post(url, headers=headers, data=authData, verify=False)
    headers['Content-Type'] = 'application/json'
    url = f'https://{server}/{query}'
    print (url)
    print (reqData)
    print(f'Get Auth Token: {resp.status_code}')
    if resp.status_code == 200:    
        # Authentication successful, Statseeker >= v5.5.4
        myToken = resp.json()
        headers['Authorization'] = f'Bearer {myToken["access_token"]}'
        print (headers)
        resp = requests.put(url, headers=headers, data=reqData, verify=False)
    if resp.status_code == 401:
        print(f'Token auth failed: {resp.status_code}, trying basic auth')
        # Either Authentication was unsuccessful (Statseeker <  v5.5.4), or API set to use basic auth
        # Try basic auth
        resp = requests.delete(url, headers=headers, auth=(user, pword), data=reqData, verify=False)
    return resp

# Function to query AP name and return IP address
def get_ap_info(base_url, username, password, ap_name):
    ap_url = base_url + f"data/AccessPoints?.full=true&.sort=ipAddress&name=endsWith(%22{ap_name}%22)"
    auth_headers = {
        "Content-Type": "application/json",
    }

    ap_response = requests.get(ap_url, headers=auth_headers, auth=(username, password), verify=False)

    if ap_response.status_code == 200:
        # Parse the XML content of the response
        xml_content = ap_response.text
        root = ET.fromstring(xml_content)
        
        # Find the element containing the variable you want
        #variable_element = root  # Replace with the actual element name
        # Find the ipAddress element
        ip_address_element = root.find(".//ipAddress/address")
        
        if ip_address_element is not None:
            address_value = ip_address_element.text
            ap_ip = address_value
            #print("Address:", address_value)
        else:
            print("Address element not found in the XML.")
        #ap_data = ()["queryResponse"]["entityId"][0]["accessPointDTO"]
        
        return ap_ip
    else:
        raise Exception(f"Failed to query AP info for AP name: {ap_name}")

# Main function to loop through a file
if __name__ == "__main__":
    try:
        base_url, username, password, ss_server,ss_user, ss_pword = load_config("config.json")
        #access_token = get_access_token(base_url, username, password)

        # Read AP names from a file (one per line)
        with open("ap_names.txt", "r") as file:
            print("Read file in list of APs to chech IP addresses")
            for line in file:
                ap_name = line.strip()
                ap_ip = get_ap_info(base_url, username, password, ap_name)
                
                #Print out the AP IP Address and AP name. Format suitable for input into Statseeker
                print(f"{ap_ip} {ap_name}")

                # Statseeker API Interaction
                # API root endpoint
                query = 'api/v2.1'
                # specify target endpoint
                query += '/cdt_device'
                # optional response formatting
                query += '/?indent=3&links=none'

                # data
                # Create the JSON string with the ap_ip
                ss_reqData = json.dumps({"fields":{"name":{"field":"name","filter":{"query":f"LIKE '{ap_name}'"}}}})
                
                # Run the request
                resp = do_request(ss_server, query, ss_user, ss_pword, ss_reqData)
                print(resp.status_code)
                print(resp.json())
                if resp.status_code == 200:
                    print(resp.status_code)
                    print(f"AP Deleted from StatSeeker {ap_ip} {ap_name}")
                    print(resp.json())
                else:
                    print(f'Error: {resp.status_code} {resp.reason}')
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

