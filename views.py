import json
from http.client import responses
from os import access

import requests
import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import redirect
from django.conf import settings
from django.utils.dateparse import parse_datetime

from integration.constants.url_constants import RETRIEVE_ALL_COMPANIES, RETRIEVE_ALL_CONTACTS, TOKEN_URL, \
    RETRIEVE_ALL_DEALS, RETRIEVE_ALL_LIST_ITEMS, RETRIEVE_ALL_PRODUCTS, COMPANY_CURRENCY, COMPANIES_TO_CONTACTS, \
    COMPANIES_TO_DEALS, CONTACTS_TO_DEALS, DEALS_TO_LINE_ITEMS, USER_API, USER_PROVISIONING_API

from integration.models import HubSpotUser, Company, Contact, Deal, Product, ListItem


def calculate_expiration_date(seconds_until_expiration):
    """
    Calculates the expiration date and time based on the number of seconds until expiration.

    :param seconds_until_expiration: The number of seconds from the current time until expiration.
    :return: A datetime object representing the expiration date and time.
    """
    current_time = datetime.datetime.now()
    expiration_time = current_time + datetime.timedelta(seconds=seconds_until_expiration)
    return expiration_time

@api_view(['GET'])
def auth(request):
    """
    Function to initiate the HubSpot OAuth authorization process.
    :param request: The incoming HTTP GET request.
    :return:
        - A redirection to the HubSpot authorization URL where the user can grant permissions.
    """

    auth_base_url = "https://app.hubspot.com/oauth/authorize"
    client_id = settings.HUBSPOT_CLIENT_ID
    redirect_uri = settings.HUBSPOT_REDIRECT_URI

    # List of scopes for easy readability and future modifications
    scopes = [
        "oauth",
        "crm.objects.users.read",
        "settings.currencies.read",
        "crm.objects.companies.read",
        "settings.users.read",
        "crm.objects.deals.read",
        "crm.objects.contacts.read",
    ]

    scopes_param = " ".join(scopes)

    auth_url = (
        f"{auth_base_url}"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scopes_param}"
    )

    return redirect(auth_url)

@api_view(['GET'])
def callback(request):
    """
    Function to handle the OAuth callback and exchange the authorization code for an access token.
    :param request: The incoming HTTP GET request containing the authorization code.
    :return: 
        A serialized response object with the following content:
            - On success (status code 200 or 201): A message indicating the user was created or already exists.
            - On error (status code 400 or relevant status code): An error message indicating the reason for failure.
    """
    code = request.GET.get('code')
    if not code:
        return Response("Authorization code not provided.", status=400)

    # Exchange the authorization code for an access token
    payload = {
        'grant_type': 'authorization_code',
        'client_id': settings.HUBSPOT_CLIENT_ID,
        'client_secret': settings.HUBSPOT_CLIENT_SECRET,
        'redirect_uri': settings.HUBSPOT_REDIRECT_URI,
        'code': code
    }
    response = requests.post(TOKEN_URL, data=payload)
    response_data = response.json()

    access_token = response_data.get('access_token')
    settings.HUBSPOT_ACCESS_TOKEN = access_token
    refresh_token = response_data.get('refresh_token')
    user_details = requests.get(f'https://api.hubapi.com/oauth/v1/access-tokens/{access_token}')
    user_details_data = user_details.json()

    hubspot_id = user_details_data.get('user_id')
    user_email = user_details_data.get('user')
    access_token = user_details_data.get('token')
    token_expiration_date = calculate_expiration_date(user_details_data.get('expires_in'))

    if user_details.ok:
        return Response({"response" : "User already exist.", "result" : user_details_data}, status=status.HTTP_200_OK)
    else:
        return Response("User created successfully.", status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_new_access_token(request):

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        'grant_type': 'refresh_token',
        'client_id': settings.HUBSPOT_CLIENT_ID,
        'client_secret': settings.HUBSPOT_CLIENT_SECRET,
        'refresh_token': settings.HUBSPOT_REFRESH_TOKEN,
    }

    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    response_data = response.json()
    new_access_token = response_data.get('access_token')
    new_refresh_token = response_data.get('refresh_token')

    if new_access_token:
        settings.HUBSPOT_ACCESS_TOKEN = new_access_token
        settings.HUBSPOT_REFRESH_TOKEN = new_refresh_token
        return Response(f"Access token: {new_access_token}")
    else:
        return Response(response_data.get('message'), status=400)


@api_view(['GET'])
def get_user_profile(request):
    # Ensure the access token is set
    access_token = settings.HUBSPOT_ACCESS_TOKEN
    if not access_token:
        return Response(response_data.get('message'), status=400)

    # Make an API request to get user profile
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    user_profile_url = "https://api.hubapi.com/owners/v2/owners/me"
    response = requests.get(user_profile_url, headers=headers)
    user_profile = response.json()

    # Return the user profile data
    return Response(user_profile)

@api_view(['GET'])
def get_hubspot_users(request):
    """
    Function to retrieve all users from HubSpot and update the local database.
    :param request: The incoming HTTP GET request.
    :return:
        - On success (status code 200): A list of users retrieved from HubSpot in JSON format.
        - On error (status code 400): An error message if no access token is available.
    """
    access_token = settings.HUBSPOT_ACCESS_TOKEN
    if not access_token:
        return Response("No access token available", status=400)

    properties = [
        "hs_job_title",
        "hs_internal_user_id",
        "hubspot_owner_id"
    ]

    properties_param = ",".join(properties)

    params = {
        'properties': properties_param,
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Fetching users from HubSpot Users API
    try:
        users_response = requests.get(USER_API, headers=headers, params=params)
        users_response.raise_for_status()  # Raise an error for bad responses
        users_data = users_response.json()
    except requests.exceptions.RequestException as e:
        return Response(f"Error fetching users: {str(e)}", status=500)

    # Fetching users from HubSpot User Provisioning API
    try:
        provisioning_response = requests.get(USER_PROVISIONING_API, headers=headers)
        provisioning_response.raise_for_status()
        provisioning_data = provisioning_response.json()
    except requests.exceptions.RequestException as e:
        return Response(f"Error fetching provisioning data: {str(e)}", status=500)

    instances = []

    # Create a mapping of internal user IDs to provisioning data
    provisioning_map = {user['id']: user for user in provisioning_data.get('results', [])}

    # Process the user data from the User API
    for user in users_data.get('results', []):
        internal_user_id = user['properties'].get('hs_internal_user_id')

        # Find the corresponding user in the User Provisioning API
        user_prov_data = provisioning_map.get(internal_user_id)

        # If user provisioning data exists, create a HubSpotUser instance
        if user_prov_data:
            instance = HubSpotUser(
                account_id=user['properties'].get('hs_object_id'),  # Set your account ID here
                internal_user_id=internal_user_id,
                hubspot_owner_id=user['properties'].get('hubspot_owner_id'),
                job_title=user['properties'].get('hs_job_title'),
                email=user_prov_data.get('email'),
                first_name=user_prov_data.get('firstName'),
                last_name=user_prov_data.get('lastName'),
                roles=user_prov_data.get('roleIds', []),
                super_admin=user_prov_data.get('superAdmin', False)
            )
            instances.append(instance)

    # Bulk create or update HubSpotUser instances
    fields = [field.name for field in HubSpotUser._meta.fields if not field.primary_key]
    HubSpotUser.objects.bulk_create(instances, update_conflicts=True, update_fields=fields)

    return Response(provisioning_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_companies(request):
    """
    Function to retrieve all companies from HubSpot and update the local database.
    :param request: The incoming HTTP GET request.
    :return: 
        - On success (status code 200): A list of companies retrieved from HubSpot in JSON format.
        - On error (status code 400): An error message if no access token is available.
    
    This function retrieves companies using the HubSpot API, processes the response, and saves or updates
    company data in the local database using bulk_create with conflict resolution. Existing records are updated
    while new ones are inserted.
    """
    access_token = settings.HUBSPOT_ACCESS_TOKEN
    if not access_token:
        return Response("No access token available", status=400)

    properties = [
        "name",
        "industry",
        "website",
        "address",
        "phone",
        "hs_created_by_user_id",
        "notes_last_updated",
        "notes_last_contacted",
        "hs_analytics_latest_source",
        "hs_lead_status",
        "hubspot_owner_id",
    ]

    properties_param = ",".join(properties)

    params = {
        'properties': properties_param,
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(RETRIEVE_ALL_COMPANIES, headers=headers, params=params)
    companies = response.json()
    instances = []
    for company in companies.get('results', []):
        instance = Company(
            name=company.get('properties', {}).get('name', ''),
            industry=company.get('properties', {}).get('industry', ''),
            website=company.get('properties', {}).get('website', ''),
            address=company.get('properties', {}).get('address', ''),
            phone_number=company.get('properties', {}).get('phone', ''),
            created_date=company.get('properties', {}).get('createdate', ''),
            created_by_user_id=company.get('properties', {}).get('hs_created_by_user_id', ''),
            last_activity_date=company.get('properties', {}).get('notes_last_updated', ''),
            last_contacted=company.get('properties', {}).get('notes_last_contacted', ''),
            latest_source=company.get('properties', {}).get('hs_analytics_latest_source', ''),
            lead_status=company.get('properties', {}).get('hs_lead_status', ''),
            owner=company.get('properties', {}).get('hubspot_owner_id', ''),
            record_id=company.get('properties', {}).get('hs_object_id', ''),
            archived=company.get('archived'),
        )
        instances.append(instance)
    fields = [field.name for field in Company._meta.fields if not field.primary_key]

    Company.objects.bulk_create(instances, update_conflicts=True, update_fields=fields)
    return Response(companies, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_contacts(request):
    """
    Function to retrieve all contacts from HubSpot and update the local database.
    :param request: The incoming HTTP GET request.
    :return:
        - On success (status code 200): A message indicating the contacts were saved successfully, along with the retrieved contact data.
        - On error (status code 400): An error message if no access token is available.
    
    This function retrieves contacts using the HubSpot API, processes the response, and saves or updates
    contact data in the local database using bulk_create with conflict resolution. Existing records are updated
    while new ones are inserted.
    """
    access_token = settings.HUBSPOT_ACCESS_TOKEN
    if not access_token:
        return Response(response_data.get('message'), status=400)

    properties = [
        "email",
        "firstname",
        "lastname",
        "hubspot_owner_id",
        "hs_created_by_user_id",
        "hs_lead_status",
        "hs_object_source_label"
    ]

    associations = [
        "companies",
    ]

    properties_param = ",".join(properties)
    associations_param = ",".join(associations)

    params = {
        'properties': properties_param,
        'associations': associations_param,
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(RETRIEVE_ALL_CONTACTS, headers=headers, params=params)
    contacts = response.json()
    instances = []
    for contact in contacts.get('results', []):
        instance, created = Contact.objects.get_or_create(
            record_id=contact.get('properties', {}).get('hs_object_id', ''),
            # Use record_id or another unique identifier
            defaults={
                'email': contact.get('properties', {}).get('email', ''),
                'first_name': contact.get('properties', {}).get('firstname', ''),
                'last_name': contact.get('properties', {}).get('lastname', ''),
                'contact_owner': contact.get('properties', {}).get('hubspot_owner_id', ''),
                'created_date': contact.get('properties', {}).get('createdate', ''),
                'created_by_user_id': contact.get('properties', {}).get('hs_created_by_user_id', ''),
                'last_modified_date': contact.get('properties', {}).get('lastmodifieddate', ''),
                'lead_status': contact.get('properties', {}).get('hs_lead_status', ''),
                'record_source': contact.get('properties', {}).get('hs_object_source_label', ''),
                'archived': contact.get('archived', False),
            }
        )

        if not created:
            instance.email = contact.get('properties', {}).get('email', '')
            instance.first_name = contact.get('properties', {}).get('firstname', '')
            instance.last_name = contact.get('properties', {}).get('lastname', '')
            instance.contact_owner = contact.get('properties', {}).get('hubspot_owner_id', '')
            instance.created_date = contact.get('properties', {}).get('createdate', '')
            instance.created_by_user_id = contact.get('properties', {}).get('hs_created_by_user_id', '')
            instance.last_modified_date = contact.get('properties', {}).get('lastmodifieddate', '')
            instance.lead_status = contact.get('properties', {}).get('hs_lead_status', '')
            instance.record_source = contact.get('properties', {}).get('hs_object_source_label', '')
            instance.archived = contact.get('archived', False)
            instance.save()

        company_ids = [
            company.get('id') for company in contact.get('associations', {}).get('companies', {}).get('results', [])
        ]

        if company_ids:
            companies = Company.objects.filter(record_id__in=company_ids)
            instance.company.set(companies)

        instances.append(instance)

    fields = [field.name for field in Contact._meta.fields if not field.primary_key]

    Contact.objects.bulk_create(instances, update_conflicts=True, update_fields=fields)
    return Response(contacts, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_deals(request):
    """
    Function to retrieve all deals from HubSpot and update the local database, including associations
    with Company and Contact models.
    :param request: The incoming HTTP GET request.
    :return:
        - On success (status code 200): A message indicating that deals were saved successfully, along with the deal data.
        - On error (status code 400): An error message if no access token is available.
    """
    access_token = settings.HUBSPOT_ACCESS_TOKEN
    if not access_token:
        return Response("No access token available", status=400)

    properties = [
        'dealname',
        'description',
        'amount',
        'hs_acv',
        'hs_arr',
        'hs_mrr',
        'closedate',
        'hs_created_by_user_id',
        'dealstage',
        'dealtype',
        'hs_manual_forecast_category',
        'hs_forecast_probability',
        'hubspot_owner_id',
        'pipeline',
        'hs_object_source_label',
        'hs_tcv',
        'hs_analytics_latest_source',
        'deal_currency_code',
        'amount_in_home_currency',
        'hs_closed_amount'
    ]

    associations = [
        "company",
        "contact",
    ]

    properties_param = ",".join(properties)
    associations_param = ",".join(associations)

    params = {
        'properties': properties_param,
        'associations': associations_param,
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(RETRIEVE_ALL_DEALS, headers=headers, params=params)
    deals = response.json()
    instances = []

    for deal in deals.get('results', []):
        instance, created = Deal.objects.get_or_create(
            record_id=deal.get('properties', {}).get('hs_object_id', None),
            defaults={
                'deal_name': deal.get('properties', {}).get('dealname', ''),
                'deal_description': deal.get('properties', {}).get('description', ''),
                'amount': deal.get('properties', {}).get('amount', 0.00) or 0.00,
                'annual_contract_value': deal.get('properties', {}).get('hs_acv', 0.00) or 0.00,
                'annual_recurring_revenue': deal.get('properties', {}).get('hs_arr', 0.00) or 0.00,
                'monthly_recurring_revenue': deal.get('properties', {}).get('hs_mrr', 0.00) or 0.00,
                'close_date': parse_datetime(deal.get('properties', {}).get('closedate')),
                'created_date': deal.get('properties', {}).get('createdate', ''),
                'created_by_user_id': deal.get('properties', {}).get('hs_created_by_user_id', None),
                'currency': deal.get('properties', {}).get('deal_currency_code', ''),
                'deal_stage': deal.get('properties', {}).get('dealstage', ''),
                'deal_type': deal.get('properties', {}).get('dealtype', ''),
                'forecast_category': deal.get('properties', {}).get('hs_manual_forecast_category', ''),
                'forecast_probability': deal.get('properties', {}).get('hs_forecast_probability', 0.00) or 0.00,
                'last_modified_date': deal.get('properties', {}).get('hs_lastmodifieddate'),
                'owner': deal.get('properties', {}).get('hubspot_owner_id', None),
                'pipeline': deal.get('properties', {}).get('pipeline', ''),
                'record_source': deal.get('properties', {}).get('hs_object_source_label', ''),
                'total_contract_value': deal.get('properties', {}).get('hs_tcv', 0.00) or 0.00,
                'latest_source': deal.get('properties', {}).get('hs_analytics_latest_source', ''),
                'closed_amount': deal.get('properties', {}).get('hs_closed_amount', 0.00) or 0.00,
                'archived': deal.get('archived', False),
            }
        )

        if not created:
            instance.deal_name = deal.get('properties', {}).get('dealname', '')
            instance.deal_description = deal.get('properties', {}).get('description', '')
            instance.amount = deal.get('properties', {}).get('amount', 0.00) or 0.00
            instance.annual_contract_value = deal.get('properties', {}).get('hs_acv', 0.00) or 0.00
            instance.annual_recurring_revenue = deal.get('properties', {}).get('hs_arr', 0.00) or 0.00
            instance.monthly_recurring_revenue = deal.get('properties', {}).get('hs_mrr', 0.00) or 0.00
            instance.close_date = parse_datetime(deal.get('properties', {}).get('closedate'))
            instance.created_date = deal.get('properties', {}).get('createdate', '')
            instance.created_by_user_id = deal.get('properties', {}).get('hs_created_by_user_id', None)
            instance.currency = deal.get('properties', {}).get('deal_currency_code', '')
            instance.deal_stage = deal.get('properties', {}).get('dealstage', '')
            instance.deal_type = deal.get('properties', {}).get('dealtype', '')
            instance.forecast_category = deal.get('properties', {}).get('hs_manual_forecast_category', '')
            instance.forecast_probability = deal.get('properties', {}).get('hs_forecast_probability', 0.00) or 0.00
            instance.last_modified_date = deal.get('properties', {}).get('hs_lastmodifieddate')
            instance.owner = deal.get('properties', {}).get('hubspot_owner_id', None)
            instance.pipeline = deal.get('properties', {}).get('pipeline', '')
            instance.record_source = deal.get('properties', {}).get('hs_object_source_label', '')
            instance.total_contract_value = deal.get('properties', {}).get('hs_tcv', 0.00) or 0.00
            instance.latest_source = deal.get('properties', {}).get('hs_analytics_latest_source', '')
            instance.deal_status = deal.get('properties', {}).get('dealstatus', '')
            instance.closed_amount = deal.get('properties', {}).get('closed_amount', 0.00) or 0.00
            instance.archived = deal.get('archived', False)
            instance.save()

        company_ids = [
            company.get('id') for company in deal.get('associations', {}).get('companies', {}).get('results', [])
        ]
        if company_ids:
            company = Company.objects.filter(record_id__in=company_ids)
            instance.company.set(company)

        contact_ids = [
            contact.get('id') for contact in deal.get('associations', {}).get('contacts', {}).get('results', [])
        ]
        if contact_ids:
            contact = Contact.objects.filter(record_id__in=contact_ids)
            instance.contact.set(contact)

        instances.append(instance)

    fields = [field.name for field in Deal._meta.fields if not field.primary_key]

    Deal.objects.bulk_create(instances, update_conflicts=True, update_fields=fields)
    return Response(deals, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_products(request):
    """
    Function to retrieve all products from HubSpot and update the local database.
    :param request: The incoming HTTP GET request.
    :return: 
        - On success (status code 200): A message indicating that products were saved successfully, along with the product data.
        - On error (status code 400): An error message if no access token is available.
    
    This function retrieves product information from HubSpot, processes it, and saves or updates product data in the local
    database using bulk_create with conflict resolution.
    """
    access_token = settings.HUBSPOT_ACCESS_TOKEN
    if not access_token:
        return Response("No access token available", status=400)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(RETRIEVE_ALL_PRODUCTS, headers=headers)
    products = response.json()
    instances = []
    for product in products.get('results', []):
        instance = Product(
            hubspot_id=product.get('id'),
            name=product.get('properties', {}).get('name', ''),
            description=product.get('properties', {}).get('description', ''),
            price=product.get('properties', {}).get('price', ''),
            created_at=parse_datetime(product.get('createdAt')),
            updated_at=parse_datetime(product.get('updatedAt')),
            archived=product.get('archived'),
        )
        instances.append(instance)
    fields = [field.name for field in Product._meta.fields if not field.primary_key]

    Product.objects.bulk_create(instances, update_conflicts=True, update_fields=fields)
    return Response({'message': 'Products saved successfully', 'results': products}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_list_items(request):
    """
    Function to retrieve all list items (line items) from HubSpot and update the local database.
    :param request: The incoming HTTP GET request.
    :return: 
        - On success (status code 200): A message indicating that list items were saved successfully, along with the list item data.
        - On error (status code 400): An error message if no access token is available.
    
    This function retrieves list items from HubSpot, processes them, and saves or updates list item data in the local
    database using bulk_create with conflict resolution.
    """
    access_token = settings.HUBSPOT_ACCESS_TOKEN
    if not access_token:
        return Response("No access token available", status=400)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(RETRIEVE_ALL_LIST_ITEMS, headers=headers)
    list_items = response.json()
    instances = []
    for list_item in list_items.get('results', []):
        instance = ListItem(
            hubspot_id=list_item.get('id'),
            amount=list_item.get('properties', {}).get('amount', ''),
            quantity=list_item.get('properties', {}).get('quantity', ''),
            product=Product.objects.filter(hubspot_id=list_item.get('properties', {}).get('hs_product_id', '')).first(),
            created_at=parse_datetime(list_item.get('createdAt')),
            updated_at=parse_datetime(list_item.get('updatedAt')),
            archived=list_item.get('archived'),
        )
        instances.append(instance)

    fields = [field.name for field in ListItem._meta.fields if not field.primary_key]

    ListItem.objects.bulk_create(instances, update_conflicts=True, update_fields=fields)
    return Response({'message': 'Products saved successfully', 'results': list_items}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_company_currency(request):
    """
    Function to retrieve company currency data from HubSpot.
    :param request: The incoming HTTP GET request.
    :return:
        - On success (status code 200): The company currency data in JSON format.
        - On error (status code 404): A message indicating that the currency data was not found.
        - On error (status code 400): An error message if no access token is available.
    
    This function retrieves currency information related to companies from HubSpot and returns it in the response.
    """
    access_token = settings.HUBSPOT_ACCESS_TOKEN
    if not access_token:
        return Response("No access token available", status=400)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(COMPANY_CURRENCY, headers=headers)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return  Response(response.status_code, status=status.HTTP_404_NOT_FOUND)
    else:
        currency = response.json()
        return Response(currency, status=status.HTTP_200_OK)

@api_view(['POST'])
def webhook_handler(request):
    """
    Function to handle webhook events sent by HubSpot.
    :param request: The incoming HTTP POST request containing webhook data.
    :return: A response with the received data and a status code of 200.
    
    This function handles incoming webhook requests, processes the data, and prints it for debugging purposes.
    """
    data = json.loads(request.body)
    print(data)
    return Response(data, status=status.HTTP_200_OK)