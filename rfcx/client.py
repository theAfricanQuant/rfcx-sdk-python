import getpass
import datetime
from os import path
import rfcx._pkce as pkce
import rfcx._api_rfcx as api_rfcx
import rfcx._api_auth as api_auth
from rfcx._credentials import Credentials

class Client(object):
    """Authenticate and perform requests against the RFCx platform"""

    def __init__(self):
        self.credentials = None
        self.default_site = None
        self.accessible_sites = None
        self.persisted_credentials_path = '.rfcx_credentials'

    def authenticate(self, persist=True):
        """Authenticate an RFCx user to obtain a token

        Returns:
            Success if an access_token was obtained
        """

        if self.credentials != None:
            print('Already authenticated')
            return

        access_token = None

        # Attempt to load the credentials from disk
        if path.exists(self.persisted_credentials_path):
            with open(self.persisted_credentials_path, 'r') as f:
                lines = f.read().splitlines()
            print(lines)
            if len(lines) == 5 and lines[0] == 'version 1':
                token_expiry = datetime.datetime.strptime(lines[3], "%Y-%m-%dT%H:%M:%S.%fZ")
                self._setup_credentials(lines[1], lines[2], token_expiry, lines[4])
                print('Using persisted authenticatation')
                return

        # Create a Code Verifier & Challenge
        code_verifier = pkce.code_verifier()
        code_challenge = pkce.code_challenge(code_verifier)

        # See: https://auth0.com/docs/integrations/using-auth0-to-secure-a-cli
        url = 'https://auth.rfcx.org/authorize?response_type=code&code_challenge={0}&code_challenge_method=S256&client_id={1}&redirect_uri={2}&audience=https://rfcx.org&scope={3}'
        client_id = 'LS4dJlP8J2iOBr2snzm6N8I5u7FLSUGd'
        redirect_uri = 'https://rfcx-app.s3.eu-west-1.amazonaws.com/login/cli.html' # TODO move to configuration
        scope = 'openid%20profile'

        # Prompt the user to open their browser. On completion, paste the auth code.
        print('Go to this URL in a browser: ' + url.format(code_challenge, client_id, redirect_uri, scope))
        code = getpass.getpass('Enter your authorization code: ')

        # Perform the exchange
        access_token, refresh_token, token_expiry, id_token = api_auth.authcode_exchange(code.strip(), code_verifier, client_id, scope)
        self._setup_credentials(access_token, refresh_token, token_expiry, id_token)
        
        print('Successfully authenticated')
        print('Default site:', self.default_site)
        print('Accessible sites:', self.accessible_sites)

        # Write token to disk
        if persist:
            with open(self.persisted_credentials_path, 'w') as f:
                f.write('version 1\n')
                f.write(access_token + '\n' + (refresh_token if refresh_token != None else '') + '\n' + token_expiry.isoformat() + 'Z\n' + id_token + '\n')

    def _setup_credentials(self, access_token, token_expiry, refresh_token, id_token):
        self.credentials = Credentials(access_token, token_expiry, refresh_token, id_token)
        app_meta = self.credentials.id_object['https://rfcx.org/app_metadata']
        if app_meta:
            self.accessible_sites = app_meta['accessibleSites']
            self.default_site = app_meta['defaultSite']

    def guardians(self, sites=None):
        """Retrieve a list of guardians from a site (TO BE DEPRECATED - use streams in future)
        
        Args:
            sites: List of site shortnames (e.g. cerroblanco). Default (None) gets all your accessible sites.

        Returns:
            List of guardians"""

        if sites == None:
            sites = self.accessible_sites

        return api_rfcx.guardians(self.credentials.id_token, sites)

    def tags(self, type, labels=None, start=None, end=None, sites=None, limit=1000):
        """Retrieve tags (annotations or confirmed/rejected reviews) from the RFCx API
        
        Args:
            type: (Required) Type of tag. Must be either: annotation, inference, inference:confirmed, or inference:rejected
            labels: List of labels. If None then returns tags of any label.
            start: Minimum timestamp of the annotations to be returned. If None then defaults to exactly 30 days ago.
            end: Maximum timestamp of the annotations. If None then defaults to now.
            sites: List of sites by shortname. If None then returns tags from any site.
            limit: Maximum results to return. Defaults to 1000. (TODO check if there is an upper limit on the API)

        Returns:
            List of tags
        """
        if self.credentials == None:
            print('Not authenticated')
            return

        if type not in ['annotation', 'inference', 'inference:confirmed', 'inference:rejected']:
            print('Unrecognized type')
            return

        if start == None:
            start = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).replace(microsecond=0).isoformat() + 'Z'
        if end == None:
            end = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
        
        return api_rfcx.tags(self.credentials.id_token, type, labels, start, end, sites, limit)
