from datetime import datetime
import pytz
import numpy as np
from dateutil.relativedelta import relativedelta
from pyspark.sql.functions import *
from pyspark.sql.functions import col, lit
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext, DynamicFrame
from awsglue.job import Job
  
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

today = datetime.now(pytz.timezone("Asia/Bangkok")).date() # "America/Toronto"
extract_date = today # able to edit datetime.strptime("yyyymmdd", "%Y%m%d")
bucket = "vnstockmarket-sample-dev"
table_name = "stg_vnindex_historical_index"

delta = relativedelta(days=1)
for date in np.arange(extract_date, today + delta, delta):
    date = date.astype(datetime)
    date_string = date.strftime("%Y%m%d")
    print(f"Processed Date: {date_string}")
    
    # source S3 path
    s3_stg_vnindex_historical_index_path = f"s3://{bucket}/{table_name}/{date_string}.csv"

    # destination S3 path
    s3_cleaned_stg_vnindex_historical_index_path = f"s3://{bucket}/cleaned/{table_name}/{date_string}.csv"
    
    stg_vnindex_historical_index = spark.read.format("csv").option("header","true"
                                                                ).load(s3_stg_vnindex_historical_index_path)
    stg_vnindex_historical_index = stg_vnindex_historical_index.select(
            to_date(col('RECORDED_DATE'), 'dd/MM/yyyy').alias('RECORDED_DATE'),
            col('CLOSE_PRICE').cast('double').alias('INDEX_SCORE'),
            regexp_replace(col('INDEX_CHANGE').substr(lit(1), instr(col('INDEX_CHANGE'), '(') - 1), 
                           ',', '').cast('double').alias('INDEX_CHANGE_VALUE'),
            regexp_replace(
                regexp_replace(
                    col('INDEX_CHANGE').substr(instr(col('INDEX_CHANGE'), '(') + 1, 
                                               length(col('INDEX_CHANGE')) - instr(col('INDEX_CHANGE'), '('))
                    , ' %\)', '')
                , 'INFINITY', '').cast('double').alias('INDEX_CHANGE_PERCENT'),
            col('MACHED_VOLUME').cast('double').alias('MACHED_VOLUME'),
            col('MACHED_AMOUNT').cast('double').alias('MACHED_AMOUNT'),
            col('SELF_DEALED_VOLUME').cast('double').alias('SELF_DEALED_VOLUME'),
            col('SELF_DEALED_AMOUNT').cast('double').alias('SELF_DEALED_AMOUNT'),
            col('OPEN_PRICE').cast('double').alias('OPEN_PRICE'),
            col('HIGHEST_PRICE').cast('double').alias('HIGHEST_PRICE'),
            col('LOWEST_PRICE').cast('double').alias('LOWEST_PRICE')
        )
    stg_vnindex_historical_index.show()
    stg_vnindex_historical_index.toPandas().to_csv(s3_cleaned_stg_vnindex_historical_index_path, index=False)
    print(f"The {table_name} data of {date_string} has been cleaned!")