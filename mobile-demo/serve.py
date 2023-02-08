from flask import Flask, request, jsonify
from pymongo import MongoClient
import json
import time
timeout = time.time() + 60*1

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

MONGO_CONN = "<MONGO_SECRET>"
client = MongoClient(MONGO_CONN)
database="fraud-detection"
write_collection = 'txn-data-stream'
read_collection = 'txn_status'

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/initiate/txn',methods=['POST'])
def initiate_txn():
    ip = user = request.json
    db = client[database]
    v = db[write_collection].insert_one(ip)
    collection = db[read_collection]
    with collection.watch([{"$match":{"fullDocument.txn_num":ip['trans_num']}}]) as stream:
        while stream.alive:
            change = stream.try_next()
            print("Current resume token: %r" % (stream.resume_token,))
            if change is not None:
                print("Change document: %r" % (change,))
                val = change['fullDocument']
                del val['_id']
                return json.dumps(val)
            if time.time() > timeout:
                return {"txn_num":ip['trans_num'], "status":"Failed", "reason":"timeout" }
# main driver function
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8889)
