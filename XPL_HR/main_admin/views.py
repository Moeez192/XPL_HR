from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.hashers import check_password 
from .forms import EmployeeForm , DepForm , LeaveForm , LoginForm , ProjectForm , LeaveApplicationForm , EmployeeUpdateForm , EducationalDocumentForm , TimesheetForm , ApprovalHierarchyForm
from .models import Employee , Department , Leaves , Projects , LeaveApplication , EducationalDocument, Timesheet , Salary, Hierarchy
from django.contrib import messages 
from django.conf import settings
from calendar import monthrange
from django.db.models import Q  # Import Q here

from wkhtmltopdf.views import PDFTemplateView
from weasyprint import HTML
from collections import defaultdict

from django.template.loader import render_to_string

from django.http import HttpResponse
from django.template.loader import get_template

from django.urls import reverse_lazy
from django.views.generic import DeleteView 
from django.views.decorators.http import require_POST
from django.views import View
from calendar import month_name
from xhtml2pdf import pisa
from io import BytesIO

from django.shortcuts import render
from django.contrib.auth import logout
from django.urls import reverse
from .models import Employee 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.utils.decorators import decorator_from_middleware
from django.middleware.cache import CacheMiddleware
from datetime import datetime
import csv


# disable the cache decorator code
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
            login(request, user)  # Log the user in
            
            # Fetch the role from the Employee model and store it in session
            try:
                employee = Employee.objects.get(email=email)
                request.session['role'] = employee.employee_role  # Store the role in session
                
                print("Session after login:", request.session.keys())  
                return redirect("dashboard")  # Redirect to dashboard
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
    return redirect('employees')


@login_required
@no_cache
def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employees')  # Redirect to the employee list or details page after saving
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'templates/sub_templates/edit_employee.html', {
        'form': form, 
        'employee': employee,
        })

@login_required
@no_cache
def edit_employee_self(request):
    employee = Employee.objects.get(email=request.user.email)
    if request.method == 'POST':
        form = EmployeeUpdateForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect to the employee list or details page after saving
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
    return redirect('departments')


@login_required
@no_cache
def employees(request):
     # Handle employee form
    total_employees = Employee.objects.count()
    total_supervisors = Employee.objects.filter(is_supervisor='yes').count()
    department_list = Department.objects.all()
    total_departments = Department.objects.count()
    employee_list = Employee.objects.all()

    if request.method == 'POST':
        if 'employee_submit' in request.POST:
            employee_form = EmployeeForm(request.POST, request.FILES)
            if employee_form.is_valid():
                employee_form.save()
                messages.success(request, 'Employee added successfully!')
                return redirect('employees')  # Redirect to avoid form resubmission
        elif 'department_submit' in request.POST:
            department_form = DepForm(request.POST)
            if department_form.is_valid():
                department_form.save()
                messages.success(request, 'Department added successfully!')
                return redirect('employees')  # Redirect to avoid form resubmission
    else:
        employee_form = EmployeeForm()  # Initialize empty form on GET request
        department_form = DepForm()  # Initialize empty form on GET request

    return render(request, 'templates/employees.html', {
        'form': employee_form,
        'total_employees': total_employees,
        'total_departments': total_departments,
        'dep_list': department_list,
        'total_supervisors':total_supervisors,
        'employee_list': employee_list,
        'dep_form': department_form,
    })

# @login_required
# @no_cache
# def leave(request):
#     employee = Employee.objects.get(email=request.user.email)
#     logged_in_user = LeaveApplication.objects.filter(employee=employee)
#     all_leaves = Leaves.objects.all()
#     leave_applications = LeaveApplication.objects.all()

#     leave_form = LeaveForm()
#     leave_application_form = LeaveApplicationForm(employee=employee)  

#     if request.method == 'POST':
#         # Check which form is being submitted
#         if 'leave_form' in request.POST:
#             leave_form = LeaveForm(request.POST)
#             if leave_form.is_valid():
#                 leave_form.save()
#                 messages.success(request, 'Leave information has been successfully submitted!')
#                 return redirect('leave')

#         elif 'leave_application_form' in request.POST:
#             leave_application_form = LeaveApplicationForm(request.POST, employee=employee)  
#             if leave_application_form.is_valid():
#                 leave_application = leave_application_form.save(commit=False)
#                 leave_application.employee = employee  
#                 print("Remarks:", leave_application_form.cleaned_data['remarks'])
#                 leave_application.save()
#                 messages.success(request, 'Leave application has been successfully submitted!')
#                 return redirect('leave')
#             else:
#                  error_message = ""
#                  non_field_errors = leave_application_form.errors.get('__all__', [])
#                  for error in non_field_errors:
#                         error_message += f"{error}" 
#                  for field, errors in leave_application_form.errors.items():
#                         if field != '__all__':
#                             for error in errors:
#                                 error_message += f"<strong>{field}</strong>: {error}<br>"
    
#                  messages.error(request,error_message)
                
#                  leave_application_form = LeaveApplicationForm(employee=employee)

#         elif 'status' in request.POST:
#             leave_application_id = request.POST.get('leave_application_id')
#             leave_application = LeaveApplication.objects.get(id=leave_application_id)
#             leave_application.status = request.POST.get('status')
#             leave_application.remarks = request.POST.get('remarks')
#             leave_application.save()
#             messages.success(request, f'Leave application {leave_application.status}.')
#             return redirect('leave')

#     return render(request, 'templates/leave.html', {
#         'leave_form': leave_form,
#         'all_leaves' : all_leaves,
#         'logged_in_user': logged_in_user,
#         'leave_application_form': leave_application_form,
#         'leave_applications': leave_applications,
#     })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import LeaveApplication, Employee, Hierarchy
from .forms import LeaveForm, LeaveApplicationForm

@login_required
@no_cache
def leave(request):
    employee = Employee.objects.get(email=request.user.email)
    logged_in_user = LeaveApplication.objects.filter(employee=employee)
    all_leaves = Leaves.objects.all()
    leave_applications = LeaveApplication.objects.none()  # Start with an empty queryset

    # Fetch the approval hierarchy for the employee's position
    approval_hierarchy = Hierarchy.objects.filter(position=employee.position).first()

    # Check if the logged-in user is an approver
    is_approver = False
    if approval_hierarchy:
        approvers = [
            approval_hierarchy.first_approver,
            approval_hierarchy.second_approver,
            approval_hierarchy.final_approver
        ]
        
        # Check if the logged-in user is in the list of approvers
        is_approver = employee in approvers
        
        if is_approver:
            # Filter leave applications for the approvers only
            leave_applications = LeaveApplication.objects.filter(
                Q(first_approver__in=approvers) | 
                Q(second_approver__in=approvers) | 
                Q(final_approver__in=approvers)
            )

    leave_form = LeaveForm()
    leave_application_form = LeaveApplicationForm(employee=employee)  

    if request.method == 'POST':
        if 'leave_application_form' in request.POST:
            leave_application_form = LeaveApplicationForm(request.POST, employee=employee)  
            if leave_application_form.is_valid():
                leave_application = leave_application_form.save(commit=False)
                leave_application.employee = employee  
                
                # Assign approvers
                if approval_hierarchy:
                    leave_application.first_approver = approval_hierarchy.first_approver
                    leave_application.second_approver = approval_hierarchy.second_approver
                    leave_application.final_approver = approval_hierarchy.final_approver
                    leave_application.current_approver = approval_hierarchy.first_approver

                leave_application.save()
                messages.success(request, 'Leave application has been successfully submitted!')
                return redirect('leave')
            else:
                messages.error(request, 'Error in leave application submission.')
                leave_application_form = LeaveApplicationForm(employee=employee)

        if 'leave_form' in request.POST:
            leave_form = LeaveForm(request.POST)
            if leave_form.is_valid():
                leave_form.save()
                messages.success(request, 'Leave information has been successfully submitted!')
                return redirect('leave')
            
        elif 'status' in request.POST:
            leave_application_id = request.POST.get('leave_application_id')
            leave_application = LeaveApplication.objects.get(id=leave_application_id)
            current_user = Employee.objects.get(email=request.user.email)

            # Check if the application is already rejected
            if leave_application.status == 'rejected':
                messages.error(request, 'This application has already been rejected and cannot be processed further.')
                return redirect('leave')

            # Rejection logic: if rejected, stop the process
            if request.POST.get('action') == 'rejected':
                leave_application.status = 'rejected'  # Set status as rejected
                leave_application.remarks = f'Rejected by {current_user.first_name}'  # Update remarks
                leave_application.current_approver = None  # No more approvers, process stops
                leave_application.save()
                messages.success(request, 'Leave application has been rejected.')
                return redirect('leave')

            # Approval logic
            if leave_application.current_approver == current_user:
                if leave_application.status == 'pending':
                    leave_application.status = 'pending second approval'  # First approver action
                    leave_application.remarks = f'Approved by {current_user.first_name}'
                    leave_application.current_approver = leave_application.second_approver  # Move to second approver
                elif leave_application.status == 'pending second approval':
                    leave_application.status = 'approved by second approver'  # Second approver action
                    leave_application.remarks = f'Approved by {current_user.first_name}'
                    leave_application.current_approver = leave_application.final_approver  # Move to final approver
                elif leave_application.status == 'approved by second approver':
                    leave_application.status = 'approved'  # Final approver action
                    leave_application.remarks = f'Final approval by {current_user.first_name}'
                    leave_application.current_approver = None  # No further approvers

                leave_application.save()
                messages.success(request, f'Leave application {leave_application.status}.')
                return redirect('leave')

    return render(request, 'templates/leave.html', {
        'leave_form': leave_form,
        'all_leaves': all_leaves,
        'logged_in_user': logged_in_user,
        'leave_application_form': leave_application_form,
        'leave_applications': leave_applications if is_approver else None,  # Only show if the user is an approver
    })










    




@login_required
@no_cache
def edit_leave(request, leave_id):
    leave = get_object_or_404(Leaves, id=leave_id)
    
    if request.method == 'POST':
        form = LeaveForm(request.POST, instance=leave)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave type updated successfully!')
            return redirect('leave')  # Redirect to the leave types list
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
    return redirect('leave')
    
@login_required
@no_cache
def projects(request):
    supervisors = Employee.objects.filter(is_supervisor='yes')
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
@require_POST
def project_delete_view(request, pk):
    project = get_object_or_404(Projects, pk=pk)
    project.delete()
    return redirect('projects')

@login_required
@no_cache
def project_edit_view(request, pk):
    project = get_object_or_404(Projects, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects')  # Replace with your project list view name
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'templates/sub_templates/edit_project.html', context)  # Replace with your template name

@login_required
@no_cache
def project_detail_view(request, pk):
    project = get_object_or_404(Projects, pk=pk)
    
    context = {
        'project': project,
    }
    return render(request, 'templates/sub_templates/view_project.html', context)  # Replace with your template name

@login_required
@no_cache 
def forget_pwd(request):
    return render(request,'templates/forget_pwd.html')



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
                messages.error(request, "Each file must be 3MB or less.")
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
def timesheet(request):
    
    employee = Employee.objects.get(email=request.user.email)

    
    timesheets = Timesheet.objects.filter(employee=employee).order_by('-date')
    timesheets_all = Timesheet.objects.all()

    
    projects = Projects.objects.filter(team_members=employee)

    months = [month_name[i] for i in range(1, 13)]
    today = datetime.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        # Get form data
        date_submitted = request.POST.get('date')
        task_description = request.POST.get('task_description')
        location = request.POST.get('location')
        notes = request.POST.get('notes')
        project_id = request.POST.get('project_id')
        

        # Ensure the date submitted is today's date
        # if str(today) != date_submitted:
        #     messages.error(request, "You can only submit timesheets for today's date.")
        #     return redirect('timesheet')

        
        existing_timesheet = Timesheet.objects.filter(
            employee=employee, 
            project_id=project_id, 
            date=today
        ).first()

        if existing_timesheet:
            if existing_timesheet.status == 'pending':
                messages.error(request, "You have already submitted a timesheet for this project today.")
                return redirect('timesheet')
            elif existing_timesheet.status == 'accepted':
                messages.error(request, "Your timesheet for this project today has been accepted. You cannot submit another one.")
                return redirect('timesheet')
            elif existing_timesheet.status == 'rejected':
                
                existing_timesheet.task_description = task_description
                existing_timesheet.location = location
                existing_timesheet.notes = notes
                existing_timesheet.status = 'pending'  # Reset status to pending
                existing_timesheet.save()
                messages.success(request, 'Timesheet resubmitted successfully after rejection.')
                return redirect('timesheet')

        try:
            
            project = Projects.objects.get(id=project_id)
        except Projects.DoesNotExist:
            
            messages.error(request, 'The selected project does not exist.')
            return redirect('timesheet')

        
        timesheet = Timesheet(
            date=date_submitted,
            task_description=task_description,
            location=location,
            notes=notes,
            employee=employee,
            project=project,
            status='pending'  
        )
        timesheet.save()

        messages.success(request, 'Timesheet submitted successfully!')
        return redirect('timesheet')

    context = {
        'projects': projects,
        'timesheets': timesheets,
        'timesheet_all': timesheets_all,
        'employee' : employee,
        'today': today, 
        'months': months,
    }
    return render(request, 'templates/timesheet.html', context)



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
    # Get the accepted timesheets for the month
    timesheets = Timesheet.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month,
        status='accepted'
    )
    
    # Get unique days from the timesheets
    unique_days_worked = set(timesheet.date for timesheet in timesheets)  # Ensures only unique dates are counted
    total_days_worked = len(unique_days_worked)
    
    print("Total unique days worked:", total_days_worked)

    # Get the number of days in the month
    days_in_month = monthrange(year, month)[1]

    # Calculate total salary
    total_salary = 0.0

    # Calculate the salary based on distinct dates and corresponding timesheets
    for work_day in unique_days_worked:
        day_timesheets = timesheets.filter(date=work_day)  # Get all timesheets for that day
        
        # Calculate the salary for each unique day
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
            'total_days_worked': 0,  # Default value if new
            'total_salary': 0.0  ,     # Default value if new
        }  # First day of the month
    )

    # Set the fields before saving
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
def setting(request):
    hierarchies = Hierarchy.objects.all()
    if request.method == 'POST':
        form = ApprovalHierarchyForm(request.POST)
        if form.is_valid():
            position = form.cleaned_data['position']  # Get the position from the form
            approval_for = form.cleaned_data['approval_for']  # Get the approval type (leave/timesheet)

            # Check if a hierarchy already exists for this position and approval type
            if Hierarchy.objects.filter(position=position, approval_for=approval_for).exists():
                messages.error(request, f"Approval hierarchy for {position} and {approval_for} is already set.")
                return redirect('settings')  # Redirect back to settings if hierarchy exists

            # Save the new approval hierarchy if it doesn't exist
            approval_hierarchy = form.save(commit=False)
            approval_hierarchy.save()
            messages.success(request, "Approval hierarchy has been successfully saved.")
            return redirect('settings')  # Redirect to a list of hierarchies after saving
    else:
        form = ApprovalHierarchyForm()

    return render(request, 'templates/settings.html', {
        'form': form,
        'hierarchies': hierarchies,
        })