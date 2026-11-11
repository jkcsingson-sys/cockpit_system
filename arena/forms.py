from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
  signature_data = forms.CharField(
      widget=forms.HiddenInput(), required=False
  )

  class Meta:
    model = Transaction
    fields = [
        'teller',
        'fight_number',
        'transaction_type',
        'amount',
        'photo',
    ]
    widgets = {
        'teller': forms.Select(attrs={'class': 'form-select form-select-lg'}),
        'fight_number': forms.NumberInput(
            attrs={'class': 'form-control form-control-lg', 'min': '1'}
        ),
        'transaction_type': forms.Select(
            attrs={'class': 'form-select form-select-lg'}
        ),
        'amount': forms.NumberInput(
            attrs={'class': 'form-control form-control-lg', 'step': '0.01'}
        ),
        'photo': forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'capture': 'environment',
            }
        ),
    }