# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/staff/', views.stafflogin, name='loginstaff'),
    path('login/', views.general_login, name='login'),
    path('register/', views.register_student, name='register'),
    path('regis/', views.register_teacher, name='regis'),
    path('success/', views.success_page, name='register_success'),
    path('studentdashboard/', views.student_dashboard, name='studentdashboard'),
    path('teacherdashboard/', views.teacher_dashboard, name='teacherdashboard'),
    path('admindashboard/', views.admin_dashboard, name='admindashboard'),
    path('teacher/<int:pk>/', views.teacher_detail, name='profileteacher'),
    path('teacher/<int:pk>/edit/', views.teacher_edit, name='editprofileteacher'),
    path('student/<int:pk>/', views.student_detail, name='studentprofile'),
    path('student/<int:pk>/edit/', views.student_edit, name='editprofilestudent'),
    path('admindashboard/system/', views.regissystem, name='semester'),
    path('admindashboard/system/delete/<int:pk>/', views.delete_system, name='deletesystem'),
    path('teacherdashboard/sectionmanage/', views.assign_section, name='assign_section'),
    path('toggle-registration/<int:semester_id>/', views.toggle_registration, name='toggle_registration'),
    path('register-course/', views.course_registration_view, name='course_registration'),
    path('course/request/', views.request_course, name='student_course_request'),
    path('course/teacher/approve/', views.teacher_approve_requests, name='teacher_approve_requests'),
    path('course/admin/approve/', views.admin_approve_requests, name='admin_approve_requests'),
    path('course/requests/status/', views.all_requests_status, name='all_requests_status'),
]