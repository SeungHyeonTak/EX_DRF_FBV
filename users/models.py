import os
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone


def get_user_profile_path(instance, filename):
    url = 'user_profile'
    ymd_path = timezone.now().strftime('%Y/%m/%d')
    uuid_name = uuid4().hex
    extension = os.path.splitext(filename)[-1].lower()

    return '/'.join([url, ymd_path, uuid_name + extension])


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('no user email address!')

        user = self.model(
            email=self.normalize_email(email),
            fullname=kwargs.get('fullname') if kwargs else '',
            nickname=kwargs.get('nickname') if kwargs else '',
            introduce=kwargs.get('introduce') if kwargs else None,
            phone=kwargs.get('phone') if kwargs else '',
            gender=kwargs.get('gender') if kwargs else 0,
            is_active=kwargs.get('is_active') if kwargs else True,
            is_admin=kwargs.get('is_admin') if kwargs else False
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    UNSET, MALE, FEMALE = 0, 1, 2
    GENDER_CHOICE = (
        (UNSET, '비공개'),
        (MALE, '남자'),
        (FEMALE, '여자'),
    )
    fullname = models.CharField(verbose_name='username', max_length=25, blank=True)  # 이름
    nickname = models.CharField(verbose_name='nickname', max_length=50, blank=True)  # 닉네임
    profile_image = models.ImageField(verbose_name='profile image', upload_to=get_user_profile_path, blank=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)  # 이메일
    introduce = models.TextField(blank=True, null=True)  # 소개
    phone = models.CharField(verbose_name='phone', max_length=11, blank=True)  # 전화번호
    gender = models.IntegerField(verbose_name='gender', choices=GENDER_CHOICE, default=0)  # 성별

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.fullname

    def following_count(self):
        return self.following.count()

    def follower_list(self):
        follower_users = Follow.objects.filter(following=self.id)
        user_list = [i.follower.nickname for i in follower_users]
        return user_list

    @property
    def is_staff(self):
        return self.is_admin

    # noinspection PyMethodMayBeStatic
    def has_perm(self, perm, obj=None):
        return True

    # noinspection PyMethodMayBeStatic
    def has_module_perms(self, app_label):
        return True


class Follow(models.Model):
    """
    following - 팔로우 당한 user
    follower - 팔로우를 한 user
    """
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
