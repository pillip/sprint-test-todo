# Todo List 웹 애플리케이션 — PRD

## 1. 개요

카테고리 기반 할 일 관리 웹 애플리케이션. FastAPI 백엔드 + SQLite DB + 단일 페이지 프론트엔드(HTML/CSS/JS)로 구성된 풀스택 Todo 앱.

## 2. 기술 스택

- **백엔드**: Python 3.11+, FastAPI, Uvicorn
- **데이터베이스**: SQLite (aiosqlite)
- **프론트엔드**: Vanilla HTML/CSS/JavaScript (별도 프레임워크 없음)
- **패키지 관리**: uv
- **테스트**: pytest + httpx (AsyncClient)

## 3. 기능 요구사항 (Functional Requirements)

### FR-1: Todo CRUD API

FastAPI REST API로 할 일의 생성(Create), 조회(Read), 수정(Update), 삭제(Delete)를 처리한다.

- `POST /api/todos` — 새 할 일 생성
- `GET /api/todos` — 전체 목록 조회 (쿼리 파라미터로 필터링)
- `GET /api/todos/{id}` — 단건 조회
- `PUT /api/todos/{id}` — 수정
- `DELETE /api/todos/{id}` — 삭제

### FR-2: Todo 데이터 모델

각 Todo 항목은 다음 필드를 가진다:

- `id` (int, auto-increment)
- `title` (string, 필수, 최대 200자)
- `description` (string, 선택, 최대 1000자)
- `category` (string, 필수 — "work", "personal", "shopping", "health" 중 택 1)
- `is_completed` (boolean, 기본값 false)
- `created_at` (datetime, 자동 생성)
- `updated_at` (datetime, 자동 갱신)

### FR-3: 카테고리 필터링

- `GET /api/todos?category=work` — 특정 카테고리의 할 일만 조회
- `GET /api/todos?is_completed=true` — 완료/미완료 필터

### FR-4: 프론트엔드 — Todo 목록 표시

단일 HTML 페이지에서 모든 할 일을 목록으로 표시한다.

- 각 항목에 제목, 카테고리 뱃지, 완료 상태 표시
- 완료된 항목은 취소선 스타일로 구분
- 빈 목록일 때 안내 메시지 표시

### FR-5: 프론트엔드 — Todo 추가 폼

- 제목, 설명, 카테고리를 입력할 수 있는 폼
- 제목 미입력 시 클라이언트 사이드 유효성 검증
- 추가 후 목록 자동 갱신

### FR-6: 프론트엔드 — 완료 토글 & 삭제

- 체크박스 클릭으로 완료/미완료 토글
- 삭제 버튼 클릭 시 확인 후 삭제
- 낙관적 UI 업데이트 (API 응답 전 즉시 반영)

### FR-7: 프론트엔드 — 카테고리 필터 탭

- 상단에 "전체 / Work / Personal / Shopping / Health" 탭 표시
- 탭 클릭 시 해당 카테고리만 필터링하여 표시
- 현재 선택된 탭 하이라이트

### FR-8: 정적 파일 서빙

- FastAPI의 `StaticFiles`로 프론트엔드 파일 서빙
- `GET /` 접속 시 `index.html` 반환

## 4. 비기능 요구사항 (Non-Functional Requirements)

### NFR-1: 반응형 디자인

- 모바일(360px)부터 데스크톱(1200px)까지 반응형 레이아웃
- CSS Grid 또는 Flexbox 활용

### NFR-2: API 에러 처리

- 존재하지 않는 Todo 접근 시 404 응답
- 유효성 검증 실패 시 422 응답과 명확한 에러 메시지
- 서버 에러 시 500 응답

### NFR-3: 데이터베이스 초기화

- 앱 시작 시 SQLite 테이블 자동 생성 (CREATE IF NOT EXISTS)
- DB 파일 경로 환경변수로 설정 가능 (`DATABASE_URL`)

## 5. 프로젝트 구조 (목표)

```
sprint-test-todo/
├── src/
│   ├── main.py          # FastAPI 앱 + 라우터
│   ├── database.py      # SQLite 연결 & 테이블 초기화
│   ├── models.py        # Pydantic 스키마
│   └── crud.py          # DB CRUD 함수
├── static/
│   ├── index.html       # 메인 페이지
│   ├── style.css        # 스타일시트
│   └── app.js           # 프론트엔드 로직
├── tests/
│   ├── test_api.py      # API 엔드포인트 테스트
│   └── test_crud.py     # CRUD 함수 단위 테스트
├── PRD.md
├── pyproject.toml
└── .gitignore
```

## 6. 실행 방법

```bash
uv sync
uv run uvicorn src.main:app --reload
# 브라우저에서 http://localhost:8000 접속
```
