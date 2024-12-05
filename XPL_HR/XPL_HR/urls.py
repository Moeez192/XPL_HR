"""XPL_HR URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main_admin import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.login_view, name='login'),
    path('files/',views.files, name='files'),
    path('delete/<int:document_id>/',views.delete_document, name='delete_document'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('forget_pwd/',views.forget_pwd, name='forget_pwd'),
    path('employees/',views.employees, name='employees'),
    path('add_employee/',views.add_employee, name='add_employee'),
    path('add_department/',views.add_department, name='add_department'),
    path('leave/',views.leave,name='leave'),
    path('leave/edit/<int:leave_id>/',views.edit_leave, name='edit_leave'),
    path('leave/delete/<int:leave_id>/',views.delete_leave, name='delete_leave'),
    path('projects/',views.projects,name='projects'),
    path('employees/<int:pk>/delete/', views.employee_delete_view, name='employee_delete'),
    path('employee/edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('edit_employee_self/',views.edit_employee_self, name='edit_employee_self'),
    path('department/edit/<int:department_id>/', views.edit_department, name='edit_department'),
    path('departments/delete/<int:department_id>/', views.delete_department, name='delete_department'),
    path('projects/delete/<int:pk>/',views.project_delete_view, name='delete_project'),
    path('projects/edit/<int:pk>/',views.project_edit_view, name='edit_project'),
    path('projects/<int:pk>/',views.project_detail_view, name='project_detail'),
    path('timesheet/',views.timesheet, name='timesheet'),
    path('settings/',views.setting, name='settings'),
    path('timesheet/action/<int:timesheet_id>/', views.timesheet_action, name='timesheet_action'),
    path('timesheet/download/<str:month>/', views.download_timesheet_pdf, name='download_timesheet'),
    path('calculate_salary/<int:employee_id>/', views.calculate_employee_salary, name='calculate_employee_salary'),
    path('delete_timesheet/<str:timesheet_group_id>/', views.delete_timesheet, name='delete_timesheet'),
    path('timesheet/edit/<str:timesheet_group_id>/', views.edit_timesheet, name='edit_timesheet'),
    path('submit_timesheet/<str:timesheet_group_id>/', views.submit_timesheet, name='submit_timesheet'),
    path('view_timesheet_group/<str:timesheet_group_id>/', views.view_timesheet, name='view_timesheet'), 
    path('accept_timesheet/<str:timesheet_group_id>/', views.accept_timesheet, name='accept_timesheet'),
    path('delete-date-range/<int:date_range_id>/', views.delete_date_range, name='delete_date_range'),
    path('project/<int:file_id>/', views.delete_project_file, name='delete_project_file'),
    path('employee/document/delete/<int:document_id>/', views.delete_employee_document, name='delete_employee_document'),
    path('departments/',views.department, name='departments'),
    path('clients/',views.clients, name='clients'),
    path('add_project/',views.add_project, name='add_project'),
    path('add_timesheet/',views.add_timesheet, name='add_timesheet'),
    path('timesheet_date_range/',views.timesheet_date_range, name='timesheet_date_range'),
    path('apply_leave/',views.apply_leave, name='apply_leave'),
    path('leave_configuration/',views.leave_configuration, name='leave_configuration'),
    path('add_client/',views.add_client, name='add_client'),








]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
