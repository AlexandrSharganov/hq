from django.contrib.auth import get_user_model
from rest_framework import serializers

from courses.models import Course, Group, Lesson
from product.settings import MAX_STUDENTS_IN_GROUP
from users.models import Subscription

User = get_user_model()


class LessonSerializer(serializers.ModelSerializer):
    """Список уроков."""

    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'id',
            'title',
            'link',
            'course'
        )


class CreateLessonSerializer(serializers.ModelSerializer):
    """Создание уроков."""

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class StudentSerializer(serializers.ModelSerializer):
    """Студенты курса."""
    
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = Subscription
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class GroupSerializer(serializers.ModelSerializer):
    """Список групп."""

    students = StudentSerializer(
        read_only=True,
        many=True
    )
    course = serializers.CharField(source='course.title', read_only=True)
    class Meta:
        model = Group
        fields = (
            'title',
            'course',
            'students',
        )


class CreateGroupSerializer(serializers.ModelSerializer):
    """Создание групп."""

    class Meta:
        model = Group
        fields = (
            'title',
            'course',
        )


class MiniLessonSerializer(serializers.ModelSerializer):
    """Список названий уроков для списка курсов."""

    class Meta:
        model = Lesson
        fields = (
            'title',
        )


class CourseSerializer(serializers.ModelSerializer):
    """Список курсов."""

    lessons = MiniLessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField(read_only=True)
    students_count = serializers.IntegerField(read_only=True)
    groups_filled_percent = serializers.SerializerMethodField(read_only=True)
    demand_course_percent = serializers.SerializerMethodField(read_only=True)
    
    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_groups_filled_percent(self, obj):
        """Процент заполнения групп, если в группе максимум 30 чел.."""
        groups = obj.groups.all()
        if not groups:
            return 0
        
        total_percentage = 0
        group_count = groups.count()

        for group in groups:
            participants_count = group.students.count()
            group_percentage = (participants_count / MAX_STUDENTS_IN_GROUP) * 100
            total_percentage += group_percentage
        
        average_percentage = total_percentage / group_count
        return round(average_percentage, 2) 

    def get_demand_course_percent(self, obj):
        """Процент приобретения курса."""
        total_users = User.objects.count()
        if total_users == 0:
            return 0
        students_count = getattr(obj, 'students_count', 0)
        return round((students_count / total_users) * 100, 2)


    class Meta:
        model = Course
        fields = (
            'id',
            'author',
            'title',
            'start_date',
            'price',
            'lessons_count',
            'lessons',
            'demand_course_percent',
            'students_count',
            'groups_filled_percent',
        )


class MyCourseSerializer(serializers.ModelSerializer):
    """Список курсовк которым есть доступ после покупки."""
    
    lessons = MiniLessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = (
            'id',
            'author',
            'title',
            'start_date',
            'price',
            'lessons',
        )


class CreateCourseSerializer(serializers.ModelSerializer):
    """Создание курсов."""

    class Meta:
        model = Course
        fields = '__all__'
