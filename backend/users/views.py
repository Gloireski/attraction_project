from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UserProfile
from .serializers import UserProfileSerializer


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
