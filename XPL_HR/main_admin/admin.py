from django.contrib import admin
from .models import *

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'employee_id', 'email', 'job_title', 'employee_status')
    search_fields = ('first_name', 'last_name', 'employee_id', 'email')
    list_filter = ('employee_status', 'employee_role', 'employment_type')
    ordering = ('employee_id',)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('dep_name', 'dep_code', 'dep_head', 'dep_description')
    search_fields = ('dep_name', 'dep_code')
    list_filter = ('dep_head',)
    ordering = ('dep_name',)

admin.site.register(Department, DepartmentAdmin)
admin.site.register(Employee, EmployeeAdmin)
