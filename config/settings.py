import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
client_id=os.getenv('client_id')
client_secret=os.getenv('client_secret')
# creates a destination for a Simple Queue Service in AWS
#
# param grantless_token The grantless token passed for authorization
# param name The name of the SQS you are creating a destination for
# param arn The arn of the SQS you are creating a destination for
#
# returns the destination ID 
def create_sqs_destination(grantless_token, name, arn):
    url = "https://sellingpartnerapi-na.amazon.com/notifications/v1/destinations"

    headers = {
        'Authorization': f'{grantless_token}',
        'x-amz-access-token': f'{grantless_token}',
        'Content-Type': 'application/json'
    }

    data = {
        'resourceSpecification': {
            'sqs': {
                'arn': f'{arn}'
            }
        },
        'name': f'{name}'
    } # data

    response = requests.post(url, headers=headers, json=data)
    print(response.json().get('destinationId'))
    if response.status_code == 200:
        destination_id = response.json().get('destinationId')
        print(f"Destination ID successfully created: {destination_id}")
        return destination_id
    else:
        print(f"failed to create destination: {response.status_code} - {response.text}")
        return None


# retreive an access token for non-grantless API calls
# param client_id client ID in Seller Central, no change
# param client_secret Client Secret in Seller Central, rotates every few months
# 
# returns a token (string)
def get_spa_access_token(client_id, client_secret):
    url = 'https://api.amazon.com/auth/o2/token'
    refresh_token=os.getenv('refresh_token')
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
    'grant_type': 'refresh_token',
    'client_id': client_id,
    'client_secret': client_secret,
    'refresh_token': refresh_token,
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        access_token = response.json().get('access_token')
        return access_token
    else:
        raise Exception(f"Failed to get access token: {response.status_code}, {response.text}")
    
ACCESS_TOKEN = get_spa_access_token(client_id, client_secret)

# Returns a token for grantless API calls
#
# param client_id Client ID in Seller Central
# param client_secret Client Secret in Seller Central
# returns a token (string) for API calls
def get_grantless_token(client_id, client_secret):
    url = 'https://api.amazon.com/auth/o2/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'sellingpartnerapi::notifications'
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"failed to get grantless token: {response.status_code} {response.text}")

GRANT_TOKEN = get_grantless_token(client_id, client_secret)

# gets the Destination ID for AWS queues, this is a grantless operation
#
# param token A grantless token passed for authorization
# returns a message with data about queue destinations, contains the destination ID
def get_destination_id(token):
    url = 'https://sellingpartnerapi-na.amazon.com/notifications/v1/destinations'
    headers = {
        'Authorization': f"Bearer {token}",
        'x-amz-access-token': f"{token}",
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers = headers)
    if response.status_code == 200:
        print("Destinations Received.")
        print(response.json())
    else:
        print(f"Error retrieving destinations: {response.status_code} {response.text}")


# creates a notification subscription for Order Status Changes
#
# Not setup for reuse at the moment
def create_order_change_subscription(access_token):
    url = "https://sellingpartnerapi-na.amazon.com/notifications/v1/subscriptions/ORDER_CHANGE"
    headers = {
        "Authorization" : access_token,
        "x-amz-access-token": access_token,
        "Content-Type" : "application/json"
    }
    data = {
        "payloadVersion": "1.0",
        "destinationId": "15cebb7d-b06d-4b02-826b-d8992508587f",
        "processingDirective": {
            "eventFilter": {
                "orderChangeTypes": ["OrderStatusChange"],
                "eventFilterType": "ORDER_CHANGE"
            }
        }
    }


    response = requests.post(url,headers=headers, json=data)
    if response.status_code == 200:
        print("Subscription success!!")
        print(response.json())
    else:
        print(f"error in subscribing: {response.status_code} {response.text}")
