from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Quiz, Choice, QuizResult
from .serializers import QuizSerializer

class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Handles the submission of a quiz, calculates the score,
        and saves the result to the database.
        """
        quiz = self.get_object()
        user_answers = request.data.get('answers', {})
        
        score = 0
        total_questions = quiz.questions.count()

        for question in quiz.questions.all():
            try:
                # Assumes there is exactly one correct choice per question
                correct_choice = Choice.objects.get(question=question, is_correct=True)
                user_choice_id = user_answers.get(str(question.id))

                if user_choice_id and int(user_choice_id) == correct_choice.id:
                    score += 1
            except Choice.DoesNotExist:
                # Handle cases where a question might not have a correct answer set
                pass
        
        # Save the result to the database
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
        except Exception as e:
            return Response({'error': str(e)}, status=500)
