"""
Demo Data based directly on Image/img_1.png, Image/img_2.png, Image/img_3.png.
Provides test articles perfectly matching the reference newspaper images.
"""

DEMO_ARTICLES = [
    # Hero Article
    {
        "title": "제미니 4 아르곤 대 GPT-6 아스트라 대 클로드 오푸스 5.5",
        "content": "구글의 차세대 프론티어 AI 모델 '제미니 4 아르곤'이 벤치마크 주요 지표에서 GPT-6 아스트라와 클로드 오푸스 5.5를 제쳤습니다. 아르곤은 주요 코딩 및 에이전트 평가 등 다수 항목에서 선두를 차지했으나 현재는 제한된 사용자에게만 제공됩니다. 제3자 평가 기관 및 내부 테스트에서는 벤치마크 대비 성능 격차가 작거나 환각률 차이가 존재하는 등 다양한 결과가 보고되었습니다. 전문가들은 단일 최고 모델에 의존하기보다 작업 특성에 맞춘 모델 라우팅 전략이 중요하다고 강조합니다.",
        "image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=1200&q=80",
        "source": "LeeJaeHoon",
        "category": "AI/ML",
        "url": ""
    },
    # Featured Article 1
    {
        "title": "“가장 싼 걸로 갈아타줘”…AI 에이전트와 ‘귀찮음 경제’의 종말 [딥다이브]",
        "content": "메타의 뮤즈와 오픈AI의 닷츠 등 최저가 검색 및 자동 결제를 수행하는 상시 작동형 AI 에이전트가 출시되어 큰 주목을 받고 있습니다. AI 에이전트가 이용자를 대신해 최고 금리 계좌로 현금을 옮기거나 최저가 상품을 직구하면서 기존 플랫폼 중개업체들이 위기에 직면했습니다. 미국 금융권에서는 예금 이탈을 우려하는 '에이전틱 뱅크런' 가능성이 제기되며 주가가 하락하는 파장이 일어났습니다. 소비자의 번거로움을 해결해 주는 AI 비서 서비스가 플랫폼과 금융 시장의 생태계를 근본적으로 바꿀 전망입니다.",
        "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80",
        "source": "LeeJaeHoon",
        "category": "AI/ML",
        "url": ""
    },
    # Featured Article 2
    {
        "title": "클로드 오푸스 5.5 최적 활용 및 프롬프트 가이드",
        "content": "클로드 오푸스 5.5는 자율적인 장기 다단계 작업 수행 능력이 대폭 향상되어 전체 작업과 중단 조건을 한 번에 전달하는 방식이 유효합니다. 스스로 추론을 진행하므로 불필요한 사고 지시는 생략하고 Claude Code의 effort 설정으로 사고량을 제어하는 것이 좋습니다. 대규모 코드베이스 작업 시에는 서브에이전트 분업과 TASKS.md 파일 기반의 작업 목록 관리가 권장됩니다. 최종 실행 결과는 변경 사항과 미확인 항목을 명확히 검증하도록 설정하여 위험을 줄일 수 있습니다.",
        "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80",
        "source": "LeeJaeHoon",
        "category": "AI/ML",
        "url": ""
    },
    # Left Column Articles (AI/ML)
    {
        "title": "챗GPT, 가상 피팅 기능 도입…AI 쇼핑 경험 확장 - (주)더블유더블유디코리아",
        "content": "오픈AI가 챗GPT에 '이미지 2.5' 업데이트를 적용하여 가상 피팅 및 상품 저장 기능을 새롭게 추가했다. 사용자는 자신의 사진을 업로드해 스타일을 미리 적용해볼 수 있으며, 향상된 조명과 질감 표현으로 완성도 높은 이미지를 제공받는다. 주간 이용자 12억 명을 보유한 챗GPT의 이러한 기능 도입은 AI 기반 리테일 유입 사용자의 구매 전환율 향상 흐름과 맞물려 커머스 시장에 큰 파급력을 미칠 것으로 예상된다.",
        "image_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=300&q=80",
        "source": "LeeJaeHoon",
        "category": "AI/ML",
        "url": ""
    },
    {
        "title": "MS, 실시간 전사·음성합성 AI 모델 3종 공개",
        "content": "마이크로소프트가 실시간 음성 전사 모델 1종과 음성합성 모델 2종을 포함한 신규 AI 모델을 공개했다. 핵심인 'MAI-Transcribe-2-Streaming'은 320밀리초 내에 첫 전사 결과를 제공하며 60개 이상의 언어를 지원한다. MS는 해당 모델들을 팀즈, 코파일럿 등 자사 서비스에 적용하는 한편 경쟁사 대비 저렴한 가격으로 개발자들에게 공급할 방침이다.",
        "image_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=300&q=80",
        "source": "LeeJaeHoon",
        "category": "AI/ML",
        "url": ""
    },
    {
        "title": "AI '순환 깊이' 기술 도입…안전성 모니터링 무력화 우려",
        "content": "차세대 AI 추론 기술인 '순환 깊이 트랜스포머'의 도입으로 모델의 내적 추론 과정이 암호화된 벡터 형태로 진행되면서 기존 사고 사슬(CoT) 모니터링 체계가 한계에 봉착했다. 인간 언어로 사고 과정을 표출하지 않는 '연속 사고의 사슬' 방식은 모델의 악성 행동이나 정당화 편법을 사전 감지하기 어렵게 만든다. 오픈AI와 앤트로픽 등 주요 연구진은 AI의 불투명성 증대에 따른 안전성 훼손을 경고하며 통제력 강화를 요구하고 있다.",
        "image_url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=300&q=80",
        "source": "LeeJaeHoon",
        "category": "AI/ML",
        "url": ""
    },
    {
        "title": "메타, 오픈소스 '뮤즈 가젯' 공개…하드웨어 생태계 확장",
        "content": "메타가 AI 에이전트 '뮤즈'를 소형 기기 및 스마트홈 장치와 연동할 수 있는 오픈소스 플랫폼 '뮤즈 가젯'을 공개했다. 개발자는 ESP32 보드용 펌웨어와 리눅스 SDK를 활용해 소형 컴퓨터나 센서, 디스플레이 등 다양한 하드웨어에 뮤즈를 직접 연결할 수 있다. 이와 함께 전용 스마트홈 연결 장치인 '뮤즈 홈 링크'를 함께 선보이며 하드웨어 플랫폼 영역으로의 생태계 확장을 본격화했다.",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=300&q=80",
        "source": "LeeJaeHoon",
        "category": "AI/ML",
        "url": ""
    },
    {
        "title": "맥북 덮개 닫아도 Claude Code 계속 실행하는 클라우드 세션",
        "content": "맥북 등 노트북의 덮개를 닫으면 잠자기 모드로 진입해 AI 작업이 정지되는 불편함이 존재합니다. 이를 해결하기 위해 노트북을 깨워 두는 플러그인이 공유되고 있으나 공식적인 안전성은 보장되지 않습니다. 가장 확실한 해결책은 노트북이 아닌 Anthropic 서버에서 실행되는 Claude Code 클라우드 세션을 이용하는 것입니다. Pro 및 Max 구독자는 별도 서버 비용 없이 클라우드 세션을 통해 24시간 안정적인 AI 작업을 유지할 수 있습니다.",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=300&q=80",
        "source": "LeeJaeHoon",
        "category": "AI/ML",
        "url": ""
    },
    # Right Column Articles
    {
        "title": "뉴로메카·KAIST, 손목 카메라 없는 휴머노이드 정밀조작 AI 개발",
        "content": "뉴로메카와 KAIST 연구팀이 손목 카메라 없이 머리 단일 RGB 카메라만으로 로봇을 정밀 제어하는 피지컬 AI 기술(SCDP)을 개발했습니다. 예상 이동 경로의 시각 정보를 선택적으로 추출하는 방식으로 복잡한 하드웨어 및 케이블 간섭 문제를 극복했습니다. 휴머노이드 로봇 '에이르'에 적용한 결과 겹쳐진 종이컵 분리와 고난도 정밀 조작 작업을 손목 카메라 방식보다 높은 성공률로 수행했습니다. 관련 연구 논문은 국제 로봇학습 학술대회 CoRL 2026에 채택되며 기술력을 입증받았습니다.",
        "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=300&q=80",
        "source": "LeeJaeHoon",
        "category": "AI/ML",
        "url": ""
    },
    {
        "title": "스탠퍼드·엔비디아, 판단 전용 AI 'CLM-8B' 공개",
        "content": "스탠퍼드대와 엔비디아 연구진이 의사결정 및 도구 선택에 특화된 오픈소스 AI 모델 'CLM-8B'를 공개했습니다. 이 모델은 대조학습 기반으로 행동 표현을 캐시하여 구글 공룡 게임 테스트에서 기존 경쟁 AI '제미니(Jev)'보다 9배 빠른 16밀리초의 지연시간을 기록했습니다. 특정 벤치마크 정확도에서는 한계를 보였으나, 텍스트 생성 대신 저렴하고 빠른 검증 및 모니터링 레이어로 활용 가능합니다. 가중치와 코드는 아파치 2.0 라이선스로 공개되어 의사결정 특화 AI 시장 경쟁이 본격화될 전망입니다.",
        "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=300&q=80",
        "source": "LeeJaeHoon",
        "category": "AI/ML",
        "url": ""
    },
    {
        "title": "호주, 유학생 비자 제한 조치 본격 시행",
        "content": "호주 정부가 편법 이민 억제 및 이주자 수 감축을 위해 학생 비자 및 가디언 비자 개정 규정 시행에 들어갔다. 새 규정에 따르면 유학생의 과정 변경 시 신규 비자 신청이 필요하며, 낮은 학위로의 전환 및 대부분의 가족 동반 입국이 금지된다. 유학 산업계의 인력난 우려에 대응해 호주 정부는 보건, 건설 등 필수 산업 직종 위주로 기술 이민 우선순위를 조정했다.",
        "image_url": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=300&q=80",
        "source": "LeeJaeHoon",
        "category": "기타",
        "url": ""
    },
    {
        "title": "벡터 데이터베이스여, 안녕 | GeekNews",
        "content": "벡터 데이터베이스 turbopuffer가 v3 개편을 통해 문서와 벡터 인덱스의 배치를 분리하는 저장 구조 개편을 추진 중입니다. 기존에는 ANN 인덱스가 기본 저장 기준이었으나, 이로 인해 비벡터 쿼리 실행 시 저장 및 쓰기 증폭이 크게 발생하는 한계가 있었습니다. v3는 문서 저장소를 분리하여 속성 필터링과 전문 검색, 집계 쿼리 성능을 최적화하고 인덱스 크기와 쿼리 시간을 대폭 단축했습니다. 이를 통해 단순 벡터 검색을 넘어 확장된 SQL 및 데이터 처리가 가능한 저장 엔진으로 진화하고 있습니다.",
        "image_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=300&q=80",
        "source": "LeeJaeHoon",
        "category": "데이터",
        "url": ""
    },
    {
        "title": "리눅스 커널, LLM 취약점 보고서 검증과 보안 대응책 발표",
        "content": "리눅스 커널 유지관리팀이 대규모 언어 모델(LLM)을 활용한 자동 취약점 보고서의 허위 경보 비율을 줄이고 실제 보안 위협을 선별하는 신규 검증 프레임워크를 발표했습니다. 정적 분석 도구와 결합된 다단계 감사 절차를 통해 커널 보안 패치 주기를 단축하고 잠재적 공격 경로를 사전에 차단하는 방안이 포함되었습니다.",
        "image_url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=300&q=80",
        "source": "LeeJaeHoon",
        "category": "보안",
        "url": ""
    }
]
