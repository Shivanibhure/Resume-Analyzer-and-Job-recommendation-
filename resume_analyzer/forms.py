from django import forms
from .models import Resume
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ('resume_file',)
