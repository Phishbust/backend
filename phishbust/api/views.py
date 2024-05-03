from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Detection
from .serializers import DetectionSerializer
from rest_framework.views import APIView
from .serializers import PredictionSerializer


class DetectionListCreate(generics.ListCreateAPIView):
    queryset = Detection.objects.all()
    serializer_class = DetectionSerializer

    def delete(self, request, *args, **kwargs):
        Detection.objects.get.all()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PredictionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PredictionSerializer(data=request.data)
        if serializer.is_valid():
            input_data = serializer.validated_data['input_data']
            # Perform prediction using your model
            prediction_result = your_prediction_function(input_data)
            return Response({'prediction_result': prediction_result})
        else:
            return Response(serializer.errors, status=400)

def your_prediction_function(input_data):
    # Your prediction logic here
    return "Prediction result"
