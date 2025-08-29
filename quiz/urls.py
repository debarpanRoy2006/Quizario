from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizSessionViewSet # Use the correct ViewSet name

router = DefaultRouter()
# Register the QuizSessionViewSet, which handles all quiz session logic
router.register(r'', QuizSessionViewSet, basename='quizsession')

urlpatterns = router.urls
