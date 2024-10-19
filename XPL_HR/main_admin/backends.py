from django.contrib.auth.backends import BaseBackend
from .models import Employee  # Adjust the import based on your project structure
from django.contrib.auth.hashers import check_password

class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = Employee.objects.get(email=email)
            if check_password(password, user.password):
                return user
        except Employee.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Employee.objects.get(pk=user_id)
        except Employee.DoesNotExist:
            return None
