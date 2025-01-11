from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Agent, Case, Callback, CaseNote
from .serializers import AgentSerializer, CaseSerializer, CallbackSerializer, CaseNoteSerializer

class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def cases(self, request, pk=None):
        agent = self.get_object()
        cases = Case.objects.filter(assigned_agent=agent)
        serializer = CaseSerializer(cases, many=True)
        return Response(serializer.data)

class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def assign_agent(self, request, pk=None):
        case = self.get_object()
        agent_id = request.data.get('agent_id')
        
        try:
            agent = Agent.objects.get(id=agent_id)
            case.assigned_agent = agent
            case.save()
            return Response({'status': 'Agent assigned successfully'})
        except Agent.DoesNotExist:
            return Response({'error': 'Agent not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        case = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        note = CaseNote.objects.create(
            case=case,
            agent=request.user.agent,
            content=content
        )
        
        serializer = CaseNoteSerializer(note)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def schedule_callback(self, request, pk=None):
        case = self.get_object()
        scheduled_time = request.data.get('scheduled_time')
        notes = request.data.get('notes', '')
        
        if not scheduled_time:
            return Response({'error': 'Scheduled time is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        callback = Callback.objects.create(
            case=case,
            scheduled_time=scheduled_time,
            notes=notes
        )
        
        serializer = CallbackSerializer(callback)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def close_case(self, request, pk=None):
        case = self.get_object()
        case.status = 'CLOSED'
        case.date_closed = timezone.now()
        case.save()
        return Response({'status': 'Case closed successfully'})

def dashboard(request):
    if not request.user.is_authenticated:
        return render(request, 'workflow/login.html')
    
    context = {
        'open_cases': Case.objects.filter(status='OPEN').count(),
        'in_progress_cases': Case.objects.filter(status='IN_PROGRESS').count(),
        'closed_cases': Case.objects.filter(status='CLOSED').count(),
        'upcoming_callbacks': Callback.objects.filter(completed=False, scheduled_time__gte=timezone.now()).count()
    }
    return render(request, 'workflow/dashboard.html', context)

def case_detail(request, case_id):
    if not request.user.is_authenticated:
        return render(request, 'workflow/login.html')
    
    case = Case.objects.get(case_id=case_id)
    context = {
        'case': case,
        'notes': case.notes.all().order_by('-created_at'),
        'callbacks': case.callbacks.all().order_by('scheduled_time')
    }
    return render(request, 'workflow/case_detail.html', context)
