from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from math import radians, cos, sin, asin, sqrt
import numpy as np
from .models import Attraction, UserProfile, Compilation, CompilationItem
from .serializers import (
   CompilationSerializer, CompilationItemSerializer
)
from users.utils import get_user_profile

# List compilations for current user
@api_view(['GET'])
def compilations_list(request):
    print( "compilations_list called" )
    profile = get_user_profile(request)
    print( "User profile:", profile )
    if not profile:
        return Response([], status=status.HTTP_200_OK)
    compilations = Compilation.objects.filter(user_profile=profile)
    serializer = CompilationSerializer(compilations, many=True)
    return Response(serializer.data)

# Create a new compilation
@api_view(['POST'])
def compilation_create(request):
    profile = get_user_profile(request)
    if not profile:
        return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CompilationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user_profile=profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Add attraction to compilation
@api_view(['POST'])
def compilation_add_attraction(request, compilation_id):
    compilation = get_object_or_404(Compilation, id=compilation_id)
    attraction_id = request.data.get('attraction_id')
    estimated_cost = request.data.get('estimated_cost', 0)
    
    try:
        attraction = Attraction.objects.get(id=attraction_id)
        item, created = CompilationItem.objects.get_or_create(
            compilation=compilation,
            attraction=attraction,
            defaults={'estimated_cost': estimated_cost}
        )
        # Update total budget
        compilation.total_budget = sum(
            item.estimated_cost for item in compilation.items.all()
        )
        compilation.save()
        serializer = CompilationItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Attraction.DoesNotExist:
        return Response({'error': 'Attraction not found'}, status=status.HTTP_404_NOT_FOUND)

# Remove attraction from compilation
@api_view(['DELETE'])
def compilation_remove_attraction(request, compilation_id):
    compilation = get_object_or_404(Compilation, id=compilation_id)
    item_id = request.data.get('item_id')
    
    try:
        item = CompilationItem.objects.get(id=item_id, compilation=compilation)
        item.delete()
        compilation.total_budget = sum(
            item.estimated_cost for item in compilation.items.all()
        )
        compilation.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except CompilationItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

# Optimize route using simple TSP (nearest neighbor)
@api_view(['POST'])
def compilation_optimize_route(request, compilation_id):
    compilation = get_object_or_404(Compilation, id=compilation_id)
    items = list(compilation.items.select_related('attraction').all())
    
    if len(items) < 2:
        return Response({'message': 'Need at least 2 attractions'})
    
    coordinates = [(float(i.attraction.latitude), float(i.attraction.longitude)) for i in items]
    
    def haversine_distance(coord1, coord2):
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return 6371 * c
    
    n = len(coordinates)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dist_matrix[i][j] = haversine_distance(coordinates[i], coordinates[j])
    
    unvisited = set(range(n))
    current = 0
    route = [current]
    unvisited.remove(current)
    
    while unvisited:
        nearest = min(unvisited, key=lambda x: dist_matrix[current][x])
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    for order, idx in enumerate(route):
        items[idx].order = order
        items[idx].save()
    
    total_distance = sum(dist_matrix[route[i]][route[i+1]] for i in range(len(route)-1))
    
    serializer = CompilationSerializer(compilation)
    return Response({
        'compilation': serializer.data,
        'total_distance_km': round(total_distance, 2),
        'route_order': route
    })

# Sort compilation items by budget
@api_view(['POST'])
def compilation_sort_by_budget(request, compilation_id):
    compilation = get_object_or_404(Compilation, id=compilation_id)
    order = request.data.get('order', 'asc')
    
    items = compilation.items.all()
    if order == 'desc':
        items = items.order_by('-estimated_cost')
    else:
        items = items.order_by('estimated_cost')
    
    for idx, item in enumerate(items):
        item.order = idx
        item.save()
    
    compilation.sort_by = f'budget_{order}'
    compilation.save()
    
    serializer = CompilationSerializer(compilation)
    return Response(serializer.data)

class CompilationViewSet(viewsets.ModelViewSet):
    serializer_class = CompilationSerializer
    
    def get_queryset(self):
        session_key = self.request.session.session_key
        if not session_key:
            return Compilation.objects.none()
        
        try:
            profile = UserProfile.objects.get(session_key=session_key)
            return Compilation.objects.filter(user_profile=profile)
        except UserProfile.DoesNotExist:
            return Compilation.objects.none()
    
    def perform_create(self, serializer):
        session_key = self.request.session.session_key
        profile = UserProfile.objects.get(session_key=session_key)
        serializer.save(user_profile=profile)
    
    @action(detail=True, methods=['post'])
    def add_attraction(self, request, pk=None):
        """Add attraction to compilation"""
        compilation = self.get_object()
        attraction_id = request.data.get('attraction_id')
        estimated_cost = request.data.get('estimated_cost', 0)
        
        try:
            attraction = Attraction.objects.get(id=attraction_id)
            item, created = CompilationItem.objects.get_or_create(
                compilation=compilation,
                attraction=attraction,
                defaults={'estimated_cost': estimated_cost}
            )
            
            # Update total budget
            compilation.total_budget = sum(
                item.estimated_cost for item in compilation.items.all()
            )
            compilation.save()
            
            serializer = CompilationItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Attraction.DoesNotExist:
            return Response(
                {'error': 'Attraction not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def remove_attraction(self, request, pk=None):
        """Remove attraction from compilation"""
        compilation = self.get_object()
        item_id = request.data.get('item_id')
        
        try:
            item = CompilationItem.objects.get(id=item_id, compilation=compilation)
            item.delete()
            
            # Update total budget
            compilation.total_budget = sum(
                item.estimated_cost for item in compilation.items.all()
            )
            compilation.save()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CompilationItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def optimize_route(self, request, pk=None):
        """Optimize route using TSP (Traveling Salesman Problem)"""
        compilation = self.get_object()
        items = compilation.items.select_related('attraction').all()
        
        if len(items) < 2:
            return Response({'message': 'Need at least 2 attractions'})
        
        # Get coordinates
        coordinates = [
            (float(item.attraction.latitude), float(item.attraction.longitude))
            for item in items
        ]
        
        # Calculate distance matrix using Haversine
        def haversine_distance(coord1, coord2):
            lat1, lon1 = coord1
            lat2, lon2 = coord2
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            return 6371 * c
        
        n = len(coordinates)
        dist_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist_matrix[i][j] = haversine_distance(coordinates[i], coordinates[j])
        
        # Solve TSP using nearest neighbor heuristic (simple approach)
        unvisited = set(range(n))
        current = 0
        route = [current]
        unvisited.remove(current)
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: dist_matrix[current][x])
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # Update order in database
        for order, idx in enumerate(route):
            items[idx].order = order
            items[idx].save()
        
        # Calculate total distance
        total_distance = sum(
            dist_matrix[route[i]][route[i+1]] for i in range(len(route)-1)
        )
        
        serializer = self.get_serializer(compilation)
        return Response({
            'compilation': serializer.data,
            'total_distance_km': round(total_distance, 2),
            'route_order': route
        })
    
    @action(detail=True, methods=['post'])
    def sort_by_budget(self, request, pk=None):
        """Sort compilation items by budget"""
        compilation = self.get_object()
        order = request.data.get('order', 'asc')  # asc or desc
        
        items = compilation.items.all()
        if order == 'desc':
            items = items.order_by('-estimated_cost')
        else:
            items = items.order_by('estimated_cost')
        
        for idx, item in enumerate(items):
            item.order = idx
            item.save()
        
        compilation.sort_by = f'budget_{order}'
        compilation.save()
        
        serializer = self.get_serializer(compilation)
        return Response(serializer.data)