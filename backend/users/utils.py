from .models import UserProfile

def get_user_profile(request):
    """
    Helper to retrieve the UserProfile based on the current session.
    Returns the profile instance or None if not found.
    """
    session_key = request.session.session_key
    if not session_key:
        return None
    try:
        return UserProfile.objects.get(session_key=session_key)
    except UserProfile.DoesNotExist:
        return None
