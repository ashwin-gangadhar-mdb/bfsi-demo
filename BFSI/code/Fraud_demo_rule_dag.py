# Databricks notebook source
# MAGIC %pip install mlflow
# MAGIC %pip install pymongo
# MAGIC %pip install xgboost

# COMMAND ----------

import mlflow
import mlflow.sklearn
import mlflow.pyfunc
import mlflow.spark
from mlflow.models.signature import infer_signature
from mlflow.utils.environment import _mlflow_conda_env
import pandas as pd 
from copy import copy
import cloudpickle

from pymongo import __version__ as mongo_version
from pymongo import MongoClient

import xgboost as xgb
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score,accuracy_score, classification_report,roc_auc_score
import numpy as np                   # array, vector, matrix calculations
import pandas as pd                  # DataFrame handling

import os
import time

# method= SMOTE()

def get_mongo_conn():
    MONGO_CONN = "<secret>"
    database="fraud-detection"
    collection="usr_auth_rule_data"
    client = MongoClient(MONGO_CONN)
    db = client[database]
    collection = db[collection]
    return collection


# COMMAND ----------

class RuleNMLModelWrapper(mlflow.pyfunc.PythonModel):
    def __init__(self):
        self.feature_columns = ["age", "amt", "cat_id", "city_pop", "day", "gender_id", "hour", "lat", "long", "merch_lat", "merch_long", "month", "zip"]
        self.thresh = 0.3
        self.rules = [self.r1,self.r2,self.r3]

    def r1(self,x):
        return x['amt']<x['ACCT_AVL_CASH_BEFORE_AMT']
    
    def r2(self,x):
        return x['amt']<x['ACCT_CL_AMT']
    
    def r3(self, x):
        return x['amt']>x['AVG_DLY_AUTHZN_AMT']

    def get_mongo_conn(self):
        MONGO_CONN = "<connection_string>"
        database="fraud-detection"
        collection="usr_auth_rule_data"
        client = MongoClient(MONGO_CONN)
        db = client[database]
        collection = db[collection]
        return collection       
        
    def predict(self, context, model_input):
        xgb_model = model = mlflow.pyfunc.load_model(f"models:/{model_name}/staging")
        ip = copy(model_input)
        rules_df = pd.DataFrame(self.get_mongo_conn().find({},{"_id":0}))
        rules_df['cc_num'] = rules_df['cc_num'].apply(int)
        ip['cc_num'] = ip['cc_num'].apply(int)
        ip = ip.merge(rules_df,on='cc_num',how='left')
        for i in range(len(self.rules)):
            ip['case'+str(i)] = self.rules[i](ip)

        op = None
        for col in [f"case{str(i)}" for i in range(len(r))]:
            if op is not None:
                op = op & ip[col]
            else:
                op = ip[col]
        ip['prediction'] = list(op)
        ip['prediction'] = ip['prediction'].astype(int)
        return (xgb_model.predict(ip[feature_columns])>self.thresh).astype(int)

# COMMAND ----------

from databricks.feature_store import feature_table
from databricks.feature_store import FeatureStoreClient
from databricks.feature_store import FeatureLookup

fdf = spark.read.table("fraud_demo_txn_data").select("_id","is_fraud")
fdf.drop("is_fraud")

feature_table_name = "default.bfsi_txn_features"

feature_names = list(fdf.columns)

feature_lookups = [
    FeatureLookup(
        table_name=feature_table_name,
        lookup_key="_id",
    ),
]
fs = FeatureStoreClient()
training_set = fs.create_training_set(
    fdf,
    feature_lookups=feature_lookups,
    exclude_columns=["_id"],
    label="is_fraud",
)
training_df = training_set.load_df().toPandas()

# COMMAND ----------

X = training_df.drop("is_fraud", axis=1)
y = training_df["is_fraud"]
X_train,X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=42)

# COMMAND ----------

X_train

# COMMAND ----------

conda_env = mlflow.pyfunc.get_default_conda_env()
conda_env['dependencies'][2]['pip'] += ['xgboost']
conda_env['dependencies'][2]['pip'] += ['sklearn']
conda_env['dependencies'][2]['pip'] += ['imblearn']
conda_env['dependencies'][2]['pip'] += ['pymongo']

with mlflow.start_run(run_name='fraud_rule_model'):    
    collection = get_mongo_conn()
    wrappedModel = RuleNMLModelWrapper()
    signature = infer_signature(X_train, wrappedModel.predict(None, X_train))
    mlflow.pyfunc.log_model("fraud_rule_model", python_model=wrappedModel, conda_env=conda_env,signature=signature)

# COMMAND ----------

run_id = mlflow.search_runs(filter_string='tags.mlflow.runName = "fraud_rule_model"').iloc[0].run_id

# COMMAND ----------

model_name = "fraud_rule_model"
model_version = mlflow.register_model(f"runs:/{run_id}/fraud_rule_model", model_name)
 
# Registering the model takes a few seconds, so add a small delay
time.sleep(15)

# COMMAND ----------

from mlflow.tracking import MlflowClient
 
client = MlflowClient()
client.transition_model_version_stage(
  name=model_name,
  version=model_version.version,
  stage="Staging",
)

# COMMAND ----------

