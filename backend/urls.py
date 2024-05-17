from django.urls import path
from . import views
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView,
    PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView
)


urlpatterns = [
  path('password_reset/', PasswordResetView.as_view(template_name='password/reset_password.html'), name='reset_password'),
  path('password_reset_done/', PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'), name='password_reset_done'),
  path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='password/password_reset_confirm.html'), name='password_reset_confirm'),
  path('password_reset_complete/', PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'), name='password_reset_complete'),

  path('', views.home, name='home'),
  path('login/', LoginView.as_view(template_name='backend/login.html'), name='login'),
  path('logout/', LogoutView.as_view(), name='logout'),
  path('register/', views.register, name='register'),
  path('register/<str:referal>/', views.ReferalRegister, name='referal'),
  path('deposit/', views.Deposit, name='deposit'),
  path('transaction/', views.history,name='transaction'),
  path('withdrawal/', views.RenderWithdrawal, name='withdrawal'),
  path('make_withdrawal/', views.MakeWithdrawal, name='makewithdrawal'),
  path('make_payment/', views.ConfirmPayment, name='payment'),
  path('make_investment/', views.ActiveInvestment, name='active'),
  path('investment_processing/', views.SubmitInvestment, name='submitinvestment'),
  path('transfer_funds/', views.InitiateTransfer, name='initiatetransfer'),
  path('transfer/', views.transfer, name='transfer'),
  path('Profile-dashboard/', views.Dashboard, name='dashboard'),
  path('verification/<uidb64>/<token>/', views.EmailVerification, name='verification'),
  path('personal_details/', views.profiledetails ,name='details'),
  path('edit_personal_details/', views.editProfile ,name='editprofile'),
  path('Referal/', views.Referal ,name='referal'),
  path('contact/', views.Contactinfo, name='contact'),
  path('complain/', views.AdminContact, name='contactadmin'),
  path('about/', views.About, name='about'),
  path('investment/', views.investment, name='investment'),
  path('faq/', views.Faq, name='faq'),
  path('terms_and_conditions/', views.terms, name='terms'),
  path('update_notification/', views.notification, name='update_notification'),









  #api url
  path('validating_earning/', views.validateEarning, name='validating' ),
  path('sending_bulking_mail/', views.DisplayEmail, name='email'),
  path('sending_mail/', views.SendBulkEmail, name='emailsent'),
]