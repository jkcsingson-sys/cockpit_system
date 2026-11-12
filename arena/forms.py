from django import forms
from django.core.exceptions import ValidationError
from .models import Transaction


class TransactionForm(forms.ModelForm):
    signature_data = forms.CharField(required=True, widget=forms.HiddenInput())

    class Meta:
        model = Transaction
        fields = ['teller', 'transaction_type', 'amount', 'photo']
        widgets = {
            'teller': forms.Select(attrs={'class': 'form-select'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '5000', 
                'max': '50000', 
                'step': '0.01'
            }),
            # Updated photo widget: 'accept="image/*"' allows image filtering, 
            # and removing strict capture attributes lets Android/iOS present 
            # the native device menu for both Camera and Gallery.
            'photo': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': 'image/*', 
                'required': 'true'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photo'].required = True
        self.fields['teller'].required = True
        self.fields['transaction_type'].required = True
        self.fields['amount'].required = True

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None:
            if amount < 5000 or amount > 50000:
                raise ValidationError("Amount must be between ₱5,000 and ₱50,000.")
        return amount