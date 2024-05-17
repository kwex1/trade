from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . models import *
# Register your models here.


class AccountAdmin(UserAdmin):
    list_display = ('full_name','email', 'phone_number', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'full_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
admin.site.register( User, AccountAdmin)


admin.site.site_header = 'Zenithport Administrator'
admin.site.site_title = 'Zenithport Administrator'



admin.site.register(Payment)
admin.site.register(Currency)
admin.site.register(Plan)
admin.site.register(History)
admin.site.register(Withdrawal)
admin.site.register(Investment)
admin.site.register(Transfer)
admin.site.register(Notification)
admin.site.register(ReferalBonus)
admin.site.register(SystemEaring)
admin.site.register(Contact)
admin.site.register(Reinvestment)
#admin.site.register(NotificationVisibility)
