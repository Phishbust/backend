from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import extract_features 
import joblib
import os
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    model = None
    print(f"Failed to load model: {e}")

class PredictView(APIView):
    def get(self, request):
        if model is None:
            return Response({'error': 'Model could not be loaded'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        url = request.query_params.get('url')
        if not url:
            return Response({'error': 'URL parameter is missing'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            features = extract_features(url)
            features = pd.DataFrame.from_dict(features, orient="index").T
        except Exception as e:
            return Response({'error': f"Failed to extract features: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            prediction = model.predict(features)
        except Exception as e:
            return Response({'error': f"Prediction failed: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'prediction': prediction[0]}, status=status.HTTP_200_OK)