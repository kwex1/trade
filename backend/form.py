from django.contrib.auth.forms import UserCreationForm
from .models import User
from . models import Payment
from django import forms

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'country', 'mobile_number', 'password1', 'password2')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder':'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder':'Last Name'}),
            'email': forms.TextInput(attrs={'placeholder':'Enter email address'}),
            'mobile_number': forms.TextInput(attrs={'placeholder':'Phone number'}),
            'password1': forms.PasswordInput(attrs={'placeholder':'Enter Password'}),
            'password2': forms.PasswordInput(attrs={'placeholder':'Confirm Password'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields = ('mobile_number', 'usdt_trc20_wallet_address','eth_wallet_address', 'btc_wallet_address')

class DepositForm(forms.ModelForm):
    class Meta:
        model=Payment
        fields= ('user','payment_option', 'amount', 'memo')