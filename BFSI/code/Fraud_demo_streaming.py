# Databricks notebook source
# MAGIC %pip install pymongo mlflow xgboost

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window
from datetime import datetime, timedelta

MONGO_CONN = "<secret>"

database="fraud-detection"


cat_lookup = spark.read.format("mongodb").option('spark.mongodb.connection.uri', MONGO_CONN).\
    option('spark.mongodb.database', database).\
	option('spark.mongodb.collection', "category_lookup").\
	option("forceDeleteTempCheckpointLocation", "true").load()
gender_lookup = spark.read.format("mongodb").option('spark.mongodb.connection.uri', MONGO_CONN).\
    option('spark.mongodb.database', database).\
	option('spark.mongodb.collection', "gender_lookup").\
	option("forceDeleteTempCheckpointLocation", "true").load()

# COMMAND ----------

read_collection="txn-data-stream"
df=(spark.readStream.format("mongodb").\
	option('spark.mongodb.connection.uri', MONGO_CONN).\
	option('spark.mongodb.database', database).\
	option('spark.mongodb.collection', read_collection).\
	option('spark.mongodb.change.stream.publish.full.document.only','true').\
	option("forceDeleteTempCheckpointLocation", "true").\
	load())

# COMMAND ----------

columns = ["_id", "trans_num","cc_num",'category','amt','zip','lat','long', 'gender','city_pop','merch_lat','merch_long','dob','trans_date_trans_time','is_fraud']
fdf = df.select(*columns)

@F.udf()
def convert_dob_dt(time):
    format = "%Y-%m-%d"
    return datetime.strptime(time,format)
@F.udf(T.IntegerType())
def convert_datetime(time):
    format = "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(time,format)
@F.udf(T.IntegerType())
def get_hour(time):
    return int(time.hour)
@F.udf(T.IntegerType())
def get_day(time):
    return time.day
@F.udf(T.IntegerType())
def get_month(time):
    return time.month
@F.udf(T.IntegerType())
def get_year(time):
    return time.year



# COMMAND ----------

fdf = fdf.withColumn("trans_date_trans_time", convert_datetime("trans_date_trans_time")).withColumn("dob",convert_dob_dt("dob"))
fdf = fdf.withColumn("hour", get_hour("trans_date_trans_time")).withColumn("day",get_day("trans_date_trans_time")).withColumn("month",get_month("trans_date_trans_time"))
fdf = fdf.withColumn("age", (get_year("trans_date_trans_time") - get_year("dob")))
fdf = fdf.withColumn("_id", F.col("trans_num"))

f_columns = ["trans_num","cc_num",'category', 'gender','amt','zip','lat','long','city_pop','merch_lat','merch_long','age','hour','day','month','is_fraud']
fdf = fdf.select(*f_columns)
fdf = fdf.withColumn("amt",fdf.amt.cast("double"))
fdf = fdf.withColumn("lat",fdf.lat.cast("double"))
fdf = fdf.withColumn("long",fdf.long.cast("double"))
fdf = fdf.withColumn("merch_lat",fdf.merch_lat.cast("double"))
fdf = fdf.withColumn("merch_long",fdf.merch_long.cast("double"))
fdf = fdf.withColumn("is_fraud",fdf.is_fraud.cast("integer"))
fdf = fdf.withColumn("city_pop",fdf.city_pop.cast("integer"))
fdf = fdf.withColumn("zip",fdf.zip.cast("integer"))
fdf = fdf.join(F.broadcast(cat_lookup),on="category")
fdf = fdf.join(F.broadcast(gender_lookup),on="gender")
fdf = fdf.drop("category")
fdf = fdf.drop("gender")

# COMMAND ----------

# import mlflow.pyfunc
# from pyspark.sql.functions import struct
# import pymongo



# model_name = "fraud_rule_model"
# model = mlflow.pyfunc.load_model(f"models:/{model_name}/staging")
 
# apply_model_udf = mlflow.pyfunc.spark_udf(spark, f"models:/{model_name}/staging")


# udf_inputs = struct(*(["cc_num","age", "amt", "cat_id", "city_pop", "day", "gender_id", "hour", "lat", "long", "merch_lat", "merch_long", "month", "zip"]))
# fdf = fdf.withColumn("prediction",apply_model_udf(udf_inputs))


# COMMAND ----------

write_collection = "txn_feature_data"
fdf.writeStream.format("mongodb").option('spark.mongodb.connection.uri', MONGO_CONN).\
	option('spark.mongodb.database', database).\
	option('spark.mongodb.collection', write_collection).\
	option("forceDeleteTempCheckpointLocation", "true").\
    outputMode("append").\
    option("checkpointLocation", "/tmp/bfsi/_checkpoint/").\
    start()

# COMMAND ----------

# from pymongo import MongoClient
# client = MongoClient(MONGO_CONN)
# db = client["fraud-detection"]
# collection = db["txn-data-stream"]
# collection.delete_many({})

# COMMAND ----------

