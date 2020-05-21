#from django.views.decorators.csrf import ensure_csrf_cookie
#from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from plaid import Client
import datetime
import os

plaid_client_id = os.getenv('PLAID_CLIENT_ID')
plaid_public_key = os.getenv('PLAID_PUBLIC_KEY') 
plaid_secret = os.getenv('PLAID_SECRET')
plaid_environment = os.getenv('PLAID_ENV', 'sandbox')

def get_plaid_client():
    return Client(client_id=plaid_client_id,
                  secret=plaid_secret,
                  public_key=plaid_public_key,
                  environment=plaid_environment)

# Global access token (workaround to make this demo simple)
# Should be stored in a database that relates access token to user account
access_token = None


def index(request):
    return render(request, 'index.html', {'plaid_public_key': plaid_public_key,
                                          'plaid_environment': plaid_environment})

def get_access_token(request):
    global access_token

    public_token = request.POST['public_token']
    client = get_plaid_client()
    exchange_response = client.Item.public_token.exchange(public_token)
    access_token = exchange_response['access_token']
    
    return JsonResponse(exchange_response)

def set_access_token(request):
    global access_token

    access_token = request.POST['access_token']

    return JsonResponse({'error': False})

def accounts(request):
    global access_token
    client = get_plaid_client()
    accounts = client.Auth.get(access_token)
    return JsonResponse(accounts)

def item(request):
    global access_token
    client = get_plaid_client()
    item_response = client.Item.get(access_token)
    institution_response = client.Institutions.get_by_id(item_response['item']['institution_id'])
    return JsonResponse({'item': item_response['item'],
                         'institution': institution_response['institution']})

def transactions(request):
    global access_token
    client = get_plaid_client()
    start_date = "{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(-30))
    end_date = "{:%Y-%m-%d}".format(datetime.datetime.now())
    response = client.Transactions.get(access_token, start_date, end_date)
    return JsonResponse(response)

def create_public_token(request):
    global access_token
    client = get_plaid_client()
    response = client.Item.public_token.create(access_token)
    return JsonResponse(response)
