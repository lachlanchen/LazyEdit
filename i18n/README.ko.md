<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

<p>
  <b>Languages:</b>
  <a href="../README.md">English</a>
  · <a href="README.zh-Hant.md">中文（繁體）</a>
  · <a href="README.zh-Hans.md">中文 (简体)</a>
  · <a href="README.ja.md">日本語</a>
  · <a href="README.ko.md">한국어</a>
  · <a href="README.vi.md">Tiếng Việt</a>
  · <a href="README.ar.md">العربية</a>
  · <a href="README.fr.md">Français</a>
  · <a href="README.es.md">Español</a>
</p>

# LazyEdit

LazyEdit는 AI 기반 자동 영상 편집 도구입니다. 전문 수준의 자막, 하이라이트, 단어 카드, 메타데이터를 자동으로 생성해 번거로운 편집 과정을 효율화합니다.

## 주요 기능

- **자동 전사**: AI로 오디오를 자동 전사
- **자동 캡션**: 영상 내용을 설명하는 캡션 생성
- **자동 자막**: 자막 생성 및 영상에 직접 삽입
- **자동 하이라이트**: 재생 중 핵심 단어 강조
- **자동 메타데이터**: 영상에서 메타데이터 추출/생성
- **단어 카드**: 언어 학습용 단어 카드 추가
- **티저 생성**: 핵심 구간을 반복해 티저 구성
- **다국어 지원**: 영어/중국어 등 다양한 언어 지원
- **커버 이미지 생성**: 최적의 커버 이미지 추출 및 텍스트 오버레이

## 설치

### 사전 요구 사항

- Python 3.10 이상
- FFmpeg
- CUDA 지원 GPU(전사 가속)
- Conda 환경 관리자

### 설치 방법

1. 저장소 클론:
   ```bash
   git clone <repository_url>
   cd lazyedit
   ```

2. 설치 스크립트 실행:
   ```bash
   chmod +x install_lazyedit.sh
   ./install_lazyedit.sh
   ```

설치 스크립트는 다음을 수행합니다:
- 필수 시스템 패키지 설치(ffmpeg, tmux)
- "lazyedit" conda 환경 생성 및 설정
- 자동 시작용 systemd 서비스 설정
- 필요한 권한 설정

## 사용 방법

LazyEdit는 웹 앱으로 동작하며 http://localhost:8081 에서 접근할 수 있습니다.

### 영상 처리 흐름

1. 웹 인터페이스에서 영상 업로드
2. LazyEdit가 자동으로 다음을 수행:
   - 전사 및 캡션 생성
   - 메타데이터와 학습 콘텐츠 생성
   - 감지된 언어의 자막 생성
   - 중요 단어 하이라이트
   - 티저 생성
   - 커버 이미지 생성
   - 결과 패키징 및 반환

### 커맨드라인 사용

아래처럼 직접 실행할 수 있습니다:

```bash
conda activate lazyedit
cd /path/to/lazyedit
python app.py -m lazyedit
```

## 프로젝트 구조

- `app.py` - 메인 애플리케이션 엔트리
- `lazyedit/` - 핵심 모듈 디렉터리
  - `autocut_processor.py` - 영상 분할 및 전사
  - `subtitle_metadata.py` - 자막 기반 메타데이터 생성
  - `subtitle_translate.py` - 자막 번역
  - `video_captioner.py` - 영상 캡션 생성
  - `words_card.py` - 단어 카드 생성
  - `utils.py` - 유틸리티 함수
  - `openai_version_check.py` - OpenAI API 호환 레이어

## 설정

systemd 서비스 설정은 `/etc/systemd/system/lazyedit.service`에 생성됩니다.

LazyEdit는 "lazyedit" 이름의 tmux 세션으로 실행되어 백그라운드에서 계속 동작합니다.

## 서비스 관리

- 시작: `sudo systemctl start lazyedit.service`
- 중지: `sudo systemctl stop lazyedit.service`
- 상태 확인: `sudo systemctl status lazyedit.service`
- 로그 확인: `sudo journalctl -u lazyedit.service`

## 고급 사용

다음 항목을 커스터마이즈할 수 있습니다:
- 티저 길이와 위치
- 단어 하이라이트 스타일
- 자막 폰트 및 위치
- 출력 폴더 구조
- GPU 선택

## 문제 해결

- 앱이 시작되지 않으면 systemd 상태와 로그 확인
- 처리 실패 시 FFmpeg 설치 여부 확인
- GPU 관련 문제는 CUDA 및 GPU 상태 확인
- conda 환경이 올바르게 활성화되었는지 확인

## 라이선스

[라이선스를 여기에 기입]

## 감사의 말

LazyEdit는 다음 오픈소스 도구를 사용합니다:
- FFmpeg (영상 처리)
- OpenAI 모델 (AI 기능)
- Tornado 웹 프레임워크
- MoviePy (영상 편집)
- CJKWrap (다국어 텍스트 처리)
