from client_event_pb2 import *
from client_batch_pb2 import *
from client_batch_submit_pb2 import *
from client_list_control_pb2 import *
from client_peers_pb2 import *
from client_receipt_pb2 import *
from client_state_pb2 import *
from client_status_pb2 import *
from client_transaction_pb2 import *

from zmq import *
import zmq
from events_pb2 import *

from sawtooth_sdk import *

#url contains the validator url
url = "tcp://localhost:4004"

#Generate Event Subscription
subscription = EventSubscription(
	event_type="sawtooth/block-commit",
	filters = [
		EventFilter(
			key = "addr",
			match_string = "*",
			filter_type = EventFilter.REGEX_ANY
		)
	]
)

#Send Event Subscription

#Connect to validator
ctx = zmq.Context()
socket = ctx.socket(zmq.DEALER)
socket.connect(url)

#Construct the request
request = ClientEventsSubscribeRequest(
	subscriptions = [subscription]
).SerializeToString()

#Construct the message wrapper
correlation_id = "123"
msg = Message(
	correlation_id=correlation_id,
	message_type=CLIENT_EVENTS_SUBSCRIBE_REQUEST,
	content = request
)

#Send the request
socket.send_multipart([msg.SerializeToString()])

#####################################################################

#Receive the response
resp = socket.recv_multipart()[-1]

#Parse the msg wrapper
msg = Message()
msg.ParseFromString(resp)

#Validate the response type
if msg.message_type != CLIENT_EVENTS_SUBSCRIBE_RESPONSE:
	print("Unexpected Msg Type received")

response = ClientEventsSubscribeResponse()
response.ParseFromString(msg.content)

#Validate the response status
if response.status != ClientEventsSubscribeResponse.OK:
	print("Subscription failed: {}".format(response.response_message))

####################################################################

#Receive the events
while True:
	resp = socket.recv_multipart()[-1]
	
	#Parse the msg Wrapper
	msg = Message()
	msg.ParseFromString(resp)
	
	#Validate response type:
	if msg.message_type != CLIENT_EVENTS:
		print("Unexpected Message Type")

	#Parse the response
	events = EventList()
	events.ParseFromString(msg.content)

	#Print the events in the list
	for event in events:
		print(event)










