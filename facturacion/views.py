from django.shortcuts import render

# Create your views here.

def start_template(request):
    return render(request, 'template.html')
