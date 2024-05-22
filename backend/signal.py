from urllib import request
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from . models import History, Payment, Withdrawal, Investment, Transfer, SystemEaring,ReferalBonus

@receiver(post_save, sender=Payment)
def HistorySave(sender, instance, created, **kwargs):
    if created:
        ids = instance.user
        History.objects.create(user=ids, payment=instance, action='Deposit', currency = str(instance.payment_option), amount=instance.amount, status = instance.status, date_created = instance.date_created )

@receiver(post_save, sender=Payment)
def UpdateHistorySave(sender, instance, created, **kwargs):
    if created == False:
        history  = History.objects.filter(payment=instance).update(action='Deposit', currency = str(instance.payment_option), status = instance.status, date_created = instance.date_created)


@receiver(post_save, sender=Withdrawal)
def WithdrawHistorySave(sender, instance, created, **kwargs):
    if created:
        ids = instance.user
        History.objects.create(user=ids, withdraw=instance,  action='Withdrawal', currency = instance.currency, amount=instance.amount, status = instance.status, date_created = instance.date_created)

@receiver(post_save, sender=Withdrawal)
def UpdateWithdrawHistorySave(sender, instance, created, **kwargs):
    if created == False:
        History.objects.filter(withdraw =instance).update(action='Withdrawal', currency = instance.currency, status = instance.status, date_created = instance.date_created)



@receiver(post_save, sender=Investment)
def InvestHistorySave(sender, instance, created, **kwargs):
    if created:
        ids = instance.user
        History.objects.create(user=ids, invest=instance,  action='Investment', currency= instance.plan, amount=instance.amount, status = instance.is_active, date_created = instance.date_created)
        



@receiver(post_save, sender=Transfer)
def TransferHistorySave(sender, instance, created, **kwargs):
    if created:
        ids = instance.user
        History.objects.create(user=ids, action='Transfer', amount=instance.amount, status = instance.status, date_created = instance.date_created)

@receiver(post_save, sender=Transfer)
def TransferUpdate(sender, instance, created, **kwargs):
    if created == False:
        History.objects.filter(transfer=instance).update(action='Transfer', status = instance.status, date_created = instance.date_created)


@receiver(post_save, sender=Investment)
def UpdateSystemEarning(sender, instance, created, **kwargs):
    if created:
        ids = instance.user
        SystemEaring.objects.create(user = ids, invest=instance, plan = instance.plan, is_active= instance.is_active, num=0, date_created = instance.date_created, date_expiration= instance.date_expiration)
























    
    




