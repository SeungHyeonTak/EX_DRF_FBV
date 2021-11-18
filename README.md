

**mac os 기준의 내용**

[기본 설정 내용 보기](https://github.com/SeungHyeonTak/DRF_example_basic_project/blob/master/README.md)

## 참고 사항

**함수형 뷰(FBV)로 작성됨**

혹시 가상환경 세팅에 있어서 잘 안되면 프로젝트 내용에 `.python-version` 파일을 지우고 다시 설정해보자.

secret_key.json은 빠져 있기때문에 따로 넣어야함

어떤 key가 들어갔는지는 아래 코드로 기록

```json
{
  "SECRET_KEY": "..."
}
```

코드 관리를 위해서 git branch를 따로 파서 작성하는 식으로 연습하자.

branch 목록

- master
- develop
- hotfix/<작업할 내용(간단히 적기)>
- feature/<작업할 내용(간단히 적기)>

**feature branch에 대해서는 작성하고 제거 해주자**

## Project 실행방법 / docker container 실행방법

기존에 프로젝트를 실행하려면 `./manage.py runserver` 를 하면 실행가능했지만, 
local, prod 로 서버 환경을 나누다 보니 각각에 맞게 runserver를 돌려주어야 한다.

### requirements install

```
$ pip install -r requirements.txt
```

### local runserver

```
$ ./manage.py runserver 8000 --settings=config.settings.local
```

### prod runserver (따로 배포 하진 않음)

```
$ ./manage.py runserver 8000 --settings=config.settings.prod
```

---
### docker image 생성

```
$ docker build -t <사용할 이름> .
```

### docker container 생성

```
$ docker run -it -p 8000:8000 --volume $(PWD):/config --name <docker container 이름> <docker image 이름>
```

**컨테이너 끄고 켜기**

켜기

```
$ docker start -i <docker image 이름>
```

끄기

```
$ docker stop <docker image 이름>
```

---

도움되었다면 위에 star 한번만 클릭해주세요 :)
