import zmq
import sys
import threading
sys.path.insert(0, '..')
from Utils import *


def receive_notifications():
    '''
    Continuously receives booking updates from server
    '''
    c = zmq.Context()
    s = c.socket(zmq.SUB)
    s.connect(f'tcp://{ip}:{owner_pub_port}')
    s.setsockopt_string(zmq.SUBSCRIBE, '')
    while True:
        notification = s.recv_pyobj()
        print(f'\n=======NEW NOTIFICATION: {notification}\n=======')

def view_reservations():
    '''
    Sends a request to server to view all reservations
    '''
    while True:
        print("\nType 1 to view all current reservations")
        inp = input()

        if inp == '1':
            c = zmq.Context()
            s = c.socket(zmq.REQ)
            s.connect(f'tcp://{ip}:{port}')
            request = Request(user_id, kind='view reservations')
            s.send_pyobj(request)
            reservations = s.recv_pyobj()
            print('\nCurrent Reservations:')
            if isinstance(reservations, Message):
                print(reservations.msg)
            else:
                for reservation in reservations:
                    print(reservation)
        
        else:
            print('Invalid choice. Please try again.')


ip = sys.argv[1]
port = sys.argv[2]
owner_pub_port = sys.argv[3]
user_id = '_restaurant_owner_'

threading.Thread(target=receive_notifications).start()
threading.Thread(target=view_reservations).start()
