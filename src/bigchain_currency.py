from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import re

bdb_root_url = 'https://test.ipdb.io/'

class Currency(object):
    def __init__(self):
        self.bdb = BigchainDB(bdb_root_url)
        # self.admin, self.initializer = generate_keypair(), generate_keypair()
        self.initializer =  {
            "name": 'initializer',
            "keypair": generate_keypair()
        }
        self.admin = {
            "name": 'admin',
            "keypair": generate_keypair()
        }
        # create admin and add 100 to his account
        # prepare the transaction with the digital asset and issue 10 tokens for bob
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
        metadata={
            'metadata': 'currency: admin=100'
        }

        prepared_token_tx = self.bdb.transactions.prepare(
            operation='CREATE',
            signers=self.initializer['keypair'].public_key,
            metadata=metadata,
            recipients=[([self.admin['keypair'].public_key], 100)],
            asset=self.currency_token)

        fulfilled_token_tx = self.bdb.transactions.fulfill(
            prepared_token_tx,
            private_keys=self.initializer['keypair'].private_key)
        self.bdb.transactions.send_commit(fulfilled_token_tx)
    
    def transfer_currency(self, user_from, user_to, metadata_string, amount):
        remaining_amount = self.get_current_balance(user_from['name'])
        print('transferring amount to %s' % user_to['name'])
        if remaining_amount - amount >= 0:
            prepared_token_tx = self.bdb.transactions.prepare(
                operation='TRANSFER',
                signers=user_from['keypair'].public_key,
                metadata=metadata_string,
                recipients=[([user_to['keypair'].public_key], amount)],
                asset=self.currency_token)

            fulfilled_token_tx = self.bdb.transactions.fulfill(
                prepared_token_tx,
                private_keys=self.initializer['keypair'].private_key)
            self.bdb.transactions.send_commit(fulfilled_token_tx)
        else:
            print('Not enough currency to carry out the transaction')
        

    def get_current_balance(self, user):
        currency = self.bdb.metadata.get(search='currency')
        latest_val = str(currency[0]['metadata'])

        expr = user + '=(\d+)'
        currency_regex = re.compile(expr)

        res = currency_regex.search(latest_val)
        if res:
            # print("Matched value: %s" % res.group(1))
            return int(res.group(1))
            # print('user not found to get the currency')
            # return
        # res = res.group(1)

        # return int(res)
        return None

    # create user and add him to metadata with zero currency value
    def create_user(self,  name):
        currency = self.bdb.metadata.get(search='currency')
        latest_value = str(currency[-1]['metadata'])
        if name in latest_value:
            print('User already exists. Try different name or ')
        else:
            new_user_keys = generate_keypair()
            user_dict = {
                'name': name,
                'keypair': new_user_keys
            }
            self.users[name] = user_dict
            new_latest_value =  "%s,%s=10" % (latest_value, name)
            self.transfer_currency(self.admin, self.users[name], new_latest_value, 10)
            print('User %s has been successfully initialized' % name)

    # show_users will print the metadata for the currency asset    
    def show_users(self):
        currency = self.bdb.metadata.get(search='currency')
        print(currency)
        # latest_value = str(currency[-1]['metadata'])
        # print(latest_value)

if __name__ == '__main__':
    cur = Currency() 
    cur.create_user('ani')
    # cur.show_users()
