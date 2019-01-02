In many cases, we run into an issue where a client application running on users machine needs to access
 AWS services. Here, the client application needs to pass AWS credentials (access key and secret) while accessing
 the APIs. However, those long lasting AWS credentials are too dangerous to hard code in the client application.
  This problem is simpler to solve, if the client application is running on a web browser, or Android or iOS, AWS does 
 provide very nice SDK's that provide temporary credentials. See these AWS documentation for getting temporary 
 credentials and accessing AWS services.  https://aws-amplify.github.io/docs/js/authentication  
    However, if the client app is not running on a web browser or Android or iOS, AWS yet does not have 
    a straight forward way to provide secure authentication and authorization. 
     So, I had to dig deeper and stitch some lower level APIs to make this temporary credentials working 
     for Python. The LoginWithCognito library is built to help a client application that wants
      to access AWS services. This library assumes that the client application already has a user known 
      to the AWS Cognito user pool and identity pool.

### How to use the LoginWithCognito library?
1.  An example of how to use this library can be found in the main.py file. Before using this api, the client 
application developer needs to have a valid user account created by the AWS administrator. The administrator 
will provide a set of username, password and environment name.
2. The client app developer needs to install the dependent libraries before using this one.  
`pip install -r requirements.txt  -t .`
3.  The client app developer needs to instantiate the LoginWithCognito class with the environment name. And then to use
 the provided username and password to get the temporary credentials. These are not permanent AWS credentials, these 
 will expire in one hour by default. The duration is configurable upto the AWS IAM role's (the role your AWS 
 admin has configured with the Cognito identity pool) duration.  
    `login = LoginWithCognito(env)`  
    `temporary_credentials = login.get_temporary_credentials(user_name, password)`
                                            
4. Then the client app should be able to access to AWS services with the temporary credentials. For 
example uploading files to S3 bucket or videos to Kinesis videos or calling API gateway. In the main.py file the sample code shows how to
 list the S3 bucket content using the temporary credentials.
 `bucket_name = env['bucket_name']
    s3 = boto3.resource('s3',
                        aws_access_key_id=temporary_credentials['temp_access_key_id'],
                        aws_secret_access_key=temporary_credentials['temp_secret_key'],
                        aws_session_token=temporary_credentials['temp_session_token'])
    s3_bucket = s3.Bucket(bucket_name)
    for obj in s3_bucket.objects.all():
        print obj
`
    
    
                            
   