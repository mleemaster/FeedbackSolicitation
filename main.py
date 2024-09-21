from services.poll_sqs import poll_messages 
import time

def main():
    count = 1
    while True:
        poll_messages(count)
        count+=1



if __name__ == "__main__":
    main()    