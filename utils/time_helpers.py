from dateutil import parser
from dateutil.parser import ParserError
from datetime import datetime, timedelta, timezone

# checks if an order is within the valid window for a solicitation
# 
# param earliest_delivery_date Earliest Delivery Date for an order
# param latest_delivery_date Latest delivery date for an order
#
# Returns a booleam, true if an order is within the valid window 
# for solicitation. False, if the date is out of range or the parser
# raises an error.
def check_solicitation_window(earliest_delivery_date, latest_delivery_date):
    print('Checking solicitation window...')
    try:
        # parse input dates and get current time    
        earlyDate = parser.parse(earliest_delivery_date).replace(tzinfo=None)
        lateDate = parser.parse(latest_delivery_date).replace(tzinfo=None)
        currentDate = datetime.now()

        # adjust dates to specified 5 after early, 30 after late
        # time window for solicitation from Amazon
        earlyDate += timedelta(days=10)
        lateDate += timedelta(days=24)
    except ParserError as e:
        # handle invalid date format
        print(f'Invalid date format in check_solicitation - {e}')
        return False
    except TypeError as e:
        print(f'Early or Late delivery date is NoneType - {e}')
        return False

    # check if current date is within solicitation window
    return earlyDate < currentDate < lateDate
    
    

