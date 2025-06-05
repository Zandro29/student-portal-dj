from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def user_directory_path(instance, filename):
    # upload to MEDIA_ROOT/profile_pics/user_<id>/<filename>
    return f'profile_pics/user_{instance.user.id}/{filename}'

class Profile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('staff', 'Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    image = models.ImageField(upload_to=user_directory_path, default='default.jpg')
    #image = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    # student-specific fields
    student_id = models.CharField(max_length=20, null=True, blank=True)
    course = models.CharField(max_length=100, null=True, blank=True)
    # Common fields
    address = models.TextField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    # student-specific fields
    faculty_id = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Subject(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    units = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.code} - {self.name}"

class Section(models.Model):
    name = models.CharField(max_length=20)
    year_level = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Room(models.Model):
    room_number = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.room_number
    
class AcademicTerm(models.Model):
    SEMESTER_CHOICES = [
        ('1st', '1st Semester'),
        ('2nd', '2nd Semester'),
        ('Summer', 'Summer'),
    ]
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    academic_year = models.CharField(max_length=20)
    is_current = models.BooleanField(default=False)  # Mark active term

    def __str__(self):
        return f"{self.academic_year} - {self.semester}"
    
class Schedule(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()

    academic_term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subject} - {self.section} ({self.academic_term})"

class StudentEnrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'student'})
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'schedule')  # prevent double enrollment

    def __str__(self):
        return f"{self.student.username} enrolled in {self.schedule.subject}"

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'student'})
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    academic_term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)

    # Grade breakdown
    midterm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    reexam = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # optional if auto-computed
    remarks = models.CharField(max_length=50, blank=True, null=True)

    date_recorded = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'schedule', 'academic_term')

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.schedule.subject.name} - {self.academic_term}"
