import csv
from datetime import datetime
import json
from io import StringIO
import boto3
from utils import get_environment

def main(event, context):
    env = get_environment()
    input_filename = event['extractor_result']['filename']
    bucket = event['extractor_result']['bucket']
    report_date = event['report_date']
    bucket = event['extractor_result']['bucket']

    output_filename = f'stage={env}/service=currency-etl-baran/dt={report_date}/exchange_rates_transformed.csv'
    file_content = read_from_s3(input_filename, bucket)
    transformed_file = transform(file_content)
    
    write_to_s3(transformed_file, output_filename, bucket)
    return_event = {
        'filename': output_filename,
        'bucket': bucket
    }
    return return_event


def read_from_s3(filename, bucket):
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, filename)
    file_content = obj.get()['Body'].read().decode('utf-8') 
    return file_content

def transform(file_content):
    json_content = json.loads(file_content)
    rates = json_content['rates']
    timestamp = json_content['timestamp']
    readable_date = datetime.utcfromtimestamp(timestamp)
    listofdict = []
    for k,v in rates.items():
        row = {
            'report_date': readable_date,
            'currency': k,
            'rate': v
        }
        listofdict.append(row)
    return listofdict
    
def write_to_s3(listofdict, filename, bucket):
    s3_resource = boto3.resource('s3')
    csv_buffer = StringIO()
    keys = listofdict[0].keys()
    dict_writer = csv.DictWriter(csv_buffer, keys)
    dict_writer.writeheader()
    dict_writer.writerows(listofdict)
    s3_resource.Object(bucket, '%s' % filename).put(Body=csv_buffer.getvalue())
    csv_buffer.close()
    print(f'{filename} written to s3')


def test_app():
    report_date = '2018-03-01'
    event = {
        'report_date': report_date,
        'extractor_result': {
            'filename': f'stage=dev/service=currency-etl-baran/dt={report_date}/exchange_rates.json',
            'bucket': 'hausmeister-sources'
        }
    }
    main(event, context=None)


if __name__ == "__main__":
    test_app()