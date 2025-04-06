from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def test_api(request):
    return Response({'message':'DRF is working cleopatra!'})


urlpatterns = [
    path('api/test/', test_api),
]
