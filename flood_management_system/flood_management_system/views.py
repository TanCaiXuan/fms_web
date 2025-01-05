from django.shortcuts import render
import pyrebase
from .firestore import *
from firebase_admin import credentials
from datetime import datetime
from django.utils.safestring import mark_safe
import json



cred = credentials.Certificate('fmsdb-e4283-firebase-adminsdk-7jzkd-f40c56c494.json')
auth = firebase.auth()

def signIn(request):
    return render(request,"signIn.html")

def home(request):
    # Get combined data from both functions
    combined_data = plotNumDate() 
    combined_age = plotAnalyzeOnAge()
    combined_gender = plotAnalyzeOnGender()
    combined_nationality = plotAnalyzeOnNationality()
    combined_medical_history = plotAnalyzeOnMedicalHistory()
    
    # Prepare context with both combined data safely serialized to JSON
    context = {
        'combined_data_json': mark_safe(json.dumps(combined_data)), 
        'combined_age_json': mark_safe(json.dumps(combined_age)), 
        'combined_gender_json': mark_safe(json.dumps(combined_gender)), 
        'combined_nationality_json': mark_safe(json.dumps(combined_nationality)), 
        'combined_medical_history_json': mark_safe(json.dumps(combined_medical_history)), 
    }

    # Render the template with the context
    return render(request, 'home.html', context)


def groups(request):
    groups = read_group()
    return render(request,"groups.html" , {'groups': groups})

def members(request):
    members = read_all_members()
    return render(request,"members.html",{'members':members})

def individuals(request):
    individuals = read_individual()
    return render(request,"individuals.html",{'individuals':individuals})


def roads(request):
    road_reports = read_road()
    return render(request, 'roads.html', {'road_reports': road_reports})


def postSign(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    user = auth.sign_in_with_email_and_password(email, password )
     # Get combined data from both functions
    combined_data = plotNumDate() 
    combined_age = plotAnalyzeOnAge()
    combined_gender = plotAnalyzeOnGender()
    combined_nationality = plotAnalyzeOnNationality()
    combined_medical_history = plotAnalyzeOnMedicalHistory()
    
    # Prepare context with both combined data safely serialized to JSON
    context = {
        'combined_data_json': mark_safe(json.dumps(combined_data)), 
        'combined_age_json': mark_safe(json.dumps(combined_age)), 
        'combined_gender_json': mark_safe(json.dumps(combined_gender)), 
        'combined_nationality_json': mark_safe(json.dumps(combined_nationality)), 
        'combined_medical_history_json': mark_safe(json.dumps(combined_medical_history)), 
    }

    return render(request,"home.html",context)
