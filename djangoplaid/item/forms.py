from django import forms
from datetime import datetime, date


class TransactionRangeForm(forms.Form):
    account = forms.ChoiceField()
    start_date = forms.DateField(initial=datetime.now().date())

    def clean_start_date(self):
        cd = self.cleaned_data
        if cd['start_date'] > datetime.now().date():
            raise forms.ValidationError('Start Date cannot be in the future.')
        return cd['start_date']

    def __init__(self, account_choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].choices = account_choices
