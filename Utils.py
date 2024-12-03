from datetime import datetime, timedelta


#### Restaurant Helpers ####
class Table:
    def __init__(self, size, table_id):
        self.size = size
        self.id = table_id
        self.reservations = []
    
    def available(self, t0):
        '''
        Checks if the table is available for a reservation at time t0.
        Assumes that each booked party will only dine for 2 hours max. 
        '''
        for reservation_t in self.reservations:
            if (reservation_t >= t0 and reservation_t - timedelta(hours=2) < t0) or \
               (reservation_t <= t0 and reservation_t + timedelta(hours=2) > t0):
                    return False
        return True
    
    def make_booking(self, t0):
        '''
        Makes reservation at time t0.
        '''
        self.reservations.append(t0)
    
    def remove_booking(self, t0):
        '''
        Removes the reservation at time t0.
        '''
        self.reservations.remove(t0)

class Bid:
    def __init__(self, user_id, bid_id, t0, party_size, price):
        self.id = bid_id
        self.user_id = user_id
        self.t0 = t0
        self.party_size = party_size
        self.price = price
    
    def __repr__(self):
        return f"Bid for {self.t0} of {self.party_size} people for ${self.price}"

class Booking:
    def __init__(self, user_id, booking_id, table_ids, t0, party_size):
        self.user_id = user_id
        self.id = booking_id
        self.table_ids = table_ids if isinstance(table_ids, list) else [table_ids]
        self.t0 = t0
        self.party_size = party_size
    
    def __repr__(self):
        table_list = ', '.join(map(str, self.table_ids))
        return f"Tables {table_list} at {self.t0} for {self.party_size} people \
            | under {self.user_id}"

class Restaurant:
    def __init__(self, table_sizes_list):
        self.tables = {}
        for i, table_size in enumerate(sorted(table_sizes_list, reverse=True)):
            self.tables[i] = Table(table_size, i)
        self.bids = {}
        self.last_bid_id = -1
        self.last_booking_id = -1
        self.bookings = {}
    
    def book(self, user_id, t0, party_size):
        '''
        Checks if tables are available to accommodate the party size at time t0.
        If no single table fits, it will combine larger tables.
        '''
        required_size = party_size
        suitable_tables = [
            table for table in self.tables.values() 
            if table.size >= party_size and table.available(t0)
        ]
        
        if suitable_tables:
            smallest_table = min(suitable_tables, key=lambda table: table.size)
            allocated_tables = [smallest_table]
            required_size -= smallest_table.size
        else: # over-sized booking
            allocated_tables = []
            for table in sorted(self.tables.values(), key=lambda x: x.size, reverse=True):
                if table.available(t0) and required_size > 0:
                    allocated_tables.append(table)
                    required_size -= table.size
        
        if required_size <= 0:
            self.last_booking_id += 1
            for table in allocated_tables:
                table.make_booking(t0)
            
            table_ids = [table.id for table in allocated_tables]
            booking = Booking(
                user_id=user_id,
                booking_id=self.last_booking_id,
                table_ids=table_ids,
                t0=t0,
                party_size=party_size
            )
            self.bookings[self.last_booking_id] = booking
            return booking
        else:
            return -1
    
    def cancel(self, booking_id):
        '''
        Cancels a booking by booking_id.
        '''
        if booking_id in self.bookings:
            booking = self.bookings[booking_id]
            t0 = booking.t0
            for table_id in booking.table_ids:
                table = self.tables[table_id]
                table.remove_booking(t0)
            del self.bookings[booking_id]
        else:
            print("Booking ID not found.")
    
    def modify(self, new_t0, booking_id):
        '''
        Modifies a booking by booking_id to a new time.
        '''
        if booking_id in self.bookings:
            booking = self.bookings[booking_id]
            party_size = booking.party_size
            self.cancel(booking_id)
            return self.book(booking.user_id, new_t0, party_size)
        else:
            print("Booking ID not found.")
    
    def make_bid(self, user_id, t0, party_size, price):
        '''
        Makes bid for a time, party size, and bid price.
        '''
        self.last_bid_id += 1
        self.bids[self.last_bid_id] = Bid(
            user_id, 
            self.last_bid_id, 
            t0, 
            party_size, 
            price)
        return self.bids[self.last_bid_id]
    
    def take_bid(self, booking_id):
        '''
        Takes the highest bid eligible for the booking by booking_id.
        '''
        my_booking = self.bookings[booking_id]
        highest_bid_id, highest_bid_price = -1, -1
        for bid in self.bids.values():
            if bid.t0 == my_booking.t0\
                and bid.party_size <=\
                    sum(self.tables[table_id].size for table_id in my_booking.table_ids):
                if bid.price > highest_bid_price:
                    highest_bid_id, highest_bid_price = bid.id, bid.price
        
        if highest_bid_id == -1:
            return None, None

        highest_bid = self.bids[highest_bid_id]
        self.cancel(booking_id)
        booking = self.book(highest_bid.user_id, highest_bid.t0, highest_bid.party_size)
        del self.bids[highest_bid_id]
        return highest_bid_price, booking

    def view_bids(self, booking_id):
        '''
        Views all bids at the restaurant that are for the same time as the
        booking by booking_id.
        '''
        my_booking = self.bookings[booking_id]
        available_bids = []
        for bid in self.bids.values():
            if bid.t0 == my_booking.t0 and\
                bid.party_size <=\
                    sum(self.tables[table_id].size for table_id in my_booking.table_ids):
                available_bids.append(bid)
        
        if not available_bids:
            return "No bids currently"
        
        return ", ".join(map(str, available_bids))
    
    def cancel_bid(self, bid_id, user_id):
        '''
        Cancels a bid by bid_id and checks if the user_id matches
        '''
        if bid_id in self.bids:
            bid = self.bids[bid_id]
            if bid.user_id == user_id:
                del self.bids[bid_id]
                return True
            else:
                return False
        return False


#### Communication Helpers ####
class Request:
    def __init__(self, user_id, kind=None, booking_id=None, t0=None, party_size=None, price=None):
        self.user_id = user_id
        self.kind = kind
        self.booking_id = booking_id
        self.t0 = t0
        self.party_size = party_size
        self.price = price

class Message:
    def __init__(self, msg):
        self.msg = msg
    
    def __repr__(self):
        return str(self.msg)
