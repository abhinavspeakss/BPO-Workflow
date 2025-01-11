from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('case/<str:case_id>/', views.case_detail, name='case_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='workflow/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
