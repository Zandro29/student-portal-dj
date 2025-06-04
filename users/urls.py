from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 
from .views import StudentLoginView, FacultyLoginView
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse_lazy
#appname = 'users'

urlpatterns = [
    path('', views.index, name='index'),
    path('dasboard/', views.home, name='home'),
    path('superadmin/', views.create_admin, name='superadmin'),
    path('fdashboard/', views.faculty_dashboard, name='faculty_home'),
    path('register/', views.register, name='register'),
    #path('login/', auth_views.LoginView.as_view(template_name='user/login_bootstrap.html'), name='login'),
    path('login/', StudentLoginView.as_view(), name='login'),
     path('faculty/', FacultyLoginView.as_view(), name='faculty_login'),
    path('logout/', views.custom_logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    #path('profile/update/', views.UserUpdateView.as_view(), name='profile-update'),
    #path('example', views.sample, name='example'),
    path('profile',  views.profile_settings, name='profile'),
    #path('grades',  views.gradesTable, name='grades'),
    path('grades/upload/<int:schedule_id>/', views.grade_uploading, name='grade_upload'),
    #path('profile2',  views.update, name='profile'),
    path('upload-grades/<int:schedule_id>/', views.grade_upload_view, name='grade_uploaded'),
    path('my-grades/', views.student_grades_view, name='student_grades'),
    #path('profile/edit/', views.edit_profile_view, name='edit_profile'),
]