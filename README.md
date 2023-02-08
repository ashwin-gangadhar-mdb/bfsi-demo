# Fraud Detection 

DEMO VIDEO : 


### Introduction
 Fraud prevention in the banking and financial services industry is the process of identifying, preventing and mitigating fraudulent activities to protect customers' assets and the financial institution's reputation. Banks and other financial institutions are particularly vulnerable to fraud because they handle large amounts of sensitive financial information and transactions.

### Architecture 1
<img width="1957" alt="image" src="images/Draft of FraudDetection - Whitepaper.png">

The high level architecture components for implementing the real time fraud detection model is as below:
1. Producer apps & SQL data source : The producer app is a simulator that mimics generation of transactions. The SQL source has been included as a sample operational data source that holds customer demographics
2. MongoDB Atlas: Atlas serves as the core persistence layer and stores the raw transactions, the transactions flagged as fraud as well customer demographics
3. Fraud detection layer on Databricks: The core fraud detection algorithm is a reference notebook provided by Databricks. MLFlow has been used to manage the MLOps for this model. The trained model is available as a REST endpoint. The model is also operating on a Delta live table to provide batch/ real time predictive analytics. Deltalake has been used as the persistence on Databricks


### Architecture 2
<img width="1957" alt="image" src="images/FraudDetection - MDB Kafka DB copy.png">

<TODO Kafka integration>

 ## Notebooks
 
 ### Model Training and Registeration

* Trains and Registers a Model based on Rules 

   #### BFSI/notebooks/Fraud_demo_rule_dag.ipynb

* Trains and Registers a Model based on Classification using XGB.
 
   #### BFSI/notebooks/Fraud_demo_model_training.ipynb
 
 <img width="1957" alt="image" src="images/db-registerd-models.png">

 ### Data Collection / Featurization and Streamoing

* Load Realtime data from mongodb > extract features > write to mongodb

   #### BFSI/notebooks/Fraud_demo_streaming.ipynb

* Load one time batch data incrementally to train model

   #### BFSI/notebooks/Fraud_demo_data_transform.ipynb
 
 
  ## Training ML Models using Databricks/ML flow/Feature store
 
 #### Data collections

 Using MongoDB Spark Connector load historical transactions data from MongoDB fraud-detection.txn_data collection to Delta live tables. This is one time dump run each time to update the Delta live table (DLT) with new transactions that have been processed between subsequent runs of this step. This stage helps extracting relevant features from the raw transactions data and create a featurized view to be easily consumed for ML model training. Also The DLT is registered as Feature store. This help maintain,verisoning, lineage for features created over time. 

 ##### Input : transactions
 ##### Output : 
 raw transaction data in mongodb
 <img width="1901" alt="image" src="images/raw_txn.png">
 processed trainsaction in feature store
 <img width="1901" alt="image" src="images/txn_features.png">


 #### xgb-model for User Agnostic transaction classification

We build a simple XGB classifier over the extracted features stored in the feature store. Using the MLflow we are able to track num of estimators used for modelling, ,model accuracy, auc to maitain details of various interations and also monitor the model performance over time. Based on the performance of the model run we promote the model to staging enviroment and post testing all the integration steps the model can be promoted to production enviroment.

Model Run Info
<img width="1901" alt="image" src="images/model_train_view.png">

Model Run Registry
<img width="1901" alt="image" src="images/model_registry.png">


#### rule-based-predict
 
Similar to the previous XGB model run. We can wrap the xgb model with some user set rule on user application to validate transactions. The model first executes the rule check by using cc_num and make a request to fraud-detection.usr_auth_rule_data collection to fetch use specific and validate the transaction features against the same. Once all the rules are satificatorily processed the transaction is verified using the XGB model built above. The combined model now is registered using ML flow. This help is versioning and maintaining various rule features introduced/removed/changed over time.

Example view of rule collection
<img width="1901" alt="image" src="images/rule_collection.png">

Rule Model Execution Flow
<img width="1901" alt="image" src="images/bfsi_rule_model_flow.drawio.png">


#### Create Workflows

Create two workflows one for model training activity and second for realtime processing of transactions. The second workflows are continously running jobs whereas the model training worflow is scheduled to run at regular intervals.
Follow steps in link to create new worflow: https://docs.databricks.com/workflows/jobs/jobs-quickstart.html

Once successfully created workflow will look as follows
Model training workflow
<img width="1686" alt="image" src="images/worflow1.png">

Streaming Worflow
<img width="1987" alt="image" src="images/worflow2.png">

#### rule-processed-mongo-sink

Reads the processed_transaciton DLT stream continuously and write into mongo collection.

### Collections

1. transactions 
   Inserts all the raw transactions as it is received from the simulator.
   
   <img width="738" alt="image" src="images/txn_stream_data.png">


2. processed transactions post feature transformation :
   Inserts the processed transaction run against the feature extraction. 
   This collection would have a featurized view of the raw transaction to be used for classificaiton of the txn a fradulent or not.
   Against this collection we set the tigger function. Upon insert or update on this collection we use the Appservice txnpred func to call the classifier.
   
   <img width="688" alt="image" src="images/txn_featurized_view.png">


3. transaction status table :  
   The pred function from Atlas App service inserts the processed transaction run against the classification model.
   This collection would have a transaction status column added to show the prediction value when run against the transaction record, also carries the transaction number for identification.
   
   <img width="655" alt="image" src="images/txn_status.png">


### Transaction Simulation

A simple python program to simulate the Transaction of record being inserted every 1 min. It randomly generates valid/fraud transactions and inserts them to the raw transactions.


### Model REST Endpoints

DEMO : https://youtu.be/Gig3Yn2QG1c

Databricks can serve the models as REST endpoints. The Models are setup in a cluster. The size of which can be changed by the user based on the need.
Below is a snapshot of the REST Endpoint exposed in a m5.xa.large cluster.
<img width="629" alt="image" src="images/model_rest_endpoint1.png">

Since the endpoint are exposed via REST the Authentication key can be generated from the databricks as shown below
<img width="867" alt="image" src="images/model_rest_endpoint2.png">

The rule model registered in the model registry is exposed as REST endpoints as shown below

#### RULE BASED MODEL : https://dbc-ca6bc27a-67f7.cloud.databricks.com/model/fraud_rule_model/Staging/invocations

<img width="1515" alt="image" src="images/model_rest_endpoint_3.png">



### Atlas Trigger Function

A Simple javascript program writtien as function under MongoDB Atlas App services to listen to the transactions features collections using set Atlas triggers. Once triggered the trigger invoke the rule model REST API's exposed and update the fraud_detection.txn_status collection. 

Setting Atlas triggers (https://www.mongodb.com/docs/atlas/triggers/)
The Code to trigger function used in this demo
<img width="1224" alt="image" src="images/atlas_trigger_fn.png">

Create a trigger function as shown in the steps above and add the code in the function block.
