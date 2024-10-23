# final-project
Emma Yan's final project assignment for MPCS 51046

**Project idea #2:**
I would like to create an enhanced restaurant table reservation system that includes a bidding functionality for fully booked restaurants. In addition to basic reservation management, users can bid for already-reserved tables. Customers who have booked tables can view bids and decide whether to swap their reservation for the highest bidder. The API will have methods to:

1. Check table availability: Users can input the date, time, and party size to check for available tables. If no tables are available for the selected time, users will be given the option to place a bid for a reserved table.
2. Make a reservation: Users can reserve a table for a specific date and time by providing their party size and contact details. If a table is available, they will receive a confirmation with their reservation details.
3. Place a bid for a table: If all tables are fully booked, users can place a bid for a specific reserved table. They will input their bid amount and contact details, and this will be added to a list of bids associated with that table.
4. View bids on reserved tables: Users with an active reservation can view bids placed on their table. Each bid will display the amount offered and the contact details of the bidder.
5. Swap a reservation for a bid: Users with a reservation can choose to accept a bid and give up their table. The table will then be transferred to the bidder, and both users will receive confirmation of the swap.
6. Cancel a reservation: Users can cancel their reservation by providing their reservation ID or contact details. If the reservation is canceled, any associated bids are removed, and the table becomes available for other customers.
7. Generate a daily reservation and bidding report: Restaurant staff can generate a report showing all reservations for the day, along with any bids placed on tables, making it easier to manage both reservations and bidding activity.

Ideally, I would like the API to be able to handle multiple types of tables as well (e.g. bars, high-rise, regular dining room, etc.) and table of different sizes (i.e. each table should have a range of party size supported). The system should also be able to handle the situation where a party size is larger than the largest table available. Similar to proposal 1, I believe zmq or flask could be the library for implementing inter-user communications.



**Execution Plan**

1. Week 4: Do some research on the Flask library and probably try a couple of sample projects to know its basics.
2. Week 5: Start implementing the server API that allows table availability queries and taking/modifying/canceling reservations and supports custom table sizes/number.
3. Week 6: Finish implementing the server API with the functionality of making and taking bids.
4. Week 7: Set up the client API that can send requests to the server API. Start transitioning both the server and client scripts into Flask.
5. Week 8: Implement the Flask communications between server and client.
6. Week 9: Buffer week to debug and make final improvements.
