from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Post
from django import forms


class CreateFileForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'author']
