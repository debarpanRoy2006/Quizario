# In quiz_backend/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- CHANGE THIS LINE ---
    path('api/quiz-sessions/', include('quiz.urls')), 
    
    path('api/users/', include('users.urls')),
]