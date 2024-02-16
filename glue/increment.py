from datetime import datetime
import pytz
import numpy as np
from dateutil.relativedelta import relativedelta
from pyspark.sql.functions import *
from pyspark.sql.functions import col, lit
from pyspark.sql.types import StructType,StructField, StringType, IntegerType
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext, DynamicFrame
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
import mysql.connector
  
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

today = datetime.now(pytz.timezone("Asia/Bangkok")).date() # "America/Toronto"
extract_date = today # datetime.strptime("yyyymmdd", "%Y%m%d") # today
bucket = "vnstockmarket-sample-dev"
table_name = "stg_vnindex_historical_index"

# connection parameters to Aurora
hostname = "aurora-1-instance-1.crpjyuxywpap.ca-central-1.rds.amazonaws.com"
port = "3306"
database_name = "mydemo"
aurora_table = "STG_VNINDEX_HISTORICAL_INDEX"
username = "admin"
pwd = "Iamshining13"

# connect to Aurora
cnx = mysql.connector.connect(user=username, password=pwd,
                              host=hostname, database=database_name)
cursor = cnx.cursor()

spark_schema = StructType([
        StructField('RECORDED_DATE', StringType(), True),
        StructField('INDEX_SCORE', StringType(), True),
        StructField('INDEX_CHANGE_VALUE', StringType(), True),
        StructField('INDEX_CHANGE_PERCENT', StringType(), True),
        StructField('MACHED_VOLUME', StringType(), True),
        StructField('MACHED_AMOUNT', StringType(), True),
        StructField('SELF_DEALED_VOLUME', StringType(), True),
        StructField('SELF_DEALED_AMOUNT', StringType(), True),
        StructField('OPEN_PRICE', StringType(), True),
        StructField('HIGHEST_PRICE', StringType(), True),
        StructField('LOWEST_PRICE', StringType(), True),
    ])

# create temp table
tmp_stg_vnindex_historical_index = spark.createDataFrame([], spark_schema)

delta = relativedelta(days=1)
for date in np.arange(extract_date, today + delta, delta):
    date = date.astype(datetime)
    date_string = date.strftime("%Y%m%d")
    mysql_date_string = date.strftime("%Y-%m-%d")
    print(f"Processed Date: {date_string}")
    
    # delete old records
    delete_stmt = f"DELETE FROM {aurora_table} WHERE RECORDED_DATE = '{mysql_date_string}';"
    print(delete_stmt)
    cursor.execute(delete_stmt)
    cnx.commit()
    
    # source S3 path
    s3_cleaned_stg_vnindex_historical_index_path = f"s3://{bucket}/cleaned/{table_name}/{date_string}.csv"

    cleaned_stg_vnindex_historical_index = spark.read.format("csv"
                                                    ).option("header","true"
                                                    ).load(s3_cleaned_stg_vnindex_historical_index_path)
    print(f"Cleaned data of {date_string} has been loaded from S3!")
    
    # append new/rerun data records
    tmp_stg_vnindex_historical_index = tmp_stg_vnindex_historical_index.union(
        cleaned_stg_vnindex_historical_index)

# close connection to Aurora
cnx.close()
    
tmp_stg_vnindex_historical_index.show(1)
num_appended_rows = tmp_stg_vnindex_historical_index.count()
print(f"({num_appended_rows}) rows will be appended!")

# overwrite Aurora table
tmp_stg_vnindex_historical_index.write.format('jdbc').options(
                                  url=f"jdbc:mysql://{hostname}:{port}/{database_name}",
                                  driver="com.mysql.jdbc.Driver",
                                  dbtable=f"{aurora_table}",
                                  user=username,
                                  password=pwd).mode('append').save()