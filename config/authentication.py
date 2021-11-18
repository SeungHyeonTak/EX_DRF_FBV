import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from users.models import User


class JWTAuthentication(authentication.BaseAuthentication):
    """
    token에 대한 정보를 API가 header를 통해서 알아들을 수 있게 하기
    """
    def authenticate(self, request):
        try:
            # header의 정보는 META를 통해서 얻을 수 있다.
            token = request.META.get('HTTP_AUTHORIZATION')
            if token is None:
                return None
            xjwt, jwt_token = token.split(' ')
            decoded = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
            pk = decoded.get('pk')
            user = User.objects.get(pk=pk)
            return user, None  # 공식문서 참고 해보기 user, None을 쓰는거에 대해서
        except (ValueError, User.DoesNotExist):
            return None
        except jwt.exceptions.DecodeError:
            raise exceptions.AuthenticationFailed(detail='JWT Format Invalid')
