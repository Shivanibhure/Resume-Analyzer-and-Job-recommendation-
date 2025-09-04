from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('result/<int:resume_id>/', views.analysis_result, name='analysis_result'),
    path('', views.upload_resume, name='home'),
]
