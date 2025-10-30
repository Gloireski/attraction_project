from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from compilations.models import Compilation
from .models import UserProfile
from .serializers import UserProfileSerializer
from rest_framework.decorators import api_view
from rest_framework import status
# from users.utils import get_user_profile


# api_view verison of  UserProfileViewSet

@api_view(['POST'])
def create_session(request):
    """Create or update user session with profile"""
    # Ensure session exists
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    profile_type = request.data.get('profile_type', 'guest')
    country = request.data.get('country', 'Unknown')

    profile, _ = UserProfile.objects.update_or_create(
        session_key=session_key,
        defaults={'profile_type': profile_type, 'country': country}
    )

    serializer = UserProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_session(request):
    """Get current user's session profile"""
    session_key = request.session.session_key
    if not session_key:
        return Response({'detail': 'No session found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        profile = UserProfile.objects.get(session_key=session_key)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response({'detail': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def logout(request):
    """Logout user and delete associated session"""
    session_key = request.session.session_key
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


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @action(detail=False, methods=['post'])
    def create_session(self, request):
        """Create or update user session with profile"""
        session_key = request.session.session_key or request.session.create()
        profile, _ = UserProfile.objects.update_or_create(
            session_key=session_key,
            defaults={
                'profile_type': request.data.get('profile_type'),
                'country': request.data.get('country')
            }
        )
        return Response(self.get_serializer(profile).data)

    @action(detail=False, methods=['get'])
    def get_session(self, request):
        session_key = request.session.session_key
        if not session_key:
            return Response({'detail': 'No session found'}, status=404)
        try:
            profile = UserProfile.objects.get(session_key=session_key)
            return Response(self.get_serializer(profile).data)
        except UserProfile.DoesNotExist:
            return Response({'detail': 'Profile not found'}, status=404)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        session_key = request.session.session_key
        if session_key:
            UserProfile.objects.filter(session_key=session_key).delete()
            request.session.flush()
        return Response({'detail': 'Logged out successfully'})
