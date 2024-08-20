from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  MyCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course, Lesson, Group


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)
    course = None
    
    def get_course(self):
        if not self.course:
            self.course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return self.course

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
         serializer.save(course=self.get_course())
    
    def get_queryset(self):
        return Lesson.objects.filter(
            course=self.get_course()
        ).select_related('course')


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)
    course = None
    
    def get_course(self):
        if not self.course:
            self.course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return self.course

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        serializer.save(course=self.get_course())

    def get_queryset(self):
        return Group.objects.filter(
            course=self.get_course()
        ).select_related('course').prefetch_related('students__user')


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы."""

    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'accessable_course']:
            return CourseSerializer
        if self.action == 'me':
            return MyCourseSerializer
        if self.action == 'pay':
            return SubscriptionSerializer
        return CreateCourseSerializer
    
    def get_queryset(self):
        user = self.request.user
        if self.action in ['accessable_course']:
            return Course.objects.filter(
                access_flag=True,
            ).exclude(customers__user=user).prefetch_related('groups', 'lessons')
        if self.action == 'me':
            return Course.objects.filter(customers__user=user).prefetch_related('groups', 'lessons')
        return Course.objects.prefetch_related(
            'groups',
            'groups__students',
            'lessons',
        ).annotate(
            students_count=Count('customers'),
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def accessable_course(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def pay(self, request):
        """Покупка доступа к курсу (подписка на курс)."""
        
        serializer = SubscriptionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )
        
    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsStudentOrIsAdmin,),
    )    
    def me(self, request):
        """Список курсов к которм есть доступ после оплаты."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
