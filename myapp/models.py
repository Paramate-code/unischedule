from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import date
import random
from django.core.exceptions import ValidationError


TIME_SLOTS = [
    ('08:00-11:00', '08:00-11:00'),
    ('11:00-12:00', '11:00-12:00'),
    # ('12:00-13:00', '12:00-13:00'),  
    ('13:00-16:00', '13:00-16:00'),
    ('16:00-17:00', '16:00-17:00'),
]

DAYS_OF_WEEK = [
    ('mon', 'จันทร์'),
    ('tue', 'อังคาร'),
    ('wed', 'พุธ'),
    ('thu', 'พฤหัส'),
    ('fri', 'ศุกร์'),
]

DEPARTMENT_CHOICES = [
    ('faculty_of_science', 'คณะวิทยาศาสตร์'),
    ('faculty_of_engineering', 'คณะวิศวกรรมศาสตร์'),
    ('faculty_of_medical', 'คณะแพทยศาสตร์'),
    ('faculty_of_law', 'คณะนิติศาสตร์'),
    ('faculty_of_economics', 'คณะเศรษฐศาสตร์'),
    ('faculty_of_education', 'คณะศึกษาศาสตร์'),
    ('faculty_of_business', 'คณะบริหารธุรกิจ'),
    ('faculty_of_commerce', 'คณะพาณิชยศาสตร์'),
    ('faculty_of_arts', 'คณะอักษรศาสตร์'),
    ('faculty_of_social_science', 'คณะสังคมศาสตร์'),
    ('faculty_of_agriculture', 'คณะเกษตรศาสตร์'),
    ('faculty_of_architecture', 'คณะสถาปัตยกรรมศาสตร์'),
    ('faculty_of_information_technology', 'คณะเทคโนโลยีสารสนเทศ'),
    ('faculty_of_agriculture_technology', 'คณะเทคโนโลยีการเกษตร'),
    ('faculty_of_design', 'คณะออกแบบ'),
    ('faculty_of_pharmacy', 'คณะเภสัชศาสตร์'),
    ('faculty_of_dentistry', 'คณะทันตแพทยศาสตร์'),
    ('faculty_of_health_science', 'คณะวิทยาศาสตร์สุขภาพ'),
    ('faculty_of_music', 'คณะดนตรี'),
    ('faculty_of_nursing', 'คณะพยาบาลศาสตร์'),
    ('blank', '-'),
]

# 1. User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, student_id, id_card_number, password=None, **extra_fields):
        if not student_id:
            raise ValueError("ต้องมีรหัสนักศึกษา (student_id)")
        if not id_card_number:
            raise ValueError("ต้องมีเลขบัตรประชาชน")

        user = self.model(
            student_id=student_id,
            id_card_number=id_card_number,
            **extra_fields
        )
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_id, id_card_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(student_id, id_card_number, password, **extra_fields)

# 2. Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    student_id = models.CharField(max_length=8, unique=True)
    id_card_number = models.CharField(max_length=13, unique=True)
    first_name = models.CharField(max_length=100, default='ไม่ระบุ')
    last_name = models.CharField(max_length=100, default='ไม่ระบุ')
    email = models.EmailField(unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, default='blank')
    

    # เพิ่ม role สำหรับแยกประเภทผู้ใช้
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    

  
    gender = models.CharField(max_length=1, choices=[('M', 'ชาย'), ('F', 'หญิง'), ('O', 'อื่นๆ')])
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(default='ไม่ระบุ')
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    

    education_level = models.CharField(
        max_length=20,
        choices=[
            ('high_school', 'มัธยมปลาย'),
            ('vocational', 'ปวช.'),
            ('diploma', 'ปวส.'),
            ('bachelor', 'ปริญญาตรี'),
        ],
        null=True,
        blank=True
    )

    education_teacher = models.CharField(
        max_length=20,
        choices=[
            ('bachelor', 'ปริญญาตรี'), 
            ('Masterdegree', 'ปริญญาโท'),
            ('Doctoral degree', 'ปริญญาเอก'),
        ],
        null=True,
        blank=True
    )

    registration_date = models.DateTimeField(default=timezone.now)

    # Permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'student_id'
    REQUIRED_FIELDS = ['id_card_number', 'first_name', 'last_name', 'email']

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def save(self, *args, **kwargs):
        # ถ้ายังไม่มี student_id ให้สร้าง
        if not self.student_id:
            buddhist_year = date.today().year + 543
            prefix = str(buddhist_year)[-2:]
            random_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            self.student_id = prefix + random_digits
            while CustomUser.objects.filter(student_id=self.student_id).exists():
                random_digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                self.student_id = prefix + random_digits
        super().save(*args, **kwargs)  # บันทึกข้อมูลหลังจากสร้าง 
##########################################################################################################################################
class Semester(models.Model):
    name = models.CharField(max_length=50)  
    academic_year = models.IntegerField()   
    is_current = models.BooleanField(default=False, verbose_name="ภาคเรียนปัจจุบัน")
    is_registration_open = models.BooleanField(default=False)

    class Meta:
        unique_together = ('name', 'academic_year')

    def save(self, *args, **kwargs):
        if self.is_current:
            Semester.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}/{self.academic_year}"
##########################################################################################################################################
class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.code} - {self.name} ({self.semester})"
##########################################################################################################################################
class Section(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='sections')
    teacher = models.ForeignKey('CustomUser', on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    students = models.ManyToManyField(CustomUser, related_name='registered_sections', blank=True)
    day = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    time_slot = models.CharField(max_length=20, choices=TIME_SLOTS, null=True)
    

    class Meta:
        unique_together = ('day', 'time_slot')
        ordering = ['day', 'time_slot']

    def clean(self):
        teacher = getattr(self, 'teacher', None)
        if not teacher:
             return  # ยังไม่มี teacher เพราะยังไม่เซ็ตจาก form
    
        overlapping = Section.objects.filter(
            day=self.day,
            time_slot=self.time_slot,
            course__semester=self.course.semester
        ).exclude(id=self.id)

        if overlapping.exists():
            raise ValidationError("ช่วงเวลานี้ถูกใช้ไปแล้วในวันเดียวกันของภาคเรียนนี้")

        teacher_overlap = Section.objects.filter(
            day=self.day,
            time_slot=self.time_slot,
            teacher=self.teacher,
            course__semester=self.course.semester
        ).exclude(id=self.id)

        if teacher_overlap.exists():
            raise ValidationError("อาจารย์มีการสอนช่วงเวลานี้แล้ว")

    def __str__(self):
        return f"{self.course.name} - {self.teacher.full_name} ({self.day} {self.time_slot})"
##########################################################################################################################################
class CourseRequest(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    request_date = models.DateTimeField(default=timezone.now)
    approved_by_teacher = models.BooleanField(default=False)
    approved_by_admin = models.BooleanField(default=False)


    def is_fully_approved(self):
        return self.approved_by_teacher and self.approved_by_admin

    def status(self):
        if self.approved_by_teacher and self.approved_by_admin:
            return "Approved"
        elif self.approved_by_teacher:
            return "Waiting for admin"
        else:
            return "Waiting for teacher"

    def __str__(self):
        return f"{self.student.full_name} - {self.course.name} ({self.status()})"
    

##########################################################################################################################################
