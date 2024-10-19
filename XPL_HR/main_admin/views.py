from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.hashers import check_password 
from .forms import EmployeeForm , DepForm , LeaveForm , LoginForm , ProjectForm , LeaveApplicationForm , EmployeeUpdateForm
from .models import Employee , Department , Leaves , Projects , LeaveApplication
from django.contrib import messages 
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import DeleteView 
from django.views.decorators.http import require_POST
from django.views import View
from django.shortcuts import render
from django.contrib.auth import logout
from django.urls import reverse
from .models import Employee 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.utils.decorators import decorator_from_middleware
from django.middleware.cache import CacheMiddleware

# disable the cache
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

# # Employee edit and delete here
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

@login_required
@no_cache
def leave(request):
    employee = Employee.objects.get(email=request.user.email)
    logged_in_user = LeaveApplication.objects.filter(employee=employee)
    leave_applications = LeaveApplication.objects.all()
    
    # Initialize forms
    leave_form = LeaveForm()
    leave_application_form = LeaveApplicationForm()

    if request.method == 'POST':
        # Check which form is being submitted
        if 'leave_form' in request.POST:
            leave_form = LeaveForm(request.POST)
            if leave_form.is_valid():
                leave_form.save()
                messages.success(request, 'Leave information has been successfully submitted!')
                return redirect('leave')
        elif 'leave_application_form' in request.POST:
            leave_application_form = LeaveApplicationForm(request.POST)
            if leave_application_form.is_valid():
                leave_application = leave_application_form.save(commit=False)
                leave_application.employee = employee  
                leave_application.save()
                messages.success(request, 'Leave application has been successfully submitted!')
                return redirect('leave')
            else:
                leave_application_form = LeaveApplicationForm(initial={'employee': employee})
        # Process the leave approval/rejection
        elif 'status' in request.POST:
            leave_application_id = request.POST.get('leave_application_id')
            leave_application = LeaveApplication.objects.get(id=leave_application_id)
            leave_application.status = request.POST.get('status')
            leave_application.save()
            messages.success(request, f'Leave application {leave_application.status}.')
            return redirect('leave')
    
    return render(request, 'templates/leave.html', {
        'leave_form': leave_form,
        'logged_in_user' : logged_in_user,
        'leave_application_form': leave_application_form,
        'leave_applications': leave_applications,
    })

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