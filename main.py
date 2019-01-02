import sys
import boto3
from environment import *
from login_with_cognito import LoginWithCognito

user_name = sys.argv[1]
password = sys.argv[2]

if __name__ == '__main__':
    env = TEST_ENVIRONMENT
    login = LoginWithCognito(env)
    print 'Going to get temporary credentials on behalf of the user.\n'
    temporary_credentials = login.get_temporary_credentials(user_name, password)
    print 'Temporary credentials: \ntemporary access key id:{0} \ntemporary secret key: {1},' \
          ' \ntemporary session token: {2} \ntemporary credentials will expire at: {3}  '.\
        format(temporary_credentials['temp_access_key_id'], temporary_credentials['temp_secret_key'],
               temporary_credentials['temp_session_token'], temporary_credentials['expiration'])
    bucket_name = env['bucket_name']
    s3 = boto3.resource('s3',
                        aws_access_key_id=temporary_credentials['temp_access_key_id'],
                        aws_secret_access_key=temporary_credentials['temp_secret_key'],
                        aws_session_token=temporary_credentials['temp_session_token'])
    s3_bucket = s3.Bucket(bucket_name)
    for obj in s3_bucket.objects.all():
        print obj
