from drf_yasg import openapi


class ErrorControlloer(object):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def get_error_code(self):
        return self.code

    def get_error_description(self):
        return openapi.Schema(
            self.message,
            default=self.message,
            type=openapi.TYPE_STRING
        )


APPLY_400_NO_REQUIRED_PARAMETERS = ErrorControlloer(
    code='000',
    message='필수파라미터가 없습니다.'
)

APPLY_400_VALUE_NOT_VALID = ErrorControlloer(
    code='002',
    message='값이 유효하지 않습니다.'
)

APPLY_400_BAD_REQUEST = ErrorControlloer(
    code='006',
    message='잘못된 요청입니다.'
)

APPLY_401_UNAUTHORIZED = ErrorControlloer(
    code='005',
    message='자격 인증데이터가 제공되지 않았습니다.'
)

APPLY_403_FORBIDDEN = ErrorControlloer(
    code='003',
    message='자격 인증 데이터(JWT)가 조회되지 않습니다.'
)

APPLY_403_USER_DOES_NOT_MATCH = ErrorControlloer(
    code='007',
    message='사용자가 일치하지 않습니다.'
)

APPLY_404_NOT_FOUND = ErrorControlloer(
    code='004',
    message='찾고자 하는 (사용자/게시물)가 없습니다.'
)

APPLY_409_EMAIL_IS_NOT_VALID = ErrorControlloer(
    code='001',
    message='해당 email로 가입된 사용자가 있습니다.'
)

APPLY_500_SERVER_ERROR = ErrorControlloer(
    code='999',
    message='서버 에러'
)
