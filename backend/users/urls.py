from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, create_session, get_session, logout

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('create_session/', create_session, name='create_session'),
    path('get_session/', get_session, name='get_session'),
    path('logout/', logout, name='logout'),
    # path('', include(router.urls)),

]