# Databricks notebook source
# MAGIC %pip install mlflow
# MAGIC %pip install imblearn
# MAGIC %pip install xgboost

# COMMAND ----------

fdf = spark.read.table("fraud_demo_txn_data").select("_id","is_fraud")
fdf.drop("is_fraud")

# COMMAND ----------

from databricks.feature_store import feature_table
from databricks.feature_store import FeatureStoreClient
from databricks.feature_store import FeatureLookup

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

training_df = training_df.drop(['cc_num',"age", "gender_id"],axis=1)
training_df

# COMMAND ----------

import mlflow
import mlflow.sklearn
import mlflow.pyfunc
import mlflow.spark
from mlflow.models.signature import infer_signature
from mlflow.utils.environment import _mlflow_conda_env

import sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import f1_score,accuracy_score, classification_report,roc_auc_score
import xgboost as xgb
import numpy as np                   # array, vector, matrix calculations
import pandas as pd                  # DataFrame handling

import os
import time


# COMMAND ----------

X = training_df.drop("is_fraud", axis=1)
y = training_df["is_fraud"]
X_train,X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=42)

# COMMAND ----------

class XGBModelWrapper(mlflow.pyfunc.PythonModel):
    def __init__(self, model):
        self.model = model

    def predict(self, context, model_input):
        return self.model.predict_proba(model_input)[:,1]

# COMMAND ----------

with mlflow.start_run(run_name='fraud_xgb_model_train'):
    n_estimators = 100
    model = xgb.XGBClassifier(n_estimators=n_estimators)
    model.fit(X_train,y_train)

    # predict_proba returns [prob_negative, prob_positive], so slice the output with [:, 1]
    predictions_test = model.predict_proba(X_test)[:,1]
    auc_score = roc_auc_score(y_test, predictions_test)
    mlflow.log_param('n_estimators', n_estimators)
    # Use the area under the ROC curve as a metric.
    mlflow.log_metric('auc', auc_score)
    wrappedModel = XGBModelWrapper(model)
    # Log the model with a signature that defines the schema of the model's inputs and outputs. 
    # When the model is deployed, this signature will be used to validate inputs.
    signature = infer_signature(X_train, wrappedModel.predict(None, X_train))

    # MLflow contains utilities to create a conda environment used to serve models.
    # The necessary dependencies are added to a conda.yaml file which is logged along with the model.
    conda_env =  _mlflow_conda_env(
        additional_conda_deps=None,
        additional_pip_deps=["scikit-learn=={}".format(sklearn.__version__), "xgboost=={}".format(xgb.__version__), "imblearn"],
        additional_conda_channels=None,
    )
    mlflow.pyfunc.log_model("fraud_xgb_model_1", python_model=wrappedModel, conda_env=conda_env, signature=signature)

# COMMAND ----------

feature_importances = pd.DataFrame(model.feature_importances_, index=X_train.columns.tolist(), columns=['importance'])
feature_importances.sort_values('importance', ascending=False)

# COMMAND ----------

y_pred = np.vstack(model.predict_proba(X_test))
auc = roc_auc_score(y_test,y_pred[:,1]>0.3)
print(classification_report(y_test,y_pred[:,1]>0.3))
print(f'AUC: {auc}')

# COMMAND ----------

run_id = mlflow.search_runs(filter_string='tags.mlflow.runName = "fraud_xgb_model_train"').iloc[0].run_id
model_name = "fraud_xgb_model_1"
model_version = mlflow.register_model(f"runs:/{run_id}/fraud_xgb_model_1", model_name)

# Registering the model takes a few seconds, so add a small delay
time.sleep(15)

# COMMAND ----------

if(auc>0.91):
    print(f"Publishing the {model_name}-{run_id} to Staging env")
    from mlflow.tracking import MlflowClient 
    client = MlflowClient()
    client.transition_model_version_stage(
      name=model_name,
      version=model_version.version,
      stage="Staging",
    )

# COMMAND ----------

model = mlflow.pyfunc.load_model(f"models:/{model_name}/staging")
y_pred = model.predict(X_test)
# Sanity-check: This should match the AUC logged by MLflow
print(f'AUC: {roc_auc_score(y_test,y_pred)}')
print(classification_report(y_test,y_pred>0.5))

# COMMAND ----------

import mlflow.pyfunc
 
apply_model_udf = mlflow.pyfunc.spark_udf(spark, f"models:/{model_name}/staging")


# COMMAND ----------

from pyspark.sql.functions import struct
 
mip = spark.read.table("fraud_demo_txn_data")
# Apply the model to the new data
udf_inputs = struct(*(X_train.columns.tolist()))
 
new_data = mip.withColumn(
  "prediction",
  apply_model_udf(udf_inputs)
)

# COMMAND ----------

new_data.filter("is_fraud like 1").show(10,False)

# COMMAND ----------

