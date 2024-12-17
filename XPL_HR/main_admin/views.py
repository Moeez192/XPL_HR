from django.shortcuts import render, redirect , get_object_or_404
from .forms import EmployeeForm , DepForm , LeaveForm , LoginForm , ProjectForm , LeaveApplicationForm , EmployeeUpdateForm , EducationalDocumentForm , TimesheetForm , ApprovalHierarchyForm , PeriodForm , ProjectFileForm, LeavePolicyForm, uploadDocTypeForm,BillingTypeForm,ClientInformationForm , PaymentTermsForm, ClientLeaveFormSet , ClientLeaveForm, XPL_ClientContactForm ,XPL_EmployeeBillingForm , XPL_PositionForm,XPL_IndustryForm , XPL_EmployeeRoleForm
from .models import Employee , Department , Leaves , Projects , LeaveApplication , EducationalDocument, Timesheet , Salary, Hierarchy , DateRange , ProjectFile , PasswordResetToken,LeavePolicy , uploadDocType , EmployeeDocument , BillingType , ClientInformation , PaymentTerms,ClientLeave,XPL_ClientContact , XPL_EmployeeBilling , XPL_EmployeeRole, XPL_Position , XPL_Industry
from django.contrib import messages
from django.core.mail import send_mail
import uuid  
from django.utils import timezone
import json
from django.db import transaction
import logging
from django.db.models import Min, Max
from datetime import timedelta
from django.conf import settings
from calendar import monthrange
from django.db.models import Q  
from weasyprint import HTML
from collections import defaultdict
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import get_template
from django.views.decorators.http import require_POST
from calendar import month_name
from django.shortcuts import render
from django.contrib.auth import logout
from .models import Employee 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.utils.decorators import decorator_from_middleware
from django.middleware.cache import CacheMiddleware
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EmployeeSerializer
from django.http import JsonResponse

logger = logging.getLogger(__name__)



class EmployeeList(APIView):
    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

class NoCacheMiddleware(CacheMiddleware):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.cache_timeout = 0

    def process_response(self, request, response):
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        return response

no_cache = decorator_from_middleware(NoCacheMiddleware)

from django.http import JsonResponse
from .models import Employee, Leaves
from datetime import datetime


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@csrf_exempt
def calculate_available_leaves(request):
    if request.method == 'POST':
        leave_type_id = request.POST.get('leave_type_id')
        employee_id = Employee.objects.get(email=request.user.email).id
        
        if not leave_type_id or not employee_id:
            return JsonResponse({'error': 'Missing required parameters'}, status=400)

        try:
            leave_type = Leaves.objects.get(id=leave_type_id)
            employee = Employee.objects.get(id=employee_id)
        except Leaves.DoesNotExist:
            return JsonResponse({'error': 'Invalid leave type ID'}, status=404)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Invalid employee ID'}, status=404)

        # Calculate available leaves
        total_leave_days = leave_type.leave_days_allowed
        monthly_leave_entitlement = total_leave_days / 12

        start_date = employee.date_of_joining
        current_date = datetime.now()
        months_worked = (current_date.year - start_date.year) * 12 + current_date.month - start_date.month
        available_leaves = months_worked * monthly_leave_entitlement

        # Deduct previously availed leaves
        approved_leaves = LeaveApplication.objects.filter(
                employee=employee,
                leave_type=leave_type,
                status='approved'
            )
        print(f"Approved Leaves: {approved_leaves}")

        leaves_taken = sum(
                (leave.end_date - leave.start_date).days + 1 for leave in approved_leaves if leave.end_date and leave.start_date
            )

        available_leaves -= leaves_taken

        return JsonResponse({'available_leaves': max(0, available_leaves)})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

  
@login_required
@no_cache
def employee_position(request):
    positions = XPL_Position.objects.all()
    return render(request, 'templates/sub_templates/employee_position.html', {
        'positions': positions,
    })

@login_required
@no_cache
def delete_employee_position(request, id):
    position = get_object_or_404(XPL_Position, id=id)
    position.delete()
    messages.success(request, 'Position deleted successfully!')
    return redirect('position')

@login_required
@no_cache
def edit_employee_position(request, id):
    position = get_object_or_404(XPL_Position, id=id)
    if request.method == 'POST':
        position_form = XPL_PositionForm(request.POST, instance=position)
        if position_form.is_valid():
            position_form.save()
            messages.success(request, 'Position updated successfully!')
            return redirect('position')
    else:
        position_form = XPL_PositionForm(instance=position)
    return render(request, 'templates/sub_templates/edit_employee_position.html', {
        'position_form': position_form,
        'position': position,
    })

@login_required
@no_cache
def add_employee_position(request):
    position_form = XPL_PositionForm(request.POST)
    if request.method == 'POST':
            position_form = XPL_PositionForm(request.POST)
            if position_form.is_valid():
                position_form.save()
                messages.success(request, 'Position added successfully!')
                return redirect('position')
    else:
        position_form = XPL_PositionForm()
    return render(request, 'templates/sub_templates/add_employee_position.html', {
        'position_form': position_form,
    })

@login_required
@no_cache
def employee_role(request):
    roles = XPL_EmployeeRole.objects.all()
    return render(request, 'templates/sub_templates/employee_role.html', {
        'roles': roles,
    })

@login_required
@no_cache
def add_employee_role(request):
    role_form = XPL_EmployeeRoleForm(request.POST)
    if request.method == 'POST':
            role_form = XPL_EmployeeRoleForm(request.POST)
            if role_form.is_valid():
                role_form.save()
                messages.success(request, 'Role added successfully!')
                return redirect('role')
    else:
        role_form = XPL_EmployeeRoleForm()
    return render(request, 'templates/sub_templates/add_employee_role.html', {
        'role_form': role_form,
    })

@login_required
@no_cache
def delete_employee_role(request, id):
    role = get_object_or_404(XPL_EmployeeRole, id=id)
    role.delete()
    messages.success(request, 'Role deleted successfully!')
    return redirect('role')

@login_required
@no_cache
def edit_employee_role(request, id):
    role = get_object_or_404(XPL_EmployeeRole, id=id)
    if request.method == 'POST':
        role_form = XPL_EmployeeRoleForm(request.POST, instance=role)
        if role_form.is_valid():
            role_form.save()
            messages.success(request, 'Role updated successfully!')
            return redirect('role')
    else:
        role_form = XPL_EmployeeRoleForm(instance=role)
    return render(request, 'templates/sub_templates/edit_employee_role.html', {
        'role_form': role_form,
        'role': role,
    })

@login_required
@no_cache
def employee_industry(request):
    industries = XPL_Industry.objects.all()
    return render(request, 'templates/sub_templates/employee_industry.html', {
        'industries': industries,
    })

@login_required
@no_cache
def add_employee_industry(request):
    industry_form = XPL_IndustryForm(request.POST)
    if request.method == 'POST':
            industry_form = XPL_IndustryForm(request.POST)
            if industry_form.is_valid():
                industry_form.save()
                messages.success(request, 'Industry added successfully!')
                return redirect('industry')
    else:
        industry_form = XPL_IndustryForm()
    return render(request, 'templates/sub_templates/add_employee_industry.html', {
        'industry_form': industry_form,
    })

@login_required
@no_cache
def delete_employee_industry(request, id):
    industry = get_object_or_404(XPL_Industry, id=id)
    industry.delete()
    messages.success(request, 'Industry deleted successfully!')
    return redirect('industry')

@login_required
@no_cache
def edit_employee_industry(request, id):
    industry = get_object_or_404(XPL_Industry, id=id)
    if request.method == 'POST':
        industry_form = XPL_IndustryForm(request.POST, instance=industry)
        if industry_form.is_valid():
            industry_form.save()
            messages.success(request, 'Industry updated successfully!')
            return redirect('industry')
    else:
        industry_form = XPL_IndustryForm(instance=industry)
    return render(request, 'templates/sub_templates/edit_employee_industry.html', {
        'industry_form': industry_form,
        'industry': industry,
    })

@login_required
@no_cache
def logout_view(request):
    logout(request)
    return redirect('login')

@no_cache
def login_view(request):
    form = LoginForm(request.POST)
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(request, email=email, password=password)

        if user is not None:
            print("User authenticated successfully")
            login(request, user)  
            
            #  role from  Employee model 
            try:
                employee = Employee.objects.get(email=email)
                request.session['role'] = employee.employee_role.id
                
                print("Session after login:", request.session.keys())  
                return redirect("dashboard")  
            except Employee.DoesNotExist:
                messages.error(request, "Employee data not found.")
                return render(request, "templates/login.html", {"form": form})

        else:
            print("Authentication failed")
            messages.error(request, "Invalid email or password.")
            return render(request, "templates/login.html", {"form": form})

    return render(request, "templates/login.html", {"form": form})

@login_required
@no_cache
def dashboard(request):
    print("User authenticated:", request.user.is_authenticated)  
    return render(request, "templates/dashboard.html")


@login_required
@no_cache
@require_POST
def employee_delete_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    messages.success(request,"Employee Deleted Successfully")
    return redirect('employees')


@login_required
@no_cache
def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)

        with transaction.atomic():

            if form.is_valid():
                form.save()  
                print("Employee data saved successfully.")

                
                for key in request.FILES:
                    if key.startswith('file_'):
                        document_id = key.split('_')[1]  
                        document = EmployeeDocument.objects.filter(id=document_id, employee=employee).first()

                        if document:
                            issue_date = request.POST.get(f'issue_date_{document_id}')
                            expiry_date = request.POST.get(f'expiry_date_{document_id}')
                            notes = request.POST.get(f'notes_{document_id}')

                            file = request.FILES.get(key)

                            if file:
                                document.file = file
                                print(f"Updated file for document {document_id}: {file.name}")

                            document.issue_date = issue_date
                            document.expiry_date = expiry_date
                            document.notes = notes
                            print(f"Updated document {document_id}: issue_date={issue_date}, expiry_date={expiry_date}, notes={notes}")

                            document.save()
                            print(f"Document {document.id} updated successfully.")
                doc_counter = {}  

                for key in request.FILES:
                    if '_file_' in key:  
                        doc_type = key.split('_file_')[0]
                        doc_count = key.split('_file_')[1]  
                        issue_date = request.POST.get(f'{doc_type}_issue_date_{doc_count}')
                        expiry_date = request.POST.get(f'{doc_type}_expiry_date_{doc_count}')
                        notes = request.POST.get(f'{doc_type}_notes_{doc_count}')
                        file = request.FILES[key]

                        if not file or not issue_date or not expiry_date:
                            messages.error(request, f"Missing fields for {doc_type.capitalize()} document. Please fill all fields.")
                            raise ValueError(f"Missing fields for {doc_type.capitalize()} document.")

                        try:
                            document_type = uploadDocType.objects.get(doc_type=doc_type)  
                        except uploadDocType.DoesNotExist:
                            document_type = None
                            messages.error(request, f"Document type '{doc_type.capitalize()}' not found in the database.")
                            raise ValueError(f"Document type '{doc_type.capitalize()}' not found in the database.")

                        if document_type:
                            EmployeeDocument.objects.create(
                                employee=employee,
                                doctype=document_type,  
                                file=file,
                                issue_date=issue_date,
                                expiry_date=expiry_date,
                                notes=notes
                            )
                            print(f"New document {file.name} added successfully.")

                messages.success(request, 'Employee Updated')
                return redirect('employees') 

    else:
        form = EmployeeForm(instance=employee)

    existing_documents = EmployeeDocument.objects.filter(employee=employee)
    print(f"Existing documents for employee {employee_id}: {existing_documents}")

    
    
    return render(request, 'templates/sub_templates/edit_employee.html', {
        'form': form,
        'employee': employee,
        'existing_documents': existing_documents,
    })

@login_required
@no_cache
def delete_employee_document(request, document_id):
    document = get_object_or_404(EmployeeDocument, id=document_id)
    employee_id = document.employee.id  
    
    
    document.delete()
    
    messages.success(request, f"Document {document.doctype.doc_type} deleted successfully!")
    return redirect('edit_employee', employee_id=employee_id)

@login_required
@no_cache
def clients(request):
    clients=ClientInformation.objects.all()
    return render(request, 'templates/clients.html',{
        'clients': clients,
    })

@login_required
@no_cache
def edit_employee_self(request):
    employee = Employee.objects.get(email=request.user.email)
    if request.method == 'POST':
        form = EmployeeUpdateForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Edited Successfully')
            return redirect('edit_employee_self')  # Redirect to the employee list or details page after saving
    else:
        form = EmployeeUpdateForm(instance=employee)
    
    return render(request, 'templates/sub_templates/edit_employee_self.html', {
        'form': form, 
        'employee': employee,
        })
    
    
@login_required
@no_cache
def edit_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        form = DepForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('employees')  # Redirect to department list
    else:
        form = DepForm(instance=department)

    return render(request, 'templates/sub_templates/edit_dep.html', {
        'form': form,
        'department': department
    })


@login_required
@no_cache
def delete_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    department.delete()
    messages.success(request, 'Department deleted successfully!')
    return redirect('employees')

@login_required
@no_cache
def add_employee(request):
    employee_form = EmployeeForm(request.POST, request.FILES)
    if request.method == 'POST':
        if 'employee_submit' in request.POST:
            employee_form = EmployeeForm(request.POST, request.FILES)

        if employee_form.is_valid():
            with transaction.atomic():
                employee = employee_form.save()

                doc_counter = {}  
                for key in request.FILES:
                    if '_file_' in key:
                        doc_type = key.split('_file_')[0]
                        doc_count = key.split('_file_')[1]  # To differentiate multiple fields of the same type
                        issue_date = request.POST.get(f'{doc_type}_issue_date_{doc_count}')
                        expiry_date = request.POST.get(f'{doc_type}_expiry_date_{doc_count}')
                        notes = request.POST.get(f'{doc_type}_notes_{doc_count}')
                        file = request.FILES[key]

                        # if not file or not issue_date or not expiry_date:
                        #     messages.error(request, f"Missing fields for {doc_type.capitalize()} document. Please fill all fields.")
                        #     # Rollback transaction
                        #     raise ValueError(f"Missing fields for {doc_type.capitalize()} document.")

                        try:
                            document_type = uploadDocType.objects.get(doc_type=doc_type.capitalize())  # Use doc_type instead of name
                        except uploadDocType.DoesNotExist:
                            document_type = None
                            messages.error(request, f"Document type '{doc_type.capitalize()}' not found in the database.")
                            raise ValueError(f"Document type '{doc_type.capitalize()}' not found in the database.")

                        if document_type:
                            EmployeeDocument.objects.create(
                                employee=employee,
                                doctype=document_type,  
                                file=file,
                                issue_date=issue_date,
                                expiry_date=expiry_date,
                                notes=notes
                            )
                        else:
                            
                            raise ValueError(f"Document type '{doc_type.capitalize()}' could not be found in the database.")

                messages.success(request, "Employee and documents saved successfully!")
                return redirect('employees')
    else:
            employee_form = EmployeeForm()
    return render(request, 'templates/sub_templates/add_emp.html', {
        'form': employee_form,
        
    })

@login_required
@no_cache
def add_department(request):
    department_form = DepForm(request.POST)

    if request.method == 'POST':
        if 'department_submit' in request.POST:
            department_form = DepForm(request.POST)
            if department_form.is_valid():
                department_form.save()
                messages.success(request, 'Department added successfully!')
                return redirect('employees')  
    else:
        department_form = DepForm()  

    return render(request, 'templates/sub_templates/add_dep.html', {
        'dep_form': department_form,
    })

@login_required
@no_cache
def department(request):
    departments = Department.objects.all()
    return render(request, 'templates/departments.html', {
        'dep_list': departments,
    })


@login_required
@no_cache
def employees(request):
     # Handle employee form
    total_employees = Employee.objects.count()
    # total_supervisors = Employee.objects.filter(is_supervisor='yes').count()
    department_list = Department.objects.all()
    department_form = DepForm(request.POST)
    total_departments = Department.objects.count()
    employee_form = EmployeeForm(request.POST, request.FILES)
    employee_list = Employee.objects.all()

    if request.method == 'POST':
        if 'employee_submit' in request.POST:
            employee_form = EmployeeForm(request.POST, request.FILES)

        if employee_form.is_valid():
            with transaction.atomic():
                employee = employee_form.save()

                doc_counter = {}  
                for key in request.FILES:
                    if '_file_' in key:
                        doc_type = key.split('_file_')[0]
                        doc_count = key.split('_file_')[1]  # To differentiate multiple fields of the same type
                        issue_date = request.POST.get(f'{doc_type}_issue_date_{doc_count}')
                        expiry_date = request.POST.get(f'{doc_type}_expiry_date_{doc_count}')
                        notes = request.POST.get(f'{doc_type}_notes_{doc_count}')
                        file = request.FILES[key]

                        if not file or not issue_date or not expiry_date:
                            messages.error(request, f"Missing fields for {doc_type.capitalize()} document. Please fill all fields.")
                            # Rollback transaction
                            raise ValueError(f"Missing fields for {doc_type.capitalize()} document.")

                        try:
                            document_type = uploadDocType.objects.get(doc_type=doc_type.capitalize())  # Use doc_type instead of name
                        except uploadDocType.DoesNotExist:
                            document_type = None
                            messages.error(request, f"Document type '{doc_type.capitalize()}' not found in the database.")
                            raise ValueError(f"Document type '{doc_type.capitalize()}' not found in the database.")

                        if document_type:
                            EmployeeDocument.objects.create(
                                employee=employee,
                                doctype=document_type,  
                                file=file,
                                issue_date=issue_date,
                                expiry_date=expiry_date,
                                notes=notes
                            )
                        else:
                            # If document_type is None, rollback
                            raise ValueError(f"Document type '{doc_type.capitalize()}' could not be found in the database.")

                messages.success(request, "Employee and documents saved successfully!")
                return redirect('employees')
        if 'department_submit' in request.POST:
            department_form = DepForm(request.POST)
            if department_form.is_valid():
                department_form.save()
                messages.success(request, 'Department added successfully!')
                return redirect('employees')  
    else:
        employee_form = EmployeeForm()  
        department_form = DepForm()  

    return render(request, 'templates/employees.html', {
        'form': employee_form,
        'total_employees': total_employees,
        'total_departments': total_departments,
        'dep_list': department_list,
        # 'total_supervisors':total_supervisors,
        'employee_list': employee_list,
        'dep_form': department_form,
    })






@login_required
@no_cache
def leave_config_dash(request):
    leaves=Leaves.objects.all()
    return render(request, 'templates/sub_templates/leave_config_dash.html', {
        'forms' : leaves,
    })


@login_required
@no_cache
def leave_configuration(request):
    leave_form = LeaveForm()
    if request.method == 'POST':
        if 'leave_form' in request.POST:
                leave_form = LeaveForm(request.POST)
                if leave_form.is_valid():
                 leave_form.save()
                 messages.success(request, 'Leave information has been successfully submitted!')
                return redirect('leave_config_dashboard')
       
    return render(request, 'templates/sub_templates/configure_leaves.html', {
        'leave_form': leave_form,
    })

# @login_required
# @no_cache
# def apply_leave(request):
#     leaves=Leaves.objects.all()
#     employee = Employee.objects.get(email=request.user.email)
#     leave_applications_to_approve = LeaveApplication.objects.none()
#     logged_in_user = LeaveApplication.objects.filter(employee=employee)

#     def get_hierarchy_for_role(employee, project=None):
#         # First, try to fetch project-specific hierarchy
#         if project:
#             hierarchy = Hierarchy.objects.filter(
#                 project_name=project,
#                 position=employee.position
#             ).order_by('order_number')
#             if hierarchy.exists():
#                 return hierarchy

#         # Fall back to role-based hierarchy if no project-specific hierarchy exists
#         return Hierarchy.objects.filter(
#             position=employee.position,
#             project_name=None
#         ).order_by('order_number')

#     def advance_to_next_approver(leave_application, approvers):
#         # Identify the current approver in the list
#         current_index = approvers.index(leave_application.current_approver) if leave_application.current_approver in approvers else -1
#         next_index = current_index + 1

#         # Move to the next approver if available; otherwise, mark as approved
#         if next_index < len(approvers):
#             leave_application.current_approver = approvers[next_index]
#             leave_application.status = 'pending'
#         else:
#             leave_application.current_approver = None
#             leave_application.status = 'approved'
#         leave_application.save()

#     # Collect leave applications for approval
#     all_applications = LeaveApplication.objects.all()
#     for application in all_applications:
#         submitter = application.employee
#         project_assignment = Projects.objects.filter(team_members=submitter).first()
        
#         # Fetch appropriate hierarchy
#         hierarchy = get_hierarchy_for_role(submitter, project=project_assignment)
#         approvers = [entry.approver for entry in hierarchy]

#         if employee in approvers:
#             leave_applications_to_approve |= LeaveApplication.objects.filter(id=application.id)

#     leave_form = LeaveForm()
#     leave_application_form = LeaveApplicationForm(employee=employee)

#     if request.method == 'POST':
#         if 'leave_form' in request.POST:
#                 leave_form = LeaveForm(request.POST)
#                 if leave_form.is_valid():
#                  leave_form.save()
#                  messages.success(request, 'Leave information has been successfully submitted!')
#                 return redirect('leave')
#         if 'leave_application_form' in request.POST:
#             leave_application_form = LeaveApplicationForm(request.POST, employee=employee)
#             if leave_application_form.is_valid():
#                 # Check if the employee is assigned to any project
#                projects = Projects.objects.filter(team_members=employee)
                
#                hierarchy = None
#                for project in projects:
#                     # First, try finding hierarchy specific to the role and project
#                     hierarchy = Hierarchy.objects.filter(position=employee.position, project_name=project).order_by('order_number')
#                     if hierarchy.exists():
#                         break
                
#                 # If no project-specific hierarchy exists, check for a general role-based hierarchy
#                if not hierarchy or not hierarchy.exists():
#                     hierarchy = Hierarchy.objects.filter(position=employee.position, project_name__isnull=True).order_by('order_number')

#                if hierarchy.exists():
#                     # Proceed with saving the leave application if a hierarchy exists
#                     leave_application = leave_application_form.save(commit=False)
#                     leave_application.employee = employee

#                     # Set the first approver in the hierarchy
#                     leave_application.current_approver = hierarchy.first().approver
#                     leave_application.status = 'pending'
#                     leave_application.save()
                    
#                     messages.success(request, 'Leave application has been successfully submitted!')
#                else:
#                     # If no hierarchy is found, show an error message and don't save the application
#                     messages.error(request, "No approval hierarchy exists for your role and project. Please contact HR for assistance.")
                
#                return redirect('leave')
#             else:
#                 error_message = ""
#                 non_field_errors = leave_application_form.errors.get('__all__', [])
#                 for error in non_field_errors:
#                         error_message += f"{error}" 
#                 for field, errors in leave_application_form.errors.items():
#                         if field != '__all__':
#                             for error in errors:
#                                 error_message += f"<strong>{field}</strong>: {error}<br>"
    
#                 messages.error(request,error_message)
                
#                 leave_application_form = LeaveApplicationForm(employee=employee)

#         elif 'status' in request.POST:
#             leave_application_id = request.POST.get('leave_application_id')
#             leave_application = LeaveApplication.objects.get(id=leave_application_id)

#             # Fetch submitter and hierarchy for the application
#             submitter = leave_application.employee
#             project_assignment = Projects.objects.filter(team_members=submitter).first()
#             hierarchy = get_hierarchy_for_role(submitter, project=project_assignment)
#             approvers = [entry.approver for entry in hierarchy]

#             if leave_application.current_approver == employee:
#                 # If status is 'rejected', update and save immediately
#                 if request.POST.get('status') == 'rejected':
#                     leave_application.status = 'rejected'
#                     leave_application.remarks = request.POST.get('remarks', '')
#                     leave_application.current_approver = None
#                     leave_application.save()
#                     messages.success(request, 'Leave application rejected.')
#                     return redirect('leave')

#                 # Otherwise, advance to the next approver or approve fully
#                 advance_to_next_approver(leave_application, approvers)
#                 messages.success(request, 'Leave application status updated.')
#                 return redirect('leave')

#     return render(request, 'templates/sub_templates/apply_leave.html', {
#         'leave_form': leave_form,
#         'leave_application_form': leave_application_form,
#         'leave_applications': leave_applications_to_approve,
#         'logged_in_user': logged_in_user,
#         'all_leaves' : leaves,
#     })


@login_required
@no_cache
def leave(request):
    employee = Employee.objects.get(email=request.user.email)
    leaves = Leaves.objects.all()

    leave_applications_to_approve = LeaveApplication.objects.filter(current_approver_id=employee, status='pending')
    print("Applications for approval:", leave_applications_to_approve)  # Debugging
    logged_in_user = LeaveApplication.objects.filter(employee=employee)

    leave_form = LeaveForm()
    leave_application_form = LeaveApplicationForm(employee=employee)

    if request.method == 'POST':
        if 'leave_application_form' in request.POST:
            leave_application_form = LeaveApplicationForm(request.POST, employee=employee)
            if leave_application_form.is_valid():
                leave_application = leave_application_form.save(commit=False)
                leave_application.employee = employee

                # Set approver from the Leaves table
                leave_type = leave_application.leave_type
                if leave_type and leave_type.leave_approver:
                    leave_application.current_approver = leave_type.leave_approver
                    leave_application.status = 'pending'
                    leave_application.save()
                    messages.success(request, 'Leave application has been successfully submitted!')
                else:
                    messages.error(request, "No approver is assigned for the selected leave type. Please contact HR.")

                return redirect('leave')
            else:
                # Handle form errors
                error_message = ""
                non_field_errors = leave_application_form.errors.get('__all__', [])
                for error in non_field_errors:
                    error_message += f"{error}" 
                for field, errors in leave_application_form.errors.items():
                    if field != '__all__':
                        for error in errors:
                            error_message += f"<strong>{field}</strong>: {error}<br>"

                messages.error(request, error_message)
                leave_application_form = LeaveApplicationForm(employee=employee)

        elif 'status' in request.POST:
            leave_application_id = request.POST.get('leave_application_id')
            leave_application = LeaveApplication.objects.get(id=leave_application_id)

            if leave_application.current_approver == employee:
                if request.POST.get('status') == 'rejected':
                    leave_application.status = 'rejected'
                    leave_application.remarks = request.POST.get('remarks', '')
                    leave_application.current_approver = None
                    leave_application.save()
                    messages.success(request, 'Leave application rejected.')
                    return redirect('leave')

                if request.POST.get('status') == 'approved':
                    leave_application.status = 'approved'
                    leave_application.current_approver = None
                    leave_application.save()
                    messages.success(request, 'Leave application approved.')
                    return redirect('leave')

    return render(request, 'templates/leave.html', {
        'leave_form': leave_form,
        'leave_application_form': leave_application_form,
        'leave_applications': leave_applications_to_approve,  
        'logged_in_user': logged_in_user, 
        'all_leaves': leaves,  
    })

@login_required
@no_cache
def apply_leave(request):
    employee = Employee.objects.get(email=request.user.email)
    leaves = Leaves.objects.all()

    leave_applications_to_approve = LeaveApplication.objects.filter(current_approver_id=employee, status='pending')
    print("Applications for approval:", leave_applications_to_approve)  # Debugging
    logged_in_user = LeaveApplication.objects.filter(employee=employee)

    leave_form = LeaveForm()
    leave_application_form = LeaveApplicationForm(employee=employee)

    if request.method == 'POST':
        if 'leave_application_form' in request.POST:
            leave_application_form = LeaveApplicationForm(request.POST, employee=employee)
            if leave_application_form.is_valid():
                leave_application = leave_application_form.save(commit=False)
                leave_application.employee = employee

                # Set approver from the Leaves table
                leave_type = leave_application.leave_type
                if leave_type and leave_type.leave_approver:
                    leave_application.current_approver = leave_type.leave_approver
                    leave_application.status = 'pending'
                    leave_application.save()
                    messages.success(request, 'Leave application has been successfully submitted!')
                else:
                    messages.error(request, "No approver is assigned for the selected leave type. Please contact HR.")

                return redirect('leave')
            else:
                # Handle form errors
                error_message = ""
                non_field_errors = leave_application_form.errors.get('__all__', [])
                for error in non_field_errors:
                    error_message += f"{error}" 
                for field, errors in leave_application_form.errors.items():
                    if field != '__all__':
                        for error in errors:
                            error_message += f"<strong>{field}</strong>: {error}<br>"

                messages.error(request, error_message)
                return redirect('leave')
                # leave_application_form = LeaveApplicationForm(employee=employee)

        elif 'status' in request.POST:
            leave_application_id = request.POST.get('leave_application_id')
            leave_application = LeaveApplication.objects.get(id=leave_application_id)

            if leave_application.current_approver == employee:
                if request.POST.get('status') == 'rejected':
                    leave_application.status = 'rejected'
                    leave_application.remarks = request.POST.get('remarks', '')
                    leave_application.current_approver = None
                    leave_application.save()
                    messages.success(request, 'Leave application rejected.')
                    return redirect('leave')

                if request.POST.get('status') == 'approved':
                    leave_application.status = 'approved'
                    leave_application.current_approver = None
                    leave_application.save()
                    messages.success(request, 'Leave application approved.')
                    return redirect('leave')

    return render(request, 'templates/sub_templates/apply_leave.html', {
        'leave_form': leave_form,
        'leave_application_form': leave_application_form,
        'leave_applications': leave_applications_to_approve,  
        'logged_in_user': logged_in_user, 
        'all_leaves': leaves,  
    })
# @login_required
# @no_cache
# def leave(request):
    
#     employee = Employee.objects.get(email=request.user.email)
#     leaves=Leaves.objects.all()
    
#     leave_applications_to_approve = LeaveApplication.objects.none()
#     logged_in_user = LeaveApplication.objects.filter(employee=employee)

#     def get_hierarchy_for_role(employee, project=None):
#         if project:
#             hierarchy = Hierarchy.objects.filter(
#                 project_name=project,
#                 position=employee.position
#             ).order_by('order_number')
#             if hierarchy.exists():
#                 return hierarchy

#         return Hierarchy.objects.filter(
#             position=employee.position,
#             project_name=None
#         ).order_by('order_number')

#     def advance_to_next_approver(leave_application, approvers):
#         current_index = approvers.index(leave_application.current_approver) if leave_application.current_approver in approvers else -1
#         next_index = current_index + 1

#         if next_index < len(approvers):
#             leave_application.current_approver = approvers[next_index]
#             leave_application.status = 'pending'
#         else:
#             leave_application.current_approver = None
#             leave_application.status = 'approved'
#         leave_application.save()

#     all_applications = LeaveApplication.objects.all()
#     for application in all_applications:
#         submitter = application.employee
#         project_assignment = Projects.objects.filter(team_members=submitter).first()
        
#         hierarchy = get_hierarchy_for_role(submitter, project=project_assignment)
#         approvers = [entry.approver for entry in hierarchy]

#         if employee in approvers:
#             leave_applications_to_approve |= LeaveApplication.objects.filter(id=application.id)

#     leave_form = LeaveForm()
#     leave_application_form = LeaveApplicationForm(employee=employee)

#     if request.method == 'POST':
#         if 'leave_application_form' in request.POST:
#             leave_application_form = LeaveApplicationForm(request.POST, employee=employee)
#             if leave_application_form.is_valid():
#                projects = Projects.objects.filter(team_members=employee)
                
#                hierarchy = None
#                for project in projects:
#                     hierarchy = Hierarchy.objects.filter(position=employee.position, project_name=project).order_by('order_number')
#                     if hierarchy.exists():
#                         break
                
#                if not hierarchy or not hierarchy.exists():
#                     hierarchy = Hierarchy.objects.filter(position=employee.position, project_name__isnull=True).order_by('order_number')

#                if hierarchy.exists():
#                     leave_application = leave_application_form.save(commit=False)
#                     leave_application.employee = employee

#                     leave_application.current_approver = hierarchy.first().approver
#                     leave_application.status = 'pending'
#                     leave_application.save()
                    
#                     messages.success(request, 'Leave application has been successfully submitted!')
#                else:
#                     messages.error(request, "No approval hierarchy exists for your role and project. Please contact HR for assistance.")
                
#                return redirect('leave')
#             else:
#                 error_message = ""
#                 non_field_errors = leave_application_form.errors.get('__all__', [])
#                 for error in non_field_errors:
#                         error_message += f"{error}" 
#                 for field, errors in leave_application_form.errors.items():
#                         if field != '__all__':
#                             for error in errors:
#                                 error_message += f"<strong>{field}</strong>: {error}<br>"
    
#                 messages.error(request,error_message)
                
#                 leave_application_form = LeaveApplicationForm(employee=employee)

#         elif 'status' in request.POST:
#             leave_application_id = request.POST.get('leave_application_id')
#             leave_application = LeaveApplication.objects.get(id=leave_application_id)

#             submitter = leave_application.employee
#             project_assignment = Projects.objects.filter(team_members=submitter).first()
#             hierarchy = get_hierarchy_for_role(submitter, project=project_assignment)
#             approvers = [entry.approver for entry in hierarchy]

#             if leave_application.current_approver == employee:
#                 if request.POST.get('status') == 'rejected':
#                     leave_application.status = 'rejected'
#                     leave_application.remarks = request.POST.get('remarks', '')
#                     leave_application.current_approver = None
#                     leave_application.save()
#                     messages.success(request, 'Leave application rejected.')
#                     return redirect('leave')

#                 advance_to_next_approver(leave_application, approvers)
#                 messages.success(request, 'Leave application status updated.')
#                 return redirect('leave')

#     return render(request, 'templates/leave.html', {
#         'leave_form': leave_form,
#         'leave_application_form': leave_application_form,
#         'leave_applications': leave_applications_to_approve,
#         'logged_in_user': logged_in_user,
#         'all_leaves' : leaves,
#     })


@login_required
@no_cache
def edit_leave(request, leave_id):
    leave = get_object_or_404(Leaves, id=leave_id)
    
    if request.method == 'POST':
        form = LeaveForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave type updated successfully!')
            return redirect('leave_config_dashboard')  # Redirect to the leave types list
    else:
        form = LeaveForm(instance=leave)

    return render(request, 'templates/sub_templates/edit_leave.html', {
        'form': form,
        'leave' : leave,
        })

@login_required
@no_cache
def delete_leave(request, leave_id):
    leave = get_object_or_404(Leaves, id=leave_id)
    leave.delete()
    messages.success(request, 'Leave Type deleted successfully!')
    return redirect('leave_config_dashboard')
    
@login_required
@no_cache
def projects(request):
    supervisors = Employee.objects.all()
    projects = Projects.objects.all()
    ongoing_projects = projects.count()
    completed_projects = Projects.objects.filter(status='complete').count()
    user = Employee.objects.get(email=request.user.email)
    user_projects = Projects.objects.filter(team_members=user)


    employees = Employee.objects.all()
    if request.method == 'POST':
        form = ProjectForm(request.POST , request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project Added Successfuly')
            return redirect('projects')
        else:
            print(form.errors)
    else:
        form = ProjectForm()
    return render(request,'templates/projects.html', {
        'form' : form,
        'user_projects' : user_projects,
        'projects' : projects,
        'ongoing_projects' : ongoing_projects,
        'completed_projects' : completed_projects,
        'supervisors': supervisors,
        'employees' : employees
        })






@login_required
@no_cache
def add_project(request):
    supervisors = Employee.objects.all()
    employees = Employee.objects.all()
    billing_types = BillingType.objects.all()  

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)

        if form.is_valid():
            project_instance = form.save(commit=False)

            client_manager = form.cleaned_data.get('client_manager')
            if client_manager:
                project_instance.client_manager = client_manager

            project_instance.save()

            team_members = request.POST.getlist('team_members[]')
            billing_types = request.POST.getlist('billing_types[]')

            if len(team_members) == len(billing_types):
                for employee_id, billing_type in zip(team_members, billing_types):
                    XPL_EmployeeBilling.objects.create(
                        project=project_instance,
                        employee_id=employee_id,
                        billing_type=billing_type
                    )

               
                project_instance.team_members.set(team_members)  

            messages.success(request, 'Project Added Successfully')
            return redirect('projects')
        else:
            team_members_ids = request.POST.getlist('team_members[]')
            form.fields['team_members'].initial = team_members_ids
            print(form.errors)  
    else:
        form = ProjectForm()

    return render(request, 'templates/sub_templates/project_configs.html', {
        'form': form,
        'supervisors': supervisors,
        'employees': employees,
        'billing_types': billing_types,
        'XPL_EmployeeBilling': XPL_EmployeeBilling  
    })






from django.http import JsonResponse
def get_client_contacts(request, client_id):
    try:
        client_contacts = XPL_ClientContact.objects.filter(client_id=client_id)
        contacts_data = [{'id': contact.id, 'full_name': contact.full_name} for contact in client_contacts]
        return JsonResponse({'contacts': contacts_data})
    except XPL_ClientContact.DoesNotExist:
        return JsonResponse({'contacts': []})




@login_required
@no_cache
def add_client(request):
    if request.method == 'POST':
        print(request.POST)
        client_form = ClientInformationForm(request.POST, request.FILES)
        
        # Dynamically collect leave forms
        leave_forms = []
        leave_count = int(request.POST.get('leave_count', 0))  # Number of leave forms
        print(leave_count)

        for i in range(leave_count):
            leave_form = ClientLeaveForm(request.POST, prefix=f'leave_{i}')
            print(leave_form)
            leave_forms.append(leave_form)

        # Dynamically collect client contact forms
        contact_forms = []
        contact_count = int(request.POST.get('contact_count', 0))  # Number of contact forms
        print(contact_count)

        for i in range(contact_count):
            contact_form = XPL_ClientContactForm(request.POST, prefix=f'contact_{i}')
            print(contact_form)
            contact_forms.append(contact_form)

        # Check if client form, all leave forms, and all contact forms are valid
        if (
            client_form.is_valid()
            and all(leave_form.is_valid() for leave_form in leave_forms)
            and all(contact_form.is_valid() for contact_form in contact_forms)
        ):
            # Save the client
            client = client_form.save()

            # Save each leave form and link it to the client
            for leave_form in leave_forms:
                leave = leave_form.save(commit=False)
                leave.client = client  # Associate the leave form with the client
                leave.save()

            # Save each contact form and link it to the client
            for contact_form in contact_forms:
                contact = contact_form.save(commit=False)
                contact.client = client  # Associate the contact form with the client
                contact.save()

            messages.success(request, 'Client, Leave Types, and Contacts Added Successfully')
            return redirect('clients')
        else:
            # Debugging errors to check what's going wrong
            print(client_form.errors)
            for leave_form in leave_forms:
                print(leave_form.errors)
            for contact_form in contact_forms:
                print(contact_form.errors)
    else:
        client_form = ClientInformationForm()
        leave_forms = [ClientLeaveForm(prefix='leave_0')]  # Start with one empty leave form
        contact_forms = [XPL_ClientContactForm(prefix='contact_0')]  # Start with one empty contact form

    return render(request, 'templates/sub_templates/add_client.html', {
        'form': client_form,
        'leave_forms': leave_forms,
        'contact_forms': contact_forms,
    })





@login_required
@no_cache
def edit_client(request, client_id):
    client = get_object_or_404(ClientInformation, id=client_id)

    if request.method == 'POST':
        print(request.POST)
        client_form = ClientInformationForm(request.POST, request.FILES, instance=client)
        
        # Dynamically collect leave forms
        leave_forms = []
        leave_count = int(request.POST.get('leave_count', 0))  # Number of leave forms
        existing_leaves = list(ClientLeave.objects.filter(client=client))  # Fetch existing leaves

        leave_ids_in_form = []  # To track leave IDs present in the form

        for i in range(leave_count):
            leave_id = request.POST.get(f'leave_{i}-id')
            if leave_id:
                leave_ids_in_form.append(int(leave_id))

            if leave_id:
                # Use existing instance for updates
                leave_instance = ClientLeave.objects.filter(id=leave_id, client=client).first()
            else:
                # New leave being added
                leave_instance = None

            leave_form = ClientLeaveForm(request.POST, prefix=f'leave_{i}', instance=leave_instance)
            leave_forms.append(leave_form)

        # Dynamically collect client contact forms
        contact_forms = []
        contact_count = int(request.POST.get('contact_count', 0))  # Number of contact forms
        existing_contacts = list(XPL_ClientContact.objects.filter(client=client))  # Fetch existing contacts

        contact_ids_in_form = []  # To track contact IDs present in the form

        for i in range(contact_count):
            contact_id = request.POST.get(f'contact_{i}-id')
            if contact_id:
                contact_ids_in_form.append(int(contact_id))

            if contact_id:
                # Use existing instance for updates
                contact_instance = XPL_ClientContact.objects.filter(id=contact_id, client=client).first()
            else:
                # New contact being added
                contact_instance = None

            contact_form = XPL_ClientContactForm(request.POST, prefix=f'contact_{i}', instance=contact_instance)
            contact_forms.append(contact_form)

        # Check if client form, all leave forms, and all contact forms are valid
        if (
            client_form.is_valid()
            and all(leave_form.is_valid() for leave_form in leave_forms)
            and all(contact_form.is_valid() for contact_form in contact_forms)
        ):
            # Save the client
            client = client_form.save()

            # Save each leave form and link it to the client
            for leave_form in leave_forms:
                leave = leave_form.save(commit=False)
                leave.client = client  # Associate the leave form with the client
                leave.save()

            # Delete leaves not present in the form
            for leave in existing_leaves:
                if leave.id not in leave_ids_in_form:
                    leave.delete()

            # Save each contact form and link it to the client
            for contact_form in contact_forms:
                contact = contact_form.save(commit=False)
                contact.client = client  # Associate the contact form with the client
                contact.save()

            # Delete contacts not present in the form
            for contact in existing_contacts:
                if contact.id not in contact_ids_in_form:
                    contact.delete()

            messages.success(request, 'Client, Leave Types, and Contacts Updated Successfully')
            return redirect('clients')
        else:
            # Debugging errors to check what's going wrong
            print(client_form.errors)
            for leave_form in leave_forms:
                print(leave_form.errors)
            for contact_form in contact_forms:
                print(contact_form.errors)
    else:
        # Pre-fill forms with existing client, leave, and contact data
        client_form = ClientInformationForm(instance=client)
        leave_forms = [
            ClientLeaveForm(prefix=f'leave_{i}', instance=leave)
            for i, leave in enumerate(ClientLeave.objects.filter(client=client))
        ]
        contact_forms = [
            XPL_ClientContactForm(prefix=f'contact_{i}', instance=contact)
            for i, contact in enumerate(XPL_ClientContact.objects.filter(client=client))
        ]

    return render(request, 'templates/sub_templates/edit_client.html', {
        'form': client_form,
        'leave_forms': leave_forms,
        'contact_forms': contact_forms,
        'client': client,
    })



@login_required
@no_cache
def delete_client(request, client_id):
    # Retrieve the client object or return 404 if not found
    client = get_object_or_404(ClientInformation, id=client_id)

    if request.method == "POST":
        # Delete the client and display a success message
        client.delete()
        messages.success(request, "Client deleted successfully!")
        return redirect('clients')  # Redirect to the client list page

    return render(request, 'templates/sub_templates/delete_client.html', {
        'client': client  # Pass client details for confirmation
    })


@login_required
@no_cache
@require_POST
def project_delete_view(request, pk):
    project = get_object_or_404(Projects, pk=pk)
    project.delete()
    messages.success(request,"Project Deleted Successfully!")
    return redirect('projects')


@login_required
@no_cache
def project_edit_view(request, pk):
    project = get_object_or_404(Projects, pk=pk)
    billing_types = BillingType.objects.all()  

    existing_billing_data = [
        (entry.employee.id, entry.billing_type) for entry in XPL_EmployeeBilling.objects.filter(project=project)
    ]
    client = project.client_name 

    client_contacts = XPL_ClientContact.objects.filter(client=client)

    current_client_manager = project.client_manager.id if project.client_manager else None
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project_instance = form.save()
            client_manager_id = request.POST.get('client_manager')
            if client_manager_id:
                client_manager = XPL_ClientContact.objects.get(id=client_manager_id)
                project_instance.client_manager = client_manager
                project_instance.save()
            team_members = request.POST.getlist('team_members[]')
            billing_types = request.POST.getlist('billing_types[]')

            if len(team_members) == len(billing_types):
                XPL_EmployeeBilling.objects.filter(project=project_instance).delete()
                for employee_id, billing_type in zip(team_members, billing_types):
                    XPL_EmployeeBilling.objects.create(
                        project=project_instance,
                        employee_id=employee_id,
                        billing_type=billing_type,
                    )
                project_instance.team_members.set(team_members)
            messages.success(request, "Project Edited Successfully!")
            return redirect('projects')
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'project': project,
        'existing_billing_data': existing_billing_data,
        'employees': Employee.objects.all(),
        'current_client_manager': current_client_manager,
        'client_contacts': client_contacts,
        'billing_types': billing_types,
        'XPL_EmployeeBilling': XPL_EmployeeBilling,
    }
    return render(request, 'templates/sub_templates/edit_project.html', context)

@login_required
@no_cache 
def project_detail_view(request, pk):
    project = get_object_or_404(Projects, pk=pk)

    if request.method == 'POST':
        form = ProjectFileForm(request.POST, request.FILES)
        if form.is_valid():
            project_file = form.save(commit=False)
            project_file.project = project
            project_file.uploaded_by = request.user  
            project_file.save()

            messages.success(request, 'File uploaded successfully!')
            return redirect('project_detail', pk=pk)
    else:
        form = ProjectFileForm()

    project_files = ProjectFile.objects.filter(project=project)

    context = {
        'project': project,
        'form': form,
        'project_files': project_files,
    }

    return render(request, 'templates/sub_templates/view_project.html', context)

@login_required
@no_cache
def client_detail_view(request, client_id):
    client = get_object_or_404(ClientInformation, id=client_id)
    client_leaves = ClientLeave.objects.filter(client=client)
    client_docs=ClientInformation.objects.filter(documents=client)
    client_contacts = XPL_ClientContact.objects.filter(client=client)
    return render(request, 'templates/sub_templates/view_client.html', {
        'form': client,
        'leave_forms': client_leaves,
        'contact_forms': client_contacts,
        'client_docs': client_docs,
    })

@login_required
@no_cache 
def delete_project_file(request, file_id):
    # Get the file object
    project_file = get_object_or_404(ProjectFile, id=file_id)

    # Check if the current user is the one who uploaded the file (optional for security)
    if project_file.uploaded_by != request.user:
        messages.error(request, "You can only delete file uploaded by you!!.")
        return redirect('project_detail', pk=project_file.project.id)

    # Delete the file
    project_file.delete()
    
    messages.success(request, "File deleted successfully!")
    return redirect('project_detail', pk=project_file.project.id)


@login_required
@no_cache
def forget_pwd(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Employee.objects.get(email=email)
            
            reset_token = PasswordResetToken.objects.create(employee=user)
            reset_url = request.build_absolute_uri(f"/reset-password/{reset_token.token}/")

            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_url}",
                from_email="from email ",
                recipient_list=[email],
            )

            messages.success(request, "A reset link has been sent to your email.")
            return redirect('login')  
        except Employee.DoesNotExist:
            messages.error(request, "No account found with this email.")
    return render(request, 'templates/forget_pwd.html')  


@login_required
@no_cache
def files(request):
    employee = Employee.objects.get(email=request.user.email)
    document_count = EducationalDocument.objects.filter(employee=employee).count()
    all_docs = EducationalDocument.objects.all()

    if document_count >= 10:
        messages.error(request, "You cannot upload more than 10 documents.")
        # return redirect('files')  # Redirect to the same form with an error

    if request.method == 'POST':
        form = EducationalDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.employee = employee

            # Restrict file size to 3MB (3 * 1024 * 1024 = 3145728 bytes)
            if document.document_file.size > 3145728:
                print("File greater than 3 mb")
                messages.error(request, "File must be 3MB or less.")
                # return redirect('files')
            else:
                document.save()
                messages.success(request, "Document uploaded successfully!")
                return redirect('files')  # Redirect after successful upload
    else:
        form = EducationalDocumentForm()

    documents = EducationalDocument.objects.filter(employee=employee)

    return render(request, 'templates/files.html', {
        'form': form,
        'all_docs': all_docs,
        'employee': employee,
        'documents': documents
    })


@login_required
@no_cache
def timesheet_date_range(request):
    employee = Employee.objects.get(email=request.user.email)
    all_ranges = DateRange.objects.all()
    timesheets = (
        Timesheet.objects.filter(employee=employee)
        .values('timesheet_group_id', 'project__project_name', 'status', 'reject_reason')
        .annotate(start_date=Min('date'), end_date=Max('date'))
        .order_by('-start_date')
    )
    pending_approval_timesheets = (
        Timesheet.objects.filter(
            status='pending',
            current_approver=employee  # Check if the employee is the current approver
        )
        .values('timesheet_group_id', 'project__project_name', 'employee__first_name')
        .annotate(start_date=Min('date'), end_date=Max('date'))
        .order_by('-start_date')
    )
    # projects = Projects.objects.filter(team_members=employee)
    projects = Projects.objects.filter(
        Q(team_members=employee) | Q(project_manager=employee)
        ).distinct()
    months = [month_name[i] for i in range(1, 13)]
    today = datetime.today().strftime('%Y-%m-%d')

    # Initialize the form for date range
    range_form = PeriodForm()

    # Initialize an empty dictionary to hold the date ranges for each project
    project_date_ranges = {}

    # # Fetch date ranges for all projects
    # for project in projects:
    #     try:
    #         # Fetch the DateRange for the project
    #         date_range = DateRange.objects.get(project=project)
    #         project_date_ranges[project.id] = {
    #             'start_date': date_range.start_date.strftime('%Y-%m-%d'),
    #             'end_date': date_range.end_date.strftime('%Y-%m-%d'),
    #         }
    #     except DateRange.DoesNotExist:
    #         project_date_ranges[project.id] = None  # No date range for this project
    # Initialize the dictionary that will hold the project date ranges
    

# Loop through each project
    for project in projects:
        print(f"Processing Project ID: {project.id}")  # Debug print

        # Fetch all date ranges associated with the project
        date_ranges = DateRange.objects.filter(project=project)
        
        if not date_ranges:
            print(f"No date ranges found for Project ID: {project.id}")  # Debug print
            continue

        # Initialize an empty list to hold month ranges for each project
        month_ranges = []
        
        for date_range in date_ranges:
            print(f"Processing DateRange: {date_range}")  # Debug print

            # Extract the month from start_date and end_date
            start_month = date_range.start_date.strftime('%B')
            start_year = date_range.start_date.year
            end_month = date_range.end_date.strftime('%B')
            end_year = date_range.end_date.year
            
            # Combine month and year for better identification
            if start_month == end_month and start_year == end_year:
                month_ranges.append({
                    'month': f"{start_month} {start_year}",
                    'start_date': date_range.start_date.strftime('%Y-%m-%d'),
                    'end_date': date_range.end_date.strftime('%Y-%m-%d'),
                })
            else:
                month_ranges.append({
                    'month': f"{start_month} {start_year} - {end_month} {end_year}",
                    'start_date': date_range.start_date.strftime('%Y-%m-%d'),
                    'end_date': date_range.end_date.strftime('%Y-%m-%d'),
                })

        # If month_ranges is not empty, add it to project_date_ranges
        if month_ranges:
            project_date_ranges[project.id] = month_ranges
        else:
            print(f"No month ranges for Project ID: {project.id}")  # Debug print

    # Print the final project_date_ranges for debugging
    print(f"Project Date Ranges: {project_date_ranges}")

    
    

    # Handle form submissions
    if request.method == 'POST':
        if 'range_form_submit' in request.POST:
            range_form = PeriodForm(request.POST)
            if range_form.is_valid():
                # Get the start and end dates, and project from the form
                start_date = range_form.cleaned_data['start_date']
                end_date = range_form.cleaned_data['end_date']
                project = range_form.cleaned_data['project']
                month = range_form.cleaned_data['month']
                year = range_form.cleaned_data['year']

                # Check for existing date ranges for the same project within the specified range
                overlapping_ranges = DateRange.objects.filter(
                    project=project,
                    end_date__gte=start_date,
                    start_date__lte=end_date,
                )

                if overlapping_ranges.exists():
                    messages.error(request, 'Date range overlaps with an existing range for this project.')
                else:
                        date_range = range_form.save(commit=False)
                        date_range.employee = employee  # Optional: associate with employee
                        date_range.save()
                        messages.success(request, 'New date range set successfully!')
                    # Check if an active range exists for the project
                    # last_date_range = DateRange.objects.filter(project=project).order_by('-end_date').first()
                    
                    # if last_date_range and last_date_range.end_date >= timezone.now().date():
                    #     messages.error(request, 'Cannot add a new date range until the current one ends.')
                    # else:
                    #     # Check if a range already exists for the project
                    #     existing_range = DateRange.objects.filter(project=project).first()
                        
                    #     if existing_range:
                    #         # Update the existing range with new dates
                    #         existing_range.start_date = start_date
                    #         existing_range.end_date = end_date
                    #         existing_range.save()
                    #         messages.success(request, 'Date range updated successfully!')
                    #     else:
                    #         # Create a new date range
                    #         date_range = range_form.save(commit=False)
                    #         date_range.employee = employee  # Optional: associate with employee
                    #         date_range.save()
                    #         messages.success(request, 'New date range set successfully!')
                        
                        return redirect('timesheet')
            else:
                messages.error(request, 'Invalid date range. Please try again.')

        
        
        if 'action' in request.POST:

            action = request.POST.get('action')
            date_from = request.POST.get('date_from')
            date_to = request.POST.get('date_to')
            project_id = request.POST.get('project_id')

            if not date_from or not date_to:
                messages.error(request, 'Please provide a valid date range.')
                return redirect('timesheet')

            try:
                project = Projects.objects.get(id=project_id)
            except Projects.DoesNotExist:
                messages.error(request, 'The selected project does not exist.')
                return redirect('timesheet')

            # Parse the date range
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            end_date = datetime.strptime(date_to, '%Y-%m-%d')

            # Generate a unique timesheet group ID for this range
            timesheet_group_id = str(uuid.uuid4())

            current_date = start_date
            missing_fields = False  # Flag to check if any required field is missing

            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                day_of_week = current_date.weekday()  # 5 = Saturday, 6 = Sunday

                # For weekdays, check for required fields
                if day_of_week not in [5, 6]:  # Not Saturday or Sunday
                    task_description = request.POST.get(f'task_description_{date_str}', '').strip()
                    location = request.POST.get(f'location_{date_str}', '').strip()


                current_date += timedelta(days=1)

            # If any required fields are missing, prevent form submission
            if missing_fields:
                return redirect('timesheet')

            # If all required fields are present, proceed with save or submit action
            if action == 'save':
                current_date = start_date
                duplicate_found = False  # Flag to track if any duplicate is found

                while current_date <= end_date:
                    date_str = current_date.strftime('%Y-%m-%d')
                    day_of_week = current_date.weekday()

                    # Check if a timesheet already exists for this date and project
                    existing_timesheet = Timesheet.objects.filter(
                        employee=employee,
                        project=project,
                        date=date_str
                    ).first()

                    if existing_timesheet:
                        print(f"Timesheet already exists for {employee} on {date_str} for project {project}. Skipping.")
                        if not duplicate_found:
                            messages.error(request,'A duplicate timesheet already exists for the project')
                            duplicate_found = True  # Mark that we've found a duplicate
                        current_date += timedelta(days=1)
                        continue  # Skip saving for this date

                    print(f"Saving timesheet for {employee} on {date_str} for project {project}")

                    task_description = request.POST.get(f'task_description_{date_str}', '').strip()
                    location = request.POST.get(f'location_{date_str}', '').strip()
                    notes = request.POST.get(f'notes_{date_str}', '').strip()
                    time_in_hrs=request.POST.get(f'time_in_hrs_{date_str}', '').strip()

                    # Save or update the timesheet
                    timesheet, created = Timesheet.objects.get_or_create(
                        employee=employee,
                        project=project,
                        date=date_str,
                        defaults={
                            'task_description': task_description,
                            'location': location,
                            'notes': notes,
                            'time_in_hrs':time_in_hrs,
                            'status': 'saved',
                            'is_editable': True,
                            'timesheet_group_id': timesheet_group_id,
                        }
                    )
                    if not created:
                        # If timesheet already exists, update it
                        timesheet.task_description = task_description
                        timesheet.location = location
                        timesheet.time_in_hrs=time_in_hrs
                        timesheet.notes = notes
                        timesheet.is_editable = True
                        timesheet.status = 'saved'
                        timesheet.timesheet_group_id = timesheet_group_id
                        timesheet.save()

                    current_date += timedelta(days=1)

                # If a duplicate was found, do not redirect to 'timesheet'
                if duplicate_found:
                    return redirect('timesheet')

                messages.success(request, 'Timesheet saved successfully!')
                return redirect('timesheet')




    context = {
        'projects': projects,
        'timesheets': timesheets,
        'employee': employee,
        'today': today,
        'months': months,
        'pending_approval_timesheets': pending_approval_timesheets, 
        'all_ranges':all_ranges,
        'range_form': range_form,
        'project_date_ranges': json.dumps(project_date_ranges),  
    }

    return render(request, 'templates/sub_templates/set_timesheet_date_range.html', context)






@login_required
@no_cache
def add_timesheet(request):
    employee = Employee.objects.get(email=request.user.email)
    timesheets = (
        Timesheet.objects.filter(employee=employee)
        .values('timesheet_group_id', 'project__project_name', 'status', 'reject_reason')
        .annotate(start_date=Min('date'), end_date=Max('date'))
        .order_by('-start_date')
    )
    pending_approval_timesheets = (
        Timesheet.objects.filter(
            status='pending',
            current_approver=employee
        )
        .values('timesheet_group_id', 'project__project_name', 'employee__first_name')
        .annotate(start_date=Min('date'), end_date=Max('date'))
        .order_by('-start_date')
    )
    projects = Projects.objects.filter(
        Q(team_members=employee) | Q(project_manager=employee)
    ).distinct()
    months = [month_name[i] for i in range(1, 13)]
    today = datetime.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        if 'action' in request.POST:
            print(request.POST)
            action = request.POST.get('action')
            date_from = request.POST.get('date_from')
            date_to = request.POST.get('date_to')
            project_id = request.POST.get('project_id')

            if not date_from or not date_to:
                messages.error(request, 'Please provide a valid date range.')
                return redirect('timesheet')

            try:
                project = Projects.objects.get(id=project_id)
            except Projects.DoesNotExist:
                messages.error(request, 'The selected project does not exist.')
                return redirect('timesheet')

            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            end_date = datetime.strptime(date_to, '%Y-%m-%d')

            timesheet_group_id = str(uuid.uuid4())
            current_date = start_date
            duplicate_found = False

            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')

                task_description = request.POST.get(f'task_description_{date_str}', '').strip()
                location = request.POST.get(f'location_{date_str}', '').strip()
                notes = request.POST.get(f'notes_{date_str}', '').strip()
                time_in_hrs = request.POST.get(f'time_in_hrs_{date_str}', '').strip()

                if action == 'save':
                    existing_timesheet = Timesheet.objects.filter(
                        employee=employee,
                        project=project,
                        date=date_str
                    ).first()

                    if existing_timesheet:
                        duplicate_found = True
                        current_date += timedelta(days=1)
                        continue

                    timesheet, created = Timesheet.objects.get_or_create(
                        employee=employee,
                        project=project,
                        date=date_str,
                        defaults={
                            'task_description': task_description,
                            'location': location,
                            'notes': notes,
                            'time_in_hrs': time_in_hrs,
                            'status': 'saved',
                            # 'is_editable': True,
                            'timesheet_group_id': timesheet_group_id,
                        }
                    )
                    if not created:
                        timesheet.task_description = task_description
                        timesheet.location = location
                        timesheet.time_in_hrs = time_in_hrs
                        timesheet.notes = notes
                        # timesheet.is_editable = True
                        timesheet.status = 'saved'
                        timesheet.timesheet_group_id = timesheet_group_id
                        timesheet.save()

                current_date += timedelta(days=1)

            if duplicate_found:
                messages.error(request, 'Duplicate timesheets detected. Some entries were skipped.')
            else:
                messages.success(request, 'Timesheet saved successfully!')

            return redirect('timesheet')

    context = {
        'projects': projects,
        'timesheets': timesheets,
        'employee': employee,
        'today': today,
        'months': months,
        'pending_approval_timesheets': pending_approval_timesheets,
    }

    return render(request, 'templates/sub_templates/add_timesheet.html', context)






@login_required
def get_project_details(request, project_id):
    try:
        project = Projects.objects.get(id=project_id)
        client = project.client_name

        client_leaves = ClientLeave.objects.filter(client=client).values('client_leave_date', 'client_leave_type')
        leave_days = [
            {
                'date': leave['client_leave_date'], 
                'name': leave['client_leave_type']
            } 
            for leave in client_leaves
        ]

        employee = request.user  
        employee_leaves = LeaveApplication.objects.filter(employee=employee)

        employee_leave_days = []
        for leave in employee_leaves:
            current_date = leave.start_date
            while current_date <= leave.end_date:
                employee_leave_days.append({
                    'date': current_date,
                    'name': leave.leave_type.leave_name 
                })
                current_date += timedelta(days=1)

        client_weekends = client.weekend.split('/')  

        return JsonResponse({
            'status': 'success',
            'leave_days': leave_days,  
            'employee_leaves': employee_leave_days, 
            'weekends': client_weekends,
        })

    except Projects.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Project not found.'}, status=404)



@login_required
@no_cache
def timesheet(request):
    employee = Employee.objects.get(email=request.user.email)
    all_ranges = DateRange.objects.all()
    timesheets = (
        Timesheet.objects.filter(employee=employee)
        .values('timesheet_group_id', 'project__project_name', 'status', 'reject_reason','accept_reason')
        .annotate(start_date=Min('date'), end_date=Max('date'))
        .order_by('-start_date')
    )
    pending_approval_timesheets = (
        Timesheet.objects.filter(
            status='pending',
            current_approver=employee  # Check if the employee is the current approver
        )
        .values('timesheet_group_id', 'project__project_name', 'employee__first_name')
        .annotate(start_date=Min('date'), end_date=Max('date'))
        .order_by('-start_date')
    )
    # projects = Projects.objects.filter(team_members=employee)
    projects = Projects.objects.filter(
        Q(team_members=employee) | Q(project_manager=employee)
        ).distinct()
    months = [month_name[i] for i in range(1, 13)]
    today = datetime.today().strftime('%Y-%m-%d')

    # Initialize the form for date range
    range_form = PeriodForm()

    # Initialize an empty dictionary to hold the date ranges for each project
    project_date_ranges = {}

    # # Fetch date ranges for all projects
    # for project in projects:
    #     try:
    #         # Fetch the DateRange for the project
    #         date_range = DateRange.objects.get(project=project)
    #         project_date_ranges[project.id] = {
    #             'start_date': date_range.start_date.strftime('%Y-%m-%d'),
    #             'end_date': date_range.end_date.strftime('%Y-%m-%d'),
    #         }
    #     except DateRange.DoesNotExist:
    #         project_date_ranges[project.id] = None  # No date range for this project
    # Initialize the dictionary that will hold the project date ranges
    

# Loop through each project
    for project in projects:
        print(f"Processing Project ID: {project.id}")  # Debug print

        # Fetch all date ranges associated with the project
        date_ranges = DateRange.objects.filter(project=project)
        
        if not date_ranges:
            print(f"No date ranges found for Project ID: {project.id}")  # Debug print
            continue

        # Initialize an empty list to hold month ranges for each project
        month_ranges = []
        
        for date_range in date_ranges:
            print(f"Processing DateRange: {date_range}")  # Debug print

            # Extract the month from start_date and end_date
            start_month = date_range.start_date.strftime('%B')
            start_year = date_range.start_date.year
            end_month = date_range.end_date.strftime('%B')
            end_year = date_range.end_date.year
            
            # Combine month and year for better identification
            if start_month == end_month and start_year == end_year:
                month_ranges.append({
                    'month': f"{start_month} {start_year}",
                    'start_date': date_range.start_date.strftime('%Y-%m-%d'),
                    'end_date': date_range.end_date.strftime('%Y-%m-%d'),
                })
            else:
                month_ranges.append({
                    'month': f"{start_month} {start_year} - {end_month} {end_year}",
                    'start_date': date_range.start_date.strftime('%Y-%m-%d'),
                    'end_date': date_range.end_date.strftime('%Y-%m-%d'),
                })

        # If month_ranges is not empty, add it to project_date_ranges
        if month_ranges:
            project_date_ranges[project.id] = month_ranges
        else:
            print(f"No month ranges for Project ID: {project.id}")  # Debug print

    # Print the final project_date_ranges for debugging
    print(f"Project Date Ranges: {project_date_ranges}")

    
    

    # Handle form submissions
    if request.method == 'POST':
        if 'range_form_submit' in request.POST:
            range_form = PeriodForm(request.POST)
            if range_form.is_valid():
                # Get the start and end dates, and project from the form
                start_date = range_form.cleaned_data['start_date']
                end_date = range_form.cleaned_data['end_date']
                project = range_form.cleaned_data['project']
                month = range_form.cleaned_data['month']
                year = range_form.cleaned_data['year']

                # Check for existing date ranges for the same project within the specified range
                overlapping_ranges = DateRange.objects.filter(
                    project=project,
                    end_date__gte=start_date,
                    start_date__lte=end_date,
                )

                if overlapping_ranges.exists():
                    messages.error(request, 'Date range overlaps with an existing range for this project.')
                else:
                        date_range = range_form.save(commit=False)
                        date_range.employee = employee  # Optional: associate with employee
                        date_range.save()
                        messages.success(request, 'New date range set successfully!')
                    # Check if an active range exists for the project
                    # last_date_range = DateRange.objects.filter(project=project).order_by('-end_date').first()
                    
                    # if last_date_range and last_date_range.end_date >= timezone.now().date():
                    #     messages.error(request, 'Cannot add a new date range until the current one ends.')
                    # else:
                    #     # Check if a range already exists for the project
                    #     existing_range = DateRange.objects.filter(project=project).first()
                        
                    #     if existing_range:
                    #         # Update the existing range with new dates
                    #         existing_range.start_date = start_date
                    #         existing_range.end_date = end_date
                    #         existing_range.save()
                    #         messages.success(request, 'Date range updated successfully!')
                    #     else:
                    #         # Create a new date range
                    #         date_range = range_form.save(commit=False)
                    #         date_range.employee = employee  # Optional: associate with employee
                    #         date_range.save()
                    #         messages.success(request, 'New date range set successfully!')
                        
                        return redirect('timesheet')
            else:
                messages.error(request, 'Invalid date range. Please try again.')

        
        
        if 'action' in request.POST:

            action = request.POST.get('action')
            date_from = request.POST.get('date_from')
            date_to = request.POST.get('date_to')
            project_id = request.POST.get('project_id')

            if not date_from or not date_to:
                messages.error(request, 'Please provide a valid date range.')
                return redirect('timesheet')

            try:
                project = Projects.objects.get(id=project_id)
            except Projects.DoesNotExist:
                messages.error(request, 'The selected project does not exist.')
                return redirect('timesheet')

            # Parse the date range
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            end_date = datetime.strptime(date_to, '%Y-%m-%d')

            # Generate a unique timesheet group ID for this range
            timesheet_group_id = str(uuid.uuid4())

            current_date = start_date
            missing_fields = False  # Flag to check if any required field is missing

            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                day_of_week = current_date.weekday()  # 5 = Saturday, 6 = Sunday

                # For weekdays, check for required fields
                if day_of_week not in [5, 6]:  # Not Saturday or Sunday
                    task_description = request.POST.get(f'task_description_{date_str}', '').strip()
                    location = request.POST.get(f'location_{date_str}', '').strip()


                current_date += timedelta(days=1)

            # If any required fields are missing, prevent form submission
            if missing_fields:
                return redirect('timesheet')

            # If all required fields are present, proceed with save or submit action
            if action == 'save':
                current_date = start_date
                duplicate_found = False  # Flag to track if any duplicate is found

                while current_date <= end_date:
                    date_str = current_date.strftime('%Y-%m-%d')
                    day_of_week = current_date.weekday()

                    # Check if a timesheet already exists for this date and project
                    existing_timesheet = Timesheet.objects.filter(
                        employee=employee,
                        project=project,
                        date=date_str
                    ).first()

                    if existing_timesheet:
                        print(f"Timesheet already exists for {employee} on {date_str} for project {project}. Skipping.")
                        if not duplicate_found:
                            messages.error(request,'A duplicate timesheet already exists for the project')
                            duplicate_found = True  # Mark that we've found a duplicate
                        current_date += timedelta(days=1)
                        continue  # Skip saving for this date

                    print(f"Saving timesheet for {employee} on {date_str} for project {project}")

                    task_description = request.POST.get(f'task_description_{date_str}', '').strip()
                    location = request.POST.get(f'location_{date_str}', '').strip()
                    notes = request.POST.get(f'notes_{date_str}', '').strip()
                    time_in_hrs=request.POST.get(f'time_in_hrs_{date_str}', '').strip()

                    # Save or update the timesheet
                    timesheet, created = Timesheet.objects.get_or_create(
                        employee=employee,
                        project=project,
                        date=date_str,
                        defaults={
                            'task_description': task_description,
                            'location': location,
                            'notes': notes,
                            'time_in_hrs':time_in_hrs,
                            'status': 'saved',
                            'is_editable': True,
                            'timesheet_group_id': timesheet_group_id,
                        }
                    )
                    if not created:
                        # If timesheet already exists, update it
                        timesheet.task_description = task_description
                        timesheet.location = location
                        timesheet.time_in_hrs=time_in_hrs
                        timesheet.notes = notes
                        timesheet.is_editable = True
                        timesheet.status = 'saved'
                        timesheet.timesheet_group_id = timesheet_group_id
                        timesheet.save()

                    current_date += timedelta(days=1)

                # If a duplicate was found, do not redirect to 'timesheet'
                if duplicate_found:
                    return redirect('timesheet')

                messages.success(request, 'Timesheet saved successfully!')
                return redirect('timesheet')




    context = {
        'projects': projects,
        'timesheets': timesheets,
        'employee': employee,
        'today': today,
        'months': months,
        'pending_approval_timesheets': pending_approval_timesheets, 
        'all_ranges':all_ranges,
        'range_form': range_form,
        'project_date_ranges': json.dumps(project_date_ranges),  
    }

    return render(request, 'templates/timesheet.html', context)

@login_required
@no_cache
def delete_date_range(request, date_range_id):
    # Ensure the request is POST for security (only allow deletions via form submissions, not URL access)
    if request.method == 'POST':
        date_range = get_object_or_404(DateRange, id=date_range_id)
        
        # Delete the date range
        date_range.delete()
        messages.success(request, 'Date range deleted successfully.')
        
    else:
        messages.error(request, 'Invalid request method for deletion.')
    
    # Redirect back to the timesheet page or wherever the date ranges are listed
    return redirect('timesheet')

@login_required
@no_cache
def view_timesheet(request, timesheet_group_id):
    timesheets = Timesheet.objects.filter(timesheet_group_id=timesheet_group_id)
    project_name = timesheets.first().project.project_name
    employee_name = timesheets.first().employee.first_name
    
    if not timesheets.exists():
        messages.error(request, 'No timesheets found for this group.')
        return redirect('timesheet')

    context = {
        'timesheets': timesheets,
        'timesheet_group_id': timesheet_group_id,
        'project_name': project_name,
        'employee_name': employee_name,
    }
    
    return render(request, 'templates/sub_templates/view_timesheet.html', context)





@login_required
@no_cache
def accept_timesheet(request, timesheet_group_id):
    current_employee = Employee.objects.get(email=request.user.email)
    timesheet_group = Timesheet.objects.filter(timesheet_group_id=timesheet_group_id)

    if not timesheet_group.exists():
        messages.error(request, 'Timesheet does not exist.')
        return redirect('timesheet')

    timesheet = timesheet_group.first()
    project_name = timesheet.project
    submitting_employee = timesheet.employee

    timesheet_approver = timesheet.project.timesheet_approver

    if timesheet_approver != current_employee:
        messages.error(request, 'You are not authorized to approve this timesheet.')
        return redirect('timesheet')

    action = request.POST.get('action')

    if action == 'accept':
        accept_reason = request.POST.get('accept_reason', '').strip()
        if accept_reason:
            timesheet_group.update(status='accepted',accept_reason=accept_reason, current_approver_id=None)
            messages.success(request, f'Timesheet Accepted due to reason: {accept_reason}')
        else:
            messages.error(request, 'Acceptance reason is required.')

    elif action == 'reject':
        reject_reason = request.POST.get('reject_reason', '').strip()
        if reject_reason:  # Check if reject_reason is not empty
            timesheet_group.update(status='rejected', reject_reason=reject_reason, current_approver_id=None)
            messages.success(request, f'Timesheet Rejected due to reason: {reject_reason}')
        else:
            messages.error(request, 'Rejection reason is required.')

    return redirect('timesheet')




@login_required
@no_cache
def delete_timesheet(request, timesheet_group_id):
    if request.method == 'POST':
        # Filter timesheets by the group ID
        timesheets = Timesheet.objects.filter(timesheet_group_id=timesheet_group_id)

        # Check if any timesheets exist for the given group ID
        if timesheets.exists():
            # Delete all timesheets in this group
            timesheets.delete()
            messages.success(request, "All timesheets for this group have been deleted successfully.")
        else:
            messages.error(request, "No timesheets found for the specified group.")

    return redirect('timesheet')  # Adjust this as per your URL pattern




@login_required
@no_cache
def submit_timesheet(request, timesheet_group_id):
    if request.method == 'POST':
        timesheets = Timesheet.objects.filter(timesheet_group_id=timesheet_group_id)
        employee = Employee.objects.get(email=request.user.email)

        if not timesheets.exists():
            messages.error(request, "No timesheets found for this group.")
            return redirect('some_view_name')

        project_name = timesheets.first().project
        project = Projects.objects.get(project_name=project_name)

        # Retrieve the timesheet approver from the project
        timesheet_approver = project.timesheet_approver

        if timesheet_approver:
            # Update timesheets status to pending and set the current approver
            timesheets.update(
                status='pending',
                current_approver=timesheet_approver,
            )
            messages.success(request, 'Timesheet group submitted for approval!')
        else:
            messages.error(request, "No timesheet approver found for this project's timesheet group. Please contact HR for assistance.")

        return redirect('timesheet')  

    return render(request, 'templates/timesheet.html')  


@login_required
@no_cache
def edit_timesheet(request, timesheet_group_id):
    timesheets = Timesheet.objects.filter(timesheet_group_id=timesheet_group_id)
    if not timesheets:
        messages.error(request, "Timesheet group not found.")
        return redirect('timesheet')

    employee = timesheets[0].employee
    project = timesheets[0].project

    if request.method == 'POST':
        print("Incoming POST data:", request.POST)  # Debugging POST data

        try:
            with transaction.atomic():
                # Update existing timesheets
                for timesheet in timesheets:
                    date_str = timesheet.date.strftime('%Y-%m-%d')
                    
                    # Retrieve updated values
                    task_description = request.POST.get(f'task_description_{date_str}', timesheet.task_description)
                    location = request.POST.get(f'location_{date_str}', timesheet.location)
                    notes = request.POST.get(f'notes_{date_str}', timesheet.notes)
                    time_in_hrs = request.POST.get(f'time_in_hrs_{date_str}', timesheet.time_in_hrs)

                    # Debug print to verify updated values
                    print(f"Updating timesheet for {date_str}:")
                    print(f"Task: {task_description}, Location: {location}, Notes: {notes}")

                    # Assign and save changes
                    timesheet.task_description = task_description
                    timesheet.location = location
                    timesheet.notes = notes
                    timesheet.time_in_hrs=time_in_hrs
                    timesheet.save()

                # Handle new timesheet rows
                new_dates = request.POST.getlist('new_date')  # List of new dates submitted

                for new_date in new_dates:
                    if new_date:  # Ensure the date is valid
                        # Convert the date string to a datetime object
                        date_obj = datetime.strptime(new_date, '%Y-%m-%d')

                        # Create new timesheet entry with updated values
                        Timesheet.objects.create(
                            employee=employee,
                            project=project,
                            date=date_obj,
                            task_description=request.POST.get(f'task_description_{new_date}', ''),
                            location=request.POST.get(f'location_{new_date}', ''),
                            notes=request.POST.get(f'notes_{new_date}', ''),
                            status='saved',
                            timesheet_group_id=timesheet_group_id  # Same group ID for the new row
                        )

            messages.success(request, "Timesheet updated successfully.")

        except Exception as e:
            logger.error(f"Error updating timesheet: {e}")
            messages.error(request, "Failed to update timesheet. Please try again.")

        return redirect('timesheet')

    context = {
        'employee': employee,
        'project': project,
        'timesheets': timesheets,
    }
    return render(request, 'templates/sub_templates/edit_timesheet.html', context)



@login_required
@no_cache
def timesheet_action(request, timesheet_id):
    if request.method == 'POST':
        try:
            timesheet = Timesheet.objects.get(id=timesheet_id)
            action = request.POST.get('action')

            if action == 'accept':
                timesheet.status = 'accepted'
            elif action == 'reject':
                timesheet.status = 'rejected'

            timesheet.save()
            messages.success(request, f"Timesheet has been {action}ed.")
        except Timesheet.DoesNotExist:
            messages.error(request, 'Timesheet does not exist.')
    
    return redirect('timesheet')


@login_required
@no_cache
def delete_document(request, document_id):
    document = get_object_or_404(EducationalDocument, id=document_id)
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, "Document deleted successfully!")
        return redirect('files')


@login_required
@no_cache
def download_timesheet_pdf(request, month):
    # Get the current logged-in employee
    employee = Employee.objects.get(email=request.user.email)

    # Filter timesheets for the selected month and current employee
    month_number = datetime.strptime(month, "%B").month
    timesheets = Timesheet.objects.filter(employee=employee, date__month=month_number)

    # Organize timesheets by project
    projects = defaultdict(lambda: {'timesheets': [], 'project_name': ''})

    for timesheet in timesheets:
        project_name = timesheet.project.project_name
        if not projects[project_name]['project_name']:
            projects[project_name]['project_name'] = project_name
        projects[project_name]['timesheets'].append(timesheet)

    # Convert to a list for rendering
    logo_url = request.build_absolute_uri(settings.STATIC_URL + 'images/XPLTransparent.png')

    projects_list = [{'project_name': k, 'timesheets': v['timesheets']} for k, v in projects.items()]

    # Render the HTML template to a string
    template = get_template('templates/pdfTemplates/timesheet.html')
    context = {
        'employee': employee,
        'projects': projects_list,  # Pass the organized projects to the template
        'month': month,
        'logo_url': logo_url,
    }
    html_string = template.render(context)
    print("Request Method:", request.method)
    print("Request Path:", request.path)
    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="timesheet_{month}.pdf"'

    # Convert HTML to PDF using WeasyPrint
    HTML(string=html_string).write_pdf(response)

    return response


@login_required
@no_cache
def calculate_salaries_for_month(year, month, employee):
    timesheets = Timesheet.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month,
        status='accepted'
    )
    
    unique_days_worked = set(timesheet.date for timesheet in timesheets)  
    total_days_worked = len(unique_days_worked)
    
    print("Total unique days worked:", total_days_worked)

    days_in_month = monthrange(year, month)[1]

    total_salary = 0.0

    for work_day in unique_days_worked:
        day_timesheets = timesheets.filter(date=work_day)  
        
        daily_salary = 0.0
        for timesheet in day_timesheets:
            if timesheet.location == 'onsite':
                daily_salary += employee.onsite_salary / days_in_month
            elif timesheet.location == 'remote':
                daily_salary += employee.remote_salary / days_in_month
        
        total_salary += daily_salary
    
    print("Total salary:", total_salary)

    # Save or update salary record
    salary, created = Salary.objects.get_or_create(
        employee=employee,
        month=datetime(year, month, 1),
          defaults={
            'total_days_worked': 0,  
            'total_salary': 0.0  ,     
        }  
    )

    salary.total_days_worked = total_days_worked
    salary.total_salary = total_salary

    salary.save()


@login_required
@no_cache
def calculate_employee_salary(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    print(employee)
    
    now = datetime.now()
    month = now.month
    year = now.year
    print("Calling calculate_salaries_for_month function")  # Before the call

    calculate_salaries_for_month(year, month, employee)

    salary_record = Salary.objects.filter(employee=employee, month=datetime(year, month, 1)).first()
    print(salary_record)

    return render(request, 'templates/employees.html', {
        'employee': employee,
        'salary_record': salary_record,
    })



@login_required
@no_cache
def add_leave_policy(request):
    leave_policy_form=LeavePolicyForm(request.POST)
    
    if request.method == 'POST':
            if leave_policy_form.is_valid():
                leave_policy_form.save()
                messages.success(request, 'Leave Policy saved successfully!')
                return redirect('settings')
            else:
                errors = leave_policy_form.non_field_errors()
            for error in errors:
                        messages.error(request, error)
            

    leave_policy_form= LeavePolicyForm()
        

    return render(request, 'templates/sub_templates/add_leave_policy.html', { 'leave_policy_form':leave_policy_form,})



@login_required
@no_cache
def add_billing_types(request):
    billing_type_form=BillingTypeForm(request.POST)
    if request.method == 'POST':
        if billing_type_form.is_valid():
            billing_type_form.save()
            messages.success(request, 'Billing Type saved successfully!')
            return redirect('billing_types')
        else:
            errors = billing_type_form.non_field_errors()
        for error in errors:
                    messages.error(request, error)
    else:
        billing_type_form = BillingTypeForm()
    return render(request, 'templates/sub_templates/add_billing_types.html', {
        'billing_type_form': billing_type_form,
    })



@login_required
@no_cache
def billingtypes(request):
    billingtype=BillingType.objects.all()
    return render(request, 'templates/sub_templates/billing_types.html', {
        'billingtype': billingtype,
    })


@login_required
@no_cache
def doc_types(request):
    doc_types = uploadDocType.objects.all()
    return render(request, 'templates/sub_templates/doc_types.html', {
        'doc_types': doc_types,
    })

@login_required
@no_cache
def add_doc_types(request):
    doc_type_form = uploadDocTypeForm(request.POST)
    if request.method == 'POST':
        if doc_type_form.is_valid():
            doc_type_form.save()
            messages.success(request, 'Document Type saved successfully!')
            return redirect('document_types')
        else:
            errors = doc_type_form.non_field_errors()
        for error in errors:
                    messages.error(request, error)
    else:
        doc_type_form = uploadDocTypeForm()
    return render(request, 'templates/sub_templates/add_doc_types.html', {
        'doc_type_form': doc_type_form,
    })

@login_required 
@no_cache
def delete_doc_type(request, id):
    doc_type = get_object_or_404(uploadDocType, id=id)
    doc_type.delete()
    messages.success(request, "Document Type Deleted Successfully!")
    return redirect('document_types')

@login_required
@no_cache
def delete_billing_type(request, id):
    billing_type = get_object_or_404(BillingType, id=id)
    billing_type.delete()
    messages.success(request, "Billing Type Deleted Successfully!")
    return redirect('billing_types')

@login_required
@no_cache
def delete_leave_policy(request, id):
    leave_policy = get_object_or_404(LeavePolicy, id=id)
    leave_policy.delete()
    messages.success(request, "Leave Policy Deleted Successfully!")
    return redirect('settings')

@login_required
@no_cache
def edit_leave_policy(request, id):
    leave_policy = get_object_or_404(LeavePolicy, id=id)
    leave_policy_form = LeavePolicyForm(request.POST or None, instance=leave_policy)
    if request.method == 'POST':
        if leave_policy_form.is_valid():
            leave_policy_form.save()
            messages.success(request, 'Leave Policy updated successfully!')
            return redirect('settings')
        else:
            errors = leave_policy_form.non_field_errors()
        for error in errors:
                    messages.error(request, error)
    return render(request, 'templates/sub_templates/edit_leave_policy.html', {
        'leave_policy_form': leave_policy_form,
    })


@login_required
@no_cache
def edit_billing_type(request, id):
    billing_type = get_object_or_404(BillingType, id=id)
    billing_type_form = BillingTypeForm(request.POST or None, instance=billing_type)
    if request.method == 'POST':
        if billing_type_form.is_valid():
            billing_type_form.save()
            messages.success(request, 'Billing Type updated successfully!')
            return redirect('billing_types')
        else:
            errors = billing_type_form.non_field_errors()
        for error in errors:
                    messages.error(request, error)
    return render(request, 'templates/sub_templates/edit_billing_type.html', {
        'billing_type_form': billing_type_form,
    })


@login_required
@no_cache
def edit_doc_type(request, id):
    doc_type = get_object_or_404(uploadDocType, id=id)
    doc_type_form = uploadDocTypeForm(request.POST or None, instance=doc_type)
    if request.method == 'POST':
        if doc_type_form.is_valid():
            doc_type_form.save()
            messages.success(request, 'Document Type updated successfully!')
            return redirect('document_types')
        else:
            errors = doc_type_form.non_field_errors()
        for error in errors:
                    messages.error(request, error)
    return render(request, 'templates/sub_templates/edit_doc_type.html', {
        'doc_type_form': doc_type_form,
    })


@login_required
@no_cache
def edit_payment_terms(request, id):
    payment_term = get_object_or_404(PaymentTerms, id=id)
    payment_terms_form = PaymentTermsForm(request.POST or None, instance=payment_term)
    if request.method == 'POST':
        if payment_terms_form.is_valid():
            payment_terms_form.save()
            messages.success(request, 'Payment Terms updated successfully!')
            return redirect('payment_terms')
        else:
            errors = payment_terms_form.non_field_errors()
        for error in errors:
                    messages.error(request, error)
    return render(request, 'templates/sub_templates/edit_payment_terms.html', {
        'payment_terms_form': payment_terms_form,
    })


@login_required
@no_cache
def leave_policy(request):
    hierarchies = Hierarchy.objects.all()
    leave_policy_form=LeavePolicyForm(request.POST)
    doc_types = uploadDocType.objects.all()
    billingtype=BillingType.objects.all()
    doc_type_form = uploadDocTypeForm(request.POST)
    billing_type_form=BillingTypeForm(request.POST)
    form = ApprovalHierarchyForm(request.POST)

    policy = LeavePolicy.objects.all()

    if request.method == 'POST':


        if 'upload_billing_type_form_submit' in request.POST:
            if billing_type_form.is_valid():
                billing_type_form.save()
                messages.success(request, 'Billing Type saved successfully!')
                return redirect('settings')
            else:
                errors = billing_type_form.non_field_errors()
            for error in errors:
                        messages.error(request, error)


        if 'upload_doc_form_submit' in request.POST:
            if doc_type_form.is_valid():
                doc_type_form.save()
                messages.success(request, 'Upload Document Type saved successfully!')
                return redirect('settings')
            else:
                errors = doc_type_form.non_field_errors()
            for error in errors:
                        messages.error(request, error)



        if 'leave_policy_form_submit' in request.POST:
            
            if leave_policy_form.is_valid():
                leave_policy_form.save()
                messages.success(request, 'Leave Policy saved successfully!')
                return redirect('settings')
            else:
                errors = leave_policy_form.non_field_errors()
            for error in errors:
                        messages.error(request, error)
            




        if 'set_heirarchy' in request.POST:  
            print("hello its working")
            
            if form.is_valid():
                approval_type = form.cleaned_data['approval_type']
                project_name = form.cleaned_data['project_name']
                position = form.cleaned_data['position']
                approver = form.cleaned_data['approver']
                is_final_approver = form.cleaned_data['is_final_approver']

                print(f"Received Data - Approval Type: {approval_type}, Project: {project_name}, Position: {position}, Approver: {approver}, Is Final: {is_final_approver}")

                if is_final_approver:
                    existing_final_approver = Hierarchy.objects.filter(
                        approval_type=approval_type,
                        project_name=project_name,
                        position=position,
                        is_final_approver=True
                    ).first()

                    if existing_final_approver:
                        print(f"Final approver already exists: {existing_final_approver}")
                        messages.error(request, f"A final approver for {approval_type} and project '{project_name}' with position '{position}' is already set.")
                        return redirect('settings')

                existing_hierarchy = Hierarchy.objects.filter(
                    approval_type=approval_type,
                    project_name=project_name,
                    position=position,
                    approver=approver
                ).first()

                if existing_hierarchy:
                    print(f"Existing Hierarchy Entry Found: {existing_hierarchy}")
                    messages.error(request, f"An approver '{approver}' for {approval_type} with position '{position}' is already set.")
                    return redirect('settings')

                last_hierarchy = Hierarchy.objects.filter(
                    approval_type=approval_type,
                    project_name=project_name,
                    position=position
                ).order_by('order_number').last()

                new_order_number = 1 if last_hierarchy is None else last_hierarchy.order_number + 1
                print(f"New Order Number: {new_order_number}")

                approval_hierarchy = Hierarchy(
                    approval_type=approval_type,
                    project_name=project_name,
                    approver=approver,
                    position=position,
                    order_number=new_order_number,
                    is_final_approver=is_final_approver
                )
                approval_hierarchy.save()

                print(f"Approval Hierarchy Saved: {approval_hierarchy}")
                messages.success(request, "Approval hierarchy successfully saved.")
                return redirect('settings')
            else:
                errors = form.non_field_errors()
            for error in errors:
                        messages.error(request, error)


    else:
        form = ApprovalHierarchyForm()
        leave_policy_form= LeavePolicyForm()
        

    return render(request, 'templates/sub_templates/leave_policy.html', {
        'form': form,
        'billing_type_form':billing_type_form,
        'billingtype':billingtype,
        'doc_types':doc_types,
        'doc_type_form':doc_type_form,
        'policy':policy,
        'leave_policy_form':leave_policy_form,
        'hierarchies': hierarchies,
        'projects': projects,
    })

@login_required
@no_cache
def add_payment_terms(request):
    payment_terms_form = PaymentTermsForm(request.POST)
    if request.method == 'POST':
        if payment_terms_form.is_valid():
            payment_terms_form.save()
            messages.success(request, 'Payment Terms saved successfully!')
            return redirect('payment_terms')
        else:
            errors = payment_terms_form.non_field_errors()
        for error in errors:
                    messages.error(request, error)
    else:
        payment_terms_form = PaymentTermsForm()
    return render(request, 'templates/sub_templates/add_payment_terms.html', {
        'payment_terms_form': payment_terms_form,
    })

@login_required
@no_cache
def payment_terms(request):
    payment_terms = PaymentTerms.objects.all()
    return render(request, 'templates/payment_terms.html', {
        'payment_terms': payment_terms,
    })




@login_required
@no_cache
def payment_term_delete_view(request, pk):
    payment_term = get_object_or_404(PaymentTerms, pk=pk)
    payment_term.delete()
    messages.success(request, "Payment Term Deleted Successfully")
    return redirect('payment_terms') 



# def generate_payroll(month_str,employee,date):
#     year, month = map(int, month_str.split('-'))
#     print("Generating payroll for:", employee, year, month)
    
#     timesheets = Timesheet.objects.filter(
#         employee=employee,
#         date__year=year,
#         date__month=month,
#         status='accepted'
#     )
    
#     project_timesheets = defaultdict(list)
#     for timesheet in timesheets:
#         project_timesheets[timesheet.project_id].append(timesheet)
    
#     project_salary_data = {}
    
#     for project_id, project_timesheet_list in project_timesheets.items():
#         unique_days_worked = set(timesheet.date for timesheet in project_timesheet_list)
#         total_days_worked = len(unique_days_worked)
        
#         total_hours_worked = 0.0  
#         total_salary = 0.0  
        
#         print(f"Project {project_id}: Total unique days worked:", total_days_worked)
        
#         for work_day in unique_days_worked:
#             day_timesheets = [t for t in project_timesheet_list if t.date == work_day]
            
#             daily_salary = 0.0
#             for timesheet in day_timesheets:
#                 total_hours = 0.0
#                 try:
#                     hours, minutes = map(int, timesheet.time_in_hrs.split(':'))
#                     total_hours = hours + (minutes / 60.0)
#                 except (ValueError, AttributeError):
#                     print(f"Invalid or missing time_in_hrs for timesheet ID {timesheet.id}. Skipping this entry.")
                
#                 total_hours_worked += total_hours
                
#                 if timesheet.location == 'onsite':
#                     daily_salary += total_hours * employee.onsite_salary
#                 elif timesheet.location == 'remote':
#                     daily_salary += total_hours * employee.remote_salary
            
#             total_salary += daily_salary
        
#         print(f"Project {project_id}: Total salary:", total_salary)
#         print(f"Project {project_id}: Total hours worked:", total_hours_worked)
        
#         project_salary_data[project_id] = {
#             'total_days_worked': total_days_worked,
#             'total_hours_worked': total_hours_worked,
#             'total_salary': total_salary,
#         }
    
#     for project_id, salary_data in project_salary_data.items():
#         salary, created = Salary.objects.get_or_create(
#             employee=employee,
#             project_id=project_id,
#             month=datetime(year, month, 1),
#             defaults={
#                 'total_days_worked': 0,
#                 'total_hours_worked': 0.0,
#                 'total_salary': 0.0,
#             }
#         )
        
#         salary.total_days_worked = salary_data['total_days_worked']
#         salary.total_hours_worked = salary_data['total_hours_worked']
#         salary.total_salary = salary_data['total_salary']
        
#         salary.save()
#         print(f"Salary record updated for Project {project_id}")

from collections import defaultdict
from datetime import datetime
from collections import defaultdict
from datetime import datetime
from collections import defaultdict
from datetime import datetime
# def generate_payroll(month_str, employee, date):
#     year, month = map(int, month_str.split('-'))
#     print(f"Generating payroll for employee: {employee}, Year: {year}, Month: {month}")

#     # Fetch approved leaves for the employee in the selected month and date range
#     leaves = LeaveApplication.objects.filter(
#         employee=employee,
#         status='approved',
#         start_date__lte=date,
#         end_date__gte=datetime(year, month, 1)
#     )

#     # Build a dictionary of leave dates for easier lookup
#     leave_dates_dict = {}
#     for leave in leaves:
#         leave_dates = set(
#             leave.start_date + timedelta(days=i)
#             for i in range((leave.end_date - leave.start_date).days + 1)
#         )
#         leave_dates_dict[leave.id] = {'dates': leave_dates, 'is_paid': leave.leave_type.is_paid}

#     timesheets = Timesheet.objects.filter(
#         employee=employee,
#         date__year=year,
#         date__month=month,
#         status='accepted'
#     )

#     # Store project-wise timesheets
#     project_timesheets = defaultdict(list)
#     for timesheet in timesheets:
#         project_timesheets[timesheet.project_id].append(timesheet)

#     project_salary_data = {}

#     for project_id, project_timesheet_list in project_timesheets.items():
#         unique_days_worked = set(timesheet.date for timesheet in project_timesheet_list)
#         total_days_worked = len(unique_days_worked)
#         total_hours_worked = 0.0
#         total_salary = 0.0

#         print(f"Project {project_id}: Total unique days worked:", total_days_worked)

#         for work_day in unique_days_worked:
#             day_timesheets = [t for t in project_timesheet_list if t.date == work_day]
#             daily_salary = 0.0

#             # Check if the work day overlaps with any approved leave
#             leave_found = False
#             for leave_id, leave_data in leave_dates_dict.items():
#                 if work_day in leave_data['dates']:
#                     leave_found = True
#                     # If leave is paid, calculate salary with onsite rate
#                     if leave_data['is_paid']:
#                         for timesheet in day_timesheets:
#                             try:
#                                 hours, minutes = map(int, timesheet.time_in_hrs.split(':'))
#                                 total_hours = hours + (minutes / 60.0)
#                                 daily_salary += total_hours * employee.onsite_salary
#                                 total_hours_worked += total_hours
#                             except (ValueError, AttributeError):
#                                 print(f"Invalid time_in_hrs for timesheet ID {timesheet.id}. Skipping this entry.")
#                         print(f"Paid leave on {work_day}: Calculating salary using onsite rate.")
#                     else:
#                         print(f"Unpaid leave on {work_day}: No salary calculated.")
#                     break  # Stop further checks for this date

#             # If no leave is found, process timesheet normally
#             if not leave_found:
#                 for timesheet in day_timesheets:
#                     try:
#                         hours, minutes = map(int, timesheet.time_in_hrs.split(':'))
#                         total_hours = hours + (minutes / 60.0)
#                         total_hours_worked += total_hours

#                         if timesheet.location == 'onsite':
#                             daily_salary += total_hours * employee.onsite_salary
#                         elif timesheet.location == 'remote':
#                             daily_salary += total_hours * employee.remote_salary
#                     except (ValueError, AttributeError):
#                         print(f"Invalid time_in_hrs for timesheet ID {timesheet.id}. Skipping this entry.")
            
#             total_salary += daily_salary

#         print(f"Project {project_id}: Total salary:", total_salary)
#         print(f"Project {project_id}: Total hours worked:", total_hours_worked)

#         project_salary_data[project_id] = {
#             'total_days_worked': total_days_worked,
#             'total_hours_worked': total_hours_worked,
#             'total_salary': total_salary,
#         }

#     # Save the salary data
#     for project_id, salary_data in project_salary_data.items():
#         salary, created = Salary.objects.get_or_create(
#             employee=employee,
#             project_id=project_id,
#             month=datetime(year, month, 1),
#             defaults={
#                 'total_days_worked': 0,
#                 'total_hours_worked': 0.0,
#                 'total_salary': 0.0,
#             }
#         )
        
#         salary.total_days_worked = salary_data['total_days_worked']
#         salary.total_hours_worked = salary_data['total_hours_worked']
#         salary.total_salary = salary_data['total_salary']
        
#         salary.save()
#         print(f"Salary record updated for Project {project_id}")


def generate_payroll(month_str, employee, date):
    year, month = map(int, month_str.split('-'))
    print(f"Generating payroll for employee: {employee}, Year: {year}, Month: {month}")

    # Fetch approved leaves for the employee in the selected month and date range
    leaves = LeaveApplication.objects.filter(
        employee=employee,
        status='approved',
        start_date__lte=date,
        end_date__gte=datetime(year, month, 1)
    )

    # Build a dictionary of leave dates for easier lookup
    leave_dates_dict = {}
    for leave in leaves:
        leave_dates = set(
            leave.start_date + timedelta(days=i)
            for i in range((leave.end_date - leave.start_date).days + 1)
        )
        leave_dates_dict[leave.id] = {'dates': leave_dates, 'is_paid': leave.leave_type.is_paid}

    timesheets = Timesheet.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month,
        status='accepted'
    )

    # Store project-wise timesheets
    project_timesheets = defaultdict(list)
    for timesheet in timesheets:
        project_timesheets[timesheet.project_id].append(timesheet)

    project_salary_data = {}

    for project_id, project_timesheet_list in project_timesheets.items():
        unique_days_worked = set(timesheet.date for timesheet in project_timesheet_list)
        total_days_worked = len(unique_days_worked)
        total_hours_worked = 0.0
        total_salary = 0.0

        print(f"Project {project_id}: Total unique days worked:", total_days_worked)

        project = Projects.objects.get(id=project_id)
        client_leaves = ClientLeave.objects.filter(client_id=project.client_name_id)

        client_leave_names = [leave.client_leave_type for leave in client_leaves]

        for work_day in unique_days_worked:
            day_timesheets = [t for t in project_timesheet_list if t.date == work_day]
            daily_salary = 0.0

            leave_found = False
            for leave_id, leave_data in leave_dates_dict.items():
                if work_day in leave_data['dates']:
                    leave_found = True
                    if leave_data['is_paid']:
                        for timesheet in day_timesheets:
                            try:
                                hours, minutes = map(int, timesheet.time_in_hrs.split(':'))
                                total_hours = hours + (minutes / 60.0)
                                daily_salary += total_hours * employee.onsite_salary
                                total_hours_worked += total_hours
                            except (ValueError, AttributeError):
                                print(f"Invalid time_in_hrs for timesheet ID {timesheet.id}. Skipping this entry.")
                        print(f"Paid leave on {work_day}: Calculating salary using onsite rate.")
                    else:
                        print(f"Unpaid leave on {work_day}: No salary calculated.")
                    break  

            if not leave_found:
                for timesheet in day_timesheets:
                    if timesheet.location in client_leave_names:
                        leave_found = True
                        try:
                            hours, minutes = map(int, timesheet.time_in_hrs.split(':'))
                            total_hours = hours + (minutes / 60.0)
                            daily_salary += total_hours * employee.onsite_salary
                            total_hours_worked += total_hours
                        except (ValueError, AttributeError):
                            print(f"Invalid time_in_hrs for timesheet ID {timesheet.id}. Skipping this entry.")
                        print(f"Client leave on {work_day}: Calculating salary using onsite rate.")
                        break

            if not leave_found:
                for timesheet in day_timesheets:
                    try:
                        hours, minutes = map(int, timesheet.time_in_hrs.split(':'))
                        total_hours = hours + (minutes / 60.0)
                        total_hours_worked += total_hours

                        if timesheet.location == 'onsite':
                            daily_salary += total_hours * employee.onsite_salary
                        elif timesheet.location == 'remote':
                            daily_salary += total_hours * employee.remote_salary
                    except (ValueError, AttributeError):
                        print(f"Invalid time_in_hrs for timesheet ID {timesheet.id}. Skipping this entry.")
            
            total_salary += daily_salary

        print(f"Project {project_id}: Total salary:", total_salary)
        print(f"Project {project_id}: Total hours worked:", total_hours_worked)

        project_salary_data[project_id] = {
            'total_days_worked': total_days_worked,
            'total_hours_worked': total_hours_worked,
            'total_salary': total_salary,
        }

    for project_id, salary_data in project_salary_data.items():
        salary, created = Salary.objects.get_or_create(
            employee=employee,
            project_id=project_id,
            month=datetime(year, month, 1),
            defaults={
                'total_days_worked': 0,
                'total_hours_worked': 0.0,
                'total_salary': 0.0,
            }
        )
        
        salary.total_days_worked = salary_data['total_days_worked']
        salary.total_hours_worked = salary_data['total_hours_worked']
        salary.total_salary = salary_data['total_salary']
        
        salary.save()
        print(f"Salary record updated for Project {project_id}")



# def generate_payroll(month_str, employee, date):
#     # Extract year and month from the month_str
#     year, month = map(int, month_str.split('-'))
    
#     end_date = datetime.strptime(date, '%Y-%m-%d')
    
#     print("Generating payroll for:", employee, year, month, "up to", end_date)
    
#     timesheets = Timesheet.objects.filter(
#         employee=employee,
#         date__year=year,
#         date__month=month,
#         date__lte=end_date, 
#         status='accepted'
#     )
    
#     project_timesheets = defaultdict(list)
    
#     for timesheet in timesheets:
#         project_timesheets[timesheet.project_id].append(timesheet)
    
#     project_salary_data = {}
    
#     for project_id, project_timesheet_list in project_timesheets.items():
#         unique_days_worked = set(timesheet.date for timesheet in project_timesheet_list)
#         total_days_worked = len(unique_days_worked)
        
#         total_hours_worked = 0.0  
#         total_salary = 0.0  
        
#         print(f"Project {project_id}: Total unique days worked:", total_days_worked)
        
#         for work_day in unique_days_worked:
#             day_timesheets = [t for t in project_timesheet_list if t.date == work_day]
            
#             daily_salary = 0.0
#             for timesheet in day_timesheets:
#                 total_hours = 0.0
#                 try:
#                     hours, minutes = map(int, timesheet.time_in_hrs.split(':'))
#                     total_hours = hours + (minutes / 60.0)
#                 except (ValueError, AttributeError):
#                     print(f"Invalid or missing time_in_hrs for timesheet ID {timesheet.id}. Skipping this entry.")
                
#                 total_hours_worked += total_hours
                
#                 if timesheet.location == 'onsite':
#                     daily_salary += total_hours * employee.onsite_salary
#                 elif timesheet.location == 'remote':
#                     daily_salary += total_hours * employee.remote_salary
            
#             total_salary += daily_salary
        
#         print(f"Project {project_id}: Total salary:", total_salary)
#         print(f"Project {project_id}: Total hours worked:", total_hours_worked)
        
#         project_salary_data[project_id] = {
#             'total_days_worked': total_days_worked,
#             'total_hours_worked': total_hours_worked,
#             'total_salary': total_salary,
#         }
    
#     for project_id, salary_data in project_salary_data.items():
#         salary, created = Salary.objects.get_or_create(
#             employee=employee,
#             project_id=project_id,
#             month=datetime(year, month, 1),
#             defaults={
#                 'total_days_worked': 0,
#                 'total_hours_worked': 0.0,
#                 'total_salary': 0.0,
#             }
#         )
        
#         salary.total_days_worked = salary_data['total_days_worked']
#         salary.total_hours_worked = salary_data['total_hours_worked']
#         salary.total_salary = salary_data['total_salary']
        
#         salary.save()
#         print(f"Salary record updated for Project {project_id}")


@login_required
@no_cache
def payroll_uae(request):
    payroll=Salary.objects.all()

    if request.method == 'POST':
        month=request.POST.get('payroll_month')
        date=request.POST.get('payment_date')
        payroll_cycle=request.POST.get('payroll_cycle')
        employees=Employee.objects.all()
        for employee in employees:
            generate_payroll(month,employee,date)
    return render(request, 'templates/sub_templates/uae_payroll.html', {
        'payroll': payroll,
    })


@login_required
@no_cache
def payroll(request):
    return render(request, 'templates/payroll.html', {
        
    })