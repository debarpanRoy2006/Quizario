from django.db.models import Sum
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Quiz, Choice, QuizResult, QuizSession
from .serializers import (
    QuizCreateSerializer,
    QuizSessionSerializer,
    LeaderboardSerializer
)

User = get_user_model()

class QuizSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage all aspects of a quiz session, from hosting to completion.
    """
    queryset = QuizSession.objects.all()
    serializer_class = QuizSessionSerializer

    def get_serializer_class(self):
        # Use a different serializer for the 'host_quiz' action
        if self.action == 'host_quiz':
            return QuizCreateSerializer
        return QuizSessionSerializer

    @action(detail=False, methods=['post'], url_path='host')
    def host_quiz(self, request):
        """
        Creates a new Quiz and a QuizSession (lobby).
        """
        create_serializer = self.get_serializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        quiz = create_serializer.save(owner=request.user)
        
        # Create a new session for the quiz
        session = QuizSession.objects.create(quiz=quiz, host=request.user)
        session.participants.add(request.user)
        
        # Use the standard session serializer for the response
        session_serializer = QuizSessionSerializer(session)
        return Response(session_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='join')
    def join_session(self, request):
        """
        Allows a user to join an existing lobby using a room code.
        """
        room_code = request.data.get('room_code')
        if not room_code:
            return Response({'error': 'Room code is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = QuizSession.objects.get(room_code__iexact=room_code, status='lobby')
            session.participants.add(request.user)
            serializer = self.get_serializer(session)
            return Response(serializer.data)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Invalid room code or the lobby is closed.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='status')
    def lobby_status(self, request, pk=None):
        """
        Periodically checked by the frontend to get lobby updates.
        """
        session = self.get_object()
        serializer = self.get_serializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='start')
    def start_game(self, request, pk=None):
        """
        Allows the host to start the quiz for all participants.
        """
        session = self.get_object()
        if session.host != request.user:
            return Response({'error': 'Only the host can start the quiz.'}, status=status.HTTP_403_FORBIDDEN)
        
        session.status = 'in_progress'
        session.save()
        return Response({'message': 'Quiz started.'})

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Receives and scores a user's answers for a quiz within a session.
        """
        session = self.get_object()
        quiz = session.quiz
        user_answers = request.data.get('answers', {})
        score = 0
        total_questions = quiz.questions.count()

        for question in quiz.questions.all():
            try:
                correct_choice = Choice.objects.get(question=question, is_correct=True)
                user_choice_id = user_answers.get(str(question.id))
                if user_choice_id and int(user_choice_id) == correct_choice.id:
                    score += 1
            except Choice.DoesNotExist:
                # This handles cases where a question might not have a correct answer marked.
                pass 
        
        # Create a record of the user's score for this quiz.
        QuizResult.objects.create(
            user=request.user, quiz=quiz, score=score, total_questions=total_questions
        )
        return Response({'score': score, 'total_questions': total_questions})

    @action(detail=False, methods=['get'], url_path='leaderboard')
    def leaderboard(self, request):
        """
        Calculates and returns the top 10 players based on total score.
        """
        user_scores = User.objects.annotate(
            total_score=Sum('quizresult__score')
        ).filter(
            total_score__isnull=False
        ).order_by(
            '-total_score'
        )[:10]

        serializer = LeaderboardSerializer(user_scores, many=True)
        return Response(serializer.data)