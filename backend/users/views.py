from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from compilations.models import Compilation
from .models import UserProfile
from .serializers import UserProfileSerializer
from rest_framework.decorators import api_view
from rest_framework import status
# from django.views.decorators.csrf import csrf_exempt

import requests
# from users.utils import get_user_profile


COUNTRY_TRANSLATIONS = {
    "Maroc": "Morocco",
    "France": "France",
    "Espagne": "Spain",
    "Italie": "Italy",
    "Allemagne": "Germany",
    "États-Unis": "United States",
    "Canada": "Canada",
    "Tunisie": "Tunisia",
    "Egypte": "Egypt",
    "Sénégal": "Senegal",
    "Côte d'Ivoire": "Ivory Coast",
    "Tchad": "Chad",
    "Afrique du sud": "South Africa",
}

def get_english_country_name(country):
    return COUNTRY_TRANSLATIONS.get(country, country)

def fetch_capital(country):
    english_name = get_english_country_name(country)
    res = requests.get(f"https://restcountries.com/v3.1/name/{english_name}?fullText=true")
    data = res.json()[0]
    print(data)
    return data.get("capital", ["Inconnue"])[0]

# api_view verison of  UserProfileViewSet

@api_view(['POST', 'PUT'])
def create_session(request):
    """Create or update user session with profile"""
    # Ensure session exists
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    profile_type = request.data.get('profile_type', 'guest')
    country = request.data.get('country', 'Unknown')
    # On ne refait pas l'appel API si le profil existe déjà
    profile, created = UserProfile.objects.get_or_create(session_key=session_key)

    if created or profile.country != country:
        capital = fetch_capital(country)
        profile.country = country
        profile.capital = capital
        profile.profile_type = profile_type
        profile.save()
    # ⚡ fetch capital côté backend
    # capital = fetch_capital(country)

    # profile, _ = UserProfile.objects.update_or_create(
    #     session_key=session_key,
    #     defaults={'profile_type': profile_type, 'country': country, 'capital': capital}
    # )

    serializer = UserProfileSerializer(profile)
    print("user ", serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_session(request):
    """Get current user's session profile"""
    session_key = request.session.session_key
    print("session_key {} ".format(session_key))
    if not session_key:
        return Response({'detail': 'No session found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        profile = UserProfile.objects.get(session_key=session_key)
        serializer = UserProfileSerializer(profile)
        print("USER PROFILE", serializer.data)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response({'detail': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def logout(request):
    """Logout user and delete associated session"""
    print("loggin out/n")
    session_key = request.session.session_key
    # print("req ", request.session)
    print("sessionid cookie:", request.COOKIES)
    print("session_key:", request.session.session_key)

    if not session_key:
        return Response({'detail': 'No active session'}, status=status.HTTP_400_BAD_REQUEST)
    # Fetch user profile first
    profile = UserProfile.objects.filter(session_key=session_key).first()
    if profile:
        # Delete associated compilations BEFORE deleting the profile
        Compilation.objects.filter(user_profile=profile).delete()
        profile.delete()

    # Clear Django session
    request.session.flush()

    return Response({'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)
