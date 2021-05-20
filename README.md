# DjangoPlaid
A repository for experimenting with Plaid using Django

This project is built with Python3.

## To run
1. Start by installing the packages contained in requirements.txt with pip.
2. Configure environment variables for PLAID_CLIENT_ID and PLAID_CLIENT_SECRET (these values can be obtained through the Plaid developer portal)
3. ```python manage.py migrate```
4. ```python manage.py run server```
5. Navigate to http://localhost:8000 and create a user or log in.

## Features
This proof of concept application demonstrates linking Plaid accounts to users, displaying linked accounts by institution linked, fetching transactions over a date range, and performing basic balance calculations given a list of transactions.
