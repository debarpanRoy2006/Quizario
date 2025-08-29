from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizSession
from users.serializers import UserSerializer # Assuming your UserSerializer is in users/serializers.py

# --- Serializers for CREATING a quiz ---

class ChoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']

class QuestionCreateSerializer(serializers.ModelSerializer):
    choices = ChoiceCreateSerializer(many=True)

    class Meta:
        model = Question
        fields = ['text', 'time_limit', 'choices']

class QuizCreateSerializer(serializers.ModelSerializer):
    questions = QuestionCreateSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'questions', 'room_code']
        read_only_fields = ['room_code', 'id']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)
        for question_data in questions_data:
            choices_data = question_data.pop('choices')
            question = Question.objects.create(quiz=quiz, **question_data)
            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)
        return quiz

# --- Serializers for READING quiz and session data ---

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'time_limit', 'choices']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'questions', 'room_code']
        
class QuizSessionSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    quiz = QuizSerializer(read_only=True)
    host = UserSerializer(read_only=True)

    class Meta:
        model = QuizSession
        fields = ['id', 'quiz', 'host', 'participants', 'status', 'room_code']

