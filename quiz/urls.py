from rest_framework.routers import DefaultRouter
from .views import QuizViewSet

router = DefaultRouter()
router.register(r'', QuizViewSet)

urlpatterns = router.urls
