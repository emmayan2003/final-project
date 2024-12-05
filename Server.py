import zmq
import sys
sys.path.insert(0, '..')
from Utils import *

ip = sys.argv[1]
port = sys.argv[2]
pub_port = sys.argv[3]
owner_pub_port = sys.argv[4]

c = zmq.Context()
s = c.socket(zmq.REP)
s.bind(f'tcp://{ip}:{port}')
customer_pub_s = c.socket(zmq.PUB)
customer_pub_s.bind(f'tcp://{ip}:{pub_port}')
owner_pub_s = c.socket(zmq.PUB)
owner_pub_s.bind(f'tcp://{ip}:{owner_pub_port}')

requests = []
table_sizes_list = list(map(int, sys.argv[5:]))
print(f"Table sizes: {table_sizes_list}")
R = Restaurant(table_sizes_list)

while True:
    request = s.recv_pyobj()
    requests.append(request)
    print(f"{request.kind} request received")

    if request.kind == "make reservation":
        new_booking = R.book(request.user_id, request.t0, request.party_size)
        if new_booking == -1:
            s.send_pyobj(Message(f"Cannot make reservation: no table is available"))
        else:
            print(new_booking)
            s.send_pyobj(new_booking)
            # push real-time notification to restaurant owner
            owner_pub_s.send_pyobj(Message(f"New Reservation: {new_booking}"))
    
    elif request.kind == "cancel reservation":
        new_booking = R.bookings[request.booking_id]
        R.cancel(request.booking_id)
        s.send_pyobj(None)
        # push real-time notification to restaurant owner
        owner_pub_s.send_pyobj(f"Cancelled Reservation: {new_booking}")
    
    elif request.kind == "change reservation":
        old_booking = R.bookings[request.booking_id]
        new_booking = R.modify(request.t0, request.booking_id)
        if new_booking == -1:
            s.send_pyobj(Message(f"Cannot change reservation: all tables are occupied"))
        else:
            s.send_pyobj(new_booking)
            # push real-time notification to restaurant owner
            owner_pub_s.send_pyobj(f"Changed Reservation: From {old_booking} to {new_booking}")
    
    elif request.kind == "view reservations":
        if len(R.bookings) == 0:
            s.send_pyobj(Message("No current reservations"))
        else:
            s.send_pyobj(list(R.bookings.values()))
    
    elif request.kind == "make bid":
        # Check if this new bid over-bids any existing bids
        new_bid = R.make_bid(request.user_id, request.t0, request.party_size, request.price)
        
        # Check for over-bidding other bids at the same time
        for existing_bid in R.bids.values():
            if (existing_bid.t0 == request.t0 and 
                existing_bid.party_size <= request.party_size and 
                existing_bid.price < request.price):
                # Send over-bidding notification to the existing bid's user
                customer_pub_s.send_pyobj({
                    'type': 'over_bid',
                    'user_id': existing_bid.user_id,
                    'new_bid': new_bid,
                    'old_bid': existing_bid
                })
        
        s.send_pyobj(new_bid)
    
    elif request.kind == "view bids":
        bids = R.view_bids(request.booking_id)
        s.send_pyobj(Message(bids))
    
    elif request.kind == "cancel bid":
        res = R.cancel_bid(request.bid_id, request.user_id)
        if res:
            s.send_pyobj(Message("Bid cancelled successfully"))
        else:
            s.send_pyobj(Message("Oh oh. System error, please try again."))

    elif request.kind == "take bid":
        old_booking = R.bookings[request.booking_id]
        price, new_booking = R.take_bid(request.booking_id)
        s.send_pyobj(Message(f"You traded your reservation for ${price}"))
        # push real-time notification to customer
        customer_pub_s.send_pyobj(new_booking)
        owner_pub_s.send_pyobj(f"Changed Reservation: From {old_booking} to {new_booking}")