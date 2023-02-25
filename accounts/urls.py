from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('service-reports/', views.ReportsView.as_view(), name='service-reports'),
    path('service-reports-by-mall/', views.ReportsByMallView.as_view(), name='service-reports-by-mall'),
    path('responsive-letter-list/', views.ResponsiveLetterListView.as_view(), name='responsive-letter-list'),
    path('responsive-letter/<int:id>/', views.ResponsiveLetterView.as_view(), name='responsive-letter'),
    path('responsive-signature/<int:pk>/', views.AddSignatureView.as_view(), name='responsive-signature'),
    path('user-responsive-signature/<int:pk>/', views.UserAddSignatureView.as_view(), name='user-responsive-signature'),
    path('non-user-responsive-signature/<int:pk>/', views.NonUserAddSignatureView.as_view(), name='non-user-responsive-signature'),
    path('generate-pdf/<int:id>/', views.generate_pdf, name='generate-pdf'),
    path('generate-privacy-pdf/', views.generate_privacy_pdf, name='generate-privacy-pdf'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('service/', views.ServiceView.as_view(), name='service'),
    path('select-service/', views.ServiceSelectView.as_view(), name='select-service'),
    path('customer/', views.CustomerView.as_view(), name='customer'),
    path('started-service-list/', views.StartedServiceListView.as_view(), name='started-service-list'),
    path('ended-service-list/', views.EndedServiceListView.as_view(), name='ended-service-list'),
    path('setting/', views.SettingView.as_view(), name='setting'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('user-responsive-letter-list/', views.UserResponsiveLetterListView.as_view(), name='user-responsive-letter-list'),
    path('user-responsive-letter/<int:id>/', views.UserResponsiveLetterView.as_view(), name='user-responsive-letter'),
    path('generate-user-pdf/<int:id>/', views.generate_user_pdf, name='generate-user-pdf'),
    path('non-user-responsive-letter/<int:id>/', views.NonUserResponsiveLetterView.as_view(), name='non-user-responsive-letter'),
    path('generate-non-user-pdf/<int:id>/', views.generate_non_user_pdf, name='generate-non-user-pdf'),
    path('non-user-privacy-policy/', views.NonUserPrivacyPolicyView.as_view(), name='non-user-privacy-policy'),
    path('user-policy-policy/', views.UserPrivacyPolicyView.as_view(), name='user-policy-policy'),
    path('pre-logout/', views.PreLogoutView.as_view(), name='pre-logout'),
    path('remarks-list/', views.UserRemarksListView.as_view(), name='remarks-list'),
    path('remark/<int:id>/', views.UserRemarkView.as_view(), name='remark'),
]