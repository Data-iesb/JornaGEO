import boto3
from botocore.exceptions import ClientError

def create_jornageo_table():
    dynamodb = boto3.resource('dynamodb')
    
    table_name = 'jornageo-registrations'
    
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        table.wait_until_exists()
        print(f"Table {table_name} created successfully")
        return table
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {table_name} already exists")
            return dynamodb.Table(table_name)
        else:
            print(f"Error creating table: {e}")
            return None

def create_speakers_table():
    dynamodb = boto3.resource('dynamodb')
    
    table_name = 'jornageo-speakers'
    
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'speaker_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'speaker_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        table.wait_until_exists()
        print(f"Table {table_name} created successfully")
        return table
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {table_name} already exists")
            return dynamodb.Table(table_name)
        else:
            print(f"Error creating table: {e}")
            return None

if __name__ == "__main__":
    print("Creating JornaGEO DynamoDB tables...")
    create_jornageo_table()
    create_speakers_table()
    print("Tables creation completed!")
