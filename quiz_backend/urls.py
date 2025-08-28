# In quiz_backend/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # These are the only two app includes you need
    path('api/quiz/', include('quiz.urls')), 
    path('api/users/', include('users.urls')),
]