import os
import random
from django.core.management.base import BaseCommand
from django_seed import Seed
from users.models import User, Follow
from apps.models import Post, Photo, Comment


class Command(BaseCommand):
    help = '해당 커멘더를 통해 테스트 데이터를 생성 할 수 있습니다.'

    def add_arguments(self, parser):
        """
        명령어 --num 뒤에 생성할 데이터 수 입력 / 입력안하면 default=2
        ./manage.py test_data --num 10
        """
        parser.add_argument(
            '--num',
            default=2,
            type=int,
            help='생성할 데이터의 수 입력'
        )

    def handle(self, *args, **options):
        data_num = options['num']  # 생성할 데이터 수
        phone = (lambda x: random.randint(00000000, 99999999))(0)  # 휴대폰 번호 010을 제외한 뒤 8자리
        gender = (lambda x: random.randint(0, 2))(0)
        path = 'core/test_image'

        user_seeder = Seed.seeder()
        post_seeder = Seed.seeder()
        photo_seeder = Seed.seeder()
        comment_seeder = Seed.seeder()
        follow_seeder = Seed.seeder()

        # User data 추가
        user_seeder.add_entity(
            User,  # User 테이블
            data_num,  # 생성할 데이터 수
            {
                'phone': f'010{phone}',
                'gender': gender,
                'is_active': True,
                'is_admin': False,
            }
        )

        user = User.objects.all()
        # Post data 추가
        post_seeder.add_entity(
            Post,
            150,
            {
                'user': lambda x: random.choice(user),
                'content': lambda x: post_seeder.faker.sentence(),
            }
        )

        # Photo data 추가
        post = Post.objects.all()
        photo_seeder.add_entity(
            Photo,
            55,
            {
                'post': lambda x: random.choice(post),
                'image': lambda x: random.choice(os.listdir(path)),
            }
        )

        # Comment data 추가
        comment_seeder.add_entity(
            Comment,
            300,
            {
                'user': lambda x: random.choice(user),
                'post': lambda x: random.choice(post),
                'content': comment_seeder.faker.sentence(),
            }
        )

        # Follow data 추가
        follow_seeder.add_entity(
            Follow,
            data_num,
            {
                'following': lambda x: random.choice(user),
                'follower': lambda x: random.choice(user),
            }
        )

        user_seeder.execute()
        post_seeder.execute()
        photo_seeder.execute()
        comment_seeder.execute()
        follow_seeder.execute()

        # 위의 코드가 정상적으로 실행되었을때 나타냄
        self.stdout.write(self.style.SUCCESS('data create success!'))
