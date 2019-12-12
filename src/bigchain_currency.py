from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import re
import time

bdb_root_url = 'https://test.ipdb.io/'
# bdb_root_url = 'http://localhost:9984'
transaction_id = 0

class Currency(object):
    def __init__(self, user_list):
        global transaction_id
        self.bdb = BigchainDB(bdb_root_url)
        self.initializer = generate_keypair()
        self.users = {}
        self.currency_token = {
            'data': {
                'token_for': {
                    'currency': {
                        'serial_number': 'LR35902'
                    }
                },
                'description': 'Time share token. Each token equals one hour of usage.',
            },
        }
        create_receipents = []
        user_key_list = []
        self.transaction_id_dict = {}
        currency_metadata = "currency :"
        for u in user_list:
            self.users[u] = generate_keypair()
            currency_metadata += u + "=" + str(100) + ","
            create_receipents.append(([self.users[u].public_key], 100))
            user_key_list.append(self.users[u].public_key)
            self.transaction_id_dict[u] = transaction_id
            transaction_id += 1
        
        metadata={
            'metadata': currency_metadata
        }

        prepared_token_tx = self.bdb.transactions.prepare(
            operation='CREATE',
            signers=self.initializer.public_key,
            metadata=metadata,
            recipients=create_receipents,
            # recipients=[(user_key_list, 100)],
            asset=self.currency_token
        )

        self.recepients = create_receipents

        fulfilled_token_tx = self.bdb.transactions.fulfill(
            prepared_token_tx,
            private_keys=self.initializer.private_key)

        self.bdb.transactions.send_commit(fulfilled_token_tx)

        self.transfer_asset = {'id': fulfilled_token_tx['id']}
        self.asset = self.transfer_asset
        # self.transfer_asset = {'id': prepared_token_tx['id']}
        # self.output_index = 3
        # self.output = fulfilled_token_tx['outputs'][self.output_index]
        self.output = fulfilled_token_tx['outputs']

    def transfer(self, from_string, to_string, amount):
        currency = self.bdb.metadata.get(search='currency')
        latest_value = str(currency[-1]['metadata']['metadata'])

        from_acc_balance = self.get_current_balance(from_string)
        to_acc_balance = self.get_current_balance(to_string)

        if from_acc_balance - amount < 0:
            print('Not sufficient amount to transfer')
            return False
        
        latest_value = latest_value.replace(from_string+"="+str(from_acc_balance), from_string+"="+str(from_acc_balance - amount))
        latest_value = latest_value.replace(to_string+"="+str(to_acc_balance), to_string+"="+str(to_acc_balance + amount))
        
        metadata_dict = {
            'metadata': latest_value
        }

        prepared_token_tx = self.bdb.transactions.prepare(
            operation='CREATE',
            signers=self.initializer.public_key,
            metadata=metadata_dict,
            recipients=self.recepients,
            asset=self.currency_token
        )

        fulfilled_token_tx = self.bdb.transactions.fulfill(
            prepared_token_tx,
            private_keys=self.initializer.private_key)
        
        self.bdb.transactions.send_commit(fulfilled_token_tx)

        return True

    def transfer1(self, from_string, to_string, amount):
        global transaction_id
        user_from = self.users[from_string]
        user_to = self.users[to_string]
        currency = self.bdb.metadata.get(search='currency')
        latest_value = str(currency[-1]['metadata']['metadata'])
        op_id = self.transaction_id_dict[from_string]
        # print(op_id)
        
        from_acc_balance = self.get_current_balance(from_string)
        to_acc_balance = self.get_current_balance(to_string)

        if from_acc_balance - amount < 0:
            print('Not sufficient amount to transfer')
            return False

        latest_value = latest_value.replace(from_string+"="+str(from_acc_balance), from_string+"="+str(from_acc_balance - amount))
        latest_value = latest_value.replace(to_string+"="+str(to_acc_balance), to_string+"="+str(to_acc_balance + amount))
        
        metadata_dict={
            'metadata': latest_value
        }
        print(len(self.output))
        print("*****here*******")
        # print(self.output[0]['condition']['details'])
        # print(self.output[0]['public_keys'])
        print(self.transfer_asset['id'])
        condition = {
            'type': 'ed25519-sha-256',
            'public_key': user_from.public_key
        }
        transfer_input = {'fulfillment': condition,
            # 'fulfills': {'output_index': self.output_index,
            'fulfills': {'output_index': 0,
                        'transaction_id': self.transfer_asset['id']
                        },
            'owners_before': [user_from.public_key]}

        prepared_token_tx = self.bdb.transactions.prepare(
                operation='TRANSFER',
                metadata=metadata_dict,
                recipients=[([user_to.public_key], amount), ([user_from.public_key], from_acc_balance - amount)],
                inputs=transfer_input,
                asset=self.asset)

        fulfilled_token_tx = self.bdb.transactions.fulfill(
                prepared_token_tx,
                private_keys=user_from.private_key)
        # fulfilled_token_tx = self.bdb.transactions.fulfill(
        #         prepared_token_tx,
        #         private_keys=self.initializer.private_key)
        self.bdb.transactions.send_commit(fulfilled_token_tx)

        self.transaction_id_dict[from_string] = transaction_id
        transaction_id += 1
        self.transfer_asset = {'id': fulfilled_token_tx['id']}
        # self.output_index = 0
        # self.output = fulfilled_token_tx['outputs'][self.output_index]
        # self.output = fulfilled_token_tx['outputs']
        print('transaction complete *************')

        return True  

    def get_current_balance(self, user):
        currency = self.bdb.metadata.get(search='currency')
        latest_val = str(currency[-1]['metadata']['metadata'])

        expr = user + '=(\d+)'
        currency_regex = re.compile(expr)

        res = currency_regex.search(latest_val)
        if res:
            return int(res.group(1))
        return None

    # show_users will print the metadata for the currency asset    
    def show_users(self):
        currency = self.bdb.metadata.get(search='currency')
        print(currency[-1]['metadata']['metadata'])

# if __name__ == '__main__':
#     users = ['ani', 'abc', 'def', 'hij']
    
#     cur = Currency(users)
#     cur.transfer('ani', 'abc', 6)
#     cur.transfer('def', 'hij', 4)
#     cur.transfer('abc', 'def', 3)
#     cur.show_users()
    