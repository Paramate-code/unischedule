from django import forms
from .models import CustomUser,Semester,Course,Section
import datetime



class StudentLoginForm(forms.Form):
    student_id = forms.CharField(max_length=10, label='รหัสนักศึกษา')
    id_card_number = forms.CharField(max_length=13, label='เลขบัตรประชาชน')

class RegisterLoginForm(forms.Form):
    teacher_id = forms.CharField(max_length=10, label='รหัสนักศึกษา')
    id_card_number = forms.CharField(max_length=13, label='เลขบัตรประชาชน')
##################################################################################################################
class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'gender',
            'birth_date',
            'address',
            'gpa',
            'education_level',
            'id_card_number',
            'department',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'gpa': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'id_card_number': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '13'}),
            'department': forms.Select(attrs={'class': 'form-control'}),  

        }
        labels = {
            'first_name': 'ชื่อ',
            'last_name': 'นามสกุล',
            'gender': 'เพศ',
            'birth_date': 'วันเกิด',
            'address': 'ที่อยู่',
            'gpa': 'เกรดเฉลี่ย',
            'education_level': 'วุฒิการศึกษา',
            'id_card_number': 'เลขบัตรประชาชน',
            'department': 'คณะที่สมัคร',

        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            css_class = 'form-control'
            if isinstance(self.fields[field].widget, forms.Select):
                css_class = 'form-select'
            self.fields[field].widget.attrs.update({'class': css_class})
            
    def clean_gpa(self):
        gpa = self.cleaned_data.get('gpa')
        if gpa is not None and (gpa < 0 or gpa > 4):
            raise forms.ValidationError("เกรดเฉลี่ยต้องอยู่ระหว่าง 0.00 ถึง 4.00")
        return gpa
############################################################################################################################
class TeacherRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'gender',
            'birth_date',
            'address',
            'education_teacher',
            'id_card_number',
            'department',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'gpa': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'id_card_number': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '13'}),
            'department': forms.Select(attrs={'class': 'form-control'}),  

        }
        labels = {
            'first_name': 'ชื่อ',
            'last_name': 'นามสกุล',
            'gender': 'เพศ',
            'birth_date': 'วันเกิด',
            'address': 'ที่อยู่',
            'education_teacher': 'วุฒิการศึกษา',
            'id_card_number': 'เลขบัตรประชาชน',
            'department': 'คณะที่สมัคร',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            css_class = 'form-control'
            if isinstance(self.fields[field].widget, forms.Select):
                css_class = 'form-select'
            self.fields[field].widget.attrs.update({'class': css_class})
####################################################################################################################################
class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'department', 'profile_picture',
            'gender', 'birth_date', 'address', 'gpa', 'education_level'
        ]
####################################################################################################################################
class SemesterForm(forms.ModelForm):
    TERM_CHOICES = [
        ('ภาคเรียนที่ 1', 'ภาคเรียนที่ 1'),
        ('ภาคเรียนที่ 2', 'ภาคเรียนที่ 2'),
        ('ภาคฤดูร้อน', 'ภาคฤดูร้อน'),
    ]

    name = forms.ChoiceField(choices=TERM_CHOICES, label='เทอม')
    
    current_year = datetime.datetime.now().year + 543  # แปลงเป็นพ.ศ.
    YEAR_CHOICES = [(year, year) for year in range(current_year, current_year + 4)]
    academic_year = forms.ChoiceField(choices=YEAR_CHOICES, label='ปีการศึกษา')

    class Meta:
        model = Semester
        fields = ['name', 'academic_year', 'is_current']
        labels = {
            'is_current': 'ภาคเรียนปัจจุบัน',
        }
###########################################################################################################################
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'description', 'semester', 'created_by']       
###########################################################################################################################
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['course', 'teacher', 'day', 'time_slot']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.role == 'teacher':
            self.fields['course'].queryset = Course.objects.filter(created_by=user)
            self.fields.pop('teacher')  # ซ่อน teacher จากฟอร์ม
            self.user = user  # เก็บ user ไว้ใช้ตอน save
            
    def save(self, commit=True):
        instance = super().save(commit=False)
        if hasattr(self, 'user') and self.user.role == 'teacher':
            instance.teacher = self.user
        if commit:
            instance.save()
        return instance