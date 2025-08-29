from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Quiz, Choice, QuizResult, QuizSession
from .serializers import QuizSerializer, QuizCreateSerializer, QuizSessionSerializer

class QuizSessionViewSet(viewsets.ViewSet):
    """
    This ViewSet handles all actions related to a quiz session using custom actions.
    """
    queryset = QuizSession.objects.all()

    @action(detail=False, methods=['post'], url_path='host')
    def host_quiz(self, request):
        """
        Action to host a new quiz. This creates a Quiz and a QuizSession.
        """
        create_serializer = QuizCreateSerializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        quiz = create_serializer.save(owner=request.user)

        session = QuizSession.objects.create(quiz=quiz, host=request.user)
        session.participants.add(request.user)

        # Explicitly use the correct serializer for the response
        response_serializer = QuizSessionSerializer(session)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='join')
    def join_session(self, request):
        """
        Action for a user to join an existing quiz session with a room code.
        """
        room_code = request.data.get('room_code')
        if not room_code:
            return Response({'error': 'Room code is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = QuizSession.objects.get(room_code__iexact=room_code, status='lobby')
            session.participants.add(request.user)
            serializer = QuizSessionSerializer(session)
            return Response(serializer.data)
        except QuizSession.DoesNotExist:
            return Response({'error': 'Invalid room code or the session is not in the lobby.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='status')
    def lobby_status(self, request, pk=None):
        """
        Action for clients to poll the lobby for updates on participants and game state.
        """
        session = self.get_object()
        serializer = QuizSessionSerializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='start')
    def start_game(self, request, pk=None):
        """
        Action for the host to start the quiz. This changes the session status.
        """
        session = self.get_object()
        if session.host != request.user:
            return Response({'error': 'Only the host can start the quiz.'}, status=status.HTTP_403_FORBIDDEN)
        
        session.status = 'in_progress'
        session.save()
        return Response({'message': 'Quiz started successfully.'})

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Action to submit answers for a quiz session.
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
                pass
        
        QuizResult.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            total_questions=total_questions
        )
        
        session.status = 'finished'
        session.save()

        return Response({
            'score': score,
            'total_questions': total_questions
        })
    
    def get_object(self):
        """Helper method to get the session object from the URL's primary key."""
        queryset = self.get_queryset()
        pk = self.kwargs.get('pk')
        return queryset.get(pk=pk)

    def get_queryset(self):
        return QuizSession.objects.all()

