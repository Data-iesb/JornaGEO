import json
import boto3
from boto3.dynamodb.conditions import Key
import uuid
import os
from datetime import datetime
import psycopg2

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
secretsmanager = boto3.client('secretsmanager')
table_name = os.environ.get('DYNAMODB_TABLE', 'jornageo-registrations')
table = dynamodb.Table(table_name)
sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')

def lambda_handler(event, context):
    # Handle SNS messages
    if 'Records' in event:
        for record in event['Records']:
            if record.get('EventSource') == 'aws:sns':
                handle_sns_message(record)
        return {'statusCode': 200}
    
    # Handle API Gateway requests
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
    }
    
    try:
        if event['httpMethod'] == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'CORS preflight'})}
        
        if event['httpMethod'] == 'POST':
            return handle_registration(event, headers)
        
        if event['httpMethod'] == 'GET':
            return handle_get_registrations(event, headers)
        
        return {'statusCode': 405, 'headers': headers, 'body': json.dumps({'error': 'Method not allowed'})}
        
    except Exception as e:
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': 'Internal server error'})}

def handle_sns_message(record):
    message = json.loads(record['Sns']['Message'])
    print(f"Received SNS message: {message}")

def handle_registration(event, headers):
    try:
        body = json.loads(event['body'])
        
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in body or not body[field].strip():
                return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': f'Field {field} is required'})}
        
        email = body['email'].strip().lower()
        if '@' not in email or '.' not in email:
            return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'Invalid email format'})}
        
        timestamp = datetime.utcnow().isoformat()
        registration_id = str(uuid.uuid4())
        
        registration_data = {
            'email': email,
            'timestamp': timestamp,
            'registration_id': registration_id,
            'name': body['name'].strip(),
            'organization': body.get('organization', '').strip(),
            'position': body.get('position', '').strip(),
            'phone': body.get('phone', '').strip(),
            'management_area': body.get('management_area', '').strip(),
            'hands_on': body.get('ai_session', False),
            'created_at': timestamp,
            'status': 'confirmed'
        }
        
        try:
            response = table.query(KeyConditionExpression=Key('email').eq(email))
            if response['Items']:
                return {'statusCode': 409, 'headers': headers, 'body': json.dumps({'error': 'Email already registered'})}
        except Exception:
            pass
        
        table.put_item(Item=registration_data)
        
        # Save to RDS
        save_to_rds(registration_data)
        
        # Subscribe registrant to SNS topic
        if sns_topic_arn:
            sns.subscribe(
                TopicArn=sns_topic_arn,
                Protocol='email',
                Endpoint=email
            )
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Registration successful',
                'registration_id': registration_id
            })
        }
        
    except Exception as e:
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': 'Registration failed'})}

def handle_get_registrations(event, headers):
    try:
        response = table.scan()
        registrations = response['Items']
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'registrations': registrations,
                'count': len(registrations)
            }, default=str)
        }
        
    except Exception as e:
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': 'Failed to retrieve registrations'})}

def save_to_rds(data):
    try:
        secret = secretsmanager.get_secret_value(SecretId='rds-master')
        db_config = json.loads(secret['SecretString'])
        
        conn = psycopg2.connect(
            host=db_config['host'],
            database=db_config['db_name'],
            user=db_config['username'],
            password=db_config['password']
        )
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO jornageo (registration_id, email, name, phone, organization, position, management_area, hands_on, status, created_at, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['registration_id'], data['email'], data['name'], data['phone'],
            data['organization'], data['position'], data['management_area'],
            data['hands_on'], data['status'], data['created_at'], data['timestamp']
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"RDS save error: {e}")
