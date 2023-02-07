# Databricks notebook source
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window

MONGO_CONN = "<secret>"

database="fraud-detection"
collection="txn-data"

# COMMAND ----------

pipeline = []
df=(spark.read.format("mongodb").\
	option('spark.mongodb.connection.uri', MONGO_CONN).\
	option('spark.mongodb.database', database).\
	option('spark.mongodb.collection', collection).\
	option("forceDeleteTempCheckpointLocation", "true").load())

# COMMAND ----------

columns = ["_id","cc_num",'category','amt','zip','lat','long', 'gender','city_pop','merch_lat','merch_long','dob','trans_date_trans_time','is_fraud']
fdf = df.select(*columns)

# COMMAND ----------

from datetime import datetime, timedelta
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

# COMMAND ----------

f_columns = ["_id","cc_num",'category', 'gender','amt','zip','lat','long','city_pop','merch_lat','merch_long','age','hour','day','month','is_fraud']

# COMMAND ----------

cat_lookup = fdf.select("category").distinct().withColumn("cat_id", F.monotonically_increasing_id())
gender_lookup = fdf.select("gender").distinct().withColumn("gender_id", F.monotonically_increasing_id())

cat_lookup.write.format("mongodb").option('spark.mongodb.connection.uri', MONGO_CONN).\
    option('spark.mongodb.database', database).\
	option('spark.mongodb.collection', "category_lookup").\
	option("forceDeleteTempCheckpointLocation", "true").mode("overwrite").save()
gender_lookup.write.format("mongodb").option('spark.mongodb.connection.uri', MONGO_CONN).\
    option('spark.mongodb.database', database).\
	option('spark.mongodb.collection', "gender_lookup").\
	option("forceDeleteTempCheckpointLocation", "true").mode("overwrite").save()

# COMMAND ----------

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
fdf.show(10,False)

# COMMAND ----------

fdf.write.mode("overwrite").format("delta").saveAsTable("fraud_demo_txn_data")

# COMMAND ----------

fdf = spark.read.table("fraud_demo_txn_data")

# COMMAND ----------

from databricks.feature_store import feature_table
from databricks.feature_store import FeatureStoreClient
fs = FeatureStoreClient()

features_df = fdf.drop("is_fraud")

customer_feature_table = fs.create_table(
  name='default.bfsi_txn_features',
  primary_keys='_id',
  schema=features_df.schema,
  description='Transaction features'
)

fs.write_table(
  name='default.bfsi_txn_features',
  df = features_df,
  mode = 'overwrite'
)

# COMMAND ----------

fdf.printSchema()

# COMMAND ----------

fdf.show(10,False)

# COMMAND ----------

fdf.schema

# COMMAND ----------

user_df = df.select("first","last", "amt", "is_fraud").groupby("first","last").agg(F.sum("amt").alias("total"),F.avg("amt").alias("avg_txn_amt"),F.sum(F.lit(1)).alias("ntxn"), F.sum("is_fraud").alias("ftxn"))

# COMMAND ----------

user_df.count()

# COMMAND ----------

