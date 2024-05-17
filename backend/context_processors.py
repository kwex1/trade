from .models import User, History, Notification,SystemEaring, Investment, NotificationVisibility


def TotalDeposit(request):
    try:
        amount= User.objects.get(user=request.user)
        bal = amount.balance
        return {'balance':bal}
    except:
        return {'balance':None}
    
def PendingWithdrawal(request):
    try:
        bal = History.objects.filter(user=request.user, status=False, action= 'Withdrawal')
        total = 0
        for i in  bal:
            total  += int(i.amount)
        return {'withdraw': total}
    except:
        return {'withdraw': None}
def TotalWithdrawal(request):
    try:
        bal = History.objects.filter(user=request.user, status=True, action= 'Withdrawal')
        total = 0
        for i in  bal:
            total  += int(i.amount)
        return {'confirm': total}
    except:
        return {'confirm': None}
    

def ActiveDeposit(request):
    try:
        bal = Investment.objects.filter(user=request.user, is_active=True)
        total = 0
        for i in  bal:
            total  += int(i.amount)
        return {'invest': total}
    except:
        return {'invest': None}
    
def ActiveEarnings(request):
    try:
        bal = SystemEaring.objects.filter(user=request.user, is_active=True)
        total = 0
        for i in  bal:
            total  += int(i.balance)
        return {'earning': total}
    except:
        return {'earning': None}
    
def Notify(request):
    data = NotificationVisibility.objects.filter(user= request.user.pk).count()
    val = Notification.objects.filter(ended=False).count() 
    if data:
        total = int(val-data)
        return {'num': total}
    else:
        return {'num': val}
    
    
    
def Message(request):
    data = NotificationVisibility.objects.filter(user= request.user.pk)
    val = Notification.objects.filter(ended = False)
    notify_id = []
    message_id = []
    item = []
    if data:
        for i in val:
            message_id.append(i.pk)
        for d in data:
            notify_id.append(d.notification_id)
        update_data = list(set(message_id) - set(notify_id))
        for y in update_data:
            dats = Notification.objects.filter(pk = y)
            for j in dats:
                items = {
                    'pk': j.pk,
                    'subject': j.subject,
                    'message': j.message,
                    'date_created': j.date_created
                }
            item.append(items)
        return {'item':item}
    else:
        return {'item': val}



    







    


