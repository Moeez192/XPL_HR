from django import forms
from .models import Employee , Department , Leaves , Projects , LeaveApplication , EducationalDocument , Timesheet , Hierarchy, DateRange, ProjectFile, LeavePolicy, uploadDocType, BillingType
from django.utils.timezone import now
from django.core.exceptions import ValidationError



class LeavePolicyForm(forms.ModelForm):
    class Meta:
        model = LeavePolicy
        fields = ['leave_policy']

class uploadDocTypeForm(forms.ModelForm):
    class Meta:
        model = uploadDocType
        fields = ['doc_type']

class BillingTypeForm(forms.ModelForm):
    class Meta:
        model = BillingType
        fields = ['billing_type']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        # fields = ['first_name', 'last_name', 'dob', 'gender', 'email', 'password', 'phone', 'address', 
        #           'nationality', 'employee_id', 'job_title', 'department', 'employment_type',
        #           'date_of_joining', 'employee_status', 'work_location', 'bonus', 'bank_account',
        #           'emergency_name', 'emergency_relation', 'emergency_phone','is_supervisor','employee_role','last_login','onsite_salary','remote_salary','account_number','iban_number','work_location','position','rate_basis','nick_name','business_unit','mol_id','source_of_hire','contract_start_date','contract_end_date','marital_status','linkdln','x_twitter','personel_phone','permanent_address','date_of_exit','reason_for_exit','can_join_again','account_type','account_type','swift_code','ifsc_code','routing_code','first_entry_in_country','latest_entry_in_country','latest_exit_from_country','total_expirence','leave_policy','sap_certifications','docs','age','days_from_latest_entry','billing_type','bank_country','wps_profile','skills']  
        fields = '__all__'
        
        

        widgets = {
            'password': forms.PasswordInput(),
            'address' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'linkdln' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'x_twitter' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'source_of_hire' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'sap_certifications' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'permanent_address' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'skills' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'reason_for_exit' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),
            'contract_start_date': forms.DateInput(attrs={'type': 'date'}),
            'contract_end_date': forms.DateInput(attrs={'type': 'date'}),
            'date_of_exit': forms.DateInput(attrs={'type': 'date'}),
            'first_entry_in_country': forms.DateInput(attrs={'type': 'date'}),
            'latest_entry_in_country': forms.DateInput(attrs={'type': 'date'}),
            'latest_exit_from_country': forms.DateInput(attrs={'type': 'date'}),
            'age' : forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'days_from_latest_entry' : forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),

        }
    docs = forms.ModelChoiceField(queryset=uploadDocType.objects.all(), empty_label="Select Document")
    def clean_skills(self):
        skills = self.cleaned_data.get("skills", "")
        # Optional validation for special characters, etc.
        return skills


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
        fields = ['leave_type', 'start_date', 'end_date', 'reason','remarks']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)  # Pass employee instance via form kwargs
        super(LeaveApplicationForm, self).__init__(*args, **kwargs)
        self.fields['leave_type'].queryset = Leaves.objects.all()  # Populate leave types

    def clean(self):
        cleaned_data = super().clean()
        leave_type = cleaned_data.get('leave_type')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Ensure all required fields are present
        if not leave_type or not start_date or not end_date:
            raise ValidationError("Leave type, start date, and end date are required.")

        # Ensure start date is not in the past
        if start_date < now().date():
            raise ValidationError("Start date cannot be in the past.")

        # Calculate leave days
        leave_days = (end_date - start_date).days + 1

        # Check 1: Ensure the number of days is positive
        if leave_days <= 0:
            raise ValidationError("The number of leave days must be greater than zero.")

        # Check 2: Ensure that the leave days do not exceed the max allowed for the leave type
        if leave_days > leave_type.leave_days_allowed:
            raise ValidationError(
                f"You can only apply for a maximum of {leave_type.leave_days_allowed} days for {leave_type.leave_name} Leave."
            )
        current_month = now().month
        current_year = now().year

        # Count approved leaves of the same type in the current month
        if self.employee:  
            approved_leaves_in_current_month = LeaveApplication.objects.filter(
                employee=self.employee,
                leave_type=leave_type,
                start_date__month=current_month,
                start_date__year=current_year,
                status='approved'  # Only count approved leaves
            ).count()

            if approved_leaves_in_current_month >= leave_type.max_leaves_per_month:
                raise ValidationError(
                    f"You can only apply for {leave_type.max_leaves_per_month} {leave_type.leave_name} leave(s) in a month."
                )

        return cleaned_data



class TimesheetForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ['date', 'task_description', 'location', 'notes','status','time_in_hrs']

        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'task_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }




class EducationalDocumentForm(forms.ModelForm):
    class Meta:
        model = EducationalDocument
        fields = ['document_name', 'document_file']

    def clean_document_file(self):
        file = self.cleaned_data.get('document_file')

        # Limit file size to 3MB
        # if file and file.size > 3 * 1024 * 1024:
        #     raise forms.ValidationError("File size should be 3MB or less.")
        return file

class EmployeeUpdateForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False, label="New Password")  

    class Meta:
        model = Employee
        fields = ['email', 'phone', 'new_password', 'emergency_name', 'emergency_relation', 'emergency_phone','profile_photo', 'cv_upload', 'signed_contract']  # Removed 'password' 'profile_photo', 'cv_upload', 'signed_contract'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password'].initial = ''  

    def save(self, commit=True):
        
        employee = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')

        if new_password:
            print("this is working")
            employee.set_password(new_password)

        if commit:
            print("commit is working")
            employee.save()

        return employee
    


class ApprovalHierarchyForm(forms.ModelForm):
    class Meta:
        model = Hierarchy
        fields = ['approval_type', 'project_name', 'approver', 'position', 'is_final_approver']

    def clean(self):
        cleaned_data = super().clean()
        approval_type = cleaned_data.get("approval_type")
        project_name = cleaned_data.get("project_name")
        is_final_approver = cleaned_data.get("is_final_approver")
        position = cleaned_data.get("position")

        # If the approver is marked as final, check for existing final approvers for that position
        if is_final_approver:
            existing_final = Hierarchy.objects.filter(
                approval_type=approval_type,
                project_name=project_name,
                position=position,
                is_final_approver=True
            )

            # Log existing final approvers for debugging
            print(f"Existing Final Approvers for {position}: {existing_final.values('approver')}")

            # If a final approver already exists for this position, raise a validation error
            if existing_final.exists():
                raise forms.ValidationError(f"A final approver is already set for the {position} position in the {approval_type} approval type and {project_name} project.")

        return cleaned_data

class ProjectFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFile
        fields = ['file_name','file', 'description']

        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
        }

    # file = forms.FileField(required=True)
    # file_name=
    # description = forms.CharField(widget=forms.Textarea, required=False)

class PeriodForm(forms.ModelForm):
    class Meta:
        model = DateRange
        fields = ['project', 'start_date', 'end_date','year','month']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }