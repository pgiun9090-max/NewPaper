# 📰 나만의 신문 제작기 (Mars Tech Daily)

Gmail의 **'News'** 라벨에 수신된 뉴스레터/메일을 매일 아침 8시(전날 오전 8시 ~ 오늘 오전 8시)에 수집하고, **Playwright**를 활용하여 비정형 링크의 원문을 크롤링한 뒤 중복을 제거하여 **고품질 맞춤형 일간 신문**을 자동으로 제작하는 파이프라인 시스템입니다.

---

## 📸 제작 결과물 미리보기

첨부해주신 참조 이미지(`Image/img_1.png`, `Image/img_2.png`, `Image/img_3.png`)의 레이아웃과 디자인을 100% 동일하게 구현하였습니다.

- **헤더 영역**: 신문 이름(`Mars Tech Daily`), 날짜(`YYYY-MM-DD`), 에디션 정보(`(Mars 에디션)`), 발행인(`발행인: LeeJaeHoon`)
- **🔥 최고 주요 소식 (Hero Card)**: 둥근 모서리 카드, 상단 강조 배지, 와이드 대표 이미지, 중앙 정렬 제목 및 요약문, 출처 태그
- **주요 기사 2열 그리드 (Featured Grid)**: 2개 카드로 구성된 상단 하이라이트
- **카테고리별 2단 컬럼 (Category Columns)**: `AI/ML`, `데이터`, `보안`, `기타` 등 좌우 컬럼에 균형 배치 및 우측 정사각형 썸네일, 점선 구분선
- **반응형 웹 및 인쇄 최적화**: PC, 모바일 반응형 및 프린트/PDF 저장 대응

생성된 신문 파일: `output/newspaper_YYYY-MM-DD.html` 및 `output/index.html`

---

## 🛠️ 기술 스택 및 구조

- **Python 가상환경**: `venv` (Python 3.14 호환)
- **메일 수집**: Python 내장 `imaplib`, `email` (Gmail IMAP SSL, KST 24시간 타임존 필터링)
- **웹 크롤러**: `Playwright` (Chromium 헤드리스 브라우저를 통한 동적 웹 크롤링)
- **HTML 파서**: `BeautifulSoup4`, `lxml`
- **신문 템플릿 엔진**: `Jinja2` + `Pretendard` 웹 폰트
- **스케줄러**: `schedule` (매일 아침 08:00 KST 자동 실행)
- **설정 관리**: `python-dotenv` (`.env`)

---

## 📁 디렉토리 구조

```text
d:\NewsPaper\
├── .env                  # Gmail 계정 및 앱 비밀번호, 신문 설정
├── .env.example          # 환경 설정 예시 파일
├── requirements.txt      # 프로젝트 필요 라이브러리 목록
├── config.py             # 환경 설정 로더 및 상수
├── mail_collector.py     # Gmail IMAP 메일 수집기 (어제 08:00 ~ 오늘 08:00)
├── mail_parser.py        # 정형 데이터(본문) / 비정형 데이터(링크) 분류기
├── crawler.py            # Playwright 기반 웹 기사 크롤러
├── deduplicator.py       # URL 정규화 및 제목 유사도 기반 중복 기사 제거기
├── newspaper_generator.py# 신문 HTML 생성기 및 레이아웃 배치 엔진
├── demo_data.py          # 첨부 이미지 기반 고정밀 데모 데이터셋
├── pipeline.py           # 전체 파이프라인 통합 오케스트레이터
├── scheduler.py          # 매일 아침 08:00 자동 실행 스케줄러
├── main.py               # 실행 진입점 (CLI)
├── templates/
│   └── newspaper.html    # 참조 이미지와 100% 일치하는 신문 Jinja2 템플릿
├── Image/                # 참조 디자인 이미지 (img_1.png, img_2.png, img_3.png)
└── output/               # 제작된 일간 신문 HTML 및 프리뷰 저장소
```

---

## ⚙️ 설정 방법 (.env)

`d:\NewsPaper\.env` 파일을 열고 Gmail 정보를 입력합니다.

```env
# Gmail 계정 정보 (IMAP 접속용)
GMAIL_USER=pgiun9090@gmail.com

# Gmail 2단계 인증 후 생성한 16자리 앱 비밀번호 (공백 없이 입력)
# 생성 경로: 구글 계정(https://myaccount.google.com/) -> 보안 -> 2단계 인증 -> 앱 비밀번호
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

# 대상 Gmail 라벨 (기본값: News)
GMAIL_LABEL=News

# 신문 기본 정보
NEWSPAPER_NAME=Mars Tech Daily
NEWSPAPER_EDITION=Mars 에디션
NEWSPAPER_PUBLISHER=LeeJaeHoon

# 스케줄 시간 (매일 아침 08:00)
SCHEDULE_TIME=08:00
```

> **Google 앱 비밀번호 생성 팁**:
> 1. [구글 계정 보안 페이지](https://myaccount.google.com/security) 접속
> 2. '2단계 인증'이 활성화되어 있는지 확인
> 3. 검색창에 '앱 비밀번호' 검색 또는 [앱 비밀번호 페이지](https://myaccount.google.com/apppasswords) 접속
> 4. 앱 이름에 `NewsPaper` 입력 후 '만들기' 클릭
> 5. 생성된 16자리 비밀번호(예: `abcd efgh ijkl mnop`)를 복사하여 `.env`의 `GMAIL_APP_PASSWORD`에 넣습니다.

---

## 🚀 실행 방법

가상환경을 활성화하거나 `venv`의 파이썬 인터프리터를 사용하여 실행합니다.

### 1. 첨부 이미지와 100% 동일한 데모 신문 즉시 확인 (미리보기)
```powershell
.\venv\Scripts\python.exe main.py --demo
```
실행 시 `output/newspaper_YYYY-MM-DD.html` 파일이 생성되며, 브라우저에서 바로 열람할 수 있습니다.

### 2. Gmail 연결 및 'News' 라벨 수신 상태 점검
```powershell
.\venv\Scripts\python.exe main.py --check-mail
```
IMAP 접속 상태, 인증 성공 여부, 어제 08:00 ~ 오늘 08:00 사이 수신된 메일 건수와 제목을 확인합니다.

### 3. 오늘의 신문 즉시 제작 실행
```powershell
.\venv\Scripts\python.exe main.py --now
```
현재 시점 기준 24시간(전날 08:00 ~ 오늘 08:00) 동안 수신된 메일을 가져와 Playwright 크롤링, 중복 기사 제거 후 신문을 바로 제작합니다.

### 4. 매일 아침 08:00 자동 스케줄러 실행
```powershell
.\venv\Scripts\python.exe main.py --schedule
```
스케줄러가 백그라운드에서 상주하며, 매일 아침 08:00가 되면 자동으로 신문 제작 파이프라인을 가동합니다.

---

## 💡 주요 동작 원리

1. **정형 데이터 vs 비정형 데이터 처리**:
   - **정형 데이터**: 메일 본문 내에 기사 제목과 본문 단락이 이미 구조화된 경우, 메일 자체에서 본문과 텍스트를 그대로 가져옵니다.
   - **비정형 데이터**: 단순 링크 모음이거나 외부 원문 링크인 경우, **Playwright** 헤드리스 브라우저가 해당 페이지로 직접 이동하여 JavaScript 동적 렌더링을 거친 후 `og:title`, 메타데이터, `h1`, 대표 이미지, 본문 단락을 추출합니다.
2. **중복 기사 필터링**:
   - URL 정규화(추적 파라미터 `utm_*`, `ref` 등 제거)
   - 제목 텍스트 정규화 및 Jaccard/N-gram 형태소 유사도 비교를 통해 동일하거나 유사한 기사를 자동 제외합니다.
3. **스마트 컬럼 밸런싱**:
   - 추출된 기사들을 Hero 기사(1건), 상단 Featured 카드(2건), 그리고 카테고리별(`AI/ML`, `데이터`, `보안`, `기타`)로 분류한 후 좌우 컬럼의 높이가 완벽히 균형을 이루도록 자동 배치합니다.
