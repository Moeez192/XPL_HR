from django import forms
from .models import Employee , Department , Leaves , Projects , LeaveApplication
from django.utils.timezone import now


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'dob', 'gender', 'email', 'password', 'phone', 'address', 
                  'nationality', 'employee_id', 'job_title', 'department', 'employment_type',
                  'date_of_joining', 'employee_status', 'work_location', 'salary', 'bonus', 'bank_account',
                  'emergency_name', 'emergency_relation', 'emergency_phone', 'profile_photo', 'cv_upload', 
                  'signed_contract','is_supervisor','employee_role','last_login']  

        widgets = {
            'password': forms.PasswordInput(),
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),
        }


class DepForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['dep_name','dep_code','dep_head','dep_description']


class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leaves
        fields = ['leave_name','leave_days_allowed','max_leaves_per_month','is_paid','auto_approval']


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)
    password = forms.CharField(widget=forms.PasswordInput)


class ProjectForm(forms.ModelForm):
     project_manager = forms.ModelChoiceField(
        queryset=Employee.objects.filter(is_supervisor='yes'),
        empty_label="Select Project Manager",  # Optional: placeholder text
        widget=forms.Select(attrs={'class': 'form-control'})
    )
     team_members = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(is_supervisor='no'),  # Query for team members
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'multiple': 'multiple'})  # Enable multiple selection
    )
     
     class Meta:
        model = Projects
        fields=['project_name','client_name','project_description','start_date','deadline','requirement_file','project_manager','team_members','is_timesheet_required','priority','status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
       

class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)
        super(LeaveApplicationForm, self).__init__(*args, **kwargs)
        self.fields['leave_type'].queryset = Leaves.objects.all()  # Populate leave types

    def clean(self):
        cleaned_data = super().clean()
        leave_type = cleaned_data.get('leave_type')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Ensure all required fields are present
        if not leave_type or not start_date or not end_date:
            raise forms.ValidationError("Leave type, start date, and end date are required.")

        # Ensure start date is not in the past
        if start_date < now().date():
            raise forms.ValidationError("Start date cannot be in the past.")

        # Calculate leave days
        leave_days = (end_date - start_date).days + 1

        # Validate maximum leave days for the selected leave type
        if leave_type and leave_days > leave_type.leave_days_allowed:
            raise forms.ValidationError(
                f"You can only apply for a maximum of {leave_type.leave_days_allowed} days for {leave_type.leave_name}."
            )

        # Get the current month
        current_month = now().month
        
        # Get the employee instance from initial data or cleaned data
        employee = self.initial.get('employee')  # Assuming you're setting 'employee' in initial data

        if employee:  # Ensure employee is not None
            # Count approved leaves of the same type in the current month
            approved_leaves_in_current_month = LeaveApplication.objects.filter(
                employee=employee,
                leave_type=leave_type,
                start_date__month=current_month,
                status='approved'  # Only count approved leaves
            ).count()

            # Validate maximum leaves per month for this leave type
            if approved_leaves_in_current_month >= leave_type.max_leaves_per_month:
                raise forms.ValidationError(
                    f"You can only apply for {leave_type.max_leaves_per_month} {leave_type.leave_name} leave(s) in a month."
                )

        return cleaned_data
    


class EmployeeUpdateForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False, label="New Password")  # Optional field

    class Meta:
        model = Employee
        fields = ['email', 'phone', 'new_password', 'emergency_name', 'emergency_relation', 'emergency_phone', 'profile_photo', 'cv_upload', 'signed_contract']  # Removed 'password'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password'].initial = ''  # Clear the initial value for new_password

    def save(self, commit=True):
        employee = super().save(commit=False)  # Get the instance
        new_password = self.cleaned_data.get('new_password')  # Get the new password

        if new_password:  # If a new password is provided
            employee.set_password(new_password)  # Hash the new password

        if commit:
            employee.save()  # Save the employee instance

        return employee