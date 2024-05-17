from django.contrib.auth.forms import UserCreationForm
from .models import User
from . models import Payment
from django import forms

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('full_name', 'email', 'country', 'phone_number', 'password1', 'password2')

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields = ('full_name','email')

class DepositForm(forms.ModelForm):
    class Meta:
        model=Payment
        fields= ('user','payment_option', 'amount', 'memo')