from django.shortcuts import render
from django.template.base import add_to_builtins

# Create your views here.

add_to_builtins('library_app.templatetags.xextends')

def home(request):
    return render(request, 'public_home.html', {  })

def about(request):
    return render(request, 'about.html', {  })



def sign_in(request):
    return render(request, 'sign_in.html', {})


def sign_up(request):
    return render(request, 'sign_up.html', {  })
