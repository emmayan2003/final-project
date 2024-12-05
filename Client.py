import zmq
import sys
from datetime import datetime
sys.path.insert(0, '..')
import threading
from Utils import *

def display_bids():
    '''
    Prints out the bids made by the customer
    '''
    if len(bids) == 0:
        print("You haven't made any bids")
        return -1
    else:
        print('Which one of the bids below would you like to select?')
        for i, bid in enumerate(bids):
            print(f"{i+1}. {bid}")
        return bids

def display_bookings():
    '''
    Prints out the bookings made by the customer
    '''
    if len(bookings) == 0:
        print("You haven't made any bookings")
        return -1
    else:
        print('Which one of the bookings below would you like to select?')
        for i, booking in enumerate(bookings):
            print(f"{i+1}. {booking}")

def datetime_from_string(string):
    try:
        return datetime.strptime(string, '%m/%d/%Y %I:%M%p')
    except:
        print('Wrong date and/or time format, please re-enter (M/D/YYYY Time)'
              ' - Time should have format h:mmam/pm, e.g. 5:30pm')
        return -1

def handle_reply(request, reply):
    '''
    Handles the reply to request from server
    '''
    print()

    if type(reply) == Message:
        print(reply)
    else:
        if request.kind == "make reservation":
            bookings.append(reply)
            print("Reservation Booked!")
        elif request.kind == "cancel reservation":
            for i, booking in enumerate(bookings):
                if booking.id == request.booking_id:
                    del bookings[i]
                    print("Reservation cancelled!")
        elif request.kind == "change reservation":
            for i, booking in enumerate(bookings):
                if booking.id == request.booking_id:
                    del bookings[i]
            bookings.append(reply)
            print("Reservation Changed!")
        elif request.kind == "make bid":
            bids.append(reply)
            print("Bid made successfully")
        elif request.kind == "cancel bid":
            for i, bid in enumerate(bids):
                if bid.id == request.bid_id:
                    del bids[i]
                    print("Bid cancelled!")

def send_request():
    '''
    Send a reservation/bidding request to server
    '''
    c = zmq.Context()
    s = c.socket(zmq.REQ)
    s.connect(f'tcp://{ip}:{port}')

    while True:
        print('''
            What would you like to do? Please say:
            Make reservation,
            Cancel reservation,
            Change reservation,
            Make bid,
            Cancel bid,
            View bids,
            Take bid''')
        request.kind = input().lower()
        
        if request.kind == "make reservation":
            print('Enter the date and time (M/D/YYYY Time):')
            tmp = -1
            while tmp == -1:
                tmp = datetime_from_string(input())
            request.t0 = tmp
            print('Enter the number of people:')
            request.party_size = int(input())
        
        elif request.kind == "cancel reservation":
            if display_bookings() == -1: continue
            idx = int(input().replace('.', ''))
            request.booking_id = bookings[idx-1].id
        
        elif request.kind == "change reservation":
            if display_bookings() == -1: continue
            idx = int(input().replace('.', ''))
            request.booking_id = bookings[idx-1].id
            print('Enter the date and time that you want to change to (M/D/YYYY Time):')
            tmp = -1
            while tmp == -1:
                tmp = datetime_from_string(input())
            request.t0 = tmp
        
        elif request.kind == "make bid":
            print('Enter the date and time:')
            tmp = -1
            while tmp == -1:
                tmp = datetime_from_string(input())
            request.t0 = tmp
            print('Enter the number of people:')
            request.party_size = int(input())
            print('Enter how much you are willing to bid for ($):')
            request.price = int(input())
        
        elif request.kind == "cancel bid":
            bids = display_bids()
            if bids == -1:
                continue
            idx = int(input().replace('.', ''))
            request.bid_id = bids[idx-1].id
        
        elif request.kind == "view bids":
            if display_bookings() == -1: continue
            idx = int(input().replace('.', ''))
            request.booking_id = bookings[idx-1].id
        
        elif request.kind == "take bid":
            if display_bookings() == -1: continue
            idx = int(input().replace('.', ''))
            request.booking_id = bookings[idx-1].id
            request.kind = "view bids"
            s.send_pyobj(request)
            bids = s.recv_pyobj()
            print(bids)
            YN = input("Would you like to take the highest bid? (Y/N)")
            if YN == "Y":
                request.kind = "take bid"
                del bookings[idx-1]
        
        elif request.kind == "quit":
            break

        else:
            print("Please type a valid request type.")
            continue

        s.send_pyobj(request)
        reply = s.recv_pyobj()

        handle_reply(request, reply)

def receive_bid_outcomes():
    '''
    Continuously receives bidding notifications from server
    '''
    c = zmq.Context()
    s = c.socket(zmq.SUB)
    s.connect(f'tcp://{ip}:{pub_port}')
    s.setsockopt_string(zmq.SUBSCRIBE, '')
    while True:
        notification = s.recv_pyobj()
        
        # push bid outcome notifications
        if isinstance(notification, Booking):
            if notification.user_id == user_id:
                bookings.append(notification)
                print('You won the bid and got booked the following:')
                print(notification)
        
        # push over-bidding notifications
        elif isinstance(notification, dict) and notification.get('type') == 'over_bid':
            if notification['user_id'] == user_id:
                print("\n=======OVER-BIDDING NOTIFICATION")
                print(f"Your bid {notification['old_bid']} has been over-bid.")
                print(f"New Bid: {notification['new_bid']}")
                print("=======")


ip = sys.argv[1]
port = sys.argv[2]
pub_port = sys.argv[3]
user_id = sys.argv[4]  # user_id must be unique

request = Request(user_id)
bookings, bids = [], []

threading.Thread(target=send_request).start()
threading.Thread(target=receive_bid_outcomes).start()
