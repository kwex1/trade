from django.contrib.auth.forms import UserCreationForm
from .models import User
from . models import Payment
from django import forms

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'country', 'mobile_number', 'password1', 'password2')

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields = ('mobile_number', 'usdt_trc20_wallet_address','eth_wallet_address', 'btc_wallet_address')

class DepositForm(forms.ModelForm):
    class Meta:
        model=Payment
        fields= ('user','payment_option', 'amount', 'memo')