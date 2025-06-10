from django.shortcuts import render, redirect, get_object_or_404
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db.models import Count
from collections import defaultdict
# for normal registration no verification required ---

# def register(request):

#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login')
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'user/registerbootstrap.html', {'form': form})

# views.py
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms_email_ver import CustomUserCreationForm
from .tokens import account_activation_token

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import login
from django.http import HttpResponse, HttpResponseForbidden


from django.views.generic import UpdateView
from .forms import UserUpdateForm, CustomPasswordChangeForm, ProfileForm, CustomLoginForm, ProfileImageForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .models import Profile, StudentEnrollment, AcademicTerm, Schedule, Section,Grade, Room

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.http import HttpResponse


def index(request):
    return redirect('login')

def create_admin(request):
    if get_user_model().objects.filter(is_superuser=True).exists():
        return HttpResponse("Superuser already exists. This page is disabled.")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        User = get_user_model()
        User.objects.create_superuser(username=username, email=email, password=password)
        return HttpResponse("Superuser created successfully. You can now delete this page.")
    #print("helos")
    return render(request, "user/create_admin.html")

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Prevent login until confirmed
            user.save()

            # Save the role to Profile
            role = form.cleaned_data.get('role')
            Profile.objects.create(user=user, role=role)

            # Send confirmation email
            current_site = get_current_site(request)
            subject = 'Activate your account'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_link = f"http://{current_site.domain}/activate/{uid}/{token}/"

            message = f'Hi {user.username},\nPlease click the link below to activate your account:\n{activation_link}'
            send_mail(subject, message, 'noreply@example.com', [user.email], fail_silently=False)

            return render(request, 'user/registration_pending.html')  # New page to tell user to check email
    else:
        form = CustomUserCreationForm()
    return render(request, 'user/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')  # Redirect to home after success
    else:
        return HttpResponse('Activation link is invalid!')

class StudentLoginView(LoginView):
    #template_name = 'user/login_bootstrap.html'
    # template_name = 'user/login.html'
    # def form_valid(self, form):
    #     """Check if user has role 'student' before allowing login."""
    #     user = form.get_user()
    #     try:
    #         if user.profile.role == 'student':
    #             login(self.request, user)
    #             return redirect(self.get_success_url())
    #         else:
    #             messages.error(self.request, "Only students are allowed to login.")
    #             return redirect('login')
    #     except Profile.DoesNotExist:
    #         messages.error(self.request, "No profile associated with this account.")
    #         return redirect('login')
    # def get_success_url(self):
    #     return reverse_lazy('home')
    authentication_form = CustomLoginForm
    template_name = 'user/login.html'

    def form_valid(self, form):
        """Check if user has role 'student' before allowing login."""
        user = form.get_user()
        try:
            if user.profile.role == 'student':
                login(self.request, user)
                return redirect(self.get_success_url())
            else:
                messages.error(self.request, "Only students are allowed to login.")
                return redirect('login')
        except Profile.DoesNotExist:
            messages.error(self.request, "No profile associated with this account.")
            return redirect('login')
    def get_success_url(self):
        return reverse_lazy('home')

class FacultyLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = 'user/login.html'
    print('hello')
    def form_valid(self, form):
        """Check if user has role 'faculty' before allowing login."""
        user = form.get_user()
        try:
            if user.profile.role == 'faculty':
                login(self.request, user)
                return redirect(self.get_success_url())
            else:
                messages.error(self.request, "Only students are allowed to login.")
                return redirect('faculty_login')
        except Profile.DoesNotExist:
            messages.error(self.request, "No profile associated with this account.")
            return redirect('faculty_login')
    def get_success_url(self):
        return reverse_lazy('faculty_home')

class StaffLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = 'user/login_staff.html'

    def form_valid(self, form):
        """Check if user has role 'student' before allowing login."""
        user = form.get_user()
        try:
            if user.profile.role == 'staff':
                login(self.request, user)
                return redirect(self.get_success_url())
            else:
                messages.error(self.request, "Only students are allowed to login.")
                return redirect('login_staff')
        except Profile.DoesNotExist:
            messages.error(self.request, "No profile associated with this account.")
            return redirect('login_staff')
    def get_success_url(self):
        return reverse_lazy('staff_home')


@login_required

def home(request):
    current_term = AcademicTerm.objects.filter(is_current=True).first()

    if not current_term:
        return render(request, 'user/dashboard.html', {'error': 'No active academic term set.'})

    enrollments = StudentEnrollment.objects.filter(
        schedule__academic_term=current_term,
        student=request.user
    )
    total_enrolled = enrollments.count()
    total_units = sum(enrollment.schedule.subject.units for enrollment in enrollments)

    
    grades = Grade.objects.filter(student=request.user, academic_term=current_term)
    total_grades_uploaded = grades.count()
    print(total_grades_uploaded)
    print(f'Total enrolled: {total_enrolled}')
    print(current_term.academic_year)
    return render(request, 'user/dashboard.html', {
        'enrollments': enrollments,
        'current_semester': current_term.semester,
        'current_academic_year': current_term.academic_year,
        'total_enrolled': total_enrolled,
        'total_units': total_units,
        'total_grades_uploaded': total_grades_uploaded,
    })

def faculty_dashboard(request):
    user = request.user
    current_term = AcademicTerm.objects.filter(is_current=True).first()

    schedules = Schedule.objects.filter(
        teacher=user,
        academic_term=current_term
    )

    total_schedules = schedules.count()
    total_units = sum(schedule.subject.units for schedule in schedules)
    for schedule in schedules:
        print(schedule.subject.name)
        print(schedule.section.name)
        print(schedule.day_of_week)
        print(schedule.subject.units)
    return render(request, 'user/faculty_dashboard.html', {
        'schedules': schedules,
        'current_term': current_term,
        'total_schedules': total_schedules,
        'total_units': total_units,
    })

def staff_dashboard(request):
    return render(request, 'user/staff_dashboard.html')

def custom_logout(request):
    logout(request)  # This will clear the session
    return redirect(reverse_lazy('login'))  # Redirect to login page after logout


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    #template_name = 'user/user_update.html'
    template_name = 'user/profile.html'
    success_url = reverse_lazy('home')  # asa mo redirect after update

    def get_object(self):
        return self.request.user

def profile_view(request):
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # change this to your actual URL name
    else:
        form = ProfileImageForm(instance=request.user.profile)
    
    return render(request, 'user/profile_pic.html', {'form': form})
def change_password(request):
    pass

def profile_settings(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        photo_form = ProfileImageForm(request.POST, request.FILES, instance=request.user.profile)
        print('helo')
        if 'user_form' in request.POST and user_form.is_valid():
            user_form.save()
            # optional: add message here
            return redirect('profile')
        elif 'password_form' in request.POST:
            if password_form.is_valid():
                print('helo')
                user = password_form.save()
                update_session_auth_hash(request, user)
                return redirect('profile')
            # optional: add message here
            else:
                print('Password form invalid:', password_form.errors)
        elif 'profile_form' in request.POST:
            if profile_form.is_valid():
                print(request.user.profile.student_id)    
                profile_form.save()
                return redirect('profile')
            else:
                print('Profile form invalid:', profile_form.errors)
        elif 'photo_form' in request.POST:
            if photo_form.is_valid():
                print("true")
                photo_form.save()
                return redirect('profile')
            else:
                print('photo form invalid:', profile_form.errors)
        
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        photo_form = ProfileImageForm(request.POST, request.FILES, instance=request.user.profile)

    return render(request, 'user/profile.html', {
        'user_form': user_form,
        'password_form': password_form,
        'profile_form': profile_form,
        'photo_form': photo_form, 
    })

def grade_uploading(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)

    # Get current academic term
    current_term = AcademicTerm.objects.filter(is_current=True).first()

    if schedule.academic_term != current_term:
        return HttpResponseForbidden("You can only upload grades for the current term.")

    # Get students enrolled in this schedule
    students = StudentEnrollment.objects.filter(schedule=schedule)
    
    return render(request, 'user/grade_uploading.html', {
        'schedule': schedule,
        'students': students,
    })

def grade_upload_view(request, schedule_id):
    
    enrollments = StudentEnrollment.objects.filter(schedule_id=schedule_id)
    #enrollments = get_object_or_404(StudentEnrollment, schedule_id=schedule_id)
    
    if enrollments.exists():
        for enrollment in enrollments:
            print(enrollment.schedule.subject.name, enrollment.student.get_full_name())
        grades_dict = {}

        if request.method == 'POST':
            for enrollment in enrollments:
                midterm = request.POST.get(f'midterm_{enrollment.id}')
                final = request.POST.get(f'final_{enrollment.id}')
                reexam = request.POST.get(f'reexam_{enrollment.id}')

                grade, _ = Grade.objects.get_or_create(
                    schedule=enrollment.schedule,
                    student=enrollment.student,
                    defaults={'academic_term': enrollment.schedule.academic_term}
                )

            # Only update if values are not empty
                grade.midterm = midterm if midterm else None
                grade.final = final if final else None
                grade.reexam = reexam if reexam else None

            
            # Just to be sure old records also have academic_term
                if not grade.academic_term:
                    grade.academic_term = enrollment.schedule.academic_term

                grade.save()

    # Fetch grades for pre-filling form fields
        for enrollment in enrollments:
            try:
                grade = Grade.objects.get(schedule=enrollment.schedule, student=enrollment.student)
            except Grade.DoesNotExist:
                grade = None

            grades_dict[enrollment.id] = grade

        context = {
            'students': enrollments,
            'schedule': enrollments.first().schedule if enrollments.exists() else None,
            'grades_dict': grades_dict,
        }

        return render(request, 'user/grade_uploading.html', context)
    else:
        return HttpResponse("No students enrolled in this schedule.")

def gradesTable(request):
    user = request.user

    # Get current academic term
    current_term = AcademicTerm.objects.filter(is_current=True).first()
    # Get grades for this student in current term
    grades = Grade.objects.filter(student=user, academic_term=current_term)
    #print(grades.midterm)
    return render(request, 'user/grades_uploaded.html', {
        'grades': grades,
        'current_term': current_term
    })

def student_grades_view(request):
    student = request.user
    if student.profile.role != 'student':
        return render(request, '403.html')  # or redirect somewhere else

    grades = Grade.objects.filter(student=student).select_related('schedule__subject', 'academic_term')
    
    # Group grades by academic term
    grades_by_term = {}
    for grade in grades:
        term_label = f"{grade.academic_term.academic_year} - {grade.academic_term.semester}"
        if term_label not in grades_by_term:
            grades_by_term[term_label] = []
        grades_by_term[term_label].append(grade)

    return render(request, 'user/grades.html', {
        'grades_by_term': grades_by_term
    })

def has_conflict(schedule, others):
    """Check if a schedule conflicts with any from the list (same room and day)."""
    for other in others:
        if other.id == schedule.id:
            continue
        if (
            schedule.start_time < other.end_time and
            schedule.end_time > other.start_time
        ):
            return True
    return False

def get_room_status(request):
    current_term = AcademicTerm.objects.filter(is_current=True).first()

    schedules = Schedule.objects.filter(academic_term=current_term) \
        .annotate(enrolled_count=Count('studentenrollment')) \
        .select_related('room', 'section', 'subject')

    # Detect conflicts
    schedule_list = []    
    duplicates_map = defaultdict(list)

    for sched in schedules:
    # Use a manual comparison instead of QuerySet filter
        same_day_schedules = [s for s in schedules if s.room == sched.room and s.day_of_week == sched.day_of_week]
    
        conflict = False
        for other in same_day_schedules:
            if sched.id == other.id:
                continue
            if sched.start_time <= other.end_time and sched.end_time >= other.start_time:
                conflict = True
                break
        sched.conflict = conflict
        sched.is_full = sched.enrolled_count >= sched.room.capacity
        # Duplicate detection key
        duplicate_key = (
            sched.room_id,
            sched.section_id,
            sched.subject_id,
            sched.day_of_week,
            sched.start_time.strftime('%H:%M'),
            sched.end_time.strftime('%H:%M'),
        )
        duplicates_map[duplicate_key].append(sched)

        schedule_list.append(sched)

    for sched in schedule_list:
        sched.is_duplicate = False  # initialize
     # Mark duplicates
    for duplicate_schedules in duplicates_map.values():
        if len(duplicate_schedules) > 1:
            for sched in duplicate_schedules:
                sched.is_duplicate = True
        else:
            duplicate_schedules[0].is_duplicate = False

    context = {
        'schedules': schedule_list,
        'term': current_term,
    }
    return render(request, 'user/room_status.html', context)