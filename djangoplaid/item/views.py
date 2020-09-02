from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404, get_list_or_404
from django.contrib import messages
from django.conf import settings
from item import plaid_client
from plaid.errors import PlaidError
from .models import PlaidItem, PlaidAccount, PlaidTransaction
from .forms import TransactionRangeForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from typing import Dict, List
import json


# Create your views here.
@login_required
def link_form(request):
    response = {}
    try:
        response = plaid_client.LinkToken.create({
            'user': {
                'client_user_id': str(request.user.id)
            },
            'client_name': "DjangoPlaid",
            'products': settings.PLAID_PRODUCTS,
            'country_codes': settings.PLAID_COUNTRY_CODES,
            'language': "en",
            'redirect_uri': settings.PLAID_REDIRECT_URI,
        })
    except PlaidError as e:
        messages.error(request, message=e.display_message)
    finally:
        return render(request, 'item/create_item.html', {
            'link_token': response.get('link_token', ''),
        })


@login_required
def get_access_token(request):
    if request.method == 'POST':
        try:
            token_response = plaid_client.Item.public_token.exchange(request.POST['public_token'])
        except PlaidError as e:
            messages.error(request, message=e.display_message)
            return render(request, 'item/create_item.html')
        institution_data = json.loads(request.POST['institution'])
        accounts_data = json.loads(request.POST['accounts'])
        new_item = create_item(token_response, institution_data, request.user.id)
        add_accounts_for_item(new_item.id, accounts_data)
        return HttpResponseRedirect(reverse('plaid_items:institution_list'))


@login_required
def institution_list(request):
    items = PlaidItem.objects.filter(user_id=request.user.id)
    return render(request, 'item/institution_list.html', {
        'items': items
    })


@login_required
def account_list(request, item_id: int = None):
    if item_id is None:
        accounts = get_list_or_404(PlaidAccount, item__user_id=request.user.id)
    else:
        accounts = get_object_or_404(PlaidItem, id=item_id).accounts.all()
    return render(request, 'item/account_list.html', {
        'accounts': accounts,
    })


@login_required
def account_detail(request, account_pk: int):
    account = get_object_or_404(PlaidAccount,
                                id=account_pk,
                                link__user_id=request.user.id)
    plaid_client.Transactions.get(account_ids=[account.account_id])
    return render(request, 'item/account_detail.html', {
        'account': account,
    })


@login_required
def account_statistic_form(request):
    accounts = PlaidAccount.objects.filter(item__user_id=request.user.id).values_list('id', 'name')
    form = TransactionRangeForm(account_choices=accounts)
    if request.method == 'POST':
        form = TransactionRangeForm(account_choices=accounts, data=request.POST)
        if form.is_valid():
            # do stats
            cd = form.cleaned_data
            account = PlaidAccount.objects.get(id=int(cd['account']), item__user_id=request.user.id)
            start_date = str(cd['start_date'])
            end_date = str(datetime.now().date())
            transaction_response = plaid_client.Transactions.get(
                account_ids=[account.account_id],
                access_token=account.item.access_token,
                start_date=start_date,
                end_date=end_date,
            )
            current_balance = transaction_response['accounts'][0]['balances']['current']
            available_balance = transaction_response['accounts'][0]['balances']['available']
            total_transactions = transaction_response['total_transactions']
            transactions = transaction_response['transactions']
            average_balance = get_average_balance(current_balance, transactions)
            new_transactions = []
            for transaction in transactions:
                new_transactions.append(PlaidTransaction(
                    name=transaction['name'],
                    date=transaction['date'],
                    amount=transaction['amount']
                ))
            return render(request, "item/transaction_stats.html", {
                'current_balance': current_balance,
                'available_balance': available_balance,
                'total_transactions': total_transactions,
                'transactions': new_transactions,
                'average_balance': average_balance,
                'start_date': start_date,
                'end_date': end_date,
            })
    return render(request, "item/transaction_stats.html", {
        'form': form,
    })


def create_item(token_response, institution_data, user_id: int):
    new_item = PlaidItem(
        item_id=token_response['item_id'],
        access_token=token_response['access_token'],
        user_id=user_id,
        institution_name=institution_data['name'],
        institution_id=institution_data['institution_id']
    )
    new_item.save()
    return new_item


def add_accounts_for_item(item_id: int, account_data) -> List[PlaidAccount]:
    new_accounts = [build_account(account, item_id) for account in account_data]
    PlaidAccount.objects.bulk_create(new_accounts)
    return new_accounts


def get_average_balance(current_balance, transactions):
    balance = current_balance
    transactions.sort(key=lambda x: x['date'], reverse=True)
    balances = [current_balance]
    for transaction in transactions:
        balance += transaction['amount']
        balances.append(balance)
    return sum(balances) / len(balances)


def build_account(account_data: Dict, item_id: int) -> PlaidAccount:
    new_account = PlaidAccount(
        account_id=account_data['id'],
        name=account_data['name'],
        official_name=account_data.get('official_name'),
        type=account_data['type'],
        subtype=account_data['subtype'],
        item_id=item_id,
        mask=account_data['mask'],
    )
    return new_account
