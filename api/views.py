from django.shortcuts import render

from rest_framework import viewsets
from .models import Candidate
from .serializers import CandidateSerializer

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all().order_by('-ai_score')
    serializer_class = CandidateSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse


@api_view(['POST'])
def create_reminder(request):
    print("Напоминание получено:", request.data)
    return Response({"status": "success", "message": "Напоминание создано (тест)"})


@api_view(['GET'])
def export_report(request, user_id):
    return HttpResponse("Здесь будет Excel файл", content_type="text/plain")