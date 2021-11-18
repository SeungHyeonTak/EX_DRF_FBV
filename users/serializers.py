from rest_framework import serializers
from .models import User, Follow


class UserSerializer(serializers.Serializer):
    """
    read_only_fields Serializer에서 어떻게 쓰는지 알기
    -> ModelSerializer가 아닌 Serializer를 사용할때 각 필드안에 read_only를 사용할 수 있는데,
       예를 들어 JSON 데이터로 POST 해야하는 상황이 있으면 read_only로 필수 항목으로 부터 제외 시킬 수 있다.
    """
    id = serializers.IntegerField(read_only=True)
    fullname = serializers.CharField(max_length=25, required=False)
    nickname = serializers.CharField(max_length=15, required=False)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True)  # write_only : json 데이터로 따로 보여지게 하기 싫을때
    introduce = serializers.CharField(max_length=255, required=False)
    phone = serializers.CharField(max_length=13, required=False)
    gender = serializers.IntegerField(default=0, required=False)
    is_active = serializers.BooleanField(default=True)
    is_admin = serializers.BooleanField(default=False)

    # def validate_email(self, value):
    #     """user 생성시 email에 대한 값이 unique인데 똑같은 값으로 생성시 예외 처리"""
    #     email = User.objects.filter(email__icontains=value).exists()
    #     if email:
    #         raise serializers.ValidationError('Duplicate Email')
    #     return value

    # def validate_nickname(self, value):
    #     """단일 데이터에 대한 검수 및 수정 처리 방법"""
    #     return value.upper()

    def validate(self, data):
        """
        필수 값인 이메일 확인
        """
        if self.instance:
            email = data.get('email', self.instance.email)
            if email.find('@') == -1:
                raise serializers.ValidationError('This is not a valid email string.')

        return data

    def update(self, instance, validated_data):
        instance.fullname = validated_data.get('fullname', instance.fullname)
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.email = validated_data.get('email', instance.email)
        instance.introduce = validated_data.get('introduce', instance.introduce)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_admin = validated_data.get('is_admin', instance.is_admin)

        instance.save()
        return instance

    def create(self, validated_data):
        password = validated_data.get('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class FollowSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    following = UserSerializer(read_only=True)
    follower = UserSerializer(read_only=True)

    def create(self, validated_data):
        return Follow.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.follower = validated_data.get('following_id', instance.follower)
        instance.save()
        return instance

    def validate(self, data):
        if self.instance:
            follower = data.get('following_id', self.instance.follower)
        else:
            follower = data.get('following_id')
        if follower:
            follower.delete()
        return data
