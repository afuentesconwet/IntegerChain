import subprocess

from zmq import *
import zmq

from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.messaging.future import Future
from sawtooth_sdk.messaging.future import FutureResult

from sawtooth_sdk.protobuf.validator_pb2 import Message

from sawtooth_sdk.protobuf.state_context_pb2 import TpStateEntry
from sawtooth_sdk.protobuf.state_context_pb2 import TpStateGetRequest
from sawtooth_sdk.protobuf.state_context_pb2 import TpStateGetResponse
from sawtooth_sdk.protobuf.state_context_pb2 import TpStateSetRequest
from sawtooth_sdk.protobuf.state_context_pb2 import TpStateSetResponse
from sawtooth_sdk.protobuf.state_context_pb2 import TpStateDeleteRequest
from sawtooth_sdk.protobuf.state_context_pb2 import TpStateDeleteResponse
from sawtooth_sdk.protobuf.state_context_pb2 import TpReceiptAddDataRequest
from sawtooth_sdk.protobuf.state_context_pb2 import TpReceiptAddDataResponse
from sawtooth_sdk.protobuf.state_context_pb2 import TpEventAddRequest
from sawtooth_sdk.protobuf.state_context_pb2 import TpEventAddResponse
from sawtooth_sdk.protobuf.events_pb2 import *
from sawtooth_sdk.protobuf.client_event_pb2 import *

ip_cmd = subprocess.Popen(["/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'"], stdout=subprocess.PIPE, shell=True)
(out, err) = ip_cmd.communicate()

#url contains the validator url
url = "tcp://"+out.decode("utf-8").rstrip('\n')+":4004"

print("URL:", url)

#Generate Event Subscription
subscription = EventSubscription(
	event_type="sawtooth/block-commit",
	filters = [
		EventFilter(
			key = "addr",
			match_string = "",
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
	correlation_id = correlation_id,
	message_type = Message.CLIENT_EVENTS_SUBSCRIBE_REQUEST,
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
if msg.message_type != Message.CLIENT_EVENTS_SUBSCRIBE_RESPONSE:
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
	if msg.message_type != Message.CLIENT_EVENTS:
		print("Unexpected Message Type")

	#Parse the response
	#events = EventList()
	#events.ParseFromString(msg.content)

	#Print the events in the list
	#for event in events:
	#	print(event)

	print("HA LLEGADO TX")
