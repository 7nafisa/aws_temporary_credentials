import boto3
from aws_requests_auth.boto_utils import AWSRequestsAuth
from warrant.aws_srp import AWSSRP

role_session_name = 'my_app_session'
temp_credential_duration = 3600  # seconds or one hour


class LoginWithCognito:

    def __init__(self, environment):
        """
        With the help of AWS Cognito this module helps a python program running outside of the AWS account to access
        AWS services with temporary AWS credentials. In order to use this module, an end user needs to provide
        username/password corresponding to an active account in the Cognito user pool. In practical terms, this means
        that the user needs to have an account for the TEE19 Monitoring UI at https://www.fd19.sports.intel.com and
        have logged in to it at least once to change the temporary initial password.
        :param environment: the deployment environment name: either DEV, TEST or PROD
        """
        self.aws_region = environment['aws_region']
        self.identity_pool_id = environment['identity_pool_id']
        self.user_pool_id = environment['user_pool_id']
        self.client_id = environment['client_id']
        self.role_arn = environment['role_arn']

    def _retrieve_tokens(self, user_name, password):
        """
        With the exchange of username and password this function retrieves an identity token.
        :param user_name: user_name as appears in the user pool
        :param password: password as set by the user after passing the password challenge
        :return: a dictionary with identity token and refresh token
        """
        client = boto3.client('cognito-idp')
        try:
            aws_srp = AWSSRP(user_name, password, self.user_pool_id, self.client_id, client=None)
            result = aws_srp.authenticate_user()
            id_token = result['AuthenticationResult']['IdToken']
            refresh_token = result['AuthenticationResult']['RefreshToken']
            return {'id_token': id_token, 'refresh_token': refresh_token}
        except (client.exceptions.NotAuthorizedException, client.exceptions.UserNotFoundException):
            raise LoginWithCognitoException('Could not get identity token from Cognito user pool. Are you sure the '
                                            'user account exists in the Cognito user pool and the password is '
                                            'valid? Please test your user account by logging into the '
                                            'monitoring tool. https://www.fd19.sports.intel.com/')

    def _retrieve_credentials(self, id_token, duration):
        """
        Using an identity token from the user pool and AWS identity pool service, this function retrieves a set of
        temporary AWS credentials, that can be used to access AWS services.
        :param id_token: identity token from user pool
        :param duration: temporary credentials duration.
        :return: a set of temporary AWS credentials
        """
        identity_client = boto3.client('cognito-identity')
        response = identity_client.get_id(IdentityPoolId=self.identity_pool_id)  # Get an temp id generated for the user
        identity_id = response['IdentityId']

        login_dictionary = {
            'cognito-idp.' + self.aws_region + '.amazonaws.com/' + self.user_pool_id: str(id_token)
        }

        response = identity_client.get_open_id_token(IdentityId=identity_id, Logins=login_dictionary)
        open_id_token = response['Token']

        sts_client = boto3.client('sts')
        response = sts_client.assume_role_with_web_identity(RoleArn=self.role_arn,
                                                            RoleSessionName=role_session_name,
                                                            WebIdentityToken=open_id_token,
                                                            DurationSeconds=duration)

        temp_credentials = {'temp_access_key_id': response['Credentials']['AccessKeyId'],
                            'temp_secret_key': response['Credentials']['SecretAccessKey'],
                            'temp_session_token': response['Credentials']['SessionToken'],
                            'expiration': response['Credentials']['Expiration']}
        return temp_credentials

    def get_auth_signer(self, credentials, hostname, aws_service_name):
        """
        To get an authorization to call a certain services hosted in the AWS.
        :param credentials a set of aws credentials
        :param hostname: Where the desired service is hosted.
        :param aws_service_name: A name of the desired service name.
        :return: An aws auth signer
        """
        signer = AWSRequestsAuth(aws_access_key=credentials['temp_access_key_id'],
                                 aws_secret_access_key=credentials['temp_secret_key'],
                                 aws_host=hostname,
                                 aws_region=self.aws_region,
                                 aws_service=aws_service_name,
                                 aws_token=credentials['temp_session_token'])
        return signer

    def get_temporary_credentials(self, username, password, duration=temp_credential_duration):
        """
        To get a set of temporary credentials, this function uses username and password. These credentials will expire
        in twelve hours.
        :param username: as appears in the Cognito user pool
        :param password: as stored in the Cognito user pool
        :param duration: temporary credentials duration, Default is one hour.
        :return: a dictionary of temporary aws access key id, secret and session token.
        """
        tokens = self._retrieve_tokens(username, password)
        temp_credentials = self._retrieve_credentials(tokens['id_token'], duration=duration)
        return temp_credentials


class LoginWithCognitoException(Exception):
    def __init__(self, message):
        super(Exception)
        print 'Error: ', message
