"""
URL configuration for flood_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.signIn, name='sign_in'),  
    path('postSign/', views.postSign, name='postSign'),  
    
         
    path('home/', views.home, name="home"),
    # road
    path('roads/', views.roads, name="roads"),
    path('approve_report/<str:road_rep_id>/', views.approve_report, name='approve_report'),
    path('edit_report/<str:road_rep_id>/', views.edit_report, name='edit_report'),
    path("delete_report/<str:road_rep_id>/", views.delete_report, name="delete_report"),

    #group
    path('groups/', views.groups, name="groups"),
    path('approve_group/<str:grp_id>/', views.approve_group, name='approve_group'),
    path('edit_group/<str:grp_id>/', views.edit_group, name='edit_group'),
    path('delete_group/<str:grp_id>/', views.delete_group, name='delete_group'),

    # member
    path('members/', views.members, name="members"),
    path('edit_member/<str:member_id>/', views.edit_member, name='edit_member'),
    path('delete_member/<str:member_id>/', views.delete_member, name='delete_member'),

    # individual
    path('individuals/', views.individuals, name="individuals"),
    path('approve_individual/<str:indivId>/', views.approve_individual, name='approve_individual'),
    path('edit_individual/<str:indivId>/', views.edit_individual, name='edit_individual'),
    path("delete_individual/<str:indivId>/", views.delete_individual, name="delete_individual"),
    
]
    





