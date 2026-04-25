# 게임 대회 팀원 경매 시스템 (초안)

이 저장소는 **게임 API/로그 접근이 불가능한 대회 운영진 환경**을 전제로 한 팀원 경매 시스템의
초기 설계 및 가격 산정 엔진(프로토타입)을 포함합니다.

## 핵심 목표
- 여러 게임에서 재사용 가능한 경매 플랫폼
- AI 연동 시 AI 기반 초기 가격 산정 + 운영진 최종 확정
- AI 미연동 시 지정 알고리즘 기반 가격 산정
- 운영자의 경매 시작 승인 전/후에 따라 관객 화면 노출을 제어하는 웹 인터페이스
- 팀별 최대 예산(상한) 일괄 설정
- 모든 경매/입찰/대회 데이터를 저장하고, 이전 대회 데이터 재참조 가능
- 관람 요소(실시간 보드/통계) 및 재미 요소(이벤트 카드, MVP 보너스 등) 확장 가능

## 구성
- `docs/auction_system_design.md` : 요구사항 반영 설계 문서
- `src/auction_pricing.py` : AI/비AI 가격 산정 엔진 프로토타입
- `src/spectator_web.py` : 운영진 승인 기반 관객 웹 인터페이스(WSGI)
- `src/schema.sql` : 데이터 저장을 위한 기본 스키마
- `tests/test_pricing.py` : 가격 산정 단위 테스트
- `tests/test_spectator_web.py` : 관객 웹 노출 제어 테스트

## 빠른 실행
```bash
python -m unittest discover -s tests
```

## 관객 웹 인터페이스 실행 예시(표준 라이브러리만 사용)
```bash
python - <<'PY'
from wsgiref.simple_server import make_server
from src.spectator_web import AuctionControlService, create_wsgi_app, AuctionViewData

service = AuctionControlService()
service.set_live_items(
    1,
    [AuctionViewData("선수A", 1300, "Blue", 20), AuctionViewData("선수B", 900, "Red", 33)],
)

app = create_wsgi_app(service)
server = make_server('0.0.0.0', 8000, app)
print('http://localhost:8000/spectator?tournament_id=1')
print('승인 전에는 대기 화면, 아래 POST 이후 실시간 화면 노출')
print('curl -X POST "http://localhost:8000/admin/approve-start?tournament_id=1"')
server.serve_forever()
PY
```
