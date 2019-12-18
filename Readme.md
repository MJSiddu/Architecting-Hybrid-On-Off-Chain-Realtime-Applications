# Hybrid on and off chain Platform for Real Time Applications

## Team Members
- Amal Sony (asony)
- Aniruddha Shamasundar (ashamas)
- Harsh Agrawal (hagrawa2)
- Siddu Madhure Jayanna (smadhur)

## Pre-requisites
- Kafka
- MongoDB
- Anaconda (recommended)
- BigchainDB (Optional)

## Setup

1. Git clone this repository or extract the zip file.
2. cd to folder.
3. Create environment
    ```
    conda env create -f environment.yml
    ```
4. Activate the environment (exact command might not work, if it doesn't change accordingly)
    ```
    conda activate realtime-app
    ```
5. Run kafka and create three topics namely entry, exit and tx.
6. Create .env in the project root folder and set the config appropriately. Seen .env.example for reference. The topic names should be the ones created in step 5.
7. Run flask app in one terminal
    ```
    python src/app.py
    ```
    or
    ```
    FLASK_APP=src/app.py FLASK_ENV=development flask run --port 3500, (for hot reloading)
    ``` 
8. Run the following consumers in separate terminals
    ```
    python src/entry_consumer.py
    ```
    ```
    python src/exit_consumer.py
    ```
    ```
    python src/tx_consumer.py
    ```
9. Create accounts in the blockchain for users/entities. For now, it done inside the code. Open tx_consumer.py and edit this line ```cur = bc.Currency(["Vehicle", "Sensor", "Customer", "Supermarket"])```. The inputs are the accounts to be created. The same account identifiers specified here should be given as the part of the request, which is explained further in the Flow section.
9. Send entry and exit requests from Postman. Update the **\_id** parameter of the entry request body to avoid having issues with mongodb. For details on the request body structure, refer the Flow section below.

### BigchainDB setup
The current code points to a publically running bigchaindb instance called [testnet](https://test.ipdb.io/ "testnet")
Follow the following steps to run Bigchaindb locally
1. Install Git, Make, Docker, and Docker Compose on your local machine.
2. Clone the following repository
```
git clone git@github.com:bigchaindb/bigchaindb.git
```
3. Change directory
```
cd bigchaindb
```
4. Run bigchaindb
```
make run
```

For bringing down the blockchain instance,
1. Change directory to bigchain db
```
cd bigchaindb
```
2. Bring down bigchaindb containers
```
docker-compose down -v
```

All the methods to create and transact a Currency are present in src/bigchain_currency.py

Following were used as a reference for building bigchain currency:
* [Testnet](https://blog.bigchaindb.com/the-status-of-the-bigchaindb-testnet-90d446edd2b4)
* [BigchainDB](http://docs.bigchaindb.com/en/latest/index.html)
* [Divisible Assets](http://docs.bigchaindb.com/projects/py-driver/en/latest/usage.html#divisible-assets)

## Flow

Any user of the platform has to upload their stream processing logic. To upload go to ```/``` endpoint and upload the file. If the server is deployed locally, the url would be ```http://localhost:3500/```. After a successful upload, a key will be shown on screen. Make note of this key. The use of this key is explained below. This file must have a 'process' function. A sample process function with the required function signature is shown below.
```
def process(entry_data,exit_data):
  data = dict(exit_data)
  data[‘entry_timestamp’] = entry_data[‘entry_timestamp']
  data['isWanted'] = <get data from law enforcement database>
  data['accumulated_penalty'] = <get data from violations database>
  data['rate_per_hour'] = 10
  data['tot_amount'] = (data['exit_timestamp']-data['entry_timestamp']) * data['rate_per_hour'] +data['accumulated_penalty']
  return data
```

The process function has two inputs: entry_data and exit_data. These two inputs represent the entry stream and the exit stream respectively. The platform supports applications that generates a maximum of two streams. For applications that generate only one stream point it to the exit stream. Two streams makes sense, for example, in the case of a parking lot application. This application will have one stream of incoming cars and one stream of outgoing cars. To calculate the parking charge, we need data from both the streams ie, when the vehicle entered and when the vehicle exited. In this case, point the entry stream (ie send a post request) to the **/entry** endpoint of the platform and point the exit stream to **/exit** endpoint of the platform.

The result of the processing should always be the amount to be transferred between the accounts and it should be put into the **tot_amount** field as shown above ie, the data returned by the process function should always have a tot_amount field.

For applications that generate only one stream, for example, in the case of a shopping application, the only stream generated is on the customer orders and this stream has enough information to calulate the total amount for a user. In this case point this stream to the /exit endpoint. Further, in the process function, ignore the entry_data input as it will be null.

When sending post requests to the /entry or /exit endpoint, the data should contain a minimum of four fields. They are **\_id**, **from_id**, **to_id**, **porcessor_id** followed by application specific data. \_id is the transaction id, from_id is the blockchain account number of the sender/customer/account from which money should be debited, to_id is the blocchain account number of the receiver/account to which the mone should be credited and processor_id is the id of the processor to be executed. This should set to the value that is returned after uploading stream processor the file mentioned earlier.

The example below for a parking application shows the flow.

- When a vehicle enters, the sensor sends a post request to the **/entry** api of the platform. The request body has the following structure
```javascript
{
  "_id": "20343434995051",
  "from_id": "0xsf34343uu44",
  "to_id": "0zdsfdhf8883434",
  "processor_id": "94ndsjsf933",
  "vehicle_id": "23554dfd77hh343",
  "entry_timestamp": 1575768689,
  "parking_loc_id": "239499fdf939494",
  "location": "sdsdsdsd"
}
```
- When the vehicle leaves, the sensor sends a post request to the **/exit** endpoint of the app. The request body has the following structure
```javascript
{
  "_id": "20343434995051",
  "from_id": "0xsf34343uu44",
  "to_id": "0zdsfdhf8883434",
  "processor_id": "94ndsjsf933",
  "vehicle_id": "23554dfd77hh343",
  "exit_timestamp": 1575768689,
  "parking_loc_id": "239499fdf939494",
  "location": "sdsdsdsd"
}
```

When the /exit api is triggered, it executes the corresponding processor refereced in the request body which then generates the processed data which will have the amount to be transferred in the 'tot_amount' field. After this a transaction will be attempted in the bigchain DB which will tranfer the amount between the accounts. The result of the transaction is printed in the terminal running the tx_consumer.py.


