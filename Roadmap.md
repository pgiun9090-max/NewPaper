# 🗺️ Roadmap.md - 나만의 신문 제작기 (NewsPaper) 개발 및 실행 로드맵

## 1. 전체 프로젝트 마일스톤

```text
[Phase 1] 기반 파이프라인 및 레이아웃 검증 (완료 ✅)
   ├── Gmail IMAP 24시간(전날 08:00 ~ 오늘 08:00) 메일 수집기 구축
   ├── Playwright 기반 비정형 링크 웹 크롤러 구현
   ├── URL 정규화 & 유사도 기반 중복 기사 제거기 구현
   ├── 참조 이미지(Image/img_1~3.png) 100% 일치 신문 Jinja2 템플릿 제작
   └── 데모 신문 생성 및 시각적 검증 완료

[Phase 2] 지능형 LLM 큐레이션 및 구조 표준화 (현재 단계 🚀)
   ├── Step 2.1: 프로젝트 디렉토리 재구조화 (Source/ 및 Output/ 표준화)
   ├── Step 2.2: LLM(Gemini) 지능형 기사 큐레이터 모듈 (Source/llm_curator.py) 구축
   ├── Step 2.3: 이미지 유무에 따른 유연한 템플릿(Fallback) 및 2단 컬럼 고도화
   ├── Step 2.4: 전체 파이프라인 통합 및 CLI 진입점 갱신
   └── Step 2.5: 신문 산출물 최종 생성(Output/YYYY-MM-DD.html) 및 품질 검증
```

---

## 2. Phase 2 세부 실행 로드맵

### Step 2.1: 디렉토리 재구조화 (`Source/` & `Output/`)
- **목표**: 사용자 요청에 맞춰 모든 실행 및 모듈 파이썬 코드를 `Source/` 디렉토리로 이전하고, 신문 산출물을 `Output/`에 년도날짜 형식으로 저장하도록 표준화.
- **세부 태스크**:
  1. `d:/NewsPaper/Source/` 디렉토리 생성.
  2. 기존 파이썬 스크립트들을 `Source/`로 이동:
     - `config.py`, `mail_collector.py`, `mail_parser.py`, `crawler.py`, `deduplicator.py`, `newspaper_generator.py`, `demo_data.py`, `pipeline.py`, `scheduler.py`, `main.py`
  3. 모듈 내 경로(`BASE_DIR`, `.env` 경로, `templates` 경로, `Output` 경로)가 `Source/` 구조에 맞도록 `config.py` 업데이트.
  4. 루트 실행 래퍼(`main.py`) 또는 `python Source/main.py` 실행 환경 구성.
  5. 기존 `output/`을 `Output/`으로 통일하고 `.gitignore` 규칙 갱신.

### Step 2.2: LLM 기반 지능형 기사 큐레이터 모듈 구축 (`Source/llm_curator.py`)
- **목표**: Gemini API(`GEMINI_API_KEY`)를 연동하여 기사 중요도 평가, 헤드라인 선별, 3줄 요약, 카테고리 자동 분류 구현.
- **세부 태스크**:
  1. `google-genai` 또는 Gemini REST/SDK 연동 환경 점검 및 라이브러리 추가(`requirements.txt`).
  2. 프롬프트 엔지니어링:
     - **중요도 평가**: 당일 파급력, 사회적/기술적 영향도, 언급 빈도를 종합하여 점수 산정.
     - **헤드라인 선별**: 최고 점수 1건을 **메인 헤드라인(1단)**으로, 차순위 2건을 **부 헤드라인(2단)**으로 자동 배정.
     - **본문 요약**: 나머지 기사들에 대해 신문 가독성에 맞춘 명확하고 간결한 3줄 요약문 생성.
     - **카테고리 분류**: `AI/ML`, `데이터`, `보안`, `기타` 등 테마별 자동 분류.
  3. **폴백(Fallback) 안전장치**:
     - API 키 미설정, 네트워크 지연, API 할당량 초과 시 Rule-based(키워드 빈도, 본문 길이, 이미지 유무 등) 알고리즘으로 자동 전환하여 파이프라인 무중단 보장.

### Step 2.3: 이미지 유무에 따른 유연한 템플릿 및 레이아웃 고도화
- **목표**: 이미지가 있는 기사와 없는 기사 모두 정갈하게 보이도록 템플릿과 CSS 고도화.
- **세부 태스크**:
  1. `templates/newspaper.html` 점검:
     - 메인 헤드라인 (1단 와이드): 이미지가 있으면 와이드 배너, 없으면 큰 볼드 타이포그래피 + 인용구 형태로 자연스럽게 표시.
     - 부 헤드라인 (2단 그리드): 이미지 없을 시 깔끔한 배경 카드 스타일 적용.
     - 일반 기사 리스트: 우측 썸네일이 없을 때 텍스트가 자연스럽게 전체 너비를 채우도록 flex 레이아웃 최적화.
  2. 로딩 오류 방지: `onerror` 처리로 깨진 이미지 아이콘 노출 방지.

### Step 2.4: 전체 파이프라인 통합 및 CLI 갱신
- **목표**: `Source/pipeline.py`와 `Source/main.py`에 변경된 모듈 및 디렉토리 구조 반영.
- **세부 태스크**:
  1. 파이프라인 흐름:
     `Gmail 수집` ➡️ `정형/비정형 파싱` ➡️ `Playwright 크롤링` ➡️ `중복 제거` ➡️ `LLM 큐레이션 및 요약` ➡️ `신문 HTML 렌더링`
  2. 산출물 파일명: `Output/YYYY-MM-DD.html` (예: `Output/2026-10-19.html`)로 생성.
  3. CLI 명령어 정리:
     - `python Source/main.py --demo`
     - `python Source/main.py --now`
     - `python Source/main.py --schedule`
     - `python Source/main.py --check-mail`

### Step 2.5: 최종 검증 및 산출물 확인
- **목표**: 2단계 전체 시스템 구동 및 최종 신문 생성 결과 검증.
- **세부 태스크**:
  1. 데모 데이터 및 실전 모드 파이프라인 실행 테스트.
  2. `Output/`에 생성된 일간 신문 HTML 브라우저 렌더링 및 스크린샷 검증.
  3. 참조 이미지와 최종 신문의 시각적 싱크 100% 일치 확인.

---

## 3. 완료 기준 (Definition of Done, DoD)
- [ ] `Source/` 폴더 내에 모든 파이썬 모듈이 체계적으로 분리 및 배치되어 정상 동작할 것.
- [ ] `Output/` 디렉토리에 년도날짜 형식(예: `Output/2026-10-19.html`)으로 완성도 높은 신문 HTML이 생성될 것.
- [ ] LLM(Gemini) 또는 폴백 알고리즘을 통해 **메인 헤드라인 1개(1단)**와 **부 헤드라인 2개(2단)**가 정확히 선별되고, 나머지 기사가 3줄 요약 및 카테고리별 2단 컬럼으로 배치될 것.
- [ ] 이미지가 없는 기사도 레이아웃이 깨지지 않고 자연스럽게 렌더링될 것.
- [ ] CLI 명령어(`--demo`, `--now`, `--schedule`, `--check-mail`)가 오류 없이 실행될 것.
