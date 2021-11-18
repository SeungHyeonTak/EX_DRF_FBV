from .tests import Test
from apps.serializers import PostSerializer
from django.contrib.auth import authenticate


class PostTest(Test):
    def setUp(self):
        super().setUp()

    def test_post_create(self):
        """게시물 생성 성공"""
        print('게시물 생성 성공')
        is_created = False
        user = authenticate(
            email=self.request.user.email,
            password='1qaz2wsx'
        )
        if user:
            serializer = PostSerializer(
                data={
                    'content': '테스트 내용',
                    'lat': '123.123',
                    'lng': '234.213'
                }
            )
            if serializer.is_valid():
                serializer.save(user=user)
                is_created = True
            self.assertEqual(True, is_created)
        else:
            print('게시물 생성 실패')
