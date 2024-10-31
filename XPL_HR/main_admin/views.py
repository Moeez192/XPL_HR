from django.shortcuts import render, redirect , get_object_or_404
from .forms import EmployeeForm , DepForm , LeaveForm , LoginForm , ProjectForm , LeaveApplicationForm , EmployeeUpdateForm , EducationalDocumentForm , TimesheetForm , ApprovalHierarchyForm
from .models import Employee , Department , Leaves , Projects , LeaveApplication , EducationalDocument, Timesheet , Salary, Hierarchy
from django.contrib import messages 
from django.utils.dateparse import parse_date
from datetime import timedelta
from django.conf import settings
from calendar import monthrange
from django.db.models import Q  
from weasyprint import HTML
from collections import defaultdict
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
    return redirect('employees')


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



# below one is new one
# @login_required
# @no_cache
# def leave(request):
#     employee = Employee.objects.get(email=request.user.email)  # The logged-in user
#     leave_applications_to_approve = LeaveApplication.objects.none()  # Start with no applications
#     logged_in_user = LeaveApplication.objects.filter(employee=employee)

#     # Fetch leave applications that require this user as an approver based on submitter's role hierarchy
#     all_applications = LeaveApplication.objects.all()
#     for application in all_applications:
#         submitter_role = application.employee.position  # Role of the submitter

#         # Fetch hierarchy list for the submitter's role
#         approval_hierarchy = Hierarchy.objects.filter(position=submitter_role).order_by('order_number')
#         approvers = [approver.approver for approver in approval_hierarchy]

#         # Check if the logged-in user is the current approver
#         if application.current_approver == employee:
#             leave_applications_to_approve |= LeaveApplication.objects.filter(id=application.id)

#     leave_form = LeaveForm()
#     leave_application_form = LeaveApplicationForm(employee=employee)

#     if request.method == 'POST':
#         if 'leave_application_form' in request.POST:
#             leave_application_form = LeaveApplicationForm(request.POST, employee=employee)
#             if leave_application_form.is_valid():
#                 leave_application = leave_application_form.save(commit=False)
#                 leave_application.employee = employee  # Submitter of the application

#                 # Fetch the first approver in the hierarchy for the submitter’s role
#                 approval_hierarchy = Hierarchy.objects.filter(position=leave_application.employee.position).order_by('order_number')
#                 approvers = [approver.approver for approver in approval_hierarchy]

#                 if approvers:
#                     leave_application.current_approver = approvers[0]  # Set the first approver
#                 leave_application.save()
                
#                 messages.success(request, 'Leave application has been successfully submitted!')
#                 return redirect('leave')

#         elif 'status' in request.POST:
#             leave_application_id = request.POST.get('leave_application_id')
#             leave_application = LeaveApplication.objects.get(id=leave_application_id)
#             current_user = employee  # Approver

#             # Check if the application has already been rejected
#             if leave_application.status == 'rejected':
#                 messages.error(request, 'This application has already been rejected.')
#                 return redirect('leave')

#             if request.POST.get('status') == 'rejected':
#                 leave_application.status = 'rejected'
#                 leave_application.remarks = request.POST.get('remarks', '')
#                 leave_application.current_approver = None
#                 leave_application.save()
#                 messages.success(request, 'Leave application has been rejected.')
#                 return redirect('leave')

#             # Check hierarchy for the submitter's role again
#             submitter_role = leave_application.employee.position  # Get submitter's role
#             approval_hierarchy = Hierarchy.objects.filter(position=submitter_role).order_by('order_number')
#             approvers = [approver.approver for approver in approval_hierarchy]

#             # Approve the leave if the current user is the expected approver
#             if leave_application.current_approver == current_user:
#                 current_index = approvers.index(current_user) if current_user in approvers else -1
#                 next_index = current_index + 1

#                 # Move to the next approver if available, else mark as approved
#                 if next_index < len(approvers):
#                     leave_application.current_approver = approvers[next_index]
#                     leave_application.status = 'pending'
#                 else:
#                     leave_application.current_approver = None
#                     leave_application.status = 'approved'

#                 messages.success(request, 'Leave application status updated successfully.')
#                 return redirect('leave')

#     return render(request, 'templates/leave.html', {
#         'leave_form': leave_form,
#         'leave_application_form': leave_application_form,
#         'leave_applications': leave_applications_to_approve,  # Show applications requiring approval
#         'logged_in_user': logged_in_user,
#     })                 leave_application.save()
#
@login_required
@no_cache
def leave(request):
    employee = Employee.objects.get(email=request.user.email)
    leave_applications_to_approve = LeaveApplication.objects.none()
    logged_in_user = LeaveApplication.objects.filter(employee=employee)

    def get_hierarchy_for_role(employee, project=None):
        # First, try to fetch project-specific hierarchy
        if project:
            hierarchy = Hierarchy.objects.filter(
                project_name=project,
                position=employee.position
            ).order_by('order_number')
            if hierarchy.exists():
                return hierarchy

        # Fall back to role-based hierarchy if no project-specific hierarchy exists
        return Hierarchy.objects.filter(
            position=employee.position,
            project_name=None
        ).order_by('order_number')

    def advance_to_next_approver(leave_application, approvers):
        # Identify the current approver in the list
        current_index = approvers.index(leave_application.current_approver) if leave_application.current_approver in approvers else -1
        next_index = current_index + 1

        # Move to the next approver if available; otherwise, mark as approved
        if next_index < len(approvers):
            leave_application.current_approver = approvers[next_index]
            leave_application.status = 'pending'
        else:
            leave_application.current_approver = None
            leave_application.status = 'approved'
        leave_application.save()

    # Collect leave applications for approval
    all_applications = LeaveApplication.objects.all()
    for application in all_applications:
        submitter = application.employee
        project_assignment = Projects.objects.filter(team_members=submitter).first()
        
        # Fetch appropriate hierarchy
        hierarchy = get_hierarchy_for_role(submitter, project=project_assignment)
        approvers = [entry.approver for entry in hierarchy]

        if employee in approvers:
            leave_applications_to_approve |= LeaveApplication.objects.filter(id=application.id)

    leave_form = LeaveForm()
    leave_application_form = LeaveApplicationForm(employee=employee)

    if request.method == 'POST':
        if 'leave_form' in request.POST:
                leave_form = LeaveForm(request.POST)
                if leave_form.is_valid():
                 leave_form.save()
                 messages.success(request, 'Leave information has been successfully submitted!')
                return redirect('leave')
        if 'leave_application_form' in request.POST:
            leave_application_form = LeaveApplicationForm(request.POST, employee=employee)
            if leave_application_form.is_valid():
                # Check if the employee is assigned to any project
               projects = Projects.objects.filter(team_members=employee)
                
               hierarchy = None
               for project in projects:
                    # First, try finding hierarchy specific to the role and project
                    hierarchy = Hierarchy.objects.filter(position=employee.position, project_name=project).order_by('order_number')
                    if hierarchy.exists():
                        break
                
                # If no project-specific hierarchy exists, check for a general role-based hierarchy
               if not hierarchy or not hierarchy.exists():
                    hierarchy = Hierarchy.objects.filter(position=employee.position, project_name__isnull=True).order_by('order_number')

               if hierarchy.exists():
                    # Proceed with saving the leave application if a hierarchy exists
                    leave_application = leave_application_form.save(commit=False)
                    leave_application.employee = employee

                    # Set the first approver in the hierarchy
                    leave_application.current_approver = hierarchy.first().approver
                    leave_application.status = 'pending'
                    leave_application.save()
                    
                    messages.success(request, 'Leave application has been successfully submitted!')
               else:
                    # If no hierarchy is found, show an error message and don't save the application
                    messages.error(request, "No approval hierarchy exists for your role and project. Please contact HR for assistance.")
                
               return redirect('leave')
            else:
                error_message = ""
                non_field_errors = leave_application_form.errors.get('__all__', [])
                for error in non_field_errors:
                        error_message += f"{error}" 
                for field, errors in leave_application_form.errors.items():
                        if field != '__all__':
                            for error in errors:
                                error_message += f"<strong>{field}</strong>: {error}<br>"
    
                messages.error(request,error_message)
                
                leave_application_form = LeaveApplicationForm(employee=employee)

        elif 'status' in request.POST:
            leave_application_id = request.POST.get('leave_application_id')
            leave_application = LeaveApplication.objects.get(id=leave_application_id)

            # Fetch submitter and hierarchy for the application
            submitter = leave_application.employee
            project_assignment = Projects.objects.filter(team_members=submitter).first()
            hierarchy = get_hierarchy_for_role(submitter, project=project_assignment)
            approvers = [entry.approver for entry in hierarchy]

            if leave_application.current_approver == employee:
                # If status is 'rejected', update and save immediately
                if request.POST.get('status') == 'rejected':
                    leave_application.status = 'rejected'
                    leave_application.remarks = request.POST.get('remarks', '')
                    leave_application.current_approver = None
                    leave_application.save()
                    messages.success(request, 'Leave application rejected.')
                    return redirect('leave')

                # Otherwise, advance to the next approver or approve fully
                advance_to_next_approver(leave_application, approvers)
                messages.success(request, 'Leave application status updated.')
                return redirect('leave')

    return render(request, 'templates/leave.html', {
        'leave_form': leave_form,
        'leave_application_form': leave_application_form,
        'leave_applications': leave_applications_to_approve,
        'logged_in_user': logged_in_user,
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


# @login_required
# @no_cache
# def timesheet(request):
    
#     employee = Employee.objects.get(email=request.user.email)

    
#     timesheets = Timesheet.objects.filter(employee=employee).order_by('-date')
#     timesheets_all = Timesheet.objects.all()

    
#     projects = Projects.objects.filter(team_members=employee)

#     months = [month_name[i] for i in range(1, 13)]
#     today = datetime.today().strftime('%Y-%m-%d')

#     if request.method == 'POST':
#         # Get form data
#         date_submitted = request.POST.get('date')
#         task_description = request.POST.get('task_description')
#         location = request.POST.get('location')
#         notes = request.POST.get('notes')
#         project_id = request.POST.get('project_id')
        

#         existing_timesheet = Timesheet.objects.filter(
#             employee=employee, 
#             project_id=project_id, 
#             date=today
#         ).first()

#         if existing_timesheet:
#             if existing_timesheet.status == 'pending':
#                 messages.error(request, "You have already submitted a timesheet for this project today.")
#                 return redirect('timesheet')
#             elif existing_timesheet.status == 'accepted':
#                 messages.error(request, "Your timesheet for this project today has been accepted. You cannot submit another one.")
#                 return redirect('timesheet')
#             elif existing_timesheet.status == 'rejected':
                
#                 existing_timesheet.task_description = task_description
#                 existing_timesheet.location = location
#                 existing_timesheet.notes = notes
#                 existing_timesheet.status = 'pending'  # Reset status to pending
#                 existing_timesheet.save()
#                 messages.success(request, 'Timesheet resubmitted successfully after rejection.')
#                 return redirect('timesheet')

#         try:
            
#             project = Projects.objects.get(id=project_id)
#         except Projects.DoesNotExist:
            
#             messages.error(request, 'The selected project does not exist.')
#             return redirect('timesheet')

        
#         timesheet = Timesheet(
#             date=date_submitted,
#             task_description=task_description,
#             location=location,
#             notes=notes,
#             employee=employee,
#             project=project,
#             status='pending'  
#         )
#         timesheet.save()

#         messages.success(request, 'Timesheet submitted successfully!')
#         return redirect('timesheet')

#     context = {
#         'projects': projects,
#         'timesheets': timesheets,
#         'timesheet_all': timesheets_all,
#         'employee' : employee,
#         'today': today, 
#         'months': months,
#     }
#     return render(request, 'templates/timesheet.html', context)


@login_required
@no_cache
def timesheet(request):
    employee = Employee.objects.get(email=request.user.email)
    timesheets = Timesheet.objects.filter(employee=employee).order_by('-date')
    projects = Projects.objects.filter(team_members=employee)
    months = [month_name[i] for i in range(1, 13)]
    today = datetime.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
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
        current_date = start_date
        missing_fields = False  # Flag to check if any required field is missing

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            day_of_week = current_date.weekday()  # 5 = Saturday, 6 = Sunday

            # Skip weekends
            if day_of_week not in [5, 6]:  # Not Saturday or Sunday
                task_description = request.POST.get(f'task_description_{date_str}', '').strip()
                location = request.POST.get(f'location_{date_str}', '').strip()
                notes = request.POST.get(f'notes_{date_str}', '').strip()

                # Check if any required field is missing for weekdays
                if not task_description or not location:
                    missing_fields = True
                    messages.error(request, f'Missing required fields on {date_str} (weekdays must have all fields filled).')
                
            current_date += timedelta(days=1)

        # If any required fields are missing, prevent form submission
        if missing_fields:
            return redirect('timesheet')

        # If all required fields are present, proceed with save or submit action
        if action == 'save':
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                day_of_week = current_date.weekday()
                
                if day_of_week not in [5, 6]:  # Only process weekdays
                    task_description = request.POST.get(f'task_description_{date_str}', '').strip()
                    location = request.POST.get(f'location_{date_str}', '').strip()
                    notes = request.POST.get(f'notes_{date_str}', '').strip()

                    timesheet, created = Timesheet.objects.get_or_create(
                        employee=employee,
                        project=project,
                        date=date_str,
                        defaults={
                            'task_description': task_description,
                            'location': location,
                            'notes': notes,
                            'status': 'saved',
                            'is_editable': True,
                        }
                    )
                    if not created:
                        # Update existing timesheet entry if needed
                        timesheet.task_description = task_description
                        timesheet.location = location
                        timesheet.notes = notes
                        timesheet.is_editable = True
                        timesheet.status = 'saved'
                        timesheet.save()

                current_date += timedelta(days=1)

            messages.success(request, 'Timesheet saved successfully!')

        elif action == 'submit':
            # Similar processing as 'save', but with 'submitted' status or additional checks
            pass

        return redirect('timesheet')

    context = {
        'projects': projects,
        'timesheets': timesheets,
        'employee': employee,
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


# @login_required
# @no_cache
# def setting(request):
#     hierarchies = Hierarchy.objects.all()
#     projects = Projects.objects.all()  # Fetch all projects
    
#     if request.method == 'POST':
#         form = ApprovalHierarchyForm(request.POST)
#         if form.is_valid():
#             approval_type = form.cleaned_data['approval_type']
#             project_name = form.cleaned_data['project_name']
#             approver = form.cleaned_data['approver']  # Ensure approver field is included in the form
#             position = form.cleaned_data['position']
#             is_final_approver = form.cleaned_data['is_final_approver']  # Assuming this field is in the form

#             # If this is a final approver, check if an existing hierarchy exists
#             if is_final_approver:
#                 if Hierarchy.objects.filter(approval_type=approval_type, project_name=project_name, is_final_approver=True).exists():
#                     messages.error(request, f"A final approver for {approval_type} and project {project_name} is already set.")
#                     return redirect('settings')  

#             # If it's not a final approver, check if a final approver exists
#             else:
#                 if Hierarchy.objects.filter(approval_type=approval_type, project_name=project_name, is_final_approver=True).exists():
#                     messages.error(request, f"A final approver for {approval_type} and project {project_name} is already set. No new approver can be added.")
#                     return redirect('settings')  

#             # Save the new hierarchy with automatic order number assignment
#             approval_hierarchy = Hierarchy(
#                 approval_type=approval_type,
#                 project_name=project_name,
#                 approver=approver,
#                 position=position,
#                 is_final_approver=is_final_approver
#             )
#             approval_hierarchy.save()  # Calls the overridden save method to handle order number assignment
            
#             messages.success(request, "Approval hierarchy has been successfully saved.")
#             return redirect('settings')  
#     else:
#         form = ApprovalHierarchyForm()

#     return render(request, 'templates/settings.html', {
#         'form': form,
#         'hierarchies': hierarchies,
#         'projects': projects,
#     })





# @login_required
# @no_cache
# def setting(request):
#     hierarchies = Hierarchy.objects.all()
#     projects = Projects.objects.all()  # Fetch all projects

#     if request.method == 'POST':
#         form = ApprovalHierarchyForm(request.POST)
#         if form.is_valid():
#             approval_type = form.cleaned_data['approval_type']
#             project_name = form.cleaned_data['project_name']
#             position = form.cleaned_data['position']
#             approver = form.cleaned_data['approver']
#             is_final_approver = form.cleaned_data['is_final_approver']

#             # Debugging output
#             print(f"Received Data - Approval Type: {approval_type}, Project: {project_name}, Position: {position}, Approver: {approver}, Is Final: {is_final_approver}")

#             # Check if the approver is a final approver
#             if is_final_approver:
#                 # Check if a final approver already exists for this approval type and position
#                 existing_final_approver = Hierarchy.objects.filter(
#                     approval_type=approval_type,
#                     project_name=project_name,
#                     position=position,
#                     is_final_approver=True
#                 ).first()

#                 # Debugging output
#                 if existing_final_approver:
#                     print(f"Final approver already exists: {existing_final_approver}")
#                     messages.error(request, f"A final approver for {approval_type} and project '{project_name}' with position '{position}' is already set.")
#                     return redirect('settings')

#             # Check for existing order numbers to avoid duplication
#             existing_hierarchy = Hierarchy.objects.filter(
#                 approval_type=approval_type,
#                 project_name=project_name,
#                 position=position,
#                 approver=approver
#             ).first()

#             # Debugging output
#             if existing_hierarchy:
#                 print(f"Existing Hierarchy Entry Found: {existing_hierarchy}")
#                 messages.error(request, f"An approver '{approver}' for {approval_type} with position '{position}' is already set.")
#                 return redirect('settings')

#             # Determine the new order number
#             last_hierarchy = Hierarchy.objects.filter(
#                 approval_type=approval_type,
#                 project_name=project_name,
#                 position=position
#             ).order_by('order_number').last()

#             # Debugging output for last hierarchy
#             new_order_number = 1 if last_hierarchy is None else last_hierarchy.order_number + 1
#             print(f"New Order Number: {new_order_number}")

#             # Create and save the new approval hierarchy entry
#             approval_hierarchy = Hierarchy(
#                 approval_type=approval_type,
#                 project_name=project_name,
#                 approver=approver,
#                 position=position,
#                 order_number=new_order_number,
#                 is_final_approver=is_final_approver
#             )
#             approval_hierarchy.save()

#             print(f"Approval Hierarchy Saved: {approval_hierarchy}")
#             messages.success(request, "Approval hierarchy successfully saved.")
#             return redirect('settings')

#     else:
#         form = ApprovalHierarchyForm()

#     return render(request, 'templates/settings.html', {
#         'form': form,
#         'hierarchies': hierarchies,
#         'projects': projects,
#     })


@login_required
@no_cache
def setting(request):
    # hierarchies = Hierarchy.objects.all()
    hierarchies = Hierarchy.objects.all()
  # Fetch all projects

    if request.method == 'POST':
        form = ApprovalHierarchyForm(request.POST)
        if form.is_valid():
            approval_type = form.cleaned_data['approval_type']
            project_name = form.cleaned_data['project_name']
            position = form.cleaned_data['position']
            approver = form.cleaned_data['approver']
            is_final_approver = form.cleaned_data['is_final_approver']

            # Debugging output
            print(f"Received Data - Approval Type: {approval_type}, Project: {project_name}, Position: {position}, Approver: {approver}, Is Final: {is_final_approver}")

            # Check if the approver is a final approver
            if is_final_approver:
                # Check if a final approver already exists for this approval type and position
                existing_final_approver = Hierarchy.objects.filter(
                    approval_type=approval_type,
                    project_name=project_name,
                    position=position,
                    is_final_approver=True
                ).first()

                # Debugging output
                if existing_final_approver:
                    print(f"Final approver already exists: {existing_final_approver}")
                    messages.error(request, f"A final approver for {approval_type} and project '{project_name}' with position '{position}' is already set.")
                    return redirect('settings')

            # Check for existing order numbers to avoid duplication
            existing_hierarchy = Hierarchy.objects.filter(
                approval_type=approval_type,
                project_name=project_name,
                position=position,
                approver=approver
            ).first()

            # Debugging output
            if existing_hierarchy:
                print(f"Existing Hierarchy Entry Found: {existing_hierarchy}")
                messages.error(request, f"An approver '{approver}' for {approval_type} with position '{position}' is already set.")
                return redirect('settings')

            # Determine the new order number
            last_hierarchy = Hierarchy.objects.filter(
                approval_type=approval_type,
                project_name=project_name,
                position=position
            ).order_by('order_number').last()

            # Debugging output for last hierarchy
            new_order_number = 1 if last_hierarchy is None else last_hierarchy.order_number + 1
            print(f"New Order Number: {new_order_number}")

            # Create and save the new approval hierarchy entry
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
        

    return render(request, 'templates/settings.html', {
        'form': form,
        'hierarchies': hierarchies,
        'projects': projects,
    })






