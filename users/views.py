import jwt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .permissions import IsSelf, IsFollow
from .models import User, Follow
from .serializers import UserSerializer, FollowSerializer
from core.error import error_controlloer


class UserPagination(PageNumberPagination):
    page_size = 20


users_response_schema_dict = {
    400: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_400_NO_REQUIRED_PARAMETERS.get_error_code():
                error_controlloer.APPLY_400_NO_REQUIRED_PARAMETERS.get_error_description(),
            error_controlloer.APPLY_400_VALUE_NOT_VALID.get_error_code():
                error_controlloer.APPLY_400_VALUE_NOT_VALID.get_error_description()
        }
    ),
    409: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_409_EMAIL_IS_NOT_VALID.get_error_code():
                error_controlloer.APPLY_409_EMAIL_IS_NOT_VALID.get_error_description()
        }
    ),
    500: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_500_SERVER_ERROR.get_error_code():
                error_controlloer.APPLY_500_SERVER_ERROR.get_error_description()
        }
    )
}


@swagger_auto_schema(
    methods=['post'],
    request_body=UserSerializer,
    responses=users_response_schema_dict
)
@api_view(['POST'])
@permission_classes([IsSelf])
def user_view(request):
    '''
    회원가입

    ---
    ## `/api/v1/users/`
    ## Request Body
    **파라미터들 type은 `application/json` 이다.**

        - email: 이메일
        - password: 비밀번호
    '''
    email = request.data.get('email', None)
    password = request.data.get('password', None)
    params_list = []

    if email is None:
        params_list.append('email')
    if password is None:
        params_list.append('password')

    if params_list:
        response_message = {
            '000': f'필수 파라미터 ({", ".join(params_list)})가 없습니다.'
        }
        return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)

    try:
        if request.method == 'POST':
            user_email = User.objects.filter(email=email).first()
            if user_email:
                response_message = {
                    '001': '해당 email로 가입된 사용자가 있습니다.',
                }
                return Response(data=response_message, status=status.HTTP_409_CONFLICT)
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                new_user = serializer.save()
                return Response(UserSerializer(new_user).data, status=status.HTTP_201_CREATED)
            else:
                print(f'serializer error : {serializer.errors}')
                response_message = {
                    '002': '값이 유효하지 않습니다.',
                }
                return Response(response_message, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f'error : {e}')
        response_message = {'999': '서버 에러'}
        return Response(response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


me_response_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema('사용자 ID', type=openapi.TYPE_INTEGER),
            "fullname": openapi.Schema('사용자 이름', type=openapi.TYPE_STRING),
            "nickname": openapi.Schema('사용자 닉네임', type=openapi.TYPE_STRING),
            "email": openapi.Schema('이메일', type=openapi.TYPE_STRING),
            "introduce": openapi.Schema('소개', type=openapi.TYPE_STRING),
            "phone": openapi.Schema('휴대폰 번호', type=openapi.TYPE_STRING),
            "gender": openapi.Schema('성별(비공개:0, 남자:1, 여자:2)', type=openapi.TYPE_INTEGER),
            "is_active": openapi.Schema('계정 활성', type=openapi.TYPE_BOOLEAN),
            "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN),
            "following_count": openapi.Schema('팔로잉 수', type=openapi.TYPE_INTEGER),
            "follower_users": openapi.Schema(
                '팔로잉 사용자(닉네임) 리스트',
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING)
            )
        }
    ),
    403: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_403_FORBIDDEN.get_error_code():
                error_controlloer.APPLY_403_FORBIDDEN.get_error_description()
        }
    ),
    500: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_500_SERVER_ERROR.get_error_code():
                error_controlloer.APPLY_500_SERVER_ERROR.get_error_description()
        }
    )
}

me_put_response_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema('상대 사용자 ID', type=openapi.TYPE_INTEGER),
            "fullname": openapi.Schema('상대 사용자 이름', type=openapi.TYPE_STRING),
            "nickname": openapi.Schema('상대 사용자 닉네임', type=openapi.TYPE_STRING),
            "email": openapi.Schema('상대 이메일', type=openapi.TYPE_STRING),
            "introduce": openapi.Schema('상대 소개', type=openapi.TYPE_STRING),
            "phone": openapi.Schema('상대 휴대폰 번호', type=openapi.TYPE_STRING),
            "gender": openapi.Schema('상대 성별(비공개:0, 남자:1, 여자:2)', type=openapi.TYPE_INTEGER),
            "is_active": openapi.Schema('계정 활성', type=openapi.TYPE_BOOLEAN),
            "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN),
        }
    ),
    400: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_400_VALUE_NOT_VALID.get_error_code():
                error_controlloer.APPLY_400_VALUE_NOT_VALID.get_error_description(),
            error_controlloer.APPLY_400_BAD_REQUEST.get_error_code():
                error_controlloer.APPLY_400_BAD_REQUEST.get_error_description()
        }
    ),
    403: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_403_FORBIDDEN.get_error_code():
                error_controlloer.APPLY_403_FORBIDDEN.get_error_description()
        }
    ),
    500: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_500_SERVER_ERROR.get_error_code():
                error_controlloer.APPLY_500_SERVER_ERROR.get_error_description()
        }
    )
}


@swagger_auto_schema(
    method='get',
    operation_summary='''내정보 조회''',
    manual_parameters=[
        openapi.Parameter(
            'authorication',
            openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            description='API 키: 헤더에 Authorization Bearer {API Key} 형태로 전달'
        )
    ],
    operation_description=
    '''
    ## `/api/v1/users/me/`
    ## Query Parameters
    **아래 파라미터들은 URL path에 포함되어 있어야 합니다.**
    ''',
    responses=me_response_schema_dict,
)
@swagger_auto_schema(
    method='put',
    manual_parameters=[
        openapi.Parameter(
            'authorication',
            openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            description='API 키: 헤더에 Authorization Bearer {API Key} 형태로 전달'
        )
    ],
    request_body=openapi.Schema(
        'parameter',
        type=openapi.TYPE_OBJECT,
        properties={
            'fullname': openapi.Schema('사용자 이름', type=openapi.TYPE_STRING),
            'nickname': openapi.Schema('사용자 닉네임', type=openapi.TYPE_STRING),
            'email': openapi.Schema('이메일', type=openapi.TYPE_STRING),
            'password': openapi.Schema('비밀번호', type=openapi.TYPE_STRING),
            'introduce': openapi.Schema('소개', type=openapi.TYPE_STRING),
            'phone': openapi.Schema('휴대폰 번호', type=openapi.TYPE_STRING),
            "gender": openapi.Schema('상대 성별(비공개:0, 남자:1, 여자:2)', type=openapi.TYPE_INTEGER),
            "is_active": openapi.Schema('계정 활성화', type=openapi.TYPE_BOOLEAN)
        }
    ),
    responses=me_put_response_schema_dict
)
@api_view(['GET', 'PUT'])
@permission_classes([IsSelf])
def me_view(request):
    """
    내정보 수정

    ---
    ## `/api/v1/users/me/`
    """
    try:
        if not request.user.is_authenticated:
            response_message = {'003': '자격 인증 데이터(JWT)가 조회되지 않습니다.'}
            return Response(data=response_message, status=status.HTTP_403_FORBIDDEN)
        if request.method == 'GET':
            serializer = UserSerializer(request.user).data
            serializer.update({
                'following_count': request.user.following_count(),
                'follower_users': request.user.follower_list(),
            })
            return Response(serializer, status=status.HTTP_200_OK)
        elif request.method == 'PUT':
            user = User.objects.get(id=request.user.pk)
            serializer = UserSerializer(user, data=request.data, partial=True)
            # 관리자 권한으로만 변경 가능한 부분
            if not user.is_admin and serializer.data.get("is_admin"):
                response_message = {
                    '006': '잘못된 요청입니다.'
                }
                return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                response_message = {'002': serializer.errors}
                return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f'error : {e}')
        response_message = {'999': '서버 에러'}
        return Response(response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


search_response_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'count': openapi.Schema('검색된 사용자 수', type=openapi.TYPE_INTEGER, default=1),
            'next': openapi.Schema(
                '다음 페이지',
                type=openapi.TYPE_FILE,
                default='http://localhost:8000/api/v1/users/search/?nickname=a&page=2'
            ),
            'previous': openapi.Schema('이전 페이지', type=openapi.TYPE_FILE),
            'results': openapi.Schema(
                '검색된 사용자',
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema('사용자 ID', type=openapi.TYPE_INTEGER),
                        "fullname": openapi.Schema('사용자 이름', type=openapi.TYPE_STRING),
                        "nickname": openapi.Schema('사용자 닉네임', type=openapi.TYPE_STRING),
                        "email": openapi.Schema('이메일', type=openapi.TYPE_STRING),
                        "introduce": openapi.Schema('소개', type=openapi.TYPE_STRING),
                        "phone": openapi.Schema('휴대폰 번호', type=openapi.TYPE_STRING),
                        "gender": openapi.Schema('성별(비공개:0, 남자:1, 여자:2)', type=openapi.TYPE_INTEGER),
                        "is_active": openapi.Schema('계정 활성', type=openapi.TYPE_BOOLEAN),
                        "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN),
                    }
                )
            ),
        }
    ),
    500: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_500_SERVER_ERROR.get_error_code():
                error_controlloer.APPLY_500_SERVER_ERROR.get_error_description()
        }
    )
}


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'nickname',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='사용자 닉네임'
        )
    ],
    responses=search_response_schema_dict
)
@api_view(['GET'])
def user_search(request):
    '''
    사용자 닉네임 검색

    ---
    ## `/api/v1/users/search/?nickname=`
    ## Query Parameters
    **아래 파라미터들은 URL query string으로 전달되어야 합니다.**

        - nickname: 사용자 닉네임
    '''
    try:
        user_nickname = request.GET.get('nickname', '')
        paginator = UserPagination()
        user = User.objects.filter(nickname__contains=user_nickname)
        if user is None:
            user = User.objects.all()
        result = paginator.paginate_queryset(user, request)
        serializer = UserSerializer(result, many=True)
        return paginator.get_paginated_response(data=serializer.data)
    except Exception as e:
        print(f'error : {e}')
        response_message = {'999': '서버 에러'}
        return Response(response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


user_detail_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema('사용자 ID', type=openapi.TYPE_INTEGER),
            "fullname": openapi.Schema('사용자 이름', type=openapi.TYPE_STRING),
            "nickname": openapi.Schema('사용자 닉네임', type=openapi.TYPE_STRING),
            "email": openapi.Schema('이메일', type=openapi.TYPE_STRING),
            "introduce": openapi.Schema('소개', type=openapi.TYPE_STRING),
            "phone": openapi.Schema('휴대폰 번호', type=openapi.TYPE_STRING),
            "gender": openapi.Schema('성별(비공개:0, 남자:1, 여자:2)', type=openapi.TYPE_INTEGER),
            "is_active": openapi.Schema('계정 활성', type=openapi.TYPE_BOOLEAN),
            "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN),
            "following_count": openapi.Schema('팔로잉 수', type=openapi.TYPE_INTEGER),
            "follower_users": openapi.Schema(
                '팔로잉 사용자(닉네임) 리스트',
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING)
            )
        }
    ),
    404: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_404_NOT_FOUND.get_error_code():
                error_controlloer.APPLY_404_NOT_FOUND.get_error_description()
        }
    ),
    500: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_500_SERVER_ERROR.get_error_code():
                error_controlloer.APPLY_500_SERVER_ERROR.get_error_description()
        }
    )
}


@swagger_auto_schema(
    method='get',
    responses=user_detail_schema_dict
)
@api_view(['GET'])
def user_detail(request, pk):
    '''
    회원 정보 조회

    ---
    ## `/api/v1/users/{id}/`
    ## Query Parameters
    **아래 파라미터들은 URL path에 포함되어 있어야 합니다.**

        - id: 사용자 id값
    '''
    try:
        if request.method == 'GET':
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user).data
            serializer.update({
                'following_count': user.following_count(),
                'follower_users': user.follower_list(),
            })
            return Response(data=serializer, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        response_message = {'004': '찾고자 하는 사용자가 없습니다.'}
        return Response(data=response_message, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f'error : {e}')
        response_message = {'999': '서버 에러'}
        return Response(response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


login_response_schema_dict = {
    201: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'token': openapi.Schema('token 값(JWT)', type=openapi.TYPE_STRING),
        },
    ),
    400: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_400_NO_REQUIRED_PARAMETERS.get_error_code():
                error_controlloer.APPLY_400_NO_REQUIRED_PARAMETERS.get_error_description()
        }
    ),
    401: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_401_UNAUTHORIZED.get_error_code():
                error_controlloer.APPLY_401_UNAUTHORIZED.get_error_description()
        }
    ),
    500: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_500_SERVER_ERROR.get_error_code():
                error_controlloer.APPLY_500_SERVER_ERROR.get_error_description()
        }
    )
}


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        'parameter',
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema('이메일', type=openapi.TYPE_STRING),
            'password': openapi.Schema('비밀번호', type=openapi.TYPE_STRING)
        },
        required=['email', 'password']
    ),
    responses=login_response_schema_dict
)
@api_view(["POST"])
def login(request):
    """
    로그인

    ---
    ## `/api/v1/users/token/`
    ## Request Body
    **파라미터들 type은 `application/json` 이다. (token type은 `Bearer`이다.)**

        - email: 이메일
        - password: 비밀번호

    """
    email = request.data.get('email', None)
    password = request.data.get('password', None)
    params_list = []

    if email is None:
        params_list.append('email')
    if password is None:
        params_list.append('password')

    if params_list:
        response_message = {
            '000': f'필수 파라미터({", ".join(params_list)})가 없습니다.'
        }
        return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 내가 로그인한 user가 진짜 맞는지 확인하는 작업이 필요함
        # from django.contrib.auth import authenticate를 선언해서 사용할 수 있다.
        # authenticate는 username과 password가 필요하다.
        # 그리고 해당 user가 맞다면 user를 return 해준다.
        user = authenticate(email=email, password=password)

        # user가 None이 아닐때 즉, user 값이 있어야 jwt 값을?
        if user is not None:
            # id 다음으로 받는 인자는 django settings.py에 있는 secret key를 사용한다.
            # settings.py의 secret key로 token의 진위를 판단 할 수 있다.
            # secret key를 로그인하기 위해서만 사용할 것이다.
            encoded_jwt = jwt.encode(
                {
                    'pk': user.pk
                },
                settings.SECRET_KEY,
                algorithm='HS256'
            )
            # 정상적으로 입력했다면 jwt 값을 받을 수 있을건데
            # 받은 jwt값을 encoded해서 우리가 위에서 담은 id값에 대한 내용을 볼 수 있다.
            # 그렇기 때문에 민감한 정보를 jwt에 담아선 안된다.
            # 단순히 user를 구별할 수 있는 식별자 수준의 정보만 담아야한다.
            # 그럼 토큰은 왜 사용하는가?
            """
            server에서는 token에 어떠한 변경사항이 하나라도 있었는지를 판단한다.
            이 데이터를 누군가 건드렸느냐 아니면 그대로이냐가 제일 중요하다.
            token 내부의 정보에 대해서는 그렇게 중요하지 않다.
            """
            return Response(data={'token': encoded_jwt}, status=status.HTTP_201_CREATED)
        else:
            # user에 대한 요청을 잘못 받아왔을때
            response_message = {
                '005': '자격 인증데이터가 제공되지 않았습니다.'
            }
            return Response(data=response_message, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(f'error : {e}')
        response_message = {
            '999': '서버 에러'
        }
        return Response(data=response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


follow_response_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(
                '팔로우 취소',
                type=openapi.TYPE_STRING,
                default='{following__email}님을 팔로우 취소 합니다.'
            )
        }
    ),
    201: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema('팔로우 ID 값', type=openapi.TYPE_INTEGER),
            'following': openapi.Schema(
                '검색된 팔로우 리스트',
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema('상대 사용자 ID', type=openapi.TYPE_INTEGER),
                        "fullname": openapi.Schema('상대 사용자 이름', type=openapi.TYPE_STRING),
                        "nickname": openapi.Schema('상대 사용자 닉네임', type=openapi.TYPE_STRING),
                        "email": openapi.Schema('상대 이메일', type=openapi.TYPE_STRING),
                        "introduce": openapi.Schema('상대 소개', type=openapi.TYPE_STRING),
                        "phone": openapi.Schema('상대 휴대폰 번호', type=openapi.TYPE_STRING),
                        "gender": openapi.Schema('상대 성별(비공개:0, 남자:1, 여자:2)', type=openapi.TYPE_INTEGER),
                        "is_active": openapi.Schema('계정 활성', type=openapi.TYPE_BOOLEAN),
                        "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN),
                    }
                )
            ),
            'follower': openapi.Schema(
                '검색된 팔로우 리스트',
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema('사용자 ID', type=openapi.TYPE_INTEGER),
                        "fullname": openapi.Schema('사용자 이름', type=openapi.TYPE_STRING),
                        "nickname": openapi.Schema('사용자 닉네임', type=openapi.TYPE_STRING),
                        "email": openapi.Schema('이메일', type=openapi.TYPE_STRING),
                        "introduce": openapi.Schema('소개', type=openapi.TYPE_STRING),
                        "phone": openapi.Schema('휴대폰 번호', type=openapi.TYPE_STRING),
                        "gender": openapi.Schema('성별(비공개:0, 남자:1, 여자:2)', type=openapi.TYPE_INTEGER),
                        "is_active": openapi.Schema('계정 활성', type=openapi.TYPE_BOOLEAN),
                        "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN),
                    }
                )
            ),
        },
    ),
    400: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_400_NO_REQUIRED_PARAMETERS.get_error_code():
                error_controlloer.APPLY_400_NO_REQUIRED_PARAMETERS.get_error_description(),
            error_controlloer.APPLY_400_VALUE_NOT_VALID.get_error_code():
                error_controlloer.APPLY_400_VALUE_NOT_VALID.get_error_description()
        }
    ),
    403: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_403_FORBIDDEN.get_error_code():
                error_controlloer.APPLY_403_FORBIDDEN.get_error_description()
        }
    ),
    500: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_500_SERVER_ERROR.get_error_code():
                error_controlloer.APPLY_500_SERVER_ERROR.get_error_description()
        }
    )
}


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'authorication',
            openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            description='API 키: 헤더에 Authorization Bearer {API Key} 형태로 전달'
        )
    ],
    request_body=openapi.Schema(
        'parameter',
        type=openapi.TYPE_OBJECT,
        properties={
            'following_id': openapi.Schema('팔로우 할 사용자 ID', type=openapi.TYPE_INTEGER)
        },
        required=['following_id']
    ),
    responses=follow_response_schema_dict,
)
@api_view(['POST'])
def follows_view(request):
    """
    팔로우 추가

    ---
    **(한번 더 추가하면 unfollow)**
    ## `/api/v1/users/follow/`
    ## Request Body
    **파라미터들 type은 `application/json` 이다.**

        - following_id: 팔로우 할 사용자 ID 값
    """
    try:
        if request.method == 'POST':
            following_id = request.data.get('following_id')

            if not following_id:
                response_message = {'000': '필수 파라미터(following_id) 없음'}
                return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)

            if not request.user.is_authenticated:
                response_message = {'003': '자격 인증 데이터(JWT)가 조회되지 않습니다.'}
                return Response(data=response_message, status=status.HTTP_403_FORBIDDEN)

            following = User.objects.get(id=following_id)

            if not request.user.is_authenticated:
                response_message = {'003': '자격 인증 데이터(JWT)가 조회되지 않습니다.'}
                return Response(data=response_message, status=status.HTTP_403_FORBIDDEN)

            serializer = FollowSerializer(data=request.data)
            user = Follow.objects.filter(following=following, follower=request.user).first()

            if not user:
                if serializer.is_valid():
                    follow = serializer.save(following=following, follower=request.user)
                    follow_serializer = FollowSerializer(follow).data
                    return Response(data=follow_serializer, status=status.HTTP_201_CREATED)
                else:
                    return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                response_message = {'message': f'{following}님을 팔로우 취소 합니다.'}
                user.delete()
                return Response(data=response_message, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        response_message = {'004': '찾고자 하는 사용자가 없습니다.'}
        return Response(data=response_message, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f'error : {e}')
        response_message = {'999': '서버 에러'}
        return Response(data=response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


follow_list_response_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'follower_nickname': openapi.Schema('사용자 닉네임', type=openapi.TYPE_STRING),
            'following_count': openapi.Schema('팔로우 수', type=openapi.TYPE_INTEGER),
            'following_nicknames': openapi.Schema(
                '팔로우 한 사용자 리스트',
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_STRING
                )
            )
        }
    ),
    404: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_404_NOT_FOUND.get_error_code():
                error_controlloer.APPLY_404_NOT_FOUND.get_error_description()
        }
    ),
    500: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_500_SERVER_ERROR.get_error_code():
                error_controlloer.APPLY_500_SERVER_ERROR.get_error_description()
        }
    )
}


@swagger_auto_schema(
    method='get',
    responses=follow_list_response_schema_dict
)
@api_view(['GET'])
@permission_classes([IsFollow])
def follow_view(request, pk):
    """
    사용자 팔로우 리스트 보기

    ---
    **특정 사용자가 구독한 팔로우 리스트 보기**
    ## `/api/v1/users/follow/{id}/`
    ## Query Parameters
    **아래 파라미터들은 URL query string으로 전달되어야 합니다.**

        - id: 사용자 id 값
    """
    try:
        user = User.objects.get(id=pk)
        if request.method == 'GET':
            serializer = {
                'follower_nickname': user.nickname,
                'following_count': user.following_count(),
                'following_nicknames': user.follower_list()
            }
            return Response(serializer, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        response_message = {'004': '찾고자 하는 사용자가 없습니다.'}
        return Response(data=response_message, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f'error : {e}')
        response_message = {'999': '서버 에러'}
        return Response(data=response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
