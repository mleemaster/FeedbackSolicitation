import boto3
import json
from services.solicitation_calls import get_solicitation_actions
from services.solicitation_calls import create_product_review_solicitation
from utils.time_helpers import check_solicitation_window
from datetime import timedelta
from dateutil import parser
from dotenv import load_dotenv
import os

load_dotenv()
AWS_ACCESS_ID=os.getenv('AWS_ACCESS_ID')
AWS_SECRET=os.getenv('AWS_SECRET')
sqs = boto3.client('sqs', aws_access_key_id=AWS_ACCESS_ID,
                   aws_secret_access_key=AWS_SECRET, 
                   region_name='us-east-2')
dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_ID,
                    aws_secret_access_key=AWS_SECRET, 
                    region_name='us-east-2')   

table = dynamodb.Table('ProcessedNotifications')

# polls, processes, and deletes messages in an SQS
#
# Method is void
def poll_messages(count):
    # gather a message
    print(f'Requesting message {count}...')
    response = sqs.receive_message(
        QueueUrl='https://sqs.us-east-2.amazonaws.com/688567305615/OrderChangeQueue',
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20
    )
    
    if 'Messages' in response:
        print(f'Message {count} received...')
        message = response['Messages'][0] # contains MessageId, ReceiptHandle, Body
        body = json.loads(message['Body'])
        notificationId = message['MessageId']
        
        if not shipped(body=body):
            delete_message(message)
            mark_noti_processed(notificationId)
            print('Order not marked as shipped - deleted and processed.')
        elif not is_noti_duplicate(notificationId):
            process_message(body)
            delete_message(message) 
            mark_noti_processed(notificationId)

    else:
        print('No messages received. Quitting...')
        exit()
    
# grabs relevant data from messages and triggers a solicitation 
# if an order meets the necessary criteria for solicitation
#
# method is void
def process_message(body):
    print('Processing message...')
    marketplaceId = body.get('Payload').get('OrderChangeNotification').get('Summary').get('MarketplaceId')
    amazonOrderId = body.get('Payload').get('OrderChangeNotification').get('AmazonOrderId')
    earliestDeliveryDate = body.get('Payload').get('OrderChangeNotification').get('Summary').get('EarliestDeliveryDate')
    latestDeliveryDate = body.get('Payload').get('OrderChangeNotification').get('Summary').get('LatestDeliveryDate')

    if earliestDeliveryDate == None:
        earliestDeliveryDate = get_purchase_date(body, 3)
        latestDeliveryDate = get_purchase_date(body, 7)

    if check_solicitation_window(earliestDeliveryDate, latestDeliveryDate):
        response = get_solicitation_actions(amazonOrderId, marketplaceId)
        if response['_links']['actions']:
            create_product_review_solicitation(amazonOrderId, marketplaceId)
    else: 
        print('solicitation not available, deleting and marking message as processed...')    


def mark_noti_processed(notificationId):
    print('marking message as processed...')
    table.put_item(Item={'ID': notificationId})


def is_noti_duplicate(notificationId):
    print('checking if message is a duplicate...')
    response = table.get_item(Key={'ID': notificationId})

    if 'Item' in response:
        return True
    else:
        return False
    
def delete_message(message):
    sqs.delete_message(
        QueueUrl='https://sqs.us-east-2.amazonaws.com/688567305615/OrderChangeQueue',
        ReceiptHandle=message['ReceiptHandle']
        )
    print(f"deleting message...") 

def shipped(body):
    print('Checking order status...')
    order_status = body.get('Payload').get('OrderChangeNotification').get('Summary').get('OrderStatus')
    
    if order_status == 'Pending' or order_status == 'Unshipped':
        return False
    else:
        return True

def get_purchase_date(body, day):
    purchase_date = body.get('Payload').get('OrderChangeNotification').get('Summary').get('PurchaseDate')
    purchase_date = parser.parse(purchase_date)
    purchase_date += timedelta(days=day)
    purchase_date = purchase_date.strftime('%Y-%m-%dT%H:%M:%S')
    return purchase_date
