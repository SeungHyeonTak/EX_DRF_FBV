from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from .models import User, Follow


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = '__all__'

    def clean_password2(self):
        """암호 일치하는지 확인"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """사용자 업데이트를 위한 양식"""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active',)


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreateForm

    list_display = ('id', 'email', 'fullname', 'nickname', 'is_active', 'is_admin',)
    list_filter = ('is_admin',)

    # 각각 공통적인 부분으로 나누고 field별로 수정 할 수 있는 속성만 적는다.
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Information', {'fields': ('fullname', 'nickname', 'phone', 'gender', 'introduce')}),
        ('Permissions', {'fields': ('is_active', 'is_admin')})
    )

    # 데이터 추가할때 처음으로 입력 받을 내용들 입력
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'fullname', 'password1', 'password2',),
        }),
    )
    search_fields = ('email',)
    ordering = ('-created_at',)
    filter_horizontal = ()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'following', 'follower',)
    list_display_links = ('id',)


admin.site.register(User, UserAdmin)
