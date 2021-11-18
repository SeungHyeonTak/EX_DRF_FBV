from rest_framework import serializers
from users.serializers import UserSerializer
from .models import Post, Comment, Photo, Like


class PostSerializer(serializers.Serializer):
    """
    (참고)
    seiralizer에서는 TextField가 없기때문에 CharField로 적어준다.
    """
    # read_only field에 대해서 알아보기 - users/serializer에 설명 있음
    id = serializers.IntegerField(read_only=True)
    user = UserSerializer(read_only=True)
    content = serializers.CharField(max_length=255)
    lat = serializers.DecimalField(max_digits=10, decimal_places=6)
    lng = serializers.DecimalField(max_digits=10, decimal_places=6)
    is_public = serializers.BooleanField(default=True)

    def create(self, validated_data):
        """
        **를 써서 인자를 받는건 validated_data를 unpack하는거다.
        """
        return Post.objects.create(**validated_data)

    def validate(self, data):
        """
        위에서 Field를 선언한것 중에 각각의 데이터를 검수 할 수 있다.
        아래의 내용은 content의 글자 길이가 2이상이어야만 content를 정상적으로 리턴 할 수 있다.
        그게 아니면 The number of characters is too small. 이라는 에러를 호출 한다.
        """
        if self.instance:
            content = data.get('content', self.instance.content)
        else:
            content = data.get('content')
        if len(content) < 2:
            raise serializers.ValidationError('The number of characters is too small!!')
        return data

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.lat = validated_data.get('lat', instance.lat)
        instance.lng = validated_data.get('lng', instance.lng)
        instance.is_public = validated_data.get('is_public', instance.is_public)

        instance.save()
        return instance


class CommentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    content = serializers.CharField(max_length=255)

    def create(self, validated_data):
        return Comment.objects.create(**validated_data)

    def validate(self, data):
        if self.instance:
            content = data.get('content', self.instance.content)
        else:
            content = data.get('content')

        if len(content) < 2:
            raise serializers.ValidationError('No comments have been entered yet.')

        return data

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)

        instance.save()
        return instance


class PhotoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    post = PostSerializer(read_only=True)
    image = serializers.ImageField()

    def create(self, validated_data):
        return Photo.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.content = validated_data.get('image', instance.image)

        instance.save()
        return instance


class LikeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    post = PostSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    def create(self, validated_data):
        return Like.objects.create(**validated_data)
