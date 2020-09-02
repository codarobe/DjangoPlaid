from django.conf import settings
import plaid

plaid_client = plaid.Client(client_id=settings.PLAID_CLIENT_ID,
                            secret=settings.PLAID_CLIENT_SECRET,
                            environment=settings.PLAID_ENVIRONMENT,
                            api_version='2019-05-29')
