import sys
import cbor
import string
import random
from urllib.error import HTTPError
from random import randint
import urllib.request

from hashlib import sha512

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
import sawtooth_sdk
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch
from sawtooth_sdk.protobuf.batch_pb2 import BatchList

#Creates a signer who will sign the tx and validate
#its identity in front of the validator
context = create_context('secp256k1')
private_key = context.new_random_private_key()

signer = CryptoFactory(context).new_signer(private_key)
print("SIGNER ES: {}".format(signer.get_public_key().as_hex()))

#Generates a transaction per number. All transactions go
#in the same batch, which is sent inside a batchlist.
print('Introduce the numbers you want to send.')
nums = [int(x) for x in input().split()]
print('The numbers: {}'.format(nums));

lenNums = range(len(nums))

#Generate the payload of the tx
#Every family has a structure to follow
#Uses the cbor format
N = 10
ran_addr = [''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
	   for i in lenNums
]

#Generate the bytes of the payload
payload = [cbor.dumps(
	{
	'Verb': 'set',
        'Name': ran_addr[i],
        'Value': num
	}
) for i, num in enumerate(nums, 0)]

#Generate the integerkey addresses
tx_addr = [
	sha512('intkey'.encode('utf-8')).hexdigest()[0:6] + sha512(ran_addr[i].encode('utf-8')).hexdigest()[-64:]
        for i in lenNums
]

#Generate the tx header
tx_header_arr = [
	TransactionHeader(
        	family_name='intkey',
                family_version='1.0',
                inputs=[tx_addr[i]],
                outputs=[tx_addr[i]],
                signer_public_key = signer.get_public_key().as_hex(),
                batcher_public_key = signer.get_public_key().as_hex(),
                dependencies=[],
                payload_sha512 = sha512(payload[i]).hexdigest()
        ).SerializeToString()
        for i in lenNums
]

#Signer signs the header:
signature_arr = [
	signer.sign(tx_header_arr[i])
	for i in lenNums
]

#Generate an array with all the transactions
tx_arr= [
        Transaction(
        	header=tx_header_arr[i],
                header_signature=signature_arr[i],
                payload = payload[i]
        )
       	for i in lenNums
]

#Create the BatchHeader
batch_header = BatchHeader(
                signer_public_key = signer.get_public_key().as_hex(),
                transaction_ids = [tx_arr[i].header_signature for i in lenNums]
        ).SerializeToString()

#Create the batch with the tx
signature_batch = signer.sign(batch_header)

batch = Batch(
                header = batch_header,
                header_signature = signature_batch,
                transactions = tx_arr
        )

#Collect all Batches in a BatchList: can contain batches from different clients
batch_list = BatchList(
                batches = [batch]
        ).SerializeToString()

#Send Batches to Validator
try:
        request = urllib.request.Request(
                        'http://rest-api:8008/batches',
                        batch_list,
                        method = 'POST',
                        headers = {'Content-Type': 'application/octet-stream'}
                )
        response = urllib.request.urlopen(request)

except HTTPError as e:
        response = e.file

print(payload);
