## LoginWithCognito

In many cases, we run into an issue where a client application running on users machine needs to access
 AWS services. Here, the client application needs to pass AWS credentials (access key and secret) while accessing
 the services. However, those long lasting AWS credentials are TOO DANGEROUS to hard code in the client application.
  This problem is simpler to solve, if the client application is running on a web browser, or Android or iOS, AWS does 
 provide very nice SDK's that provide temporary credentials. See these AWS documentation for getting temporary 
 credentials and accessing AWS services.  https://aws-amplify.github.io/docs/js/authentication  
    However, if the client app is NOT running on a web browser or Android or iOS, AWS yet does not have 
    a straight forward way to provide secure authentication and authorization. 
     So, I had to dig deeper and stitch some lower level APIs to make this temporary credentials working 
     for Python. The LoginWithCognito library is built to help a client application that wants
      to access AWS services. This library assumes that the client application already has a user known 
      to the AWS Cognito user pool.

### To run the sample code
1. On any machine where Python 2.7 is installed. Run:
`python main.py <user_name> <password>`

### How to configure AWS Cognito that will provide temporary credentials to the client app?
(This section is for AWS admin)
1. On the AWS console, open Cognito service and create a user pool. For details follow only the step one of this AWS 
doc  https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pool-as-user-directory.html. 
2. Create a user account in the user pool.
3. Create a client id in the same user pool.
4. Go to Cognito Federated Identities and create an identity pool. This will automatically create an IAM role or you can
 specify an existing IAM role. 
5. When the identity pool creation is done, go to edit identity pool.
6. Expand the authentication providers section and select Cognito. 
7. In the authentication providers section put the user pool id and app id you created in the above steps. This means 
your identity pool will allow users known to your user pool. Here we are using Cognito user pool as a third party 
identity provider. You may also choose Amazon.com, Facebook.com, Goggle.com etc, if you prefer.
8. Create an S3 bucket  and upload some sample files there, so that the attached example code can list the content of 
the bucket.
9. Collect the aws region, user pool id, client id, identity pool id and bucket name and fill in the environment.py 
file attached. Then, you should be able to run the main.py file from any machine.


### How to use the LoginWithCognito library?
(This section is for the app developer)
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
    
   




    
                            
   