from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone



class Employee(models.Model):
    # Personal Information
    first_name = models.CharField(max_length=100,)
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
    password = models.CharField(max_length=255,default="pakistan",blank=True )
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.password:
            self.password = "pakistan"
        
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
        ('intern', 'Intern'),
    ]
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    
    date_of_joining = models.DateField()
    
    EMPLOYEE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on-leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]
    
    employee_status = models.CharField(max_length=20, choices=EMPLOYEE_STATUS_CHOICES)
    
    IS_SUPERVISOR = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ]
    
    is_supervisor = models.CharField(max_length=20, choices=IS_SUPERVISOR)
   
    work_location = models.CharField(max_length=255)

    salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2)
    bank_account = models.CharField(max_length=100)

    emergency_name = models.CharField(max_length=100)
    emergency_relation = models.CharField(max_length=100)
    emergency_phone = models.CharField(max_length=12)

    profile_photo = models.ImageField(upload_to='profile_photos/')
    cv_upload = models.FileField(upload_to='cv_uploads/')
    signed_contract = models.FileField(upload_to='signed_contracts/')
    
    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.employee_id}"
    
    def set_password(self, raw_password ):
        self.password = make_password(raw_password)
        



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
    AUTO_APPROVAL = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    leave_name = models.CharField(max_length=20)
    leave_days_allowed = models.IntegerField(max_length=3, blank=True, null=True)  
    max_leaves_per_month = models.IntegerField(max_length=3)  
    is_paid = models.CharField(max_length=4,choices=IS_PAID)
    auto_approval = models.CharField(max_length=4,choices=AUTO_APPROVAL)

    def __str__(self):
        return self.leave_name
    

class Projects(models.Model):
    project_name = models.CharField(max_length=30)
    client_name = models.CharField(max_length=20)
    project_description = models.CharField(max_length=256)
    start_date = models.DateField()
    deadline = models.DateField()
    requirement_file = models.FileField(upload_to='projects/')
    project_manager = models.CharField(max_length=20)
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

    def remaining_days(self):
        if self.deadline and self.start_date:
            total_days = (self.deadline - self.start_date).days
            elapsed_days = (timezone.now().date() - self.start_date).days
            remaining = total_days - elapsed_days
            return max(0, remaining)  # Return 0 if all days have elapsed
        return None  # or return a default value if start_date or deadline is None


class LeaveApplication(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Link to the Employee model
    leave_type = models.ForeignKey(Leaves, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='Pending')  # Default status

    def __str__(self):
        return f"{self.employee.first_name} - {self.leave_type.leave_name} ({self.start_date} to {self.end_date})"
    
    @property
    def leave_days(self):
        return (self.end_date - self.start_date).days + 1
    
    

