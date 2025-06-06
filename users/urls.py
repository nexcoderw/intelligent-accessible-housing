from users.views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'users'

urlpatterns = [
    path('dashboard/', dashboard, name="dashboard"),
    path('search/', search, name="search"),

    path('properties/', properties, name="properties"),

    path('notifications/', notifications, name="notifications"),

    path('applications/', getApplications, name='getApplications'),
    path('property/<int:id>/apply/', sendApplication, name="sendApplication"),

    path('contracts/', getContracts, name='getContracts'),
    path('contract/accept/<int:contract_id>/', acceptContract, name='acceptContract'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)