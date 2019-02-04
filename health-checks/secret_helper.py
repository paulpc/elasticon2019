import json
from azure.keyvault import KeyVaultClient, KeyVaultAuthentication
from azure.common.credentials import ServicePrincipalCredentials

class SecretHelper():
    """helper class to retrieve credentials from Azure Key Valut"""
    def __init__(self, client_id, secret, tenant, resource):
        """Initialize the connection to Key Vault"""
        credentials = ServicePrincipalCredentials(
            client_id = client_id,
            secret = secret,
            tenant = tenant,
            resource = resource
        )
        self.client = KeyVaultClient(credentials)

    def get_secret(self, vault_base_url, secret_name, secret_version=""):
        """get a secret from Azure Key Vault"""
        secret_bundle = self.client.get_secret(vault_base_url=vault_base_url, secret_name=secret_name, secret_version=secret_version)
        return secret_bundle

    def get_secret_json(self, vault_base_url, secret_name, secret_version=""):
        """get a secret from Azure Key Vault and return it as parsed json""" 
        secret_bundle = self.client.get_secret(vault_base_url=vault_base_url, secret_name=secret_name, secret_version=secret_version)
        return json.loads(secret_bundle.value)