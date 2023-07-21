from django.urls import path
from .views import *

urlpatterns = [
    path('', PrediccionTemplateAPIView, name='predict_score_template'),

]