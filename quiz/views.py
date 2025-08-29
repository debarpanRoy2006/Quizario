from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Quiz, Choice, QuizResult
from .serializers import QuizSerializer, QuizCreateSerializer

# --- CHANGE THIS from ReadOnlyModelViewSet to ModelViewSet ---
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()

    def get_serializer_class(self):
        # Use the create serializer for the 'create' action
        if self.action == 'create':
            return QuizCreateSerializer
        # Use the standard serializer for all other actions (list, retrieve)
        return QuizSerializer

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as the quiz owner
        serializer.save(owner=self.request.user)
    
    # This overrides the default create response to ensure the room_code is included
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Use the read-serializer to format the response
        read_serializer = QuizSerializer(serializer.instance)
        
        headers = self.get_success_headers(serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        quiz = self.get_object()
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
                # This handles cases where a question might not have a correct answer marked
                pass
        
        QuizResult.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            total_questions=total_questions
        )
        
        return Response({
            'score': score,
            'total_questions': total_questions
        })

    @action(detail=False, methods=['post'], url_path='join')
    def join_quiz(self, request):
        room_code = request.data.get('room_code')
        if not room_code:
            return Response({'error': 'Room code is required.'}, status=400)
        
        try:
            quiz = Quiz.objects.get(room_code__iexact=room_code)
            serializer = self.get_serializer(quiz)
            return Response(serializer.data)
        except Quiz.DoesNotExist:
            return Response({'error': 'Invalid room code.'}, status=404)