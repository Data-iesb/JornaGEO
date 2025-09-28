import json
import boto3
import uuid
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE', 'jornageo-registrations')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
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
            'created_at': timestamp,
            'status': 'confirmed'
        }
        
        try:
            response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email))
            if response['Items']:
                return {'statusCode': 409, 'headers': headers, 'body': json.dumps({'error': 'Email already registered'})}
        except Exception:
            pass
        
        table.put_item(Item=registration_data)
        
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
