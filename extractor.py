import json
from base64 import b64decode
import logging
import requests
import boto3
from utils import get_environment, get_secret

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def main(event, context):
    env = get_environment()
    report_date = event['report_date']
    output_filename = f'stage={env}/service=currency-etl-baran/dt={report_date}/exchange_rates.json'
    bucket = 'hausmeister-sources'
    request_url = f'https://openexchangerates.org/api/historical/{report_date}.json'
    logger.info('asking to secret manager')
    secret = get_secret()
    
    params = {'app_id': secret['app_id']}
    r = requests.get(request_url, params=params)

    write_to_s3(r.json(), output_filename, bucket)
    return_event = {
        'bucket': bucket,
        'filename': output_filename,
    }
    return return_event
    

def write_to_s3(dict_data, filename, bucket):
    s3_resource = boto3.resource('s3')
    s3_resource.Object(bucket, '%s' %filename).put(Body=json.dumps(dict_data))
    logger.info(f'{filename} written to s3')


def test_app():
    event = {'report_date': '2018-03-01'}
    main(event, context = None)

if __name__ == "__main__":
    test_app()
