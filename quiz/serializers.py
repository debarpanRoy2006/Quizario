from rest_framework import serializers
from .models import Quiz, Question, Choice

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        # IMPORTANT: Exclude 'is_correct' so the answer is not sent to the frontend
        fields = ['id', 'text'] 

class QuestionSerializer(serializers.ModelSerializer):
    # This nests the choices inside each question
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'choices']

class QuizSerializer(serializers.ModelSerializer):
    # This nests the questions inside each quiz
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'questions']