import os
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from .models import *
from django import forms
from twilio.rest import Client
from django.core.mail import send_mail
from phonenumber_field.widgets import PhoneNumberPrefixWidget


admin.site.site_title = "Motocornio"
admin.site.site_header = "Motocornio Administration"
admin.site.index_title = "Motocornio Administration"


# account_sid = os.environ['TWILIO_ACCOUNT_SID']
# auth_token = os.environ['TWILIO_AUTH_TOKEN']
# client = Client(account_sid, auth_token)


class UserCreationForm(BaseUserCreationForm):
    password1 = None
    password2 = None
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True, help_text="Phone Number With Country Code e.g. (+1123763989)")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is already exists")
        return username

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Phone is already exists")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already exists")
        return email

    def clean(self):
        password = BaseUserManager().make_random_password()
        self.cleaned_data['password1'] = password
        self.cleaned_data['password2'] = password
        print('password:', password)
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token) 
        # def send_text_password(sender, instance, created, **kwargs):
        #     if created:
        #         phone = str(instance.phone)
        #         user = instance.username
        #         message = client.messages.create(  
        #                             messaging_service_sid=os.environ.get('MESSAGE_SERVICE_SID'), 
        #                             body='Hello User! Welcome To Motocornio, Your Username is '+user+ ' And Password is '+ password,      
        #                             to=phone
        #                         )
        #         print('message_sid:', message.sid)
        #         print('phone:', phone)
        #         print('password:', password)
        # models.signals.post_save.connect(send_text_password, sender=User)
        # def send_whatsapp_password(sender, instance, created, **kwargs):
        #     if created:
        #         phone = str(instance.phone)
        #         user = instance.username
        #         whatsapp = client.messages.create( 
        #                             from_= os.environ.get('WHATSAPP'),  
        #                             body='Hello User! Welcome To Motocornio, Your Username is '+user+ ' and Password is '+ password,      
        #                             to='whatsapp:'+phone
        #                         )
        #         print('whatsapp_sid:',whatsapp.sid)
        # models.signals.post_save.connect(send_whatsapp_password, sender=User)
        def send_email_password(sender, instance, created, **kwargs):
            if created:
                user = instance.username
                send_mail(
                'Your Password',
                f'Hello User! Welcome to Motocornio, Your Username is {user} and Password is {password}.',
                ('EMAIL_HOST_USER'),
                [instance.email],
                fail_silently=False,
                )
        models.signals.post_save.connect(send_email_password, sender=User)



class UserModelAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    list_display = ('id', 'username', 'name', 'surname', 'email', 'phone', 'is_active', 'action', 'created_at', 'updated_at', )
    list_display_links = ['id', 'username', 'name', 'surname', 'email', 'phone']
    list_filter = ('is_superuser', 'is_active', 'created_at', 'updated_at')
    fieldsets = (
        ('User Credentials', {'fields': ('username', 'phone', 'password')}),
        ('Personal info', {'fields': ('email', 'name', 'surname')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'surname', 'email', 'phone', 'is_staff', 'is_superuser'),
        }),
    )
    search_fields = ('username', 'name', 'surname', 'email', 'phone')
    ordering = ('id', 'username', 'name', 'surname', 'email', 'phone', 'created_at', 'updated_at')
    list_per_page = 15
    filter_horizontal = ()
    readonly_fields = ('created_at', 'updated_at')

    def action(self, obj):
        if obj.id:
            return mark_safe("<a class='button btn' style='color:green; padding:0 1rem; ' href='/administration/accounts/user/{}/change/'>Edit</a>".format(obj.id)
                             + "    " + "<a class='button btn' style='color:red; padding:0 1rem; ' href='/administration/accounts/user/{}/delete/'>Delete</a>".format(obj.id))
        else:
            social_button = '<a  href="#">---</a>'
            return mark_safe(u''.join(social_button))
admin.site.register(User, UserModelAdmin)


# class CellPhoneForm(forms.ModelForm):
#     class Meta:
#         widgets = {
#             'cellphone': PhoneNumberPrefixWidget(),
#         }


@admin.register(Customers)
class CustomersAdmin(admin.ModelAdmin):
    # form = CellPhoneForm
    list_display = ['id', 'name', 'surname', 'cellphone', 'email', 'age', 'user', 'created_at', 'updated_at', 'action']
    search_fields = ('name', 'surname', 'cellphone', 'age', 'email', 'user__name', 'user__surname', 'created_at', 'updated_at')
    ordering = ('id', 'name', 'surname', 'cellphone', 'age', 'email', 'user', 'created_at', 'updated_at')
    list_per_page = 15
    filter_horizontal = ()
    list_filter = ['user', 'age', 'created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')
    def action(self, obj):
        if obj.id:
            return mark_safe("<a class='button btn' style='color:green; padding:0 1rem; ' href='/administration/accounts/customers/{}/change/'>Edit</a>".format(obj.id)
                             + "    " + "<a class='button btn' style='color:red; padding:0 1rem; ' href='/administration/accounts/customers/{}/delete/'>Delete</a>".format(obj.id))
        else:
            social_button = '<a  href="#">---</a>'
            return mark_safe(u''.join(social_button))


@admin.register(Malls)
class MallsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address', 'created_at', 'updated_at']
    search_fields = ('name', 'address', 'created_at', 'updated_at')
    ordering = ('id', 'name', 'address','created_at', 'updated_at')
    list_per_page = 15
    filter_horizontal = ()
    list_filter = ['name', 'created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')



@admin.register(Remark)
class RemarkAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'remarkcomment',  'created_at', 'updated_at']
    search_fields = ('user__username', 'remarkcomment', 'created_at', 'updated_at')
    ordering = ('id', 'user', 'remarkcomment', 'created_at', 'updated_at')
    list_per_page = 10
    filter_horizontal = ()
    list_filter = ['user', 'created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'number', 'serial_number', 'mall_assigned', 'created_at', 'updated_at']
    search_fields = ('name', 'number', 'serial_number', 'mall_assigned__name', 'created_at', 'updated_at')
    ordering = ('id', 'name', 'number', 'serial_number', 'mall_assigned', 'created_at', 'updated_at')
    list_per_page = 15
    filter_horizontal = ()
    list_filter = ['mall_assigned', 'created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price',  'time', 'created_at', 'updated_at']
    search_fields = ('name', 'price',  'time', 'created_at', 'updated_at')
    ordering = ('id', 'name', 'price',  'time', 'created_at', 'updated_at')
    list_per_page = 15
    filter_horizontal = ()
    list_filter = ['name', 'price',  'time', 'created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['id', 'service', 'customer', 'mall_assigned',  'payment_method', 'payment_date', 'created_at', 'updated_at']
    search_fields = ('service', 'customer__name', 'mall_assigned__name',  'payment_method', 'payment_date', 'created_at', 'updated_at')
    ordering = ('id', 'service', 'customer', 'mall_assigned',  'payment_method', 'payment_date', 'created_at', 'updated_at')
    list_per_page = 15
    filter_horizontal = ()
    list_filter = ['payment_method', 'customer', 'mall_assigned', 'payment_date', 'created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ResponsiveLetter)
class ResponsiveLetterAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customer', 'created_at', 'updated_at']
    ordering = ('id', 'user', 'customer', 'created_at', 'updated_at')
    search_fields = ('user__name', 'customer__name',)
    list_per_page = 10
    filter_horizontal = ()
    list_filter = ['user', 'customer', 'created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ['id', 'heading', 'created_at', 'updated_at']
    ordering = ('id',)
    search_fields = ('heading',)
    list_per_page = 7
    filter_horizontal = ()
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')

