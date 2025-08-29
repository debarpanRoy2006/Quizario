import random
import string
from django.db import models
from django.conf import settings

def generate_room_code():
    """Generates a random 6-character room code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room_code = models.CharField(max_length=6, default=generate_room_code, unique=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    time_limit = models.IntegerField(default=30) # Time in seconds

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.text[:20]}... -> {self.text}"

class QuizSession(models.Model):
    STATUS_CHOICES = [
        ('lobby', 'Lobby'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished'),
    ]
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE, related_name="session")
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='quiz_sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lobby')
    room_code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Copy the room_code from the related Quiz when the session is created
        if not self.room_code:
            self.room_code = self.quiz.room_code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Session for '{self.quiz.title}' - Status: {self.status}"

class QuizResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}: {self.score}/{self.total_questions}"

