import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta


# Firebase configuration details
config = {
    'apiKey': "AIzaSyC2K-8XhD4GmMXIMlNnYP4vFpy_0Vp3nJA",
    'authDomain': "fmsdb-e4283.firebaseapp.com",
    'databaseURL': "https://fmsdb-e4283-default-rtdb.firebaseio.com",
    'projectId': "fmsdb-e4283",
    'storageBucket': "fmsdb-e4283.firebasestorage.app",
    'messagingSenderId': "103372056660",
    'appId': "1:103372056660:web:262807c1c3b118982925c1",
    'measurementId': "G-Z85BTDYZ5V"
}

# Initialize Pyrebase Firebase app
firebase = pyrebase.initialize_app(config)

# Initialize Firebase Admin SDK and Firestore
def init_firestore_client():
    try:
        # Initialize Firestore with credentials
        cred = credentials.Certificate('fmsdb-e4283-firebase-adminsdk-7jzkd-f40c56c494.json')
        firebase_admin.initialize_app(cred)
        return firestore.client()
    except ValueError:
        # If app is already initialized, return the Firestore client
        return firestore.client()

# Initialize the Firestore client
db = init_firestore_client()

# Function to read road reports from Firestore
def read_road():
    road_ref = db.collection('road_reports')
    docs = road_ref.stream()

    road_reports = [
        {
            'image_url': doc.get('image_url'),
            'location': doc.get('location'),
            'reason': doc.get('reason'),
            'road_rep_id': doc.get('road_rep_id'),
            'timestamp': doc.get('timestamp'),
            'user_id': doc.get('user_id'),
            'statusOfApproved': doc.get('statusOfApproved'),
        }
        for doc in docs
    ]

    return road_reports

# Approve a road report by updating its status
def approve_report(request, road_rep_id):
    road_ref = db.collection('road_reports').document(road_rep_id)
    report = road_ref.get()

    if report.exists:
        road_ref.update({'statusOfApproved': 'true'})
    
    return redirect('roads')  # Redirect to the list of road reports

# Edit a road report
def edit_report(request, road_rep_id):
    road_ref = db.collection('road_reports').document(road_rep_id)
    report = road_ref.get()

    if not report.exists:
        return redirect('roads')  # Redirect if the report doesn't exist

    report_data = report.to_dict()

    if request.method == 'POST':
        updated_location = request.POST.get('location')
        updated_reason = request.POST.get('reason')
        updated_status_of_approval = request.POST.get('status_of_approved') == 'true'

        # Update Firestore document
        road_ref.update({
            'location': updated_location,
            'reason': updated_reason,
            'statusOfApproved': updated_status_of_approval,
        })

        return redirect('roads')  # Redirect to the list of road reports

    return render(request, 'edit_report.html', {'report': report_data})

# Delete a road report
def delete_report(request, road_rep_id):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method. Only GET is allowed."}, status=400)

    try:
        road_ref = db.collection('road_reports').document(road_rep_id)
        road_ref.delete()

        print(f"Document with ID {road_rep_id} has been successfully deleted.")
        return redirect('roads')  # Redirect to the list of road reports

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

#groups

def read_group():
    group_ref = db.collection('groups')  
    docs = group_ref.stream()  # Stream all documents

    groups = [
        {
            'grp_name': doc.get('grp_name'),
            'location': doc.get('location'),
            'statusOfApproved': doc.get('statusOfApproved'),
            'timestamp': doc.get('timestamp'),
            'leader_id': doc.get('leader_id'),
            'member_ids': doc.get('member_ids'),
            'grp_id':  doc.get('grp_id'),
        }
        for doc in docs
    ]

    return groups


# Approve a group by updating its status
def approve_group(request, grp_id):
    group_ref = db.collection('groups').document(grp_id)
    group = group_ref.get()

    if group.exists:
        group_ref.update({'statusOfApproved': 'true'})
    
    return redirect('groups')  # Redirect to the list of groups

# Edit a group
def edit_group(request, grp_id):
    group_ref = db.collection('groups').document(grp_id)
    group = group_ref.get()

    if not group.exists:
        return redirect('groups')  # Redirect if the group doesn't exist

    group_data = group.to_dict()
    old_member_ids = group_data.get('member_ids', [])

    if request.method == 'POST':
        updated_grp_name = request.POST.get('grp_name')
        updated_location = request.POST.get('location')
        updated_status_of_approval = request.POST.get('status_of_approved') 

        # Get the updated member IDs (comma-separated)
        updated_member_ids = request.POST.get('member_ids')  

        # Convert the comma-separated string to a list
        updated_member_ids_list = [member_id.strip() for member_id in updated_member_ids.split(',')]

        # Find which members have been added or removed
        added_member_ids = set(updated_member_ids_list) - set(old_member_ids)
        removed_member_ids = set(old_member_ids) - set(updated_member_ids_list)

        # Update member documents for the added member IDs
        for member_id in added_member_ids:
            member_ref = db.collection('member_details').document(member_id)
            member_ref.update({
                'grp_id': firestore.ArrayUnion([grp_id])  
            })

        # Update member documents for the removed member IDs
        for member_id in removed_member_ids:
            member_ref = db.collection('member_details').document(member_id)
            member_ref.update({
                'grp_id': firestore.ArrayRemove([grp_id])  
            })

        # Update the group document with the new data
        group_ref.update({
            'grp_name': updated_grp_name,
            'location': updated_location,
            'statusOfApproved': updated_status_of_approval,
            'member_ids': updated_member_ids_list,  # Update the member_ids field as a list
        })

        return redirect('groups')  # Redirect to the list of groups

    return render(request, 'edit_group.html', {'group': group_data})

# member
def read_all_members():
    # Reference to the 'member_details' collection in Firestore
    member_ref = db.collection('member_details')  
    
    # Stream all documents in the collection
    docs = member_ref.stream()

    # Create a list of member details based on the documents retrieved
    members = [
        {
            'name': doc.get('name'),
            'birthday': format_birthday(doc.get('birthday')),
            'gender': doc.get('gender'),
            'grp_id': doc.get('grp_id'),
            'ic_number': doc.get('ic_number'),
            'medical_history': doc.get('medical_history'),
            'member_id': doc.get('member_id'),
            'nationality': doc.get('nationality'),
            'passportNum': doc.get('passportNum'),
            'phone_number': doc.get('phone_number'),
            'position': doc.get('position'),
            'race': doc.get('race'),
            'timestamp': doc.get('timestamp'),
            'user_id': doc.get('user_id'),
            'address': doc.get('address'),                       
        }
        for doc in docs
    ]

    return members

def edit_member(request, member_id):
    # Fetch the member from Firestore
    member_ref = db.collection('member_details').document(member_id)
    member = member_ref.get()

    if not member.exists:
        return redirect('members')  # Redirect if the member doesn't exist

    member_data = member.to_dict()

    # Format the birthday field if it's a datetime object
    if member_data.get('birthday'):
        try:
            # If the birthday is a string, we may need to convert it to datetime and then to string in the format 'YYYY-MM-DD'
            birthday = member_data['birthday']
            if isinstance(birthday, str):
                birthday = datetime.strptime(birthday, '%m/%d/%Y')  # Adjust the format if necessary
            member_data['birthday'] = birthday.strftime('%Y-%m-%d')  # Format it as 'YYYY-MM-DD'
        except ValueError:
            # If conversion fails, keep it as is (or handle appropriately)
            pass

    if request.method == 'POST':
        updated_data = {
            'address': request.POST.get('address'),  
            'name': request.POST.get('name'),
            'birthday': request.POST.get('birthday'),
            'gender': request.POST.get('gender'),
            'grp_id': request.POST.get('grp_id'),
            'ic_number': request.POST.get('ic_number'),
            'medical_history': request.POST.get('medical_history'),
            'member_id': request.POST.get('member_id'),
            'nationality': request.POST.get('nationality'),
            'passportNum': request.POST.get('passportNum'),
            'phone_number': request.POST.get('phone_number'),
            'position': request.POST.get('position'),
            'race': request.POST.get('race'),
            'timestamp': request.POST.get('timestamp'),
            'user_id': request.POST.get('user_id'),
            
           }

        # Update Firestore document
        member_ref.update(updated_data)

        return redirect('members')  # Redirect to the members list after update

    return render(request, 'edit_member.html', {'member': member_data})

def format_birthday(birthday):
    if birthday:
        try:
            # Try to convert the string to a datetime object
            if isinstance(birthday, str):
                birthday = datetime.strptime(birthday, '%m/%d/%Y')  # Adjust format if needed
            return birthday.strftime('%m/%d/%Y')  # Return formatted date
        except ValueError:
            # In case the string is not in the expected format, just return it as is
            return birthday
    return None  

# Delete a group and its associated members
def delete_group(request, grp_id):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method. Only GET is allowed."}, status=400)

    try:
        # Delete associated members first
        members_ref = db.collection('member_details').where('grp_id', '==', grp_id)
        members = members_ref.stream()
        
        # Delete all members of the group
        for member in members:
            member_ref = db.collection('member_details').document(member.id)
            member_ref.delete()
            print(f"Member with ID {member.id} has been successfully deleted.")

        # Now, delete the group
        group_ref = db.collection('groups').document(grp_id)
        group_ref.delete()
        
        print(f"Group with ID {grp_id} has been successfully deleted.")
        return redirect('groups')  

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Delete a member
def delete_member(request, member_id):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method. Only GET is allowed."}, status=400)

    try:
        # Delete the member document from the 'member_details' collection
        member_ref = db.collection('member_details').document(member_id)
        member_data = member_ref.get()
        
        if not member_data.exists:
            return JsonResponse({"error": "Member not found."}, status=404)

        # Get the group ID from the member data to update the group collection
        group_id = member_data.to_dict().get('grp_id')
        
        if group_id:
            # Update the 'groups' collection to remove the member_id from the group's 'member_ids' list
            group_ref = db.collection('groups').document(group_id)
            group_ref.update({
                'member_ids': firestore.ArrayRemove([member_id])  # Remove the member_id from the list
            })
            print(f"Member ID {member_id} has been removed from the group {group_id}.")

        # Now delete the member document
        member_ref.delete()
        print(f"Document with ID {member_id} has been successfully deleted.")

        return redirect('members')  # Redirect to the list of members

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# individuals
def read_individual():
    indiv_ref = db.collection('individual_reports')
    docs = indiv_ref.stream()

    individuals = [
        {
            'user_id': doc.get('user_id'),
            'statusOfApproved': doc.get('statusOfApproved'),
            'address': doc.get('address'),
            'birthday': doc.get('birthday'),
            'gender': doc.get('gender'),
            'icNumber': doc.get('ic_number'),
            'indivId': doc.get('indivId'),
            'location': doc.get('location'),
            'medical_history': doc.get('medical_history'),
            'name': doc.get('name'),
            'nationality': doc.get('nationality'),
            'passportNum': doc.get('passportNum'),
            'phone_number': doc.get('phone_number'),
            'race': doc.get('race'),
            'timestamp': doc.get('timestamp'),
		
        }
        for doc in docs
    ]

    return individuals


def approve_individual(request, indivId):
    # Reference the individual report document
    indiv_ref = db.collection('individual_reports').document(indivId)
    
    # Retrieve the report from the database
    report = indiv_ref.get()

    if report.exists:
        # Update the 'statusOfApproved' field to 'true'
        indiv_ref.update({'statusOfApproved': True})
        
        # Redirect to the 'individuals' page
        return redirect('individuals')
     

def edit_individual(request, indivId):
    # Fetch the individual document from Firestore
    indiv_ref = db.collection('individual_reports').document(indivId)
    individual = indiv_ref.get()

    if not individual.exists:
        return redirect('individuals')  # Redirect if the individual doesn't exist

    individual_data = individual.to_dict()

    # Format the birthday field if it's a datetime object
    if individual_data.get('birthday'):
        try:
            # If the birthday is a string, convert it to datetime and then to string in the format 'YYYY-MM-DD'
            birthday = individual_data['birthday']
            if isinstance(birthday, str):
                birthday = datetime.strptime(birthday, '%m/%d/%Y')  # Adjust the format if necessary
            individual_data['birthday'] = birthday.strftime('%Y-%m-%d')  # Format as 'YYYY-MM-DD'
        except ValueError:
            # If conversion fails, keep it as is (or handle appropriately)
            pass

    if request.method == 'POST':
        # Collect updated data from the form
        updated_data = {
            'location': request.POST.get('location'),
            'address': request.POST.get('address'),
            'birthday': request.POST.get('birthday'),
            'gender': request.POST.get('gender'),
            'ic_number': request.POST.get('ic_number'),
            'indivId': request.POST.get('indivId'),
            'medical_history': request.POST.get('medical_history'),
            'name': request.POST.get('name'),
            'nationality': request.POST.get('nationality'),
            'passport_num': request.POST.get('passport_num'),
            'phone_number': request.POST.get('phone_number'),
            'race': request.POST.get('race'),
            'status_of_approved': request.POST.get('status_of_approved') == 'true',  # Convert string to boolean
            'timestamp': request.POST.get('timestamp')
        }

        # Update Firestore document with the new data
        indiv_ref.update(updated_data)

        return redirect('individuals')  # Redirect to the individuals list after update

    return render(request, 'edit_individual.html', {'individual': individual_data})

def delete_individual(request, indivId):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method. Only GET is allowed."}, status=400)

    try:
        indiv_ref = db.collection('individual_reports').document(indivId)
        indiv_ref.delete()

        print(f"Document with ID {indivId} has been successfully deleted.")
        return redirect('individuals')  # Redirect to the list of road reports

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
#plot
def plotNumDate():
    # Read data from Firestore collections
    groups, members, individuals = read_group(), read_all_members(), read_individual()

    # Process group data
    group_dates = [
        datetime.datetime.strptime(group['timestamp'], '%Y-%m-%d').date()
        if isinstance(group['timestamp'], str)
        else group['timestamp'].date()
        for group in groups if group.get('timestamp')
    ]
    group_member_counts = Counter()
    for group in groups:
        if group.get('timestamp') and group.get('member_ids'):
            date = (
                datetime.datetime.strptime(group['timestamp'], '%Y-%m-%d').date()
                if isinstance(group['timestamp'], str)
                else group['timestamp'].date()
            )
            group_member_counts[date] += len(group.get('member_ids', []))

    # Process member data (if additional member-level counts are needed)
    member_dates = [
        datetime.datetime.strptime(member['timestamp'], '%Y-%m-%d').date()
        if isinstance(member['timestamp'], str)
        else member['timestamp'].date()
        for member in members if member.get('timestamp')
    ]
    member_counts = Counter(member_dates)

    # Process individual reports data
    indiv_dates = [
        datetime.datetime.strptime(indiv['timestamp'], '%d/%m/%Y').date()
        if isinstance(indiv['timestamp'], str)
        else indiv['timestamp'].date()
        for indiv in individuals if indiv.get('timestamp')
    ]
    indiv_counts = Counter(indiv_dates)

    # Combine all dates
    all_dates = sorted(set(group_member_counts.keys()) | set(member_counts.keys()) | set(indiv_counts.keys()))
    combined_data = {
        'dates': [date.strftime('%Y-%m-%d') for date in all_dates],
        'members': [group_member_counts.get(date, 0) for date in all_dates],
        'individuals': [indiv_counts.get(date, 0) for date in all_dates],
        'all_members': [group_member_counts.get(date, 0) + member_counts.get(date, 0) for date in all_dates],
    }

    return combined_data


# four graph
def plotAnalyzeOnAge():
    members = read_all_members() or []  
    individuals = read_individual() or []  

    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)

    # Initialize the data containers
    filtered_members = []
    filtered_individuals = []
    ic_numbers_seen = set()  # To track counted ic_numbers

    # Step 1: Calculate age for members
    member_ages = {}
    for member in members:
        if 'ic_number' not in member:
            continue  # Skip if 'ic_number' is missing
        
        if isinstance(member['timestamp'], datetime):
            member['timestamp'] = member['timestamp'].replace(tzinfo=None)

        # Calculate member age
        if isinstance(member.get('birthday'), str):
            member['birthday'] = datetime.strptime(member['birthday'], '%d/%m/%Y')
        birth_year = member['birthday'].year
        age = now.year - birth_year

        # Filter based on timestamp and ic_number uniqueness
        if member['timestamp'] <= seven_days_ago and member['ic_number'] not in ic_numbers_seen:
            ic_numbers_seen.add(member['ic_number'])
            filtered_members.append(member)
            member_ages[age] = member_ages.get(age, 0) + 1

    # Step 2: Calculate age for individuals
    individual_ages = {}
    for individual in individuals:
        if 'ic_number' not in individual:
            continue  # Skip if 'ic_number' is missing
        
        # Calculate individual age
        if isinstance(individual['birthday'], str):
            individual['birthday'] = datetime.strptime(individual['birthday'], '%d/%m/%Y')
        birth_year = individual['birthday'].year
        age = now.year - birth_year

        # Filter based on ic_number uniqueness
        if individual['ic_number'] not in ic_numbers_seen:
            ic_numbers_seen.add(individual['ic_number'])
            filtered_individuals.append(individual)
            individual_ages[age] = individual_ages.get(age, 0) + 1

    # Combine filtered member and individual data for final count
    combined_ages = member_ages.copy()  # Start with member age data
    for age, count in individual_ages.items():
        combined_ages[age] = combined_ages.get(age, 0) + count

    # Prepare the final result with age and count
    combined_data_age = [{'age': age, 'count': count} for age, count in combined_ages.items()]
    combined_data_age = sorted(combined_data_age, key=lambda x: x['age'])

    return combined_data_age  

def plotAnalyzeOnGender():
    members = read_all_members() or []  
    individuals = read_individual() or []  

    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)

    # Initialize the data containers
    filtered_members = []
    filtered_individuals = []
    ic_numbers_seen = set()  # To track counted ic_numbers

    # Step 1: Count gender for members
    member_genders = {'male': 0, 'female': 0, 'other': 0}  # Initialize gender counts
    for member in members:
        if 'ic_number' not in member:
            continue  # Skip if 'ic_number' is missing
        
        if isinstance(member['timestamp'], datetime):
            member['timestamp'] = member['timestamp'].replace(tzinfo=None)

        # Filter based on timestamp and ic_number uniqueness
        if member['timestamp'] <= seven_days_ago and member['ic_number'] not in ic_numbers_seen:
            ic_numbers_seen.add(member['ic_number'])
            filtered_members.append(member)
            
            # Count gender
            gender = member.get('gender', '').lower()  # Assuming gender is stored as 'male', 'female', 'other'
            if gender in member_genders:
                member_genders[gender] += 1

    # Step 2: Count gender for individuals
    individual_genders = {'male': 0, 'female': 0, 'other': 0}  # Initialize gender counts
    for individual in individuals:
        if 'ic_number' not in individual:
            continue  # Skip if 'ic_number' is missing
        
        # Filter based on ic_number uniqueness
        if individual['ic_number'] not in ic_numbers_seen:
            ic_numbers_seen.add(individual['ic_number'])
            filtered_individuals.append(individual)
            
            # Count gender
            gender = individual.get('gender', '').lower()  # Assuming gender is stored as 'male', 'female', 'other'
            if gender in individual_genders:
                individual_genders[gender] += 1

    # Combine filtered member and individual gender data for final count
    combined_genders = member_genders.copy()  # Start with member gender data
    for gender, count in individual_genders.items():
        combined_genders[gender] += count

    # Prepare the final result with gender and count
    combined_data_gender = [{'gender': gender, 'count': count} for gender, count in combined_genders.items()]

    return combined_data_gender

def plotAnalyzeOnNationality():
    members = read_all_members() or []  
    individuals = read_individual() or []  

    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)

    # Initialize the data containers
    filtered_members = []
    filtered_individuals = []
    ic_numbers_seen = set()  # To track counted ic_numbers

    # Step 1: Count nationality for members
    member_nationalities = {}  # Initialize nationality counts
    for member in members:
        if 'ic_number' not in member:
            continue  # Skip if 'ic_number' is missing
        
        if isinstance(member['timestamp'], datetime):
            member['timestamp'] = member['timestamp'].replace(tzinfo=None)

        # Filter based on timestamp and ic_number uniqueness
        if member['timestamp'] <= seven_days_ago and member['ic_number'] not in ic_numbers_seen:
            ic_numbers_seen.add(member['ic_number'])
            filtered_members.append(member)
            
            # Count nationality
            nationality = member.get('nationality', '').lower()  # Assuming nationality is a field in the member data
            if nationality:
                member_nationalities[nationality] = member_nationalities.get(nationality, 0) + 1

    # Step 2: Count nationality for individuals
    individual_nationalities = {}  # Initialize nationality counts
    for individual in individuals:
        if 'ic_number' not in individual:
            continue  # Skip if 'ic_number' is missing
        
        # Filter based on ic_number uniqueness
        if individual['ic_number'] not in ic_numbers_seen:
            ic_numbers_seen.add(individual['ic_number'])
            filtered_individuals.append(individual)
            
            # Count nationality
            nationality = individual.get('nationality', '').lower()  # Assuming nationality is a field in the individual data
            if nationality:
                individual_nationalities[nationality] = individual_nationalities.get(nationality, 0) + 1

    # Combine filtered member and individual nationality data for final count
    combined_nationalities = member_nationalities.copy()  # Start with member nationality data
    for nationality, count in individual_nationalities.items():
        combined_nationalities[nationality] = combined_nationalities.get(nationality, 0) + count

    # Prepare the final result with nationality and count
    combined_data_nationality = [{'nationality': nationality, 'count': count} for nationality, count in combined_nationalities.items()]

    return combined_data_nationality

def plotAnalyzeOnMedicalHistory():
    members = read_all_members() or []  
    individuals = read_individual() or []  

    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)

    # Initialize the data containers
    filtered_members = []
    filtered_individuals = []
    ic_numbers_seen = set()  # To track counted ic_numbers

    
    member_medical_history = {}  
    for member in members:
        if 'ic_number' not in member:
            continue  
        
        if isinstance(member['timestamp'], datetime):
            member['timestamp'] = member['timestamp'].replace(tzinfo=None)

        # Filter based on timestamp and ic_number uniqueness
        if member['timestamp'] <= seven_days_ago and member['ic_number'] not in ic_numbers_seen:
            ic_numbers_seen.add(member['ic_number'])
            filtered_members.append(member)
            
           
            medical_history = member.get('medical_history', '').lower() 
            if medical_history:
                member_medical_history[medical_history] = member_medical_history.get(medical_history, 0) + 1

   
    individual_medical_history = {} 
    for individual in individuals:
        if 'ic_number' not in individual:
            continue 
        
        # Filter based on ic_number uniqueness
        if individual['ic_number'] not in ic_numbers_seen:
            ic_numbers_seen.add(individual['ic_number'])
            filtered_individuals.append(individual)
            

            medical_history = individual.get('medical_history', '').lower()  
            if medical_history:
                individual_medical_history[medical_history] = individual_medical_history.get(medical_history, 0) + 1

   
    combined_medical_history = member_medical_history.copy()  
    for medical_history, count in individual_medical_history.items():
        combined_medical_history[medical_history] = combined_medical_history.get(medical_history, 0) + count

    combined_data_medical_history = [{'medical_history': medical_history, 'count': count} for medical_history, count in combined_medical_history.items()]

    return combined_data_medical_history











