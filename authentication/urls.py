from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('otp_verify/', views.otp_verify, name='otp_verify'),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'), # Add this line

]
