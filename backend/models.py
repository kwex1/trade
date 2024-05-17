from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
import random
from django.utils.crypto import get_random_string
from django_countries.fields import CountryField
import qrcode
from django.core.files import File
from PIL import Image, ImageDraw
from io import BytesIO
from .utils import WithdrawalMail, CommisionMail, DepositMail, TransferMail, TransferRecieverMail


class MyUserManager(BaseUserManager):
    def create_user(self,email, full_name, password=None):
        if not email:
            raise ValueError('User must have an email address')

        if not full_name:
            raise ValueError('User must enter full name')

        user = self.model(
            email = self.normalize_email(email),
            full_name=full_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, full_name,email,password):
        user = self.create_user(
            email = self.normalize_email(email),
            full_name=full_name,
            password=password,
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    full_name    = models.CharField(max_length=100)
    email         = models.EmailField(max_length=100, unique=True)
    referal = models.CharField(max_length=20, unique=True, blank=True, null=True)
    refered_by = models.CharField(max_length=50, blank=True, null=True)
    phone_number  = models.CharField(max_length=100)
    balance = models.IntegerField(default=0)
    country = CountryField(blank_label="(select country)")
    btc_wallet_address = models.CharField(max_length=300, blank=True, null=True)
    eth_wallet_address = models.CharField(max_length=300, blank=True, null=True)
    usdt_trc20_wallet_address = models.CharField(max_length=300, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)

    
    
    date_joined   = models.DateTimeField(auto_now_add=True) 
    last_login    = models.DateTimeField(auto_now_add=True)   
    is_admin      = models.BooleanField(default=False)
    is_staff      = models.BooleanField(default=False)
    is_active     = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name',]

    objects = MyUserManager()


    def __str__(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True
    


class Contact(models.Model):
    name =  models.CharField(max_length=300)
    email =  models.EmailField(max_length=200)
    message = models.TextField(max_length=1000)

    def __str__(self):
        return f"{self.name}---------{self.email}"
    

class Currency(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    rate = models.CharField(max_length=20, blank=True, null=True)
    wallet_id = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='wallet/', blank=True, null=True)

    class Meta:
        verbose_name_plural='Currencies'

    def __str__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        img = qrcode.make(self.wallet_id)
        canvas = Image.new('RGB',(390,290), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(img)
        name = f'{self.name}QRCODE.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.image.save(name, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)




class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    payment_option= models.ForeignKey(Currency, on_delete=models.DO_NOTHING, blank=True, null=True)
    amount = models.FloatField()
    memo = models.CharField(max_length=200, blank=True, null=True)
    status = models.BooleanField(default=False) 
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user}---------{self.payment_option}-------------{self.amount}"
    
    def save(self, *args, **kwargs):
        if self.status == True:
            account = self.user
            payment = Currency.objects.get(name = str(self.payment_option))
            total = self.amount
            account.balance += total
            account.save()
            amount = self.amount
            user = self.user
            currency = self.payment_option
            reinvestment =  Reinvestment.objects.filter(user = user)
            for i in reinvestment:
                i.number_of_investment = 0
                i.save()
            DepositMail(user,amount, currency)
        super().save(*args, **kwargs)

class Investment(models.Model):
    choice = (
        ('Starter', 'Starter'),
        ('Premium', 'Premium'),
        ('Vip', 'Vip'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    plan = models.CharField(max_length=100, choices=choice)
    amount = models.FloatField()
    is_active = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    date_expiration = models.DateTimeField(default=timezone.now) 
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user}--------{self.amount}------------{self.date_created}"
    
    def save(self, *args, **kwargs):
        plan  =  Plan.objects.get(name = self.plan)
        self.date_expiration =  self.date_created + timezone.timedelta(days=plan.duration)
        if timezone.now() > self.date_expiration and self.is_active == True and self.is_completed == False:
            total =  User.objects.get(user=self.user)
            total.balance += self.amount
            total.save()
            self.is_active = False
            self.is_completed =True
        super().save(*args, **kwargs)

class Plan(models.Model):
    name = models.CharField(max_length=30, blank=True, null=True)
    profit =  models.IntegerField()
    duration = models.IntegerField()
    referal =  models.IntegerField()
     

    def __str__(self):
        return self.name
     
class Withdrawal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    currency = models.CharField(max_length=20, blank=True, null=True)
    amount = models.IntegerField()
    status = models.BooleanField(default=False) 
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user}---------{self.currency}---------{self.amount}"
    
    def save(self, *args, **kwargs):
        user = self.user
        amount = self.amount
        if self.status == True:
            WithdrawalMail( user, amount)
        else:
            pass
        super().save(*args, **kwargs)
    

class Transfer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    reciever = models.CharField(max_length=20, blank=True, null=True)
    amount = models.IntegerField()
    status = models.BooleanField(default=False) 
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user}---------{self.amount}------------{self.reciever}"
    
    def save(self, *args, **kwargs):
        user =  self.user
        amount =  self.amount
        referer =  self.reciever
        if self.status == True:
            TransferMail(user,referer,amount)
            TransferRecieverMail(referer, amount, user)
            bal =  User.objects.get(user= self.user)
            bal.balance -= int(amount)
            recieved = User.objects.get(username=self.reciever)
            custom = User.objects.get(user = recieved.pk)
            custom.balance += int(amount)
            custom.save()
            bal.save()
        else:
            pass
        super().save(*args, **kwargs)
    
class History(models.Model):
    choice  =  (
        ('Withdrawal', 'Withdrawal'),
        ('Deposit', 'Deposit'),
        ('Transfer', 'Transfer'),
        ('Investment', 'Investment'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)
    withdraw = models.ForeignKey(Withdrawal, on_delete=models.CASCADE, blank=True, null=True)
    invest = models.ForeignKey(Investment, on_delete=models.CASCADE, blank=True, null=True)
    action =  models.CharField(max_length=200, choices=choice, blank=True, null=True, editable=False)
    currency = models.CharField(max_length=20, blank=True, null=True)
    amount = models.CharField(max_length=20)
    status = models.BooleanField(default=False) 
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural ='Histories'
        ordering = ('-date_created',)

    def __str__(self):
        return f"{self.user}----------{self.amount}-------{self.action}------------{self.date_created}-------{self.status}"


class Notification(models.Model):
    subject =  models.CharField(max_length=100, blank=True, null=True)
    message  =  models.TextField( blank=True, null=True)
    ended =  models.BooleanField(default=False)
    date_created =  models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.subject
    

class NotificationVisibility(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    notification_id =  models.IntegerField()

    def __str__(self):
        return f"{self.user}  id: {self.notification_id}"

class SystemEaring(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    invest = models.ForeignKey(Investment, on_delete=models.CASCADE, blank=True, null=True)
    num =  models.IntegerField(default=0)
    plan = models.CharField(max_length=50, blank=True, null=True)   
    balance = models.IntegerField(default=0)
    date_expiration =  models.DateTimeField(default=timezone.now)
    date_created =  models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        plans = Plan.objects.get(name = str(self.invest.plan))
        total =  User.objects.filter(user=self.user)
        fig =  timezone.now().date() - self.date_created.date()
        diff = fig.days
        profit =  plans.profit
        profit_per_day = ((profit * int(self.invest.amount)))/100
        
        if diff == 0:
            pass
        else:
            if timezone.now() <= self.date_expiration: 
                if ((diff + 1) - self.num) == 1 and self.balance == diff * profit_per_day:
                    self.balance += profit_per_day
                    self.num += 1
                else:
                    self.num = diff + 1
                    self.balance = diff * profit_per_day                           
            else:
                total =  User.objects.get(user=self.user)
                total.balance += self.balance
                total.save()
                self.is_active = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user}---------{self.balance}============{self.is_active}"
    
    



class ReferalBonus(models.Model):
    user =  models.CharField(max_length=200, blank=True, null=True)
    earnings = models.IntegerField(default=0)

    def __str__(self):
        return f" {self.user}--------{self.earnings}"
    
    def save(self, *args, **kwargs):
        try:
            refer = User.objects.get(username = self.user)
            referer= refer
            bal =  User.objects.get(user = refer.pk)
            bal.balance += self.earnings
            user = User.objects.filter(refered_by = self.user).last()
            bal.save()
            bonus = self.earnings
            CommisionMail(user,referer, bonus)
        except:
            pass  
        super().save(*args, **kwargs )

class Reinvestment(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE, blank=True, null=True)
    plan = models.CharField(max_length=100, blank=True, null=True)
    number_of_investment =  models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user}-------{self.number_of_investment}"







