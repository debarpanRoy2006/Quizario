from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Quiz, Question, Choice, QuizSession

User = get_user_model()

# --- ADD THIS NEW SERIALIZER ---
class LeaderboardSerializer(serializers.Serializer):
    """
    Serializer for leaderboard data. Not a ModelSerializer.
    """
    username = serializers.CharField()
    total_score = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'text', 'time_limit', 'choices']

class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'questions']

# Serializer for viewing a lobby session
class QuizSessionSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    host = UserSerializer(read_only=True)
    quiz = QuizDetailSerializer(read_only=True)

    class Meta:
        model = QuizSession
        fields = ['id', 'quiz', 'room_code', 'status', 'host', 'participants']

# --- Writable Serializers for Creating a Quiz ---

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