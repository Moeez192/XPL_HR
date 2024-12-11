from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.conf import settings
from django.utils.timezone import now, timedelta
import uuid , requests
from datetime import datetime
from django.utils.timezone import now
import os, json


def get_country_choices():
    try:
        # Construct the file path
        file_path = os.path.join(settings.STATIC_ROOT, 'countries.json')

        # Open and load the JSON file
        with open(file_path, "r") as file:
            data = json.load(file)

        # Extract and return the list of tuples (code, name)
        return [(country["code"], country["name"]) for country in data]

    except Exception as e:
        # Handle and log any exceptions
        print(f"Error reading country data: {e}")
        return []

def generate_year_choices():
    current_year = datetime.now().year
    return [(year, str(year)) for year in range(current_year - 5, current_year + 51)]   

def get_currency_choices():
    try:
        # Construct the file path for the currencies JSON file
        file_path = os.path.join(settings.STATIC_ROOT, 'currencies.json')

        # Open and load the JSON file
        with open(file_path, "r") as file:
            data = json.load(file)

        # Extract and return the list of tuples (code, name)
        return [(currency["cc"], currency["name"]) for currency in data]

    except Exception as e:
        # Handle and log any exceptions
        print(f"Error reading currency data: {e}")
        return []


class LeavePolicy(models.Model):
    leave_policy = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.leave_policy}"
    
class uploadDocType(models.Model):
    doc_type = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.doc_type}" 


class BillingType(models.Model):
    billing_type=models.CharField(max_length=50)

    def __str__(self):
        return f"{self.billing_type}"


class Employee(models.Model):
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    email = models.EmailField(unique=True)
    last_login = models.DateTimeField(null=True, blank=True) 
    password = models.CharField(max_length=255,default="Progrc@123",blank=True )
    phone = models.CharField(max_length=20)
    address = models.TextField()
    nationality = models.CharField(max_length=100,choices=get_country_choices())

    
    def save(self, *args, **kwargs):
        
        if not self.password:
         self.password = make_password("Progrc@123")  
        else:
        
         if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

    # Job Details
    ROLE = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    employee_role=models.CharField(max_length=20,choices=ROLE,default="user")
    employee_id = models.CharField(max_length=10, unique=True)
    job_title = models.CharField(max_length=100)
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,  
        null=True,                   
        blank=True                   
    )

    
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full-time', 'Full-Time'),
        ('part-time', 'Part-Time'),
        ('contract', 'Contract'),
        ('trainee', 'Trainee'),
        ('intern', 'Intern'),
    ]
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    
    
    
    EMPLOYEE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('resigned', 'Resigned'),
        ('fired', 'Fired'),
        ('blacklisted', 'Blacklisted'),
        ('terminated', 'Terminated'),
    ]
    
    employee_status = models.CharField(max_length=20, choices=EMPLOYEE_STATUS_CHOICES)
    
    # IS_SUPERVISOR = [
    #     ('yes', 'Yes'),
    #     ('no', 'No'),
    #     ]
    
    # is_supervisor = models.CharField(max_length=20, choices=IS_SUPERVISOR)
   
    
    # salary = models.PositiveIntegerField()
    bonus = models.PositiveIntegerField(null=True,blank=True)



    
    #new Fields (new ones) 2
    RATE_BASIS = [
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('n/a', 'N/A'),
    ]
    rate_basis=models.CharField(max_length=20, choices=RATE_BASIS)
    nick_name = models.CharField(max_length=100,null=True,blank=True)
    business_unit = models.CharField(max_length=50,null=True,blank=True)
    mol_id = models.PositiveIntegerField(max_length=14,null=True,blank=True)
    source_of_hire = models.TextField(max_length=50,null=True,blank=True)
    contract_start_date =  models.DateField()
    contract_end_date = models.DateField()
    MARTIAL_STATUS = [
        ('single', 'Single'),
        ('maried ', 'Maried'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('seperated', 'Seperated'),
    ]
    marital_status = models.TextField(max_length=20,choices=MARTIAL_STATUS,default='single')
    linkdln=models.TextField(null=True,blank=True)
    x_twitter=models.TextField(null=True,blank=True)
    personel_phone = models.CharField(max_length=20)
    permanent_address = models.TextField()

        #Seperation Information

    date_of_exit= models.DateField(null=True,blank=True)
    reason_for_exit= models.TextField(null=True,blank=True)
    CAN_JOIN_AGAIN  = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    can_join_again = models.TextField(max_length=4,choices=CAN_JOIN_AGAIN,null=True,blank=True)
    TIMESHEET_REQUIRED=[
        ('yes','Yes'),
        ('no','No')
    ]
    timesheet_required=models.CharField(max_length=4,choices=TIMESHEET_REQUIRED,default='yes')
    account_type = models.CharField(max_length=256)
    routing_code= models.CharField(max_length=256)
    swift_code = models.CharField(max_length=256)
    ifsc_code = models.CharField(max_length=256)
    first_entry_in_country= models.DateField()
    latest_entry_in_country= models.DateField()
    total_expirence = models.CharField(max_length=20)
    latest_exit_from_country= models.DateField(null=True,blank=True)
    leave_policy = models.ForeignKey(LeavePolicy, on_delete=models.SET_NULL,null=True, related_name='employee_leave_policy')
    sap_certifications = models.TextField(null=True,blank=True)
    age = models.CharField(max_length=50,default='0')
    docs = models.ForeignKey(uploadDocType, on_delete=models.SET_NULL,null=True,blank=True, related_name='employee_docs_upload')
    billing_type = models.ForeignKey(BillingType, on_delete=models.SET_NULL,null=True,blank=True, related_name='billing_type_table')
    days_from_latest_entry=models.CharField(max_length=50,default='0')
    bank_country = models.CharField(max_length=100, choices=get_country_choices(), blank=True, null=True)
    WPS_PROFILE =[
        ('yes-uae','Yes-UAE'),
        ('yes-ksa','Yes-KSA'),
        ('no','No')
    ] 
    wps_profile= models.TextField(max_length=10,choices=WPS_PROFILE,default='no')
    skills=models.TextField()
    reporting_manager = models.ForeignKey('self',on_delete=models.SET_NULL,null=True,blank=True,related_name="report_to_manager")



    
    # (new fields (old ones))
    bank_account = models.CharField(max_length=100)
    onsite_salary = models.PositiveIntegerField(null=True)
    remote_salary = models.PositiveIntegerField(null=True)
    account_number = models.CharField(max_length=20,null=True)
    iban_number = models.CharField(max_length=20,null=True)

    WORK_LOCATION = [
        ('ksa - kingdom of saudia arabia', 'KSA - Kingdom Of Saudia Arabia'),
        ('dxb - dubai', 'DXB - Dubai'),
        ('pk - pakistan','Pk - Pakistan'),
        ]
    

    POSITION = [
        ('developer', 'Developer'),
        ('management', 'Management'),
        ]
    

    position = models.CharField(max_length=20,choices=POSITION,null=True)


    work_location = models.CharField(max_length=35,choices=WORK_LOCATION,null=True)

    # employeement_type=models.CharField(max_length=35,null=True)

    date_of_joining = models.DateField()




    emergency_name = models.CharField(max_length=256)
    emergency_relation = models.CharField(max_length=256)
    emergency_phone = models.CharField(max_length=20)

    profile_photo = models.ImageField(upload_to='profile_photos/')
    cv_upload = models.FileField(upload_to='cv_uploads/',null=True,blank=True)
    signed_contract = models.FileField(upload_to='signed_contracts/',null=True,blank=True)
    
    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.employee_id}"
    
    def set_password(self, raw_password):
        print("set pwd function is also woring")
        self.password = make_password(raw_password)
        

class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    doctype = models.ForeignKey(uploadDocType, on_delete=models.CASCADE)
    file = models.FileField(upload_to='employee_documents/',blank=True, null=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.doctype.doc_type} - {self.file.name}"

class Department(models.Model):
    dep_name=models.CharField(max_length=50)
    dep_code=models.CharField(max_length=20,blank=True)
    dep_head = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='department_head')
    dep_description=models.CharField(max_length=200,blank=True)

    def __str__(self):
        return self.dep_name
    


class Leaves(models.Model):
     
    IS_PAID = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    leave_name = models.CharField(max_length=20)
    leave_days_allowed = models.PositiveIntegerField()  
    max_leaves_per_month = models.PositiveIntegerField()  
    is_paid = models.CharField(max_length=4,choices=IS_PAID)

    def __str__(self):
        return self.leave_name
    

   
class PaymentTerms(models.Model):
    name = models.CharField(max_length=50)
    days = models.IntegerField()
    def __str__(self):
        return f"{self.name} - {self.days} days"

class ClientInformation(models.Model):
    customer_id = models.CharField(max_length=10)
    CUSTOMER_TYPE = [
        ('Business', 'Business'),
        ('Individual', 'Individual'),
    ]
    customer_type = models.CharField(max_length=50,choices=CUSTOMER_TYPE,blank=False,null=False,default='business')
    company_name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50)
    email_address = models.EmailField()
    customer_number = models.PositiveIntegerField(max_length=20)
    phone=models.IntegerField()
    
    #other Details
    tax_treatment = models.CharField(max_length=50)
    place_of_supply = models.CharField(max_length=50)

    currency = models.CharField(max_length=50,choices=get_currency_choices())
    payment_terms = models.ForeignKey(PaymentTerms,on_delete=models.SET_NULL,null=True,blank=True)
    PORTAL_LANGUAGE = [
        ('english', 'English'),
        ('arabic', 'Arabic'),
    ]
    portal_language = models.CharField(max_length=50,choices=PORTAL_LANGUAGE)
    documents = models.FileField(upload_to='client_documents/',null=True,blank=True)

    # Billing Address
    billing_address = models.TextField()
    INDUSTRY = [
        ('IT', 'IT'),
        ('Software', 'Software'),
    ]
    industry=models.CharField(max_length=50,choices=INDUSTRY,default='IT')
    country_region = models.CharField(max_length=50,choices=get_country_choices())
    address= models.TextField()
    city = models.CharField(max_length=50)
    state= models.CharField(max_length=50)
    zip_code = models.IntegerField()
    phone_number = models.IntegerField()
    fax_number = models.IntegerField()

    # client Calendar settings
    WEEKEND=[
        ('Friday/Saturday','Friday/Saturday'),
        ('Saturday/Sunday','Saturday/Sunday'),
    ]
    YEARS=[
        ('2022','2022'),
        ('2023','2023'),
        ('2024','2024'),
        ('2025','2025'),
        ('2026','2026'),
        ('2027','2027')
    ]
    year=models.CharField(max_length=4,choices=YEARS,default='2024')
    weekend=models.CharField(max_length=50,choices=WEEKEND,default='Saturday/Sunday')

    def __str__(self):
        return f"{self.company_name}"

class ClientLeave(models.Model):
    client = models.ForeignKey(ClientInformation, related_name="client_leaves", on_delete=models.CASCADE)
    client_leave_type = models.CharField(max_length=100)
    client_leave_date = models.DateField()

    def __str__(self):
        return f"{self.leave_type} on {self.leave_date}"

class XPL_ClientContact(models.Model):
    client = models.ForeignKey(ClientInformation, on_delete=models.CASCADE, related_name='client_contacts')
    full_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    client_position = models.CharField(max_length=100)
    client_contact_number = models.CharField(max_length=20)

    def __str__(self):
            return f"{self.full_name}"

class Projects(models.Model):
    project_name = models.CharField(max_length=30)
    project_description = models.TextField()
    start_date = models.DateField()
    deadline = models.DateField()
    requirement_file = models.FileField(upload_to='projects/')
    project_manager = models.CharField(max_length=100)
    team_members = models.ManyToManyField(Employee, related_name='project_team_members')
    IS_TIMESHEET_REQUIRED = [
        ('yes','Yes'),
        ('no','No'),
    ]
    is_timesheet_required = models.CharField(max_length=4,choices=IS_TIMESHEET_REQUIRED)
    PRIORITY = [
        ('high','High'),
        ('medium','Medium'),
        ('low','Low'),
    ]
    priority = models.CharField(max_length=20,choices=PRIORITY)
    STATUS = [
        ('not started','Not Started'),
        ('in progress','In Progress'),
        ('complete','Complete'),
    ]
    status=models.CharField(max_length=20,choices=STATUS)

    # new Fields
    client_manager=models.ForeignKey(XPL_ClientContact,on_delete=models.SET_NULL,null=True,blank=True,related_name='client_manager')
    project_sponsor=models.ForeignKey(Employee,on_delete=models.SET_NULL,null=True,blank=True,related_name='project_sponsor')
    timesheet_approver=models.ForeignKey(Employee,on_delete=models.SET_NULL,null=True,blank=True,related_name='timesheet_approver')
    client_name=models.ForeignKey(ClientInformation,on_delete=models.CASCADE,null=True,blank=True,related_name='client_name')
    BILLING_METHOD={
        ('Time & Material','Time & Material'),
        ('Fixed Price','Fixed Price'),
    }
    billing_method=models.CharField(max_length=20,choices=BILLING_METHOD,default='Fixed Price')
    project_budget=models.PositiveIntegerField()
    project_location=models.CharField(max_length=256)

    def remaining_days(self):
        if self.deadline and self.start_date:
            total_days = (self.deadline - self.start_date).days
            elapsed_days = (timezone.now().date() - self.start_date).days
            remaining = total_days - elapsed_days
            return remaining  # Return 0 if all days have elapsed
        return None  # or return a default value if start_date or deadline is None
    def __str__(self):
            return self.project_name


class XPL_EmployeeBilling(models.Model):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='employee_billings')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='project_assignments')
    BILLING_TYPE = [
        ('E1', 'E1'),
        ('E2', 'E2'),
        ('A1', 'A1'),
        ('C1', 'C1'),
    ]
    billing_type = models.CharField(max_length=50, choices=BILLING_TYPE)

class LeaveApplication(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Link to the Employee model
    leave_type = models.ForeignKey(Leaves, on_delete=models.CASCADE)
    resource_replacement_email_id = models.EmailField()
    start_date = models.DateField()
    end_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    reason = models.TextField()
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Default status

    # Fields for approvers
    # first_approver = models.ForeignKey(Employee, related_name='leave_first_approvals', null=True, blank=True, on_delete=models.SET_NULL)
    # second_approver = models.ForeignKey(Employee, related_name='leave_second_approvals', null=True, blank=True, on_delete=models.SET_NULL)
    # final_approver = models.ForeignKey(Employee, related_name='leave_final_approvals', null=True, blank=True, on_delete=models.SET_NULL)
    current_approver = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL, related_name='current_approvals')

    # Remarks from approvers
    # remarks_first_approver = models.TextField(null=True, blank=True)
    # remarks_second_approver = models.TextField(null=True, blank=True)
    # remarks_final_approver = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.first_name} - {self.leave_type.leave_name} ({self.start_date} to {self.end_date})"
    
    @property
    def leave_days(self):
        return (self.end_date - self.start_date).days + 1
    

class Timesheet(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    date = models.DateField()
    task_description = models.TextField(blank=True, null=True)
    current_approver = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL, related_name='current_approvers')
    reject_reason = models.TextField(blank=True, null=True)
    time_in_hrs = models.CharField(max_length=6, null=True, blank=True)

    location = models.CharField(
        max_length=250,
        # choices=[('onsite', 'Onsite'),
        #         ('remote', 'Remote'),
        #         # ('holiday','Holiday'),
        #         ]
    )
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('saved', 'Saved'),  
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]
    notes = models.TextField(blank=True, null=True)
    supervisor_approved = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=True)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    timesheet_group_id = models.CharField(max_length=100, blank=True, null=True)  

    def __str__(self):
        return f"{self.employee.first_name} - {self.project.project_name} - {self.date}"


class EducationalDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    document_name = models.CharField(max_length=255)
    document_file = models.FileField(upload_to='documents/')
    file_size = models.PositiveIntegerField(null=True)  # Storing file size in bytes
    upload_date = models.DateTimeField(default=now)  # Automatically track upload date

    def save(self, *args, **kwargs):
        # Calculate file size in KB or MB (bytes / 1024 = KB)
        self.file_size = self.document_file.size
        super().save(*args, **kwargs)

class Salary(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='salaries'  # Use a different related name
    )
    month = models.DateField()  # Or any suitable field for the month
    total_days_worked = models.IntegerField(null=False)
    total_salary = models.IntegerField()


class Hierarchy(models.Model):
    APPROVAL_TYPES = [
        ('leave', 'Leave'),
        ('timesheet', 'Timesheet'),
    ]
    
    POSITION_CHOICES = [
        ('developer', 'Developer'),
        ('management', 'Management'),
    ]

    approval_type = models.CharField(max_length=50, choices=APPROVAL_TYPES)
    project_name = models.ForeignKey(Projects, null=True, blank=True, on_delete=models.SET_NULL)  
    approver = models.ForeignKey(Employee,on_delete=models.CASCADE)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    order_number = models.PositiveIntegerField() 
    is_final_approver = models.BooleanField(default=False)

    class Meta:
        unique_together = ('approval_type','position', 'project_name', 'order_number') 

    def __str__(self):
        return f'{self.approval_type} Approval by {self.approver} in project {self.project_name or "General"}'

    def save(self, *args, **kwargs):
        if not self.order_number:  
            last_order = Hierarchy.objects.filter(
                approval_type=self.approval_type, project_name=self.project_name
            ).order_by('order_number').last()

            # If there are no previous approvers, start from 1
            if last_order:
                self.order_number = last_order.order_number + 1
            else:
                self.order_number = 1  # Start numbering from 1 if none exist

        super().save(*args, **kwargs)



class ProjectFile(models.Model):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="project_files")
    file_name= models.CharField(max_length=100,null=False, blank=False)
    uploaded_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_on = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=False, blank=False)

    def __str__(self):
        return f"File for {self.project.project_name} uploaded by {self.uploaded_by.username if self.uploaded_by else 'Unknown'}"


class PasswordResetToken(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="reset_tokens")
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex  # Generate a unique token
        if not self.expiry_at:
            self.expiry_at = now() + timedelta(minutes=5)  # Set expiry to 5 minutes from now
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if the token is still valid."""
        return now() <= self.expiry_at

class DateRange(models.Model):
    project = models.ForeignKey(Projects,on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    month = models.CharField(max_length=50)
    year = models.IntegerField(default=2019)

    def __str__(self):
        return f"{self.project.project_name}: {self.start_date} - {self.end_date}"
 




    
