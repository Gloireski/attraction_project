from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .filters import AttractionFilter
from .models import Attraction
from .serializers import AttractionSerializer

def home(request):
    return HttpResponse("Bienvenue dans mon projet Django 🚀")

@api_view(['GET'])
def get_attractions(request):
    filterset = AttractionFilter(request.GET, queryset=Attraction.objects.all())
    if filterset.is_valid():
        serializer = AttractionSerializer(filterset.qs, many=True)
        return Response(serializer.data)
    return Response(filterset.errors, status=400)

@api_view(['GET'])
def get_categories(request):
    categories = Attraction.objects.values_list('category', flat=True).distinct()
    data = [{"id": idx + 1, "name": cat} for idx, cat in enumerate(categories)]
    return Response(data)