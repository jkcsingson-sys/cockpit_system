from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    signature_data = forms.CharField(required=True)

    class Meta:
        model = Transaction
        fields = ['teller', 'fight_number', 'transaction_type', 'amount', 'photo']
        widgets = {
            'teller': forms.Select(attrs={'class': 'form-select'}),
            'fight_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'required': 'true'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photo'].required = True
        self.fields['teller'].required = True
        self.fields['fight_number'].required = True
        self.fields['transaction_type'].required = True
        self.fields['amount'].required = True