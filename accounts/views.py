from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .models import *
import datetime
from datetime import timedelta
from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import pdfkit
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpRequest
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from twilio.rest import Client
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views import generic
from django.core.mail import send_mail
from .forms import SignatureForm



@method_decorator(login_required, name='dispatch')
class ReportsView(View):
    def get(self, request):
        if request.user.is_superuser:
            return render (request, 'admin/reports.html')
        return redirect ('started-service-list')
    def post(self, request):
        if request.user.is_superuser:
            # service = Income.objects.values_list('name', flat=True).distinct()
            service = Service.objects.all()
            malls = Malls.objects.all()
            start_date = request.POST.get('start_date1')
            end_date = request.POST.get('end_date1')
            total_income = Income.objects.filter(payment_date__date__gte=start_date, payment_date__date__lte=end_date).aggregate(Sum('service__price'))
            card_income = Income.objects.filter(payment_method= 'Card', payment_date__date__gte=start_date, payment_date__date__lte=end_date).aggregate(Sum('service__price'))
            cash_income = Income.objects.filter(payment_method= 'Cash', payment_date__date__gte=start_date, payment_date__date__lte=end_date).aggregate(Sum('service__price'))
            service_list = []  
            for all_service in service:
                service_income = Income.objects.filter(service = all_service, payment_date__date__gte=start_date, payment_date__date__lte=end_date).aggregate(Sum('service__price'))
                service_incomes = list(service_income.values())
                service_list.append(service_incomes[0])
            service_incomes = service_list
            mall_list = []
            for all_mall in malls:
                mall_income = Income.objects.filter(mall_assigned = all_mall, payment_date__date__gte=start_date, payment_date__date__lte=end_date).aggregate(Sum('service__price'))
                mall_incomes = list(mall_income.values())
                mall_list.append(mall_incomes[0])
            mall_incomes = mall_list
            return render (request, 'admin/reports_final.html', {'total_income':total_income, 'card_income':card_income, 'cash_income':cash_income, 'mall_incomes':mall_incomes, 'malls':malls, 'service_incomes':service_incomes, 'service':service})
        return redirect ('started-service-list')



@method_decorator(login_required, name='dispatch')
class ReportsByMallView(View):
    def get(self, request):
        if request.user.is_superuser:
            malls = Malls.objects.all()
            return render (request, 'admin/reports_by_mall.html', {'malls':malls})
        return redirect ('started-service-list')
    def post(self, request):
        if request.user.is_superuser:
            service = Service.objects.all()
            mall = request.POST.get('choose_mall')
            start_date = request.POST.get('start_date2')
            end_date = request.POST.get('end_date2')
            total_income = Income.objects.filter(mall_assigned=mall, payment_date__date__gte=start_date, payment_date__date__lte=end_date).aggregate(Sum('service__price'))
            card_income = Income.objects.filter(mall_assigned=mall, payment_method= 'Card', payment_date__date__gte=start_date, payment_date__date__lte=end_date).aggregate(Sum('service__price'))
            cash_income = Income.objects.filter(mall_assigned=mall, payment_method= 'Cash', payment_date__date__gte=start_date, payment_date__date__lte=end_date).aggregate(Sum('service__price'))
            service_list = []
            for all_service in service:
                service_income = Income.objects.filter(service = all_service, payment_date__date__gte=start_date, payment_date__date__lte=end_date).aggregate(Sum('service__price'))
                service_incomes = list(service_income.values())
                service_list.append(service_incomes[0])
            print(service_list)
            service_incomes = service_list
            return render (request, 'admin/reports_final_mall.html', {'total_income':total_income, 'card_income':card_income, 'cash_income':cash_income, 'service_incomes':service_incomes, 'service':service})
        return redirect ('started-service-list')


@method_decorator(login_required, name='dispatch')
class ResponsiveLetterListView(View):
    def get(self, request):
        if request.user.is_superuser:
            responsive_letters = ResponsiveLetter.objects.all()
            return render (request, 'admin/responsive-letter-list.html', {'responsive_letters':responsive_letters})
        return redirect ('started-service-list')


@method_decorator(login_required, name='dispatch')
class ResponsiveLetterView(View):
    def get(self, request, id):
        if request.user.is_superuser:
            responsive_letter = ResponsiveLetter.objects.get(id=id)
            return render (request, 'admin/responsive-letter.html', {'responsive_letter':responsive_letter})
        return redirect ('started-service-list')


@method_decorator(login_required, name='dispatch')
class PrivacyPolicyView(View):
    def get(self, request):
        if request.user.is_superuser:
            privacy_policy = PrivacyPolicy.objects.all()
            return render (request, 'admin/privacy-policy.html', {'privacy_policy':privacy_policy})
        return redirect ('started-service-list')


@login_required
def generate_pdf(request, id, format=None):
    print("Hello")
    if request.user.is_superuser:
        responsive_letter = ResponsiveLetter.objects.get(id=id)
        html = render_to_string('admin/pdf.html', {'responsive_letter': responsive_letter})
        options = {
            'page-size': 'Letter',
            'encoding': "UTF-8",
        }
        # pdfkit.configuration(wkhtmltopdf='/home/mobapps/Desktop') 
        pdf = pdfkit.from_string(html, False, options=options)
        response = HttpResponse(pdf, content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename=" {}.pdf"'.format(responsive_letter)
        response['Content-Disposition'] = 'attachment; filename="responsive_letter.pdf"'
        return response
    return redirect ('started-service-list')


@login_required
def generate_privacy_pdf(request, format=None):
    print("Hello")
    if request.user.is_superuser:
        privacy_policy = PrivacyPolicy.objects.all()
        html = render_to_string('admin/privacy_pdf.html', {'privacy_policy': privacy_policy})
        options = {
            'page-size': 'Letter',
            'encoding': "UTF-8",
        }
        # pdfkit.configuration(wkhtmltopdf='/home/mobapps/Desktop') 
        pdf = pdfkit.from_string(html, False, options=options)
        response = HttpResponse(pdf, content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename=" {}.pdf"'.format(privacy_policy)
        response['Content-Disposition'] = 'attachment; filename="privacy_policy.pdf"'
        return response
    return redirect ('started-service-list')


class UserLoginView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            malls = Malls.objects.all()
            return render (request, 'registration/login.html', {'malls':malls})
        if not request.user.is_superuser:
            return redirect ('started-service-list')
        return redirect ('/admin/')
    def post(self, request):
        if not request.user.is_authenticated:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if not user.is_superuser:
                    login(request, user)
                    mall = request.POST.get('choose_mall')
                    mall_id = Malls.objects.get(id=mall)
                    user_mall = User.objects.filter(id=request.user.id)
                    user_mall.update(mall=mall_id)
                    incomes = Income.objects.filter(mall_assigned=mall, end_time__gte=timezone.now()).order_by('-end_time')
                    paginator = Paginator(incomes, per_page=10)
                    page_number = request.GET.get('page')
                    page_object= paginator.get_page(page_number)
                    return render (request, 'accounts/inventory.html', {'page_obj':page_object})
                messages.success(request, 'Admin Cant Not Login From Here')
                return redirect ('login')
            messages.success(request, 'User Does Not Exists')
            return redirect ('login')
        return redirect ('started-service-list')


@method_decorator(login_required, name='dispatch')
class StartedServiceListView(View):
    def get(self, request):
        if not request.user.is_superuser:
            print(timezone.now())
            incomes = Income.objects.filter(mall_assigned=request.user.mall, end_time__gte=timezone.now()).order_by('-end_time')
            paginator = Paginator(incomes, per_page=10)
            page_number = request.GET.get('page')
            page_object= paginator.get_page(page_number)
            return render (request, 'accounts/started-service-list.html', {'page_obj':page_object})
        return redirect ('/admin/')


@method_decorator(login_required, name='dispatch')
class EndedServiceListView(View):
    def get(self, request):
        if not request.user.is_superuser:
            incomes = Income.objects.filter(mall_assigned=request.user.mall, end_time__lte=timezone.now())
            paginator = Paginator(incomes, per_page=10)
            page_number = request.GET.get('page')
            page_object= paginator.get_page(page_number)
            return render (request, 'accounts/ended-service-list.html', {'page_obj':page_object})
        return redirect ('/admin/')


@method_decorator(login_required, name='dispatch')
class ServiceSelectView(View):
    def get(self, request):
        if not request.user.is_superuser:
            service_id = request.GET.get('service_id')
            service = Service.objects.get(id=service_id)
            time = service.time
            price = service.price
            data = {'time':time, 'price':price}
            return JsonResponse (data)
        return redirect ('/admin/')


@method_decorator(login_required, name='dispatch')
class ServiceView(View):
    def get(self, request):
        if not request.user.is_superuser:
            customers = Customers.objects.filter(user=request.user).order_by('-id')
            services = Service.objects.all()
            equipments = Inventory.objects.filter(mall_assigned=request.user.mall).exclude(booking_end__gte=timezone.now())
            return render (request, 'accounts/service.html', {'customers':customers, 'services':services, 'equipments':equipments})
        return redirect ('/admin/')
    def post(self, request):
        if not request.user.is_superuser:
            customers = request.POST.get('choose_customer')
            services = request.POST.get('choose_service')
            equipments = request.POST.get('choose_equipment')
            payment_methods = request.POST.get('payment_method')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            service = Service.objects.get(id=services)
            responsive = ResponsiveLetter.objects.first()
            description = responsive.description
            customer = Customers.objects.get(id=customers)
            equipment = Inventory.objects.get(id=equipments)
            equipments = Inventory.objects.filter(id=equipments)
            Income.objects.create(mall_assigned=request.user.mall, customer=customer, service=service, equipment=equipment, payment_method=payment_methods, start_time=start_time, end_time=end_time)
            user_responsive = ResponsiveLetter.objects.create(customer=customer, user=request.user, description=description)
            pk_letter = str(user_responsive.pk)
            equipments.update(booking_end=end_time)
            messages.info(request, 'You Service Detail Has Been Added')
            account_sid = os.environ.get('TWILIO_ACCOUNT_SID') 
            auth_token = os.environ.get('TWILIO_AUTH_TOKEN') 
            client = Client(account_sid, auth_token) 
            # message = client.messages.create(  
            #                     messaging_service_sid=os.environ.get('MESSAGE_SERVICE_SID'), 
            #                     body='Your Service Will Start at '+ str(start_time) + ' and Your Service Will Finish at '+str(end_time)+
            #                     ' and View Your Responsive Letter at http://69.49.235.253:8006/non-user-responsive-letter/'+pk_letter+'/ and Read Our Privacy Policy at http://69.49.235.253:8006/non-user-privacy-policy/', 
            #                     to=str(customer.cellphone)
            #                 )
            # print(message.sid)
            # whatsapp = client.messages.create(
            #                     from_=os.environ.get('WHATSAPP'),  
            #                     body='Your Service Will Start at '+ str(start_time) + ' and Your Service Will Finish at '+str(end_time)+
            #                     ' and View Your Responsive Letter at http://69.49.235.253:8006/non-user-responsive-letter/'+pk_letter+'/ and Read Our Privacy Policy at http://69.49.235.253:8006/non-user-privacy-policy/',     
            #                     to='whatsapp:'+str(customer.cellphone)
            #                 )
            # print(whatsapp.sid)
            send_mail(
            'Your Motocornio Service',
            f'Your Service Will Start at {str(start_time)} and Your Service Will Finish at {str(end_time)} and View Your Responsive Letter at http://69.49.235.253:8006/non-user-responsive-letter/{pk_letter}/ and Read Our Privacy Policy at http://69.49.235.253:8006/non-user-privacy-policy/.',
            ('EMAIL_HOST_USER'),
            [str(customer.email)],
            fail_silently=False,
            )
            return redirect ('started-service-list')
        return redirect ('/admin/')



@method_decorator(login_required, name='dispatch')
class CustomerView(View):
    def get(self, request):
        if not request.user.is_superuser:
          return render (request, 'accounts/customers.html')
        return redirect ('/admin/')
    def post(self, request):
        if not request.user.is_superuser:
            name = request.POST.get('name')
            surname = request.POST.get('surname')
            age = request.POST.get('age')
            email = request.POST.get('email')
            cellphone = request.POST.get('cellphone')
            if not Customers.objects.filter(cellphone=cellphone):
                if not Customers.objects.filter(email=email):
                    Customers.objects.create(name=name, surname=surname, cellphone=cellphone, age=age, email=email, user=request.user)
                    messages.info(request, 'Customer Has Been Added')
                    return JsonResponse({'message':'Customer Has Been Added'})
                messages.error(request, 'Email Already Exists')
                return JsonResponse({'message':'Cellphone Already Exists'})
            messages.error(request, 'Cellphone Already Exists')
            return JsonResponse({'message':'Cellphone Already Exists'})
        return redirect ('/admin/')


@method_decorator(login_required, name='dispatch')
class SettingView(View):
    def get(self, request):
        if not request.user.is_superuser:
          return render (request, 'accounts/setting.html')
        return redirect ('/admin/')
    def post(self, request):
        if not request.user.is_superuser:
            id = request.user.id
            name = request.POST.get('name')
            surname = request.POST.get('surname')
            username = request.POST.get('username')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            if not User.objects.filter(username=username).exclude(username=request.user.username):
                if not User.objects.filter(email=email).exclude(email=request.user.email):
                    if not User.objects.filter(phone=phone).exclude(phone=request.user.phone):
                        User.objects.filter(id=id).update(username=username, email=email, name=name, surname=surname, phone=phone)
                        messages.info(request, 'User Detail Updated')
                        return JsonResponse({'message':'User Detail Updated'})
                    messages.error(request, 'Phone Already Exists')
                    return JsonResponse({'message':'Phone Already Exists'})
                messages.error(request, 'Email Already Exists')
                return JsonResponse({'message':'Email Already Exists'})
            messages.error(request, 'Username Already Exists')
            return JsonResponse({'message':'Username Already Exists'})
        return redirect ('/admin/')


@method_decorator(login_required, name='dispatch')
class ChangePasswordView(View):
    def get(self, request):
        if not request.user.is_superuser:
          return render (request, 'accounts/change_password.html')
        return redirect ('/admin/')
    def post(self, request):
        if not request.user.is_superuser:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if old_password and new_password and confirm_password:
                if request.user.check_password(old_password):
                    if new_password == confirm_password:
                        user = User.objects.get(username=request.user.username)
                        user.set_password(new_password)
                        user.save()
                        messages.info(request, 'Password Change Successfully')
                        return redirect('change-password')
                    messages.error(request, 'New Password and Confirm Password Did Not Match')
                    return redirect('change-password')
                messages.error(request, 'Old Password Is Incorrect')
                return redirect('change-password')
            messages.error(request, 'We Required Old Password and New Password and Confirm Password Fields')
            return redirect('change-password')
        return redirect ('/admin/')


@method_decorator(login_required, name='dispatch')
class UserResponsiveLetterListView(View):
    def get(self, request):
        if not request.user.is_superuser:
            responsive_letters = ResponsiveLetter.objects.filter(user=request.user).order_by('-id')
            return render (request, 'accounts/responsive-letter-list.html', {'responsive_letters':responsive_letters})
        return redirect ('/admin/')


@method_decorator(login_required, name='dispatch')
class UserResponsiveLetterView(View):
    def get(self, request, id):
        if not request.user.is_superuser:
            responsive_letter = ResponsiveLetter.objects.get(id=id)
            return render (request, 'accounts/responsive-letter.html', {'responsive_letter':responsive_letter})
        return redirect ('/admin/')


class NonUserResponsiveLetterView(View):
    def get(self, request, id):
        responsive_letter = ResponsiveLetter.objects.get(id=id)
        return render (request, 'accounts/non-user-responsive-letter.html', {'responsive_letter':responsive_letter})


class NonUserPrivacyPolicyView(View):
    def get(self, request):
        privacy_policy = PrivacyPolicy.objects.all()
        return render (request, 'accounts/non-user-privacy-policy.html', {'privacy_policy':privacy_policy})


@login_required
def generate_user_pdf(request, id, format=None):
    if not request.user.is_superuser:
        responsive_letter = ResponsiveLetter.objects.get(id=id)
        html = render_to_string('accounts/pdf.html', {'responsive_letter': responsive_letter})
        options = {
            'page-size': 'Letter',
            'encoding': "UTF-8",
        }
        # pdfkit.configuration(wkhtmltopdf='/home/mobapps/Desktop') 
        pdf = pdfkit.from_string(html, False, options=options)
        response = HttpResponse(pdf, content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename=" {}.pdf"'.format(responsive_letter)
        response['Content-Disposition'] = 'attachment; filename="responsive_letter.pdf"'
        return response
    return redirect ('/admin/')


def generate_non_user_pdf(request, id, format=None):
    responsive_letter = ResponsiveLetter.objects.get(id=id)
    html = render_to_string('accounts/pdf.html', {'responsive_letter': responsive_letter})
    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }
    # pdfkit.configuration(wkhtmltopdf='/home/mobapps/Desktop') 
    pdf = pdfkit.from_string(html, False, options=options)
    response = HttpResponse(pdf, content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename=" {}.pdf"'.format(responsive_letter)
    response['Content-Disposition'] = 'attachment; filename="responsive_letter.pdf"'
    return response



@method_decorator(login_required, name='dispatch')
class UserPrivacyPolicyView(View):
    def get(self, request):
        if not request.user.is_superuser:
            privacy_policy = PrivacyPolicy.objects.all()
            return render (request, 'accounts/privacy-policy.html', {'privacy_policy':privacy_policy})
        return redirect ('/admin/')


@method_decorator(login_required, name='dispatch')
class PreLogoutView(View):
    def get(self, request):
        if not request.user.is_superuser:
            date = datetime.date.today()
            service = Service.objects.all()
            total_income =Income.objects.filter(payment_date__date__gte=date).aggregate(Sum('service__price'))
            card_income = Income.objects.filter(payment_date__date__gte=date,payment_method= 'Card',).aggregate(Sum('service__price'))
            cash_income = Income.objects.filter(payment_date__date__gte=date,payment_method= 'Cash',).aggregate(Sum('service__price'))
            return render (request,'accounts/pre-logout.html', {'total_income':total_income, 'card_income':card_income, 'cash_income':cash_income, 'service':service})
        return redirect ('/admin/')
    def post(self,request):
        if not request.user.is_superuser:
            remarkcomment=request.POST.get('remarkcomment')
            data=Remark.objects.create(user=request.user, remarkcomment=remarkcomment)
            print(data)
            return redirect ('logout')
        return redirect ('/admin/')


@method_decorator(login_required, name='dispatch')
class UserRemarksListView(View):
    def get(self, request):
        if not request.user.is_superuser:
            remarks = Remark.objects.filter(user=request.user)
            return render (request, 'accounts/remarks-list.html', {'remarks':remarks})
        return redirect ('/admin/')


@method_decorator(login_required, name='dispatch')
class UserRemarkView(View):
    def get(self, request, id):
        if not request.user.is_superuser:
            remark = Remark.objects.get(id=id)
            return render (request, 'accounts/remark.html', {'remark':remark})
        return redirect ('/admin/')


@method_decorator(staff_member_required, name='dispatch')
class AddSignatureView(generic.UpdateView):
    template_name = 'accounts/service_sign.html'
    model = ResponsiveLetter
    fields = ['signature']
    success_url = reverse_lazy('responsive-letter-list')
      

@method_decorator(login_required, name='dispatch')
class UserAddSignatureView(generic.UpdateView):
    template_name = 'accounts/service_sign.html'
    model = ResponsiveLetter
    fields = ['signature']
    success_url = reverse_lazy('user-responsive-letter-list')


class NonUserAddSignatureView(generic.UpdateView):
    template_name = 'accounts/service_sign.html'
    model = ResponsiveLetter
    fields = ['signature']
    success_url = reverse_lazy('non-user-privacy-policy')