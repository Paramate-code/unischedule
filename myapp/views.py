from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Semester, Course,Section,CourseRequest
from .forms import CustomUserForm,StudentRegistrationForm, TeacherRegistrationForm,SemesterForm, CourseForm,SectionForm


# หน้าแรก
def index(request):
    return render(request, 'index.html')
# -----------------------------
# login ครูนักเรียน
# -----------------------------
def general_login(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')  # ใช้ student_id สำหรับทั้งนักเรียนและครู
        password = request.POST.get('password')

        # ล็อคอินโดยใช้ student_id และรหัสผ่าน
        user = authenticate(request, username=student_id, password=password)

        if user is not None:
            if user.role == 'student':
                login(request, user)
                next_url = request.GET.get('next') or reverse('studentdashboard')
                return redirect(next_url)
            elif user.role == 'teacher':
                login(request, user)
                next_url = request.GET.get('next') or reverse('teacherdashboard')
                return redirect(next_url)
        else:
            return render(request, 'login.html', {'error': 'รหัสผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'})
    return render(request, 'login.html')
# -----------------------------
# login staff
# -----------------------------
def stafflogin(request):
    if request.method == 'POST':
        username = request.POST['student_id']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:  # ตรวจสอบว่า user นี้เป็น admin
                login(request, user)
                return redirect('admindashboard')  # ไปหน้า dashboard ของ admin
            else:
                messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงส่วนของเจ้าหน้าที่')
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    
    return render(request, 'loginstaff.html')  # หน้า login สำหรับ admin
# -----------------------------
# dashboard แอดมิน+นับ
# -----------------------------
@login_required
def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')  # เผื่อกรณีไม่ได้ล็อกอิน

    if request.user.role != 'admin':
        return redirect('index')  # หรือ render error page

    # ✅ ดึงข้อมูลผู้ใช้งาน
    teachers = CustomUser.objects.filter(role='teacher')
    students = CustomUser.objects.filter(role='student')

   
    context = {
        'admin': request.user,
        'teachers': teachers,
        'students': students,
        'teacher_count': teachers.count(),
        'student_count': students.count()
    }

    return render(request, 'admindashboard.html', context)
# -----------------------------
# dashboard นักเรียน
# -----------------------------
def student_dashboard(request):
    student = request.user  
    registered_sections = student.registered_sections.all()  
    courses = [section.course for section in registered_sections]  

    return render(request, 'studentdashboard.html', {
        'student': student,
        'registered_sections': registered_sections,
        'courses': courses,  
    })
# -----------------------------
# dashboard ครู
# -----------------------------
@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        return redirect('index')

    teacher = request.user
    sections = Section.objects.select_related('course', 'teacher').filter(teacher=teacher)

    # ดึงคำร้องที่รออาจารย์อนุมัติ โดยเช็กว่า course ของคำร้องอยู่ในวิชาที่อาจารย์สอน
    course_ids = sections.values_list('course_id', flat=True)
    pending_requests = CourseRequest.objects.filter(course__in=course_ids, approved_by_teacher=False)

    context = {
        'teacher': teacher,
        'sections': sections,
        'pending_request_count': pending_requests.count(),
    }

    return render(request, 'teacherdashboard.html', context)
# -----------------------------
# หน้าลงทะเบียนนักเรียน
# -----------------------------
def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.set_password(student.id_card_number)  
            student.save()
            success_url = reverse('register_success') + f'?student_id={student.student_id}&full_name={student.full_name}'
            return HttpResponseRedirect(success_url)
    else:
        form = StudentRegistrationForm()

    return render(request, 'register_student.html', {'form': form})
# -----------------------------
# หน้าลงทะเบียนครูอาจารย์
# -----------------------------
def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            teacher = form.save(commit=False)
            teacher.set_password(teacher.id_card_number)  
            teacher.role = 'teacher'  
            teacher.save()
            
            
            success_url = reverse('register_success') + f'?user_type=ครู&student_id={teacher.student_id}&full_name={teacher.full_name}'
            return HttpResponseRedirect(success_url)
    else:
        form = TeacherRegistrationForm()

    return render(request, 'register_teacher.html', {'form': form})

# -----------------------------
# หน้าลงทะเบียนสำเร็จนักเรียน
# -----------------------------
def success_page(request):
    # รับข้อมูลจาก request
    user_type = request.GET.get('user_type')  
    full_name = request.GET.get('full_name')
    student_id = request.GET.get('student_id')  


    return render(request, 'register_success.html', {
        'full_name': full_name,
        'student_id': student_id,  
        'user_type': user_type,    
    })
# -----------------------------
# แสดงและแก้ไขรูปอาจารย์
# -----------------------------
# ดูโปรไฟล์อาจารย์
def teacher_detail(request, pk):
    teacher = get_object_or_404(CustomUser, pk=pk, role='teacher')
    sections = Section.objects.select_related('course', 'teacher').filter(teacher=teacher)
    return render(request, 'profileteacher.html', {
        'teacher': teacher,
        'sections': sections
    })

# แก้ไขโปรไฟล์
def teacher_edit(request, pk):
    teacher = get_object_or_404(CustomUser, pk=pk, role='teacher')
    if request.method == 'POST':
        form = CustomUserForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            return render(request, 'profileteacher.html', {'teacher': teacher})
    else:
        form = CustomUserForm(instance=teacher)
    return render(request, 'editprofileteacher.html', {'form': form, 'teacher': teacher})
# -----------------------------
# แสดงและแก้ไขรูปนักเรียน
# -----------------------------
# ดูโปรไฟล์นักเรียน
def student_detail(request, pk):
    student = get_object_or_404(CustomUser, pk=pk, role='student')
    registered_sections = student.registered_sections.select_related('course', 'teacher').all()
    
    return render(request, 'studentprofile.html', {
        'student': student,
        'registered_sections': registered_sections
    })
# แก้ไขโปรไฟล์นักเรียน
def student_edit(request, pk):
    student = get_object_or_404(CustomUser, pk=pk, role='student')
    if request.method == 'POST':
        form = CustomUserForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return render(request, 'studentprofile.html', {'student': student})
    else:
        form = CustomUserForm(instance=student)
    return render(request, 'editprofilestudent.html', {'form': form, 'student': student})
# -----------------------------
# ระบบลงทะเบียนเรียน
# -----------------------------
def regissystem(request):
    if request.user.role != 'admin':
        return redirect('index')  

    if request.method == 'POST':
        if 'add_semester' in request.POST:
            semester_form = SemesterForm(request.POST)
            if semester_form.is_valid():
                semester_form.save()
                return redirect('semester')
        elif 'add_course' in request.POST:
            course_form = CourseForm(request.POST)
            if course_form.is_valid():
                course_form.save()
                return redirect('semester')
    else:
        semester_form = SemesterForm()
        course_form = CourseForm()

    semesters = Semester.objects.all()
    courses = Course.objects.all()

   
    registered_semesters = Semester.objects.filter(is_current=True)  
    registered_courses = Course.objects.filter(semester__in=registered_semesters)

    return render(request, 'semester.html', {
        'semester_form': semester_form,
        'course_form': course_form,
        'semesters': semesters,
        'courses': courses,
        'registered_courses': registered_courses,  
    })
# -----------------------------
# ระบบลบข้อมูลในระบบ
# -----------------------------
def delete_system(request, pk):
    if request.user.role != 'admin':
        return redirect('index')  

    # ตรวจสอบว่าเป็นการลบเทมหรือวิชา
    semester = get_object_or_404(Semester, pk=pk)
    courses = Course.objects.filter(semester=semester)  

    if request.method == 'POST':
        # ลบวิชาทั้งหมดในเทอมนี้
        for course in courses:
            course.delete()
        # ลบเทอม
        semester.delete()
        return redirect('semester')  

    return render(request, 'deletesystem.html', {'semester': semester, 'courses': courses})
# -----------------------------
# เพิ่ม Section
# -----------------------------
@login_required
def assign_section(request):
    if request.method == 'POST':
        form = SectionForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('index')  
    else:
        form = SectionForm(user=request.user)

    
    assigned_sections = Section.objects.filter(teacher=request.user).select_related('course')

    return render(request, 'assign_section.html', {
        'form': form,
        'assigned_sections': assigned_sections
    })
# -----------------------------
# เปิดปิดระบบ
# -----------------------------
def toggle_registration(request, semester_id):
    semester = get_object_or_404(Semester, id=semester_id)

    semester.is_registration_open = not semester.is_registration_open
    semester.save()

    messages.success(request, f"ระบบลงทะเบียน {'เปิด' if semester.is_registration_open else 'ปิด'} แล้ว")
    return redirect('admindashboard')  
# -----------------------------
# ลงทะเบียนเรียน
# -----------------------------
from django.urls import reverse

@login_required
def course_registration_view(request):
    current_semester = Semester.objects.filter(is_registration_open=True).last()

    if not current_semester:
        return redirect(f"{reverse('studentdashboard')}?registration_closed=1")

    if request.method == 'POST':
        section_id = request.POST.get('section_id')
        section = get_object_or_404(Section, id=section_id)

        section.students.add(request.user)

        messages.success(request, "ลงทะเบียนเรียบร้อยแล้ว")
        return redirect('studentdashboard')

    sections = Section.objects.select_related('course', 'teacher').filter(course__semester=current_semester)
    return render(request, 'course_registration.html', {'sections': sections})
# -----------------------------
# นักศึกษาส่งคำร้อง
# -----------------------------
@login_required
def request_course(request):
    current_semester = Semester.objects.filter(is_registration_open=True).last()
    if request.user.role != 'student':
        return redirect('index')
    
    if not current_semester:
        # ใช้ query string เพื่อส่งสถานะไปยัง dashboard
        return redirect(f"{reverse('studentdashboard')}?registration_closed=1")


    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        # ตรวจสอบว่าซ้ำไหม
        if CourseRequest.objects.filter(student=request.user, course=course).exists():
            messages.warning(request, "คุณได้ยื่นคำร้องสำหรับวิชานี้แล้ว")
        else:
            CourseRequest.objects.create(student=request.user, course=course)
            messages.success(request, "ส่งคำร้องเรียบร้อยแล้ว")

        return redirect('student_course_request')

    courses = Course.objects.all()
    student_requests = CourseRequest.objects.filter(student=request.user)
    return render(request, 'student_course_request.html', {
        'courses': courses,
        'requests': student_requests
    })
# -----------------------------
# อาจารย์อนุมัติคำร้อง
# -----------------------------
@login_required
def teacher_approve_requests(request):
    if request.user.role != 'teacher':
        return redirect('index')  # หรือ return HttpResponseForbidden()

    # ดึง courses ที่อาจารย์คนนี้สอน
    course_ids = Section.objects.filter(teacher=request.user).values_list('course_id', flat=True)
    
    course_requests = CourseRequest.objects.filter(
        course_id__in=course_ids,
        approved_by_teacher=False
    )

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        try:
            course_request = CourseRequest.objects.get(id=request_id, course_id__in=course_ids)
            course_request.approved_by_teacher = True
            course_request.save()
        except CourseRequest.DoesNotExist:
            pass  # ป้องกันการกด approve วิชาที่ไม่ได้สอน

        return redirect('teacher_approve_requests')

    return render(request, 'teacher_approve_requests.html', {'requests': course_requests})
# -----------------------------
# แอดมินอนุมัติคำร้อง
# -----------------------------
@login_required
def admin_approve_requests(request):
    if request.user.role != 'admin':
        return redirect('index')

    requests = CourseRequest.objects.filter(approved_by_teacher=True, approved_by_admin=False)

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        course_request = get_object_or_404(CourseRequest, id=request_id)
        course_request.approved_by_admin = True
        course_request.save()
        messages.success(request, "คำร้องได้รับการอนุมัติจากแอดมินเรียบร้อย")
        return redirect('admin_approve_requests')

    return render(request, 'admin_approve_requests.html', {'requests': requests})
# -----------------------------
# เช็คสถานะ
# -----------------------------
@login_required
def all_requests_status(request):
    if request.user.role not in ['teacher', 'admin']:
        return redirect('index')
    all_requests = CourseRequest.objects.all().order_by('-request_date')
    return render(request, 'all_requests_status.html', {'all_requests': all_requests})