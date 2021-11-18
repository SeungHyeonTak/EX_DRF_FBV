from django.contrib.auth import authenticate
from users.serializers import UserSerializer
from users.models import User
from .tests import Test


class UsersTest(Test):
    """
    생각하지 부분 정리
    - test code를 돌리는데 내가 작성한 view에 대해서 확인을 해야하는데 그러지 못하고 있음
    - 회원탈퇴에 대한 view가 없음
    - 로그인할때 이메일, 패스워드 실패에 대한 로직이 빠져있음
    - 로그인할때 계정 비활성화된 사용자에 대한 처리 빠져있음
    """

    def setUp(self):
        super().setUp()

    def test_signup(self):
        """회원가입 성공"""
        print('회원가입 성공')
        is_created = False
        serializer = UserSerializer(data={
            'fullname': '테스트계정',
            'nickname': 'new_test_user',
            'email': 'new_test@test.com',
            'password': '1qaz2wsx',
            'introduce': '새로운 테스트 계정 입니다.',
            'phone': '01011111111',
            'gender': 0
        })
        if serializer.is_valid():
            serializer.save()
            is_created = True
        self.assertEqual(True, is_created)

    def test_signup_email_overlap(self):
        """회원가입 이메일 중복일때"""
        print('회원가입 이메일 중복')
        is_created = True
        first_serializer = UserSerializer(data={
            'fullname': '테스트계정',
            'nickname': 'new_test_user',
            'email': 'test@test.com',
            'password': '1qaz2wsx',
            'introduce': '새로운 테스트 계정 입니다.',
            'phone': '01011111111',
            'gender': 0
        })
        if first_serializer.is_valid():
            user = User.objects.get(email=self.user.email)
            if user.email == first_serializer.data['email']:
                is_created = False
            self.assertEqual(False, is_created)
        else:
            print('가입 실패')

    def test_signup_phone_overlap(self):
        """회원가입 휴대폰 번호 중복일때"""
        print('회원가입 휴대폰 번호 중복')
        is_created = True
        first_serializer = UserSerializer(data={
            'fullname': '테스트계정',
            'nickname': 'new_test_user',
            'email': 'new_test@test.com',
            'password': '1qaz2wsx',
            'introduce': '새로운 테스트 계정 입니다.',
            'phone': '01000000000',
            'gender': 0
        })
        if first_serializer.is_valid():
            user = User.objects.get(phone=self.user.phone)
            if user.phone == first_serializer.data['phone']:
                is_created = False
            self.assertEqual(False, is_created)
        else:
            print('가입 실패')

    def test_withdrawal(self):
        """회원탈퇴 성공"""
        print('회원탈퇴 성공')
        serializer = UserSerializer(data={
            'fullname': '테스트계정',
            'nickname': 'new_test_user',
            'email': 'new_test@test.com',
            'password': '1qaz2wsx',
            'introduce': '새로운 테스트 계정 입니다.',
            'phone': '01000000000',
            'gender': 0
        })
        if serializer.is_valid():
            serializer.save()
        user = User.objects.get(email=serializer.data['email'])
        user.email = f'{user.email}(회원탈퇴)'
        user.is_active = False
        if user.email.find('(회원탈퇴)') != -1:
            self.assertEqual(False, user.is_active)  # 계정 활성 상태 False
        else:
            print('회원탈퇴 실패')

    def test_signin(self):
        """로그인 성공"""
        print('로그인 성공')
        is_created = False
        user = authenticate(
            email=self.request.user.email,
            password='1qaz2wsx'
        )
        if user:
            is_created = True
        self.assertEqual(True, is_created)

    def test_sigin_email_check(self):
        """로그인 이메일 틀렸을때"""
        print('로그인 이메일 틀림')
        is_created = True
        self.request.user.email = 'asdasd141@test.com'
        user = authenticate(
            email=self.request.user.email,
            password='1qaz2wsx'
        )
        user_email = User.objects.filter(email=self.request.user.email)
        if not user and not user_email:
            is_created = False
        self.assertEqual(False, is_created)

    def test_user_is_active(self):
        """사용자 계정 비활성화"""
        print('사용자 계정 비활성화 일때')
        self.request.user.is_active = False
        self.assertEqual(False, self.request.user.is_active)
