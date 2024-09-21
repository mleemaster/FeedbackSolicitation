import requests
from config import settings


# calls the getSolicitationActionsForOrder API
#
# @param amazonOrderId specifies the order for which actions are gathered
# @param marketplaceId specifies the marketplace in which the order was placed
#
# @return the standard json response from the API
def get_solicitation_actions(amazonOrderId, marketplaceId):
    print('getting solicitation actions...')
    headers = {
        'Authorization': f'Bearer {settings.ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f'https://sellingpartnerapi-na.amazon.com/solicitations/v1/orders/{amazonOrderId}?marketplaceIds={marketplaceId}', 
                            headers = headers)

        if response.status_code == 200:
            return response.json()
        else:
            print({response.status_code} - {response.text})
            return None
    except requests.RequestException as e:
        print(f'GET Solicitation request failed: {e}')
        return None


# creates a product review and feedback solicitation for an order
#
# @param amazonOrderId specifies the order for which actions are gathered
# @param marketplaceId specifies the marketplace in which the order was placed
#
# @return void, prints a success or fail message.
def create_product_review_solicitation(amazonOrderId, marketplaceId):
    print('creating product review solicitation...')
    headers = {
        'Authorization': f'Bearer {settings.ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(f'https://sellingpartnerapi-na.amazon.com/solicitations/v1/orders/{amazonOrderId}/solicitations/productReviewAndSellerFeedback?marketplaceIds={marketplaceId}', 
                                 headers = headers)

        if response.status_code == 201:
            print('Feedback successfully requested')
        else:
            print(f'{response.status_code} - {response.text}')
    except requests.RequestException as e:
        print(f'POST request failed {e}')

