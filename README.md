# FeedbackSolicitation
This program is written in Python. It uses the 'Amazon SP-API' to allow 3rd-party Amazon sellers to automatically solicit feedback and product reviews from customers.
It can be used to create an AWS Simple Queue Service, subsribe to ORDER_CHANGE notifications, process those notifications (handles duplicate notifications using a 
DynamoDB table), and send customers product review and feedback solicitations if their order is within the valid solicitation window--5 days after Earliest Delivery Date
to 30 days after the Latest Delivery Date.

### Notes for use
1. When subscribing to ORDER_CHANGE notifications you will need to update the destinationId variable with your own respective SQS Destination ID
2. You will need to configure a .env file with your own client id, client secret, and refresh token that you receive when registering your application
with Amazon Developer Central
3. The first couple weeks of notifications received by your SQS will not be eligible for solicitation--these orders are just not old enough and likely 
haven't been delivered. Because of this, you'll notice the first couple weeks of notification processing won't result in any actual solicitations, don't worry about this.   

#### Built by Morgan LeeMaster
