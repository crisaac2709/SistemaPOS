from django.shortcuts import render, redirect



def MyHome(request):
    return render(request, "index.html")