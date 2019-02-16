import base64
from datetime import datetime
import json
import boto3
import psycopg2
from utils import run_query, get_environment, get_secret

def main(event, context):
    input_filename = event['transformer_result']['filename']
    bucket = event['transformer_result']['bucket']
    write_from_s3_to_redshift(input_filename, bucket)

def write_from_s3_to_redshift(filename, bucket):
    iam_role = get_secret()['iam_role']
    table_name = 'exchange_rates'
    schema = 'dbt_dev_baran'
    query = f"""
            DROP TABLE dbt_dev_baran.{table_name};

            CREATE TABLE IF NOT EXISTS dbt_dev_baran.{table_name} (
                report_date TIMESTAMP,
                currency VARCHAR(3),
                rate FLOAT(4)
            );
            
            TRUNCATE {schema}.{table_name};

            COPY {schema}.{table_name} (report_date, currency, rate)
            FROM 's3://{bucket}/{filename}'
            IAM_ROLE '{iam_role}'
            DELIMITER ','
            IGNOREHEADER 1
            REMOVEQUOTES;
    """
    run_query(query=query)
    print(f'{filename} written to {table_name}')

def test_app():
    report_date = '2018-03-01'
    event = {
        'report_date': report_date,
        'transformer_result': {
            'filename': f'stage=dev/service=currency-etl-baran/dt={report_date}/exchange_rates_transformed.csv',
            'bucket': 'hausmeister-sources'
        }
    }
    main(event, context=None)


if __name__ == "__main__":
    test_app()
