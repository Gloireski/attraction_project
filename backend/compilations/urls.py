from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompilationViewSet, compilation_add_attraction, compilation_optimize_route, compilations_list, compilation_create, compilation_add_attraction, compilation_remove_attraction, compilation_sort_by_budget

router = DefaultRouter()
router.register(r'compilations', CompilationViewSet, basename='compilation')

urlpatterns = [
    # path('', include(router.urls)),
    # List all compilations
    path('', compilations_list, name='compilations_list'),

    # Create a new compilation
    path('create/', compilation_create, name='compilation_create'),

    # Add attraction to a compilation
    path('<int:compilation_id>/add_attraction/', compilation_add_attraction, name='compilation_add_attraction'),

    # Remove attraction from a compilation
    path('<int:compilation_id>/remove_attraction/', compilation_remove_attraction, name='compilation_remove_attraction'),

    # Optimize route
    path('<int:compilation_id>/optimize_route/', compilation_optimize_route, name='compilation_optimize_route'),

    # Sort by budget
    path('<int:compilation_id>/sort_by_budget/', compilation_sort_by_budget, name='compilation_sort_by_budget'),

]