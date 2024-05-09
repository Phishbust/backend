from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Detection
from .serializers import DetectionSerializer


class DetectionListCreate(generics.ListCreateAPIView):
    queryset = Detection.objects.all()
    serializer_class = DetectionSerializer

    def delete(self, request, *args, **kwargs):
        Detection.objects.get.all()
        return Response(status=status.HTTP_204_NO_CONTENT)


