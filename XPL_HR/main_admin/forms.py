from django import forms 
from django.forms import modelformset_factory
from .models import Employee , Department , Leaves , Projects , LeaveApplication , EducationalDocument , Timesheet , Hierarchy, DateRange, ProjectFile, LeavePolicy, uploadDocType, BillingType , ClientInformation , PaymentTerms, ClientLeave, XPL_ClientContact , XPL_EmployeeBilling, XPL_EmployeeRole,XPL_Industry,XPL_Position
from django.utils.timezone import now
from datetime import datetime
from django.db.models import Sum
from django.core.exceptions import ValidationError
import random



class XPL_IndustryForm(forms.ModelForm):
    class Meta:
        model = XPL_Industry
        fields = ['industry_name']

class XPL_PositionForm(forms.ModelForm):
    class Meta:
        model = XPL_Position
        fields = ['position_name']

class XPL_EmployeeRoleForm(forms.ModelForm):
    class Meta:
        model = XPL_EmployeeRole
        fields = ['role_name']

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
        fields = '__all__'

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        # fields = ['first_name', 'last_name', 'dob', 'gender', 'email', 'password', 'phone', 'address', 
        #           'nationality', 'employee_id', 'job_title', 'department', 'employment_type',
        #           'date_of_joining', 'employee_status', 'work_location', 'bonus', 'bank_account',
        #           'emergency_name', 'emergency_relation', 'emergency_phone','employee_role','last_login','onsite_salary','remote_salary','account_number','iban_number','work_location','position','rate_basis','nick_name','business_unit','mol_id','source_of_hire','contract_start_date','contract_end_date','marital_status','linkdln','x_twitter','personel_phone','permanent_address','date_of_exit','reason_for_exit','can_join_again','account_type','account_type','swift_code','ifsc_code','routing_code','first_entry_in_country','latest_entry_in_country','latest_exit_from_country','total_expirence','leave_policy','sap_certifications','docs','age','days_from_latest_entry','billing_type','bank_country','wps_profile','skills']  
        fields = '__all__'
        
        

        widgets = {
            'password': forms.PasswordInput(),
            'linkdln' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'x_twitter' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'source_of_hire' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'sap_certifications' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'permanent_address' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'skills' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'reason_for_exit' : forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'dob': forms.DateInput(attrs={'type': 'date','required':True}),
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),
            'contract_start_date': forms.DateInput(attrs={'type': 'date'}),
            'contract_end_date': forms.DateInput(attrs={'type': 'date'}),
            'date_of_exit': forms.DateInput(attrs={'type': 'date'}),
            'first_entry_in_country': forms.DateInput(attrs={'type': 'date'}),
            'latest_entry_in_country': forms.DateInput(attrs={'type': 'date'}),
            'latest_exit_from_country': forms.DateInput(attrs={'type': 'date'}),
            'age' : forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'days_from_latest_entry' : forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
             'profile_photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'profilePhoto',
                'clear_checkbox_label': '', 
                 'currently':'' # Optional: Removes 'Clear' label if present
            }),

        } 
        # docs = forms.ModelChoiceField(queryset=uploadDocType.objects.all(), empty_label="Select Document")

    docs = forms.ModelChoiceField(queryset=uploadDocType.objects.all(),required=False)
    def clean_skills(self):
        skills = self.cleaned_data.get("skills", "")
        return skills
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['profile_photo'].initial = None


class DepForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['dep_name','dep_code','dep_head','dep_description']


class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leaves
        fields = ['leave_name','leave_days_allowed','max_leaves_per_month','is_paid','leave_approver']


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)
    password = forms.CharField(widget=forms.PasswordInput)


class ProjectForm(forms.ModelForm):
     project_manager = forms.ModelChoiceField(
        queryset=Employee.objects.all(), 
        empty_label="Select Project Manager",  
        widget=forms.Select(attrs={'class': 'form-control'})
    )
     client_manager = forms.ModelChoiceField(queryset=XPL_ClientContact.objects.all(), empty_label="Select a Client Manager")
     project_sponsor = forms.ModelChoiceField(
        queryset=Employee.objects.all(),  
        empty_label="Select Project Sponser",  
        widget=forms.Select(attrs={'class': 'form-control'})
    )
     timesheet_approver = forms.ModelChoiceField(
        queryset=Employee.objects.all(),  
        empty_label="Select Timesheet Approver",  
        widget=forms.Select(attrs={'class': 'form-control'})
    )
     team_members = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.all(),  
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'multiple': 'multiple'}),
        required=False  
    )
     billing_type = forms.ChoiceField(
        choices=[],  # Referencing the model's choices
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

     project_description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
     
     class Meta:
        model = Projects
        fields='__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices dynamically from the BillingType table
        self.fields['billing_type'].choices = [
            (bt.id, bt.billing_type,bt.rate) for bt in BillingType.objects.all()
        ]



class LeaveApplicationForm(forms.ModelForm):
    available_leaves = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))

    class Meta:
        model = LeaveApplication
        fields = ['leave_type', 'start_date', 'end_date', 'reason','remarks','resource_replacement_email_id']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'resource_replacement_email_id':forms.EmailInput(attrs={'class': 'form-control','type':'email'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


    
    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)  
        super(LeaveApplicationForm, self).__init__(*args, **kwargs)
    
        if self.employee and self.employee.leave_policy_id:  
            self.fields['leave_type'].queryset = Leaves.objects.filter(id=self.employee.leave_policy_id)  
        else:
            self.fields['leave_type'].queryset = Leaves.objects.none()  

        if self.employee:
                self.calculate_available_leaves()

    def calculate_available_leaves(self):
        
        # leave_type = self.employee.leave_policy_id  
        
        # if not leave_type:
        #     raise ValidationError("Leave policy not found for the employee.")
        # leave_type=Leaves.objects.get(id=leave_type)
        # total_leave_days = leave_type.leave_days_allowed  
        # monthly_leave_entitlement = total_leave_days / 12  

        # start_date = self.employee.date_of_joining  
        # current_date = datetime.now()
        # months_worked = (current_date.year - start_date.year) * 12 + current_date.month - start_date.month

        # available_leaves = months_worked * monthly_leave_entitlement
        # approved_leaves = LeaveApplication.objects.filter(
        #         employee=self.employee,
        #         leave_type=leave_type,
        #         status='approved'
        #     )
        # print(f"Approved Leaves: {approved_leaves}")

        # approved_leave_days = sum(
        #         (leave.end_date - leave.start_date).days + 1 for leave in approved_leaves if leave.end_date and leave.start_date
        #     )

        # available_leaves -= approved_leave_days  
        # print(f"Available Leaves After Deduction: {available_leaves}")


        print("hello")



    def clean(self):
        

        cleaned_data = super().clean()
        leave_type = cleaned_data.get('leave_type')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if not leave_type or not start_date or not end_date:
            raise ValidationError("Leave type, start date, and end date are required.")

        if start_date < now().date():
            raise ValidationError("Start date cannot be in the past.")

        leave_days = (end_date - start_date).days + 1

        if leave_days <= 0:
            raise ValidationError("The number of leave days must be greater than zero.")

        if leave_days > leave_type.leave_days_allowed:
            raise ValidationError(
                f"You can only apply for a maximum of {leave_type.leave_days_allowed} days for {leave_type.leave_name} Leave."
            )

        
        total_leave_days = leave_type.leave_days_allowed  
        monthly_leave_entitlement = total_leave_days / 12 

        if self.employee:
            start_date = self.employee.date_of_joining
            current_date = datetime.now()
            months_worked = (current_date.year - start_date.year) * 12 + current_date.month - start_date.month
            print(f"Months Worked: {months_worked}")

            available_leaves = months_worked * monthly_leave_entitlement
            print(f"Available Leaves: {available_leaves}")

            approved_leaves = LeaveApplication.objects.filter(
                employee=self.employee,
                leave_type=leave_type,
                status__in=['approved', 'pending']
            )
            print(f"Approved Leaves: {approved_leaves}")

            approved_leave_days = sum(
                (leave.end_date - leave.start_date).days + 1 for leave in approved_leaves if leave.end_date and leave.start_date
            )

            available_leaves -= approved_leave_days  
            print(f"Available Leaves After Deduction: {available_leaves}")

            if leave_days > available_leaves:
                raise ValidationError(
                    f"You cannot apply for more than {available_leaves:.2f} days based on your months worked and already availed leaves."
                )

        current_month = now().month
        current_year = now().year
        if self.employee:
            approved_leaves_in_current_month = LeaveApplication.objects.filter(
                employee=self.employee,
                leave_type=leave_type,
                start_date__month=current_month,
                start_date__year=current_year,
                status='approved'  
            ).count()

            if approved_leaves_in_current_month >= leave_type.max_leaves_per_month:
                print(approved_leaves_in_current_month)
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
    

class ClientInformationForm(forms.ModelForm):
    class Meta:
        model = ClientInformation
        fields = '__all__'

        widgets = {
            'customer_id': forms.TextInput(attrs={'readonly': 'readonly','class': 'form-control',}),
            'customer_type': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only generate ID for new instances
        if not self.instance.pk:  
            while True:
                # Generate a unique 4-digit ID
                customer_id = str(random.randint(1000, 9999))
                if not ClientInformation.objects.filter(customer_id=customer_id).exists():
                    self.fields['customer_id'].initial = customer_id
                    break


class PaymentTermsForm(forms.ModelForm):
    class Meta:
        model = PaymentTerms
        fields = '__all__'


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


class ClientLeaveForm(forms.ModelForm):
     class Meta:
            model = ClientLeave
            fields = '__all__'
            widgets = {
            'client_leave_date': forms.DateInput(attrs={'type': 'date'}),
        }
            exclude = ['client']  # Exclude the client field


        # Create a formset for Leave model
ClientLeaveFormSet = modelformset_factory(
    ClientLeave,
    form=ClientLeaveForm,
    extra=1,  # number of empty forms initially shown
    can_delete=True  # Allow deletion of leave records
)


class XPL_ClientContactForm(forms.ModelForm):
    class Meta:
        model = XPL_ClientContact
        fields = '__all__'
        widgets = {
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_type': forms.Select(attrs={'class': 'form-select'}),
        }
        exclude = ['client']  # Exclude the client field



class XPL_EmployeeBillingForm(forms.ModelForm):
    class Meta:
        model = XPL_EmployeeBilling
        fields = '__all__'
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'billing_type': forms.Select(attrs={'class': 'form-select'}),
        }
