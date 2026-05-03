from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CandidateViewSet, create_reminder, export_report

router = DefaultRouter()

router.register(r'candidates', CandidateViewSet, basename='candidate')

urlpatterns = [
    path('', include(router.urls)),
    path('reminder/', create_reminder),
    path('report/<int:user_id>/', export_report),
]
