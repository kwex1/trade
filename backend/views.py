from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from .form import RegistrationForm
from django.contrib import messages
from .models import *
from .form import *
from django.contrib.auth.views import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .utils import TokenGenerator, SendReferalMail, SendEmail
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view



def home(request):
    return render(request, 'backend/index.html')


def EmailVerification(request, uidb64, token):
    try:
        uid =  force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError,ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and TokenGenerator.check_token(user, token):
        user.is_active=  True
        user.save()
        messages.add_message(request, messages.SUCCESS, 'Email verification complete' )
        return redirect('/login')
    return JsonResponse('User verified', safe=False)


def register(request):
    if request.method=='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active =False
            user.save()
            website = get_current_site(request).domain
            email_subject = 'Email Verification'
            email_body =  render_to_string('email/activation.html',{
                'user':user.first_name,
                'domain':website,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': TokenGenerator.make_token(user)
            })
            email = EmailMessage(subject=email_subject, body=email_body,
                from_email='ZenithPort <support@zenithport.com>', to=[user.email]
                )
            email.content_subtype = 'html'
            email.send()
            messages.success(request, 'A Verification mail has been sent to your email or spam box')
            return redirect('/login')
    else:    
        form = RegistrationForm()
    args = {'form':form}
    return render(request, 'backend/register.html', args)


def ReferalRegister(request, referal):
    if request.method=='POST':
        referer =  User.objects.get(referal=referal)
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active =False
            user.save()


            website = get_current_site(request).domain
            email_subject = 'Email Verification'
            email_body =  render_to_string('email/activation.html',{
                'user':user.first_name,
                'domain':website,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': TokenGenerator.make_token(user)
            })
            email = EmailMessage(subject=email_subject, body=email_body,
                from_email='ZenithPort <support@zenithport.com>', to=[user.email]
                ) 
            email.content_subtype = 'html'
            email.send()
            SendReferalMail(user,referer)
            messages.success(request, 'A Verification mail has been sent to your email or spam box')
            return redirect('/login')
    else:     
        form = RegistrationForm()
    args = {'form':form}
    return render(request, 'backend/register.html', args)




@login_required(login_url='/login/')  
def Dashboard(request):
    user = request.user
    data = History.objects.filter(user = user)[:10]
    detail = User.objects.get(email= request.user.email)

    #referer

    refer = User.objects.all().filter(refered_by = str(request.user))
    bonus = ReferalBonus.objects.all().filter(user=str(request.user))
    total = 0
    for i in bonus:
        total += i.earnings
    arg = {'detail':detail, 'data':data, 'total':refer.count(), 'refer': detail.referal, 'earnings':total}
    return render(request, 'backend/dashboard.html', arg)




@login_required(login_url='/login/')
def Deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            current = form.save(commit=False)
            current.user= request.user
            current.save()
            bills = Payment.objects.last()
            qrcode =  Currency.objects.filter(name=bills.payment_option).last()
            return render(request, 'backend/confirmpayment.html', {'currency':current.payment_option, 'amount':current.amount, 'type':qrcode})
    else:
        form = DepositForm()
    arg = {'form':form}
    return render(request, 'backend/deposit.html', arg)

@login_required(login_url='/login/')
def ConfirmPayment(request):
    user = request.user
    bill = Payment.objects.filter(user = user).last()
    return JsonResponse('Admin Notified About Payment', safe=False)
    
@login_required(login_url='/login/')  
def profiledetails(request):
    detail =  User.objects.get(email = request.user.email)
    arg = {'details':detail}
    return render(request, 'backend/profiledetails.html', arg)

@login_required(login_url='/login/')  
def Referal(request):
    detail =  User.objects.get(user = request.user)
    refer = User.objects.all().filter(refered_by = str(request.user.username))
    bonus = ReferalBonus.objects.all().filter(user=str(request.user))
    total = 0
    for i in bonus:
        total += i.earnings
    arg = {'total':refer.count(), 'refer': detail.referal, 'earning':total}
    return render(request, 'backend/referal.html', arg)

@login_required(login_url='/login/')  
def history(request):
    user = request.user
    data = History.objects.filter(user = user)
    args = {'data':data}
    return render(request, 'backend/history.html', args)

@login_required(login_url='/login/')
def editProfile(request):
    if request.method=='POST':
        forms = UserForm(request.POST, instance = request.user)
        if forms.is_valid():
            data = forms.save()
            messages.add_message(request, messages.SUCCESS, 'Profile updated!',)
            return redirect('/edit_personal_details')
            
    else:
        forms =  UserForm(instance=request.user)
    args = {'forms':forms}
    return render(request, 'backend/editprofile.html' , args)


@login_required(login_url='/login/') 
def RenderWithdrawal(request):
    data =  Currency.objects.all()
    args = {'data':data}
    return render(request, 'backend/withdrawal.html', args)

@login_required(login_url='/login/') 
def MakeWithdrawal(request):
    amount = request.POST['amount']
    select = request.POST['select']
    withdraw = Withdrawal.objects.create(user= request.user, currency = select, amount= amount)
    withdraw.save()
    bal =  User.objects.get(email= request.user.email)
    bal.balance -= int(amount)
    bal.save()
    return JsonResponse('Succesfully placed withdrawal', safe=False)


def Contactinfo(request):
        
    
    return render(request, 'backend/contact.html')


def terms(request):

    return render(request, 'backend/terms.html')


def AdminContact(request):
    name = request.POST['name']
    email = request.POST['email']
    message = request.POST['message']
    data = Contact.objects.create(name=name, email=email, message=message)
    data.save()
    return JsonResponse('DATA SUBMITTED', safe=False)



def About(request):
    return render(request, 'backend/about.html')



def investment(request):
    
    return render(request, 'backend/investment.html')

@login_required(login_url='/login/') 
def ActiveInvestment(request):
    invest =  Plan.objects.all().values
    args = {'invest':invest}
    return render(request, 'backend/active.html', args)

@login_required(login_url='/login/') 
def SubmitInvestment(request):
    amount = request.POST['amount']
    select = request.POST['select']

    reinvest = Reinvestment.objects.filter(user=request.user, plan=select)

    if reinvest.exists():
        counting = Reinvestment.objects.get(user=request.user, plan=select)
        if counting.plan == 'Starter' and counting.number_of_investment < 2 or counting.plan == 'Premium' and counting.number_of_investment <4 or counting.plan == 'Vip' and counting.number_of_investment >= 0:
            invest = Investment.objects.create(user= request.user, plan= select, amount= amount, is_active= True)
            referal =  User.objects.get(email=request.user.email)

            def Earn():
                if select == 'Starter':
                    return 2
                elif select == 'Premium':
                    return 3
                else:
                    return 5
            ReferalBonus.objects.create(user = str(referal.refered_by), earnings = Earn())
            bal =  User.objects.get(email=request.user.email)
            bal.balance -= int(amount)
            bal.save()
            counting.number_of_investment += 1
            counting.save()
            return JsonResponse('Investment successfully', safe=False)
        else:
            return JsonResponse(f"Number of Reinvestment reached for {select}", safe=False)
    else:
        new = Reinvestment.objects.create(user=request.user, plan=select)
        invest = Investment.objects.create(user= request.user, plan= select, amount= amount, is_active= True)
        referal =  User.objects.get(email=request.user.email)

        def Earn():
            if select == 'Starter':
                return 2
            elif select == 'Premium':
                return 3
            else:
                return 5
        ReferalBonus.objects.create(user = str(referal.refered_by), earnings = Earn())
        bal =  User.objects.get(user= request.user)
        bal.balance -= int(amount)
        bal.save()
        new.number_of_investment += 1
        new.save()
        return JsonResponse('Investment successfully', safe=False)
        

    
 
def Faq(request):

    return render(request, 'backend/faq.html')

@login_required(login_url='/login/') 
def transfer(request):
    amount = request.POST['amount']
    username = request.POST['username']
    transfer = Transfer.objects.create(user= request.user, reciever=username, amount=amount, status = False  )
    transfer.save()
    return JsonResponse('Transfer Pending', safe=False)


@login_required(login_url='/login/') 
def InitiateTransfer(request):
    
    return render(request, 'backend/transfer.html')



@login_required(login_url='/login/') 
def notification(request):
    
    return render(request, 'backend/tr.html')


# Api endpoint for validating earning and investment
@api_view(['GET','POST', 'PUT'])
def validateEarning(request):
    earn =  SystemEaring.objects.filter(is_active=True)
    invest =  Investment.objects.filter(is_active=True)
    for x in earn: 
        x.save()
    for y in invest:
        y.save()
    return Response({'message': 'Processed Successfully'}, status=status.HTTP_202_ACCEPTED)


#Email view organisation

def DisplayEmail(request):

    return render(request, 'backend/mailsending.html')


def SendBulkEmail(request):
    email  =  request.POST['email']
    subject =  request.POST['subject']
    val = request.POST['value']
    message =  request.POST['message']

    if val == 'true':
        item = User.objects.all()
        for i in item:
            user = {
                'username': i.first_name,
                'email': i.email
            }
            SendEmail(subject, user, message)
    else:
        item = User.objects.filter(email = email)
        for i in item:
            user = {
                'username': i.first_name,
                'email': i.email
            }
            SendEmail(subject, user, message)
    return JsonResponse({'message': 'Email Successfully Sent'})

@login_required(login_url='/login/') 
def notification(request):
    user = request.user
    id =  request.POST['id']
    data = NotificationVisibility.objects.update_or_create(user = user, notification_id=int(id))
    return JsonResponse('successfully updated', safe=False)

