from django.test import TestCase
from django.http.request import HttpRequest
from users.models import User


class Test(TestCase):
    """공용 테스트 케이스"""

    def setUp(self) -> None:
        """테스트 환경을 위한 DB 세팅"""
        self.user = User(
            fullname='테스트',
            nickname='test_user',
            email='test@test.com',
            introduce='테스트 계정 입니다.',
            phone='01000000000',
            gender=0,
            is_active=True,
            is_admin=False
        )
        self.user.set_password('1qaz2wsx')
        self.user.save()

        self.user2 = User(
            fullname='테스트2',
            nickname='test2_user',
            email='test2@test.com',
            introduce='테스트 계정 입니다.',
            phone='01012344321',
            gender=0,
            is_active=True,
            is_admin=False
        )
        self.user2.set_password('1qaz2wsx')
        self.user2.save()

        self.request = HttpRequest()
        self.request.user = self.user

        self.request2 = HttpRequest()
        self.request.user2 = self.user2
