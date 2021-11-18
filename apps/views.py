import json
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from core.error import error_controlloer
from .models import Post, Comment, Photo, Like
from .serializers import PostSerializer, CommentSerializer, PhotoSerializer, LikeSerializer
from .permissions import IsOwner, PhotoOwner


class OwnPagination(PageNumberPagination):
    """
    pagination custom 하기
    """
    # page_size 조정하기
    page_size = 20


post_get_response_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'count': openapi.Schema('총 게시물 수', type=openapi.TYPE_INTEGER, default=1),
            'next': openapi.Schema(
                '다음 페이지',
                type=openapi.TYPE_FILE,
                default='http://localhost:8000/api/v1/post/?page=2'
            ),
            'previous': openapi.Schema('이전 페이지', type=openapi.TYPE_FILE),
            'results': openapi.Schema(
                '게시물 리스트',
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema('게시물 ID', type=openapi.TYPE_INTEGER),
                        'user': openapi.Schema(
                            '게시물을 생성한 user 정보',
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
                        ),
                        'content': openapi.Schema('게시물 내용', type=openapi.TYPE_STRING),
                        'lat': openapi.Schema('위도', type=openapi.TYPE_STRING),
                        'lng': openapi.Schema('경도', type=openapi.TYPE_STRING),
                        'is_public': openapi.Schema('게시물 활성화', type=openapi.TYPE_BOOLEAN)
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
post_response_schema_dict = {
    201: PostSerializer,
    400: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
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
    operation_summary='''게시물 리스트 조회''',
    operation_description=
    '''
    ## `/api/v1/post/`
    ''',
    responses=post_get_response_schema_dict
)
@swagger_auto_schema(
    method='post',
    operation_summary='''게시물 생성''',
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
    ## `/api/v1/post/`
    ''',
    request_body=openapi.Schema(
        'parameter',
        type=openapi.TYPE_OBJECT,
        properties={
            'content': openapi.Schema('게시물 내용', type=openapi.TYPE_STRING),
            'lat': openapi.Schema('위도', type=openapi.TYPE_STRING),
            'lng': openapi.Schema('경도', type=openapi.TYPE_STRING),
            'is_public': openapi.Schema('게시물 활성화', type=openapi.TYPE_BOOLEAN, default=True)
        },
        required=['content', 'lat', 'lng']
    ),
    responses=post_response_schema_dict
)
@api_view(["GET", "POST"])
def posts_view(request):
    """
    """
    try:
        if request.method == 'GET':
            # pagination 사용하기
            # paginator = PageNumberPagination()
            # paginator.page_size = 10
            paginator = OwnPagination()

            posts = Post.objects.all()
            # paginate에 request를 파싱하는건 paginator가 page query argument를 찾아낼 수 있기 때문이다.
            result = paginator.paginate_queryset(posts, request)

            # context에 request를 담아주는 이유는 현재 serializer를 누가 보고 있는지 알아내기 위해 request를 serializer로 보내준다.
            serializer = PostSerializer(result, many=True, context={'request': request})
            # django에서의 response와는 다르다. (django는 http response)
            # rest framework의 response는 api등 많은것들을 할 수 있다.
            # Response()는 pagination을 사용하려면 바꿔야한다.
            # paginator의 응답(response)를 return 해줘야한다.
            # return Response(serializer)
            return paginator.get_paginated_response(serializer.data)
        elif request.method == 'POST':
            # print(request.data)  # dict 형태로 나태내어진다.
            if not request.user.is_authenticated:
                response_message = {'003': '자격 인증 데이터(JWT)가 조회되지 않습니다.'}
                return Response(data=response_message, status=status.HTTP_403_FORBIDDEN)
            serializer = PostSerializer(data=request.data)
            if serializer.is_valid():
                # serializer.create()  # 직접 create()를 호출하면 안된다.
                post = serializer.save(user=request.user)  # 대신 save()를 호출해야한다.
                post_serializer = PostSerializer(post).data
                # 본인이 생성한 data를 response data에 담아서 보내주면 생성한 값들을 볼 수 있다.
                return Response(data=post_serializer, status=status.HTTP_201_CREATED)
            else:
                # serializer.errors를 response하게 되면 어떤 에러가 났는지 증상을 명확하게 알 수 있다.
                response_message = {'000': serializer.errors}
                return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f'error : {e}')
        response_message = {'999': '서버 에러'}
        return Response(data=response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


specific_post_get_schema = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema('게시물 ID', type=openapi.TYPE_INTEGER),
            'user': openapi.Schema(
                '게시물을 생성한 user 정보',
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
            ),
            'content': openapi.Schema('게시물 내용', type=openapi.TYPE_STRING),
            'lat': openapi.Schema('위도', type=openapi.TYPE_STRING),
            'lng': openapi.Schema('경도', type=openapi.TYPE_STRING),
            'is_public': openapi.Schema('게시물 활성화', type=openapi.TYPE_BOOLEAN),
            'like_count': openapi.Schema('게시물 좋아요 갯수', type=openapi.TYPE_INTEGER)
        }
    ),
    403: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_403_USER_DOES_NOT_MATCH.get_error_code():
                error_controlloer.APPLY_403_USER_DOES_NOT_MATCH.get_error_description()
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

specific_post_put_schema = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema('게시물 ID', type=openapi.TYPE_INTEGER),
            'user': openapi.Schema(
                '게시물을 생성한 user 정보',
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
            ),
            'content': openapi.Schema('게시물 내용', type=openapi.TYPE_STRING),
            'lat': openapi.Schema('위도', type=openapi.TYPE_STRING),
            'lng': openapi.Schema('경도', type=openapi.TYPE_STRING),
            'is_public': openapi.Schema('게시물 활성화', type=openapi.TYPE_BOOLEAN),
        }
    ),
    400: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_400_VALUE_NOT_VALID.get_error_code():
                error_controlloer.APPLY_400_VALUE_NOT_VALID.get_error_description()
        }
    ),
    403: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_403_USER_DOES_NOT_MATCH.get_error_code():
                error_controlloer.APPLY_403_USER_DOES_NOT_MATCH.get_error_description()
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

specific_post_delete_schema = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(
                type=openapi.TYPE_STRING,
                default='게시물이 삭제되었습니다.'
            )
        }
    ),
    403: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_403_USER_DOES_NOT_MATCH.get_error_code():
                error_controlloer.APPLY_403_USER_DOES_NOT_MATCH.get_error_description()
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
    operation_summary='''특정 게시물 조회''',
    operation_description=
    '''
    ## `api/v1/post/{id}/`
    
        - id: 게시물(Post) ID
    ''',
    responses=specific_post_get_schema
)
@swagger_auto_schema(
    method='put',
    operation_summary='''게시물 수정''',
    operation_description=
    '''
    ## `api/v1/post/{id}/`
    
        - id: 게시물(Post) ID
    ''',
    manual_parameters=[
        openapi.Parameter(
            'authorication',
            openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            description='API 키: 헤더에 Authorization Bearer {API Key} 형태로 전달'
        )
    ],
    responses=specific_post_put_schema
)
@swagger_auto_schema(
    method='delete',
    operation_summary='''게시물 삭제''',
    operation_description=
    '''
    ## `api/v1/post/{id}/`
    
        - id: 게시물(Post) ID
    ''',
    manual_parameters=[
        openapi.Parameter(
            'authorication',
            openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            description='API 키: 헤더에 Authorization Bearer {API Key} 형태로 전달'
        )
    ],
    responses=specific_post_delete_schema
)
@api_view(["GET", "PUT", "DELETE"])
def post_view(request, pk):
    """
    특정 Post를 확인하기 위해선 pk가 필요하다.
    관련 메서드에는 GET, PUT, DELETE가 있는데 공통적으로 필요한 변수는 Post의 pk값이다.
    하지만 각 조건마다 pk값을 똑같이 선언해서 사용하는것 보다.
    post_view()안에서 전역 변수로 선언 해놓고 각 HTTP_METHOD마다 pk를 가져가서 사용하는게 더 가독성이 좋다.
    """
    try:
        post = Post.objects.get(pk=pk)
        if request.method == "GET":
            serializer = PostSerializer(post).data
            serializer.update({
                'like_count': Like.objects.filter(post_id=post.id).count()
            })
            return Response(serializer, status=status.HTTP_200_OK)
        elif request.method == "PUT":
            if post.user != request.user:
                response_message = {'007': '사용자가 일치하지 않습니다.'}
                return Response(data=response_message, status=status.HTTP_403_FORBIDDEN)
            # seriazlier에서 키워드 인자로 쓰이는 partial=True는 데이터를 모두 보내는 것이 아니라 내가 바꾸고 싶은 데이터만 보내게 하는것임.
            # 그렇지 않으면 모든 값을 업데이트 하기 바랄것이다.
            serializer = PostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                post = serializer.save()
                return Response(PostSerializer(post).data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == "DELETE":
            if post.user != request.user:
                response_message = {'007': '사용자가 일치하지 않습니다.'}
                return Response(data=response_message, status=status.HTTP_403_FORBIDDEN)
            post.delete()
            response_message = {'message': '게시물이 삭제되었습니다.'}
            return Response(data=response_message, status=status.HTTP_200_OK)
    except Post.DoesNotExist:
        response_message = {'004': '찾고자 하는 게시물이 없습니다.'}
        return Response(data=response_message, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f'error : {e}')
        response_message = {'999': '서버 에러'}
        return Response(data=response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


post_fav_get_response_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'success': openapi.Schema('좋아요', type=openapi.TYPE_STRING, default='게시물(post_id) 좋아요'),
            'message': openapi.Schema('좋아요 취소', type=openapi.TYPE_STRING, default='게시물(post_id) 좋아요 취소')
        }
    ),
    400: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
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
            'post_id': openapi.Schema('게시물 ID', type=openapi.TYPE_INTEGER)
        },
        required=['post_id']
    ),
    responses=post_fav_get_response_schema_dict
)
@api_view(["POST"])
def posts_fav(request):
    """
    게시물 좋아요

    ---
    **(한번 더 추가하면 좋아요 취소)**
    ## `/api/v1/post/favs/`
    ## Request Body
    **파라미터들 type은 `application/json` 이다.**

        - post_id: 게시물 ID
    """
    try:
        # paginator = OwnPagination()
        # like = Like.objects.all()
        # result = paginator.paginate_queryset(like, request)
        # serializer = LikeSerializer(result, many=True, context={'request': request})
        # return paginator.get_paginated_response(serializer.data)
        if request.method == 'POST':
            if not request.user.is_authenticated:
                response_message = {'003': '자격 인증 데이터(JWT)가 조회되지 않습니다.'}
                return Response(data=response_message, status=status.HTTP_403_FORBIDDEN)

            post_id = request.data.get('post_id')
            if not post_id:
                response_message = {'000': '필수 파라미터 post_id가 없습니다.'}
                return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)

            serializer = LikeSerializer(data=request.data)
            post = Post.objects.get(id=post_id)
            like = Like.objects.filter(post=post, user=request.user).first()
            if not like:
                if serializer.is_valid():
                    # like = serializer.save(post=post, user=request.user)
                    serializer.save(post=post, user=request.user)
                    # like_serializer = LikeSerializer(like).data
                    response_message = {'success': f'게시물({post_id}) 좋아요'}
                    return Response(data=response_message, status=status.HTTP_200_OK)
                else:
                    response_message = {'002': serializer.errors}
                    return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)
            else:
                response_message = {'message': f'게시물({post_id}) 좋아요 취소'}
                like.delete()
                return Response(data=response_message, status=status.HTTP_200_OK)
    except Exception as e:
        print(f'error : {e}')
        response_message = {'999': '서버 에러'}
        return Response(data=response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


post_fav_list_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'post_id': openapi.Schema('게시물 ID', type=openapi.TYPE_INTEGER),
            'like_count': openapi.Schema('해당 게시물 좋아요 갯수', type=openapi.TYPE_INTEGER),
            'user_list': openapi.Schema(
                '좋아요 누른 사용자 리스트',
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
    responses=post_fav_list_schema_dict
)
@api_view(["GET"])
def post_fav(request, pk):
    """
    특정 게시물 좋아요 리스트

    ---
    ## `/api/v1/post/favs/{id}`

        - id: Post ID
    """
    try:
        if request.method == 'GET':
            post_id = Like.objects.filter(post_id=pk)
            serializer = {
                'post_id': pk,
                'like_count': post_id.count(),
                'user_list': [i.user.nickname for i in post_id],
            }
            return Response(data=serializer, status=status.HTTP_200_OK)
    except Like.DoesNotExist:
        response_message = {'004': 'post_id가 없습니다.'}
        return Response(data=response_message, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f'error : {e}')
        response_message = {'999': '서버 에러'}
        return Response(response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


post_search_response_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'count': openapi.Schema('총 게시물 수', type=openapi.TYPE_INTEGER, default=1),
            'next': openapi.Schema(
                '다음 페이지',
                type=openapi.TYPE_FILE,
                default='http://localhost:8000/api/v1/post/?page=2'
            ),
            'previous': openapi.Schema('이전 페이지', type=openapi.TYPE_FILE),
            'results': openapi.Schema(
                '게시물 리스트',
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema('게시물 ID', type=openapi.TYPE_INTEGER),
                        'user': openapi.Schema(
                            '게시물을 생성한 user 정보',
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
                        ),
                        'content': openapi.Schema('게시물 내용', type=openapi.TYPE_STRING),
                        'lat': openapi.Schema('위도', type=openapi.TYPE_STRING),
                        'lng': openapi.Schema('경도', type=openapi.TYPE_STRING),
                        'is_public': openapi.Schema('게시물 활성화', type=openapi.TYPE_BOOLEAN)
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
            'is_public',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='게시물 활성 여부'
        ),
        openapi.Parameter(
            'lat',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='위도'
        ),
        openapi.Parameter(
            'lng',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='경도'
        ),
    ],
    responses=post_search_response_schema_dict
)
@api_view(['GET'])
def post_search(request):
    """
    게시물 검색

    ---
    ## `/api/v1/post/search/`
    ## Query Parameters
    **아래 파라미터들은 URL query string으로 전달되어야 합니다. (아무것도 입력 안할 시 전체 검색 함)**

        - is_public: 게시물 활성화 여부(True/False)
        - lat: 위도 좌표 (+-0.005의 위치까지의 범위는 인식 가능)
        - lng: 경도 좌표 (+-0.005의 위치까지의 범위는 인식 가능)
    """
    try:
        is_public = request.GET.get('is_public', None)
        lat = request.GET.get('lat', None)
        lng = request.GET.get('lng', None)
        filter_kwargs = {}
        # 여러개 사용할때 이렇게 쓰면 유용할듯하다.
        # 지금은 하나만 예시로 들었다.
        if is_public is not None:
            filter_kwargs['is_public'] = is_public
        if lat is not None and lng is not None:
            filter_kwargs['lat__gte'] = float(lat) - 0.005  # gte -> 크거나 같음  / -는 왼쪽
            filter_kwargs['lat__lte'] = float(lat) + 0.005  # lte -> 작거나 같음  / +는 오른쪽
            filter_kwargs['lng__gte'] = float(lng) - 0.005
            filter_kwargs['lng__lte'] = float(lng) + 0.005
        paginator = OwnPagination()
        posts = Post.objects.filter(**filter_kwargs)
        result = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        print(f'error : {e}')
        response_message = {'999': '서버 에러'}
        return Response(data=response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


comments_get_response_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'count': openapi.Schema('검색된 댓글 갯수', type=openapi.TYPE_INTEGER, default=1),
            'next': openapi.Schema(
                '다음 페이지',
                type=openapi.TYPE_FILE,
                default="http://localhost:8000/api/v1/photo/?page=2",
            ),
            'previous': openapi.Schema('이전 페이지', type=openapi.TYPE_FILE),
            'results': openapi.Schema(
                '사진을 사용한 게시물',
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema('댓글(Comment) ID', type=openapi.TYPE_INTEGER),
                        "user": openapi.Schema(
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
                                "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN)
                            }
                        ),
                        "post": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema('Post(게시물) ID', type=openapi.TYPE_INTEGER),
                                "user": openapi.Schema(
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
                                        "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN)
                                    }
                                ),
                                "content": openapi.Schema('게시물 내용', type=openapi.TYPE_STRING),
                                "lat": openapi.Schema('위도', type=openapi.TYPE_STRING),
                                "lng": openapi.Schema('경도', type=openapi.TYPE_STRING),
                                "is_public": openapi.Schema('게시물 활성화', type=openapi.TYPE_BOOLEAN)
                            }
                        ),
                        "content": openapi.Schema('댓글 내용', type=openapi.TYPE_STRING)
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
comments_post_response_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema('댓글(Comment) ID', type=openapi.TYPE_INTEGER),
            "user": openapi.Schema(
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
                    "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN)
                }
            ),
            "post": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema('Post(게시물) ID', type=openapi.TYPE_INTEGER),
                    "user": openapi.Schema(
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
                            "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN)
                        }
                    ),
                    "content": openapi.Schema('게시물 내용', type=openapi.TYPE_STRING),
                    "lat": openapi.Schema('위도', type=openapi.TYPE_STRING),
                    "lng": openapi.Schema('경도', type=openapi.TYPE_STRING),
                    "is_public": openapi.Schema('게시물 활성화', type=openapi.TYPE_BOOLEAN)
                }
            ),
            "content": openapi.Schema('댓글 내용', type=openapi.TYPE_STRING)
        }
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
    401: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_401_UNAUTHORIZED.get_error_code():
                error_controlloer.APPLY_401_UNAUTHORIZED.get_error_description()
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
    operation_summary='''댓글 리스트''',
    operation_description=
    '''
    ## `/api/v1/comment/`
    ''',
    responses=comments_get_response_schema_dict
)
@swagger_auto_schema(
    method='post',
    operation_summary='''댓글 생성''',
    operation_description=
    '''
    ## `/api/v1/comment/`
    
        - post_id : 게시물 ID
    ''',
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
            'post_id': openapi.Schema('게시물 ID', type=openapi.TYPE_INTEGER),
            'content': openapi.Schema('댓글 내용', type=openapi.TYPE_STRING)
        },
        required=['post_id', 'content']
    ),
    responses=comments_post_response_schema_dict
)
@api_view(['GET', 'POST'])
def comments_view(request):
    """
    GET: 댓글 리스트
    POST: 댓글 작성
    """
    try:
        if request.method == 'GET':
            paginator = OwnPagination()
            comments = Comment.objects.all()
            result = paginator.paginate_queryset(comments, request)
            serializer = CommentSerializer(result, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        elif request.method == 'POST':
            # 필수 파라미터 검증
            post_id = request.data.get('post_id')
            if not post_id:
                response_message = {'000': '필수 파라미터(post_id) 없음'}
                return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)
            if not request.user.is_authenticated:
                response_message = {'005': '자격 인증데이터가 제공되지 않았습니다.'}
                return Response(data=response_message, status=status.HTTP_401_UNAUTHORIZED)

            post = Post.objects.get(id=post_id)
            if post.user == request.user:
                serializer = CommentSerializer(data=request.data)
                if serializer.is_valid():
                    comment = serializer.save(user=request.user, post=post)
                    comment_serializer = CommentSerializer(comment).data
                    return Response(data=comment_serializer, status=status.HTTP_200_OK)
                else:
                    print(f'serializer is_valid error: {serializer.errors}')
                    response_message = {'002': '값이 유효하지 않습니다.'}
                    return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)
            else:
                response_message = {'003': '자격 인증 데이터(JWT)가 조회되지 않습니다.'}
                return Response(data=response_message, status=status.HTTP_403_FORBIDDEN)

    except Post.DoesNotExist:
        response_message = {'004': '찾고자 하는 (사용자/게시물)가 없습니다.'}
        return Response(data=response_message, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f'error: {e}')
        response_message = {'999': '서버 에러'}
        return Response(data=response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


comment_get_response_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema('댓글(Comment) ID', type=openapi.TYPE_INTEGER),
            "user": openapi.Schema(
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
                    "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN)
                }
            ),
            "post": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema('Post(게시물) ID', type=openapi.TYPE_INTEGER),
                    "user": openapi.Schema(
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
                            "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN)
                        }
                    ),
                    "content": openapi.Schema('게시물 내용', type=openapi.TYPE_STRING),
                    "lat": openapi.Schema('위도', type=openapi.TYPE_STRING),
                    "lng": openapi.Schema('경도', type=openapi.TYPE_STRING),
                    "is_public": openapi.Schema('게시물 활성화', type=openapi.TYPE_BOOLEAN)
                }
            ),
            "content": openapi.Schema('댓글 내용', type=openapi.TYPE_STRING)
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
comment_put_response_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema('댓글(Comment) ID', type=openapi.TYPE_INTEGER),
            "user": openapi.Schema(
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
                    "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN)
                }
            ),
            "post": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema('Post(게시물) ID', type=openapi.TYPE_INTEGER),
                    "user": openapi.Schema(
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
                            "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN)
                        }
                    ),
                    "content": openapi.Schema('게시물 내용', type=openapi.TYPE_STRING),
                    "lat": openapi.Schema('위도', type=openapi.TYPE_STRING),
                    "lng": openapi.Schema('경도', type=openapi.TYPE_STRING),
                    "is_public": openapi.Schema('게시물 활성화', type=openapi.TYPE_BOOLEAN)
                }
            ),
            "content": openapi.Schema('댓글 내용', type=openapi.TYPE_STRING)
        }
    ),
    400: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
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
comment_delete_response_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(
                type=openapi.TYPE_STRING,
                default='게시물이 삭제되었습니다.'
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
    operation_summary='''특정 댓글 보기''',
    operation_description=
    '''
    ## `/api/v1/comment/{id}/`
    
        - id : 댓글(Comment) ID
    ''',
    responses=comment_get_response_schema_dict
)
@swagger_auto_schema(
    method='put',
    operation_summary='''댓글 수정''',
    operation_description=
    '''
    ## `/api/v1/comment/{id}/`

        - id : 댓글(Comment) ID
    ''',
    manual_parameters=[
        openapi.Parameter(
            'authorication',
            openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            description='API 키: 헤더에 Authorization Bearer {API Key} 형태로 전달'
        )
    ],
    responses=comment_put_response_schema_dict
)
@swagger_auto_schema(
    method='delete',
    operation_summary='''댓글 삭제''',
    operation_description=
    '''
    ## `/api/v1/comment/{id}/`

        - id : 댓글(Comment) ID
    ''',
    manual_parameters=[
        openapi.Parameter(
            'authorication',
            openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            description='API 키: 헤더에 Authorization Bearer {API Key} 형태로 전달'
        )
    ],
    responses=comment_delete_response_schema_dict
)
@api_view(['GET', 'PUT', 'DELETE'])
# @permission_classes([IsOwner])
def comment_view(request, pk):
    """
    GET: comment detail 보기 (로그인한 상태에서만 확인가능)
    PUT: comment 수정
    DELETE: comment 삭제
    """
    try:
        comment = Comment.objects.get(pk=pk)
        if request.method == 'GET':
            serializer = CommentSerializer(comment).data
            return Response(serializer)
        elif comment.user == request.user:
            if request.method == 'PUT':
                serializer = CommentSerializer(comment, data=request.data, partial=True)
                if serializer.is_valid():
                    comment = serializer.save()
                    return Response(CommentSerializer(comment).data)
                else:
                    print(f'serializer is_valid error : {serializer.errors}')
                    response_message = {'002': '값이 유효하지 않습니다.'}
                    return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)
            elif request.method == 'DELETE':
                comment.delete()
                response_message = {'message': '정상적으로 삭제 되었습니다.'}
                return Response(data=response_message, status=status.HTTP_200_OK)
        else:
            response_message = {'003': '자격 인증 데이터(JWT)가 조회되지 않습니다.'}
            return Response(data=response_message, status=status.HTTP_403_FORBIDDEN)
    except Comment.DoesNotExist:
        response_message = {'004': '찾고자하는 내용이 없습니다.'}
        return Response(data=response_message, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f'error : {e}')
        response_message = {'999': '서버 에러'}
        return Response(data=response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


photos_get_api_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'count': openapi.Schema('검색된 사진 갯수', type=openapi.TYPE_INTEGER, default=1),
            'next': openapi.Schema(
                '다음 페이지',
                type=openapi.TYPE_FILE,
                default="http://localhost:8000/api/v1/photo/?page=2",
            ),
            'previous': openapi.Schema('이전 페이지', type=openapi.TYPE_FILE),
            'results': openapi.Schema(
                '사진을 사용한 게시물',
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema('Photo(사진) ID', type=openapi.TYPE_INTEGER),
                        "post": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema('Post(게시물) ID', type=openapi.TYPE_INTEGER),
                                "user": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "fullname": openapi.Schema('사용자 이름', type=openapi.TYPE_STRING),
                                        "nickname": openapi.Schema('사용자 닉네임', type=openapi.TYPE_STRING),
                                        "email": openapi.Schema('이메일', type=openapi.TYPE_STRING),
                                        "introduce": openapi.Schema('소개', type=openapi.TYPE_STRING),
                                        "phone": openapi.Schema('휴대폰 번호', type=openapi.TYPE_STRING),
                                        "gender": openapi.Schema('성별(비공개:0, 남자:1, 여자:2)', type=openapi.TYPE_INTEGER),
                                        "is_active": openapi.Schema('계정 활성', type=openapi.TYPE_BOOLEAN),
                                        "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN)
                                    }
                                ),
                                "content": openapi.Schema('게시물 내용', type=openapi.TYPE_STRING),
                                "lat": openapi.Schema('위도', type=openapi.TYPE_STRING),
                                "lng": openapi.Schema('경도', type=openapi.TYPE_STRING),
                                "is_public": openapi.Schema('게시물 활성화', type=openapi.TYPE_BOOLEAN)
                            }
                        ),
                        "image": openapi.Schema('사진 경로', type=openapi.TYPE_STRING)
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

photos_post_api_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(
                type=openapi.TYPE_STRING,
                default='사진 저장이 완료되었습니다.'
            )
        }
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
    401: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_401_UNAUTHORIZED.get_error_code():
                error_controlloer.APPLY_401_UNAUTHORIZED.get_error_description()
        }
    ),
    403: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_403_USER_DOES_NOT_MATCH.get_error_code():
                error_controlloer.APPLY_403_USER_DOES_NOT_MATCH.get_error_description()
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
    operation_summary='''사진 리스트 조회''',
    operation_description=
    '''
    ## `api/v1/photo/`
    ''',
    responses=photos_get_api_schema_dict
)
@swagger_auto_schema(
    method='post',
    operation_summary='''사진 생성''',
    operation_description=
    '''
    ## `api/v1/photo`
    ## Request Body
    **파라미터들 type은 `application/json` 이다.**
    
        - post_id: 게시물 ID
        - image: 이미지 경로
    ''',
    responses=photos_post_api_schema_dict
)
@api_view(['GET', 'POST'])
def photos_view(request):
    try:
        if request.method == 'GET':
            paginator = OwnPagination()
            photos = Photo.objects.all()
            result = paginator.paginate_queryset(photos, request)
            serializer = PhotoSerializer(result, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        elif request.method == 'POST':
            post_id = request.data.get('post_id')
            if not post_id:
                response_message = {'000': '필수 파라미터(post_id) 없음'}
                return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)
            if not request.user.is_authenticated:
                response_message = {'005': '자격 인증데이터가 제공되지 않았습니다.'}
                return Response(data=response_message, status=status.HTTP_401_UNAUTHORIZED)

            post = Post.objects.get(id=post_id)
            if post.user != request.user:
                response_message = {'007': '사용자가 일치하지 않습니다.'}
                return Response(data=response_message, status=status.HTTP_403_FORBIDDEN)

            serializer = PhotoSerializer(data=request.data)
            if serializer.is_valid():
                photo = serializer.save(post=post)
                # photo_serializer = PhotoSerializer(photo).data
                response_message = {'message': '사진 저장이 완료되었습니다.'}
                return Response(data=response_message, status=status.HTTP_200_OK)
            else:
                print(f'serializer is_valid error : {serializer.errors}')
                response_message = {'002': '값이 유효하지 않습니다.'}
                return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)
    except Post.DoesNotExist:
        response_message = {'004': '찾고자 하는 (사용자/게시물)가 없습니다.'}
        return Response(data=response_message, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f'error: {e}')
        response_message = {'999': '서버 에러'}
        return Response(data=response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


photo_get_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema('Photo(사진) ID', type=openapi.TYPE_INTEGER),
            "post": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema('Post(게시물) ID', type=openapi.TYPE_INTEGER),
                    "user": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "fullname": openapi.Schema('사용자 이름', type=openapi.TYPE_STRING),
                            "nickname": openapi.Schema('사용자 닉네임', type=openapi.TYPE_STRING),
                            "email": openapi.Schema('이메일', type=openapi.TYPE_STRING),
                            "introduce": openapi.Schema('소개', type=openapi.TYPE_STRING),
                            "phone": openapi.Schema('휴대폰 번호', type=openapi.TYPE_STRING),
                            "gender": openapi.Schema('성별(비공개:0, 남자:1, 여자:2)', type=openapi.TYPE_INTEGER),
                            "is_active": openapi.Schema('계정 활성', type=openapi.TYPE_BOOLEAN),
                            "is_admin": openapi.Schema('관리자', type=openapi.TYPE_BOOLEAN)
                        }
                    ),
                    "content": openapi.Schema('게시물 내용', type=openapi.TYPE_STRING),
                    "lat": openapi.Schema('위도', type=openapi.TYPE_STRING),
                    "lng": openapi.Schema('경도', type=openapi.TYPE_STRING),
                    "is_public": openapi.Schema('게시물 활성화', type=openapi.TYPE_BOOLEAN)
                }
            ),
            "image": openapi.Schema('사진 경로', type=openapi.TYPE_STRING)
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
photo_put_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(
                type=openapi.TYPE_STRING,
                default='수정 완료'
            )
        }
    ),
    400: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_400_VALUE_NOT_VALID.get_error_code():
                error_controlloer.APPLY_400_VALUE_NOT_VALID.get_error_description()
        }
    ),
    403: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_403_USER_DOES_NOT_MATCH.get_error_code():
                error_controlloer.APPLY_403_USER_DOES_NOT_MATCH.get_error_description()
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
photo_delete_schema_dict = {
    200: openapi.Schema(
        'response_data',
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(
                type=openapi.TYPE_STRING,
                default='정상적으로 삭제 되었습니다.'
            )
        }
    ),
    403: openapi.Schema(
        'error_response',
        type=openapi.TYPE_OBJECT,
        properties={
            error_controlloer.APPLY_403_USER_DOES_NOT_MATCH.get_error_code():
                error_controlloer.APPLY_403_USER_DOES_NOT_MATCH.get_error_description()
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
    operation_summary='''사진 조회''',
    operation_description=
    '''
    ## `/api/v1/photo/{id}`
    
        - id: Photo(사진) ID
    ''',
    responses=photo_get_schema_dict
)
@swagger_auto_schema(
    method='put',
    operation_summary='''사진 수정''',
    operation_description=
    '''
    ## `/api/v1/photo/{id}`

        - id: Photo(사진) ID
    ''',
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
            'image': openapi.Schema('사진 경로', type=openapi.TYPE_STRING)
        }
    ),
    responses=photo_put_schema_dict
)
@swagger_auto_schema(
    method='delete',
    operation_summary='''사진 삭제''',
    operation_description=
    '''
    ## `/api/v1/photo/{id}`

        - id: Photo(사진) ID
    ''',
    manual_parameters=[
        openapi.Parameter(
            'authorication',
            openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            description='API 키: 헤더에 Authorization Bearer {API Key} 형태로 전달'
        )
    ],
    responses=photo_delete_schema_dict
)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([PhotoOwner])
def photo_view(request, pk):
    try:
        photo = Photo.objects.get(pk=pk)
        if request.method == 'GET':
            serializer = PhotoSerializer(photo).data
            return Response(serializer, status=status.HTTP_200_OK)
        elif photo.post.user == request.user:
            if request.method == 'PUT':
                serializer = PhotoSerializer(photo, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    # serializer = PhotoSerializer(photo).data
                    response_message = {'message': '수정 완료'}
                    return Response(data=response_message, status=status.HTTP_200_OK)
                else:
                    response_message = {'002': '값이 유효하지 않습니다.'}
                    return Response(data=response_message, status=status.HTTP_400_BAD_REQUEST)
            elif request.method == 'DELETE':
                photo.delete()
                response_message = {'message': '정상적으로 삭제 되었습니다.'}
                return Response(data=response_message, status=status.HTTP_200_OK)
        else:
            response_message = {'007': '사용자가 일치하지 않습니다.'}
            return Response(data=response_message, status=status.HTTP_403_FORBIDDEN)
    except Photo.DoesNotExist:
        response_message = {'004': '찾고자 하는 (사용자/게시물)가 없습니다.'}
        return Response(data=response_message, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f'error: {e}')
        response_message = {'999': '서버 에러'}
        return Response(data=response_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
