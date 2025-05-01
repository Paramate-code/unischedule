from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,Section
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class CustomUserCreationForm(forms.ModelForm):
    """Form สำหรับสร้าง user ใหม่ในหน้า admin"""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('student_id', 'id_card_number', 'first_name', 'last_name', 'email', 'birth_date', 'gender', 'role', 'department')  # เพิ่ม 'department'

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    """Form สำหรับแก้ไข user ในหน้า admin"""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = '__all__'

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser

    list_display = ('student_id','id_card_number','full_name', 'email', 'role', 'department', 'is_staff')  
    list_filter = ('role', 'is_staff', 'is_active', 'education_level', 'department')  
    search_fields = ('student_id', 'first_name', 'last_name', 'email', 'department')  
    ordering = ('student_id',)

    fieldsets = (
        (None, {'fields': ('student_id', 'password')}),
        ('ข้อมูลส่วนตัว', {'fields': ('first_name', 'last_name', 'email', 'id_card_number', 'birth_date', 'gender', 'address', 'gpa', 'education_level', 'department',)}),  
        ('สิทธิ์การเข้าถึง', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('ข้อมูลอื่นๆ', {'fields': ('registration_date',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('student_id', 'id_card_number', 'password1', 'password2', 'first_name', 'last_name', 'email', 'birth_date', 'gender', 'role', 'department', 'is_active', 'is_staff'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('course', 'teacher', 'day', 'time_slot')
    list_filter = ('day', 'time_slot')
    search_fields = ('course__name', 'teacher__first_name', 'teacher__last_name')
