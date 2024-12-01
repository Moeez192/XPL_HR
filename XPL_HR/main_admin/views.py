from django.shortcuts import render, redirect , get_object_or_404
from .forms import EmployeeForm , DepForm , LeaveForm , LoginForm , ProjectForm , LeaveApplicationForm , EmployeeUpdateForm , EducationalDocumentForm , TimesheetForm , ApprovalHierarchyForm , PeriodForm , ProjectFileForm, LeavePolicyForm, uploadDocTypeForm,BillingTypeForm
from .models import Employee , Department , Leaves , Projects , LeaveApplication , EducationalDocument, Timesheet , Salary, Hierarchy , DateRange , ProjectFile , PasswordResetToken,LeavePolicy , uploadDocType , EmployeeDocument , BillingType
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
logger = logging.getLogger(__name__)

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
            login(request, user)  
            
            #  role from  Employee model 
            try:
                employee = Employee.objects.get(email=email)
                request.session['role'] = employee.employee_role  
                
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
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Edited Successfully')
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
def employees(request):
     # Handle employee form
    total_employees = Employee.objects.count()
    total_supervisors = Employee.objects.filter(is_supervisor='yes').count()
    department_list = Department.objects.all()
    department_form = DepForm(request.POST)
    total_departments = Department.objects.count()
    employee_form = EmployeeForm(request.POST, request.FILES)
    employee_list = Employee.objects.all()

    if request.method == 'POST':
        if 'employee_submit' in request.POST:
            # Handle Employee Form
            employee_form = EmployeeForm(request.POST, request.FILES)
            
            if employee_form.is_valid():
                # Save the employee first
                employee = employee_form.save()

                # Now process the uploaded files
                for doc_type in request.FILES:
                    # Extract the document type name (passport_file, visa_file, etc.)
                    doc_type_name = doc_type.split('_')[0]

                    # Try to get the document type from the database
                    try:
                        doc_type_instance = uploadDocType.objects.get(doc_type=doc_type_name)
                    except uploadDocType.DoesNotExist:
                        messages.error(request, f"Document type '{doc_type_name}' not found.")
                        continue  # Skip this document type if not found

                    # Get the uploaded file
                    file = request.FILES[doc_type]

                    # Create the document record for the employee
                    EmployeeDocument.objects.create(
                        employee=employee,
                        doctype=doc_type_instance,
                        file=file
                    )

                messages.success(request, 'Employee added successfully!')
                return redirect('employees')
            else:
                 print("Form errors:", employee_form.errors)
        if 'department_submit' in request.POST:
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




@login_required
@no_cache
def leave(request):
    leaves=Leaves.objects.all()
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
        'all_leaves' : leaves,
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
    messages.success(request,"Project Deleted Successfully!")
    return redirect('projects')

@login_required
@no_cache
def project_edit_view(request, pk):
    project = get_object_or_404(Projects, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES ,instance=project )
        if form.is_valid():
            form.save()
            messages.success(request,"Project Eddited Successfully!")
            return redirect('projects')  # Replace with your project list view name
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'project': project,
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
def timesheet(request):
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

    # Fetch date ranges for all projects
    for project in projects:
        try:
            # Fetch the DateRange for the project
            date_range = DateRange.objects.get(project=project)
            project_date_ranges[project.id] = {
                'start_date': date_range.start_date.strftime('%Y-%m-%d'),
                'end_date': date_range.end_date.strftime('%Y-%m-%d'),
            }
        except DateRange.DoesNotExist:
            project_date_ranges[project.id] = None  # No date range for this project

    # Handle form submissions
    if request.method == 'POST':
        if 'range_form_submit' in request.POST:
            range_form = PeriodForm(request.POST)
            if range_form.is_valid():
                # Get the start and end dates, and project from the form
                start_date = range_form.cleaned_data['start_date']
                end_date = range_form.cleaned_data['end_date']
                project = range_form.cleaned_data['project']

                # Check for existing date ranges for the same project within the specified range
                overlapping_ranges = DateRange.objects.filter(
                    project=project,
                    end_date__gte=start_date,
                    start_date__lte=end_date
                )

                if overlapping_ranges.exists():
                    messages.error(request, 'Date range overlaps with an existing range for this project.')
                else:
                    # Check if an active range exists for the project
                    last_date_range = DateRange.objects.filter(project=project).order_by('-end_date').first()
                    
                    if last_date_range and last_date_range.end_date >= timezone.now().date():
                        messages.error(request, 'Cannot add a new date range until the current one ends.')
                    else:
                        # Check if a range already exists for the project
                        existing_range = DateRange.objects.filter(project=project).first()
                        
                        if existing_range:
                            # Update the existing range with new dates
                            existing_range.start_date = start_date
                            existing_range.end_date = end_date
                            existing_range.save()
                            messages.success(request, 'Date range updated successfully!')
                        else:
                            # Create a new date range
                            date_range = range_form.save(commit=False)
                            date_range.employee = employee  # Optional: associate with employee
                            date_range.save()
                            messages.success(request, 'New date range set successfully!')
                        
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

                    # Check if any required field is missing for weekdays
                    # if not task_description or not location:
                    #     # missing_fields = True
                    #     messages.error(request, f'Missing required fields on {date_str} (weekdays must have all fields filled).')

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

                    # Save or update the timesheet
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
                            'timesheet_group_id': timesheet_group_id,
                        }
                    )
                    if not created:
                        # If timesheet already exists, update it
                        timesheet.task_description = task_description
                        timesheet.location = location
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
    employee_role = submitting_employee.position

    approval_hierarchy = Hierarchy.objects.filter(
        approval_type='timesheet',
        project_name=project_name,
        position=employee_role,
    ).order_by('order_number')  

    if not approval_hierarchy.exists():
        messages.error(request, 'No approval hierarchy found for this project.')
        return redirect('timesheet')

    # Determine the action (accept or reject) from the POST request
    action = request.POST.get('action')
   
    current_approver_index = approval_hierarchy.filter(approver_id=current_employee.id).first()
    final_approver = approval_hierarchy.last()

    if action == 'accept':
        if current_approver_index:
            if current_employee.id == final_approver.approver_id:
                timesheet_group.update(status='accepted', current_approver_id=None)
                messages.success(request, 'Timesheet accepted successfully!')
            else:
                # Mark as pending for final approval
                timesheet_group.update(status='pending', current_approver_id=current_employee.id)
                messages.success(request, 'Timesheet marked as approved and is pending final approval.')

                # Update the current approver to the next in the hierarchy
                next_approver = approval_hierarchy.filter(order_number__gt=current_approver_index.order_number).first()
                if next_approver:
                    timesheet_group.update(current_approver_id=next_approver.approver_id)
        else:
            messages.error(request, 'You are not authorized to approve this timesheet.')

    elif action == 'reject':
        reject_reason = request.POST.get('reject_reason', '').strip()
        print(f"Reject Reason: {reject_reason}")  # Debugging line
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
def submit_timesheet(request, timesheet_group_id):
    if request.method == 'POST':
        timesheets = Timesheet.objects.filter(timesheet_group_id=timesheet_group_id)
        employee = Employee.objects.get(email=request.user.email)
        employee_role=employee.position


        if not timesheets.exists():
            messages.error(request, "No timesheets found for this group.")
            return redirect('some_view_name')

        project_name = timesheets.first().project  
        hierarchy = Hierarchy.objects.filter(
            approval_type='timesheet',
            project_name=project_name,
            position=employee_role,
        ).order_by('order_number')

        if hierarchy.exists():
            first_approver = hierarchy.first()
            timesheets.update(
                status='pending',
                current_approver=first_approver.approver,
            )

            messages.success(request, 'Timesheet group submitted for approval!')
        else:
            messages.error(request, "No approval hierarchy exists for this project's timesheet group. Please contact HR for assistance.")

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

                    # Debug print to verify updated values
                    print(f"Updating timesheet for {date_str}:")
                    print(f"Task: {task_description}, Location: {location}, Notes: {notes}")

                    # Assign and save changes
                    timesheet.task_description = task_description
                    timesheet.location = location
                    timesheet.notes = notes
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
        

    return render(request, 'templates/settings.html', {
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






