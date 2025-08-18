# my_social_feed
# 🏭 My Social Feed - 팩토리 모니터링 통합 소셜 플랫폼
# https://mysocial.streamlit.app/

## 📖 프로젝트 개요

일반적인 소셜 미디어 기능에 **실시간 팩토리 모니터링 시스템**이 통합된 웹 애플리케이션입니다. 사용자들은 일반적인 소셜 활동을 하면서 동시에 팩토리의 실시간 상태를 모니터링할 수 있습니다.

## ✨ 주요 기능

### 📱 소셜 미디어 기능
- **회원가입/로그인** - 사용자 계정 관리
- **게시물 작성** - 텍스트, 이미지, 데이터 차트 포스트
- **좋아요/리포스트** - 소셜 인터랙션
- **팔로우 시스템** - 사용자 간 팔로우/언팔로우
- **프로필 관리** - 이모지 프로필, 비밀번호 변경

### 🏭 팩토리 모니터링 기능
- **실시간 상태 추적** - 온도, 압력, RPM, 생산량
- **3단계 알림 시스템** - 정상(🟢) / 경고(🟡) / 위험(🔴)
- **시각적 대시보드** - 실시간 차트 및 메트릭
- **자동 알림** - 이상 상황 발생시 소셜 피드에 자동 포스팅

### 🔗 통합 시스템
- **소셜 피드 통합** - 팩토리 알림이 일반 포스트와 함께 표시
- **실시간 차트** - 팩토리 데이터를 소셜 포스트에 차트로 표시
- **우선순위 알림** - 긴급 상황시 피드 상단에 우선 표시

## 🗂️ 파일 구조

```
📁 my_social_feed/
├── 📄 app.py                    # 메인 애플리케이션
├── 📄 auth.py                   # 사용자 인증 관리
├── 📄 post.py                   # 게시물 관리
├── 📄 sidebar.py                # 사이드바 네비게이션
├── 📄 follow.py                 # 팔로우 시스템
├── 📄 sim_factory.py            # 팩토리 시뮬레이션 엔진
├── 📄 factory_manager.py        # 팩토리 데이터 관리
├── 📄 factory_dashboard.py      # 팩토리 대시보드 UI
├── 📄 factory_integration.py    # 소셜-팩토리 통합
├── 📄 enhanced_post_display.py  # 향상된 포스트 표시
├── 📄 scheduler.py              # 자동 모니터링 (선택)
└── 📁 post_images/              # 업로드된 이미지
```

## 📊 데이터 저장

### CSV 파일 기반 데이터베이스
- **users.csv** - 사용자 정보 (ID, 사용자명, 비밀번호, 프로필 이모지)
- **posts.csv** - 게시물 (ID, 작성자, 내용, 좋아요 수, 리포스트 수)
- **likes.csv** - 좋아요 데이터 (좋아요 ID, 게시물 ID, 사용자)
- **followers.csv** - 팔로우 관계 (팔로워 ID, 팔로잉 ID)
- **factories.csv** - 팩토리 정보 (ID, 이름, 위치, 마지막 상태)
- **factory_posts.csv** - 팩토리 알림 포스트

## 🚀 실행 방법

### 1. 의존성 설치
```bash
pip install streamlit pandas numpy matplotlib pillow
```

### 2. 애플리케이션 실행
```bash
streamlit run app.py
```

### 3. 웹 브라우저에서 접속
- 로컬
- 자동으로 브라우저가 열립니다

## 🎮 사용법

### 기본 사용 흐름
1. **회원가입** 또는 **로그인**
2. **홈 화면**에서 일반 포스트 작성 및 확인
3. **🏭 팩토리 대시보드**에서 팩토리 추가 및 관리
4. **상태 업데이트** 버튼으로 실시간 모니터링
5. **소셜 피드 동기화**로 팩토리 알림을 소셜 피드에 통합

### 팩토리 관리
```python
# 새 팩토리 추가
factory_id = factory_manager.add_factory("서울공장", "서울시 강남구")

# 상태 업데이트 (정상 상황)
status = factory_manager.update_factory_status(factory_id)

# 강제 이상 상황 테스트
status = factory_manager.update_factory_status(factory_id, force_abnormal=True)
```

## 🎯 핵심 컴포넌트

### FactoryManager 클래스
```python
class FactoryManager:
    def add_factory(name, location)          # 팩토리 추가
    def update_factory_status(id, force)     # 상태 업데이트  
    def get_factory_summary()                # 전체 현황 요약
    def get_factory_feed(limit)              # 팩토리 알림 피드
```

### 상태 분류 시스템
- **🟢 정상 (normal)** - 모든 수치가 정상 범위
- **🟡 경고 (warning)** - 압력 부족, RPM 이상
- **🔴 위험 (critical)** - 과열 상황 (220°C 이상)

### 알림 임계값
- **온도**: 220°C 이상 → 🔥 과열 경고
- **압력**: 120bar 미만 → ⚠️ 압력 부족
- **RPM**: 35rpm 미만 → ⚙️ 속도 이상

## 🛠️ 기술 스택

### Frontend
- **Streamlit** - 웹 애플리케이션 프레임워크
- **Matplotlib** - 차트 및 그래프 생성
- **CSS/HTML** - 사용자 정의 스타일링

### Backend
- **Python 3.x** - 메인 프로그래밍 언어
- **Pandas** - 데이터 처리 및 분석
- **NumPy** - 수치 계산

### Data Storage
- **CSV Files** - 경량 데이터베이스
- **Local File System** - 이미지 저장

## 🔧 확장 가능한 아키텍처

### 모듈별 역할
- **sim_factory.py** - 팩토리 시뮬레이션 로직
- **factory_manager.py** - 비즈니스 로직 및 데이터 관리
- **factory_dashboard.py** - UI 컴포넌트
- **factory_integration.py** - 시스템 간 통합

### 새로운 팩토리 타입 추가
```python
class AdvancedFactory(Sim_Factory):
    def __init__(self, name, factory_type="advanced"):
        super().__init__(name)
        self.additional_sensors = {...}
```


### 건강도 점수 시스템
- **90-100점**: 정상 운영
- **70-89점**: 주의 필요
- **30-69점**: 경고 상태
- **0-29점**: 위험 상태

## 🎨 사용자 인터페이스
- **데스크톱** - 멀티 컬럼 레이아웃


### 시각적 요소
- **상태별 색상 코딩** - 직관적인 상태 인식
- **실시간 메트릭** - 수치 변화 시각화
- **인터랙티브 차트** - 사용자 친화적 데이터 표시

## 🚨 알림 시스템

### 3단계 알림 체계
1. **정보성 알림** - 정상 상태 업데이트
2. **주의 알림** - 수치 이상 감지
3. **긴급 알림** - 즉시 조치 필요

### 소셜 피드 통합
- **시스템 사용자** (`🏭_Factory_System`)를 통한 자동 포스팅
- **우선순위 표시** - 긴급 상황은 피드 상단 고정
- **차트 데이터** - 실시간 상태를 시각적으로 표시

## 🔒 보안 및 데이터 관리

### 사용자 인증
- **세션 기반** 로그인 상태 관리
- **비밀번호 평문 저장** (데모용 - 실제 운영시 해싱 권장)

### 데이터 무결성
- **CSV 백업** 자동 생성
- **중복 포스트 방지** 시스템
- **데이터 유효성 검증**

## 📚 추가 정보

### 트러블슈팅
- **한글 폰트 오류** - matplotlib 폰트 설정 필요
- **JSON 직렬화 오류** - datetime 객체 처리
- **모듈 import 오류** - 파일 경로 및 이름 확인

---