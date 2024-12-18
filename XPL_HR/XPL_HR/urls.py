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
from django.shortcuts import redirect


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
    path('leave_policy/',views.leave_policy, name='leave_policy'),
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
    path('payment_terms/',views.payment_terms, name='payment_terms'),
    path('add_payment_terms/',views.add_payment_terms, name='add_payment_terms'),
    path('payment_term_delete/<int:pk>/', views.payment_term_delete_view, name='payment_term_delete'),
    path('edit_client/<int:client_id>/', views.edit_client, name='edit_client'),
    path('delete_client/<int:client_id>/', views.delete_client, name='delete_client'),
    path('get-client-contacts/<int:client_id>/', views.get_client_contacts, name='get_client_contacts'),
    path('api/project/<int:project_id>/', views.get_project_details, name='get_project_details'),
    path('leave_config_dashboard/', views.leave_config_dash, name='leave_config_dashboard'),
    path('view_client/<int:client_id>/', views.client_detail_view, name='view_client'),
    path('api/employees/', views.EmployeeList.as_view(), name='employee-list'),
    path('add_leave_policy/', views.add_leave_policy, name='add_leave_policy'),
    path('billing_types/', views.billingtypes, name='billing_types'),
    path('add_billing_types/', views.add_billing_types, name='add_billing_types'),
    path('document_types/', views.doc_types, name='document_types'),
    path('add_document_types/', views.add_doc_types, name='add_document_types'),
    path('delete_doc_types/<int:id>/', views.delete_doc_type, name='delete_doc_types'),
    path('delete_billing_types/<int:id>/', views.delete_billing_type, name='delete_billing_types'),
    path('delete_leave_policy/<int:id>/', views.delete_leave_policy, name='delete_leave_policy'),
    path('edit_leave_policy/<int:id>/', views.edit_leave_policy, name='edit_leave_policy'),
    path('edit_billing_types/<int:id>/', views.edit_billing_type, name='edit_billing_types'),
    path('edit_doc_types/<int:id>/', views.edit_doc_type, name='edit_doc_types'),
    path('edit_payment_terms/<int:id>/', views.edit_payment_terms, name='edit_payment_terms'),
    path('settings/', lambda request: redirect('billing_types'), name='settings'),
    path('position/', views.employee_position, name='position'),
    path('add_position/', views.add_employee_position, name='add_position'),
    path('delete_position/<int:id>/', views.delete_employee_position, name='delete_position'),
    path('edit_position/<int:id>/', views.edit_employee_position, name='edit_position'),
    path('industry/', views.employee_industry, name='industry'),
    path('add_industry/', views.add_employee_industry, name='add_industry'),
    path('delete_industry/<int:id>/', views.delete_employee_industry, name='delete_industry'),
    path('edit_industry/<int:id>/', views.edit_employee_industry, name='edit_industry'),
    path('role/', views.employee_role, name='role'),
    path('add_role/', views.add_employee_role, name='add_role'),
    path('delete_role/<int:id>/', views.delete_employee_role, name='delete_role'),
    path('edit_role/<int:id>/', views.edit_employee_role, name='edit_role'),
    path('calculate-available-leaves/', views.calculate_available_leaves, name='calculate_available_leaves'),
    path('payroll_uae/', views.payroll_uae, name='payroll_uae'),
    path('payroll/', lambda request: redirect('payroll_uae'), name='payroll'),
    path('generate_payroll', views.generate_payroll, name='generate_payroll'),
    path('edit_leave_application/<int:id>/', views.leave_application_edit, name='edit_leave_application'),
    path('delete_leave_application/<int:id>/', views.delete_leave_application, name='delete_leave_application'),








]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
