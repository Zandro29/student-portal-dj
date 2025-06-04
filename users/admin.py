from django.contrib import admin
from .models import Subject, Section, Room, Schedule, Profile, StudentEnrollment, AcademicTerm, Grade

admin.site.site_header = "School Management System Admin"
admin.site.site_title = "School Management System Admin Portal"
admin.site.index_title = "Welcome to the School Management System Admin Portal"
#admin.site.register(Profile)
admin.site.register(Subject)
admin.site.register(Section)
admin.site.register(Room)
admin.site.register(Schedule)
admin.site.register(AcademicTerm)
@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'schedule', 'date_enrolled']
    search_fields = ['student__username', 'schedule__subject__name']

# @admin.register(Grade)
# class GradeAdmin(admin.ModelAdmin):
#     list_display = ['student', 'schedule', 'grade_value', 'academic_term']
#     search_fields = ['student__username', 'schedule__subject__name']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'schedule', 'midterm', 'final', 'reexam', 'final_grade', 'remarks']
    search_fields = ['student__username', 'schedule__subject__name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'student_id', 'course', 'contact_number')
    search_fields = ('user__username', 'student_id', 'course')