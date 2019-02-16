import base64
import json
import os
import psycopg2
import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_connection():
    secret = get_secret()
    connection_string = secret['connection_string']
    conn = psycopg2.connect(connection_string)
    conn.autocommit = True
    return conn

def run_query(query):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)

def get_secret():
    secret_name = "baran_redshift_user"
    secret_manager = boto3.client('secretsmanager')
    try:
        secret_value_response = secret_manager.get_secret_value(SecretId=secret_name)

    except ClientError as e:
        if e.response['Error']['Code'] in ['DecryptionFailureException', 'InternalServiceErrorException',
                                           'InvalidParameterException', 'InvalidRequestException',
                                           'ResourceNotFoundException']:
            raise e
        else:
            logger.erawsr('not handled error: '+ str(e))
            raise Exception('Not known error')

    if 'SecretString' in secret_value_response:
        secret = secret_value_response['SecretString']

    else:
        secret = base64.b64decode(secret_value_response['SecretBinary'])
    return json.loads(secret)

            
    
def get_environment():
    return os.environ.get('SLS_STAGE', 'dev')
