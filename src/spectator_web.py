from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import escape
from typing import Dict, List
from urllib.parse import parse_qs


@dataclass
class AuctionViewData:
    item_name: str
    current_price: float
    leading_team: str
    remaining_seconds: int


@dataclass
class TournamentAuctionState:
    tournament_id: int
    approved_at: datetime | None = None
    live_items: List[AuctionViewData] = field(default_factory=list)

    @property
    def is_approved(self) -> bool:
        return self.approved_at is not None


class AuctionControlService:
    """운영진 승인 여부를 기준으로 관객 화면 노출을 제어한다."""

    def __init__(self) -> None:
        self._states: Dict[int, TournamentAuctionState] = {}

    def get_or_create_state(self, tournament_id: int) -> TournamentAuctionState:
        if tournament_id not in self._states:
            self._states[tournament_id] = TournamentAuctionState(tournament_id=tournament_id)
        return self._states[tournament_id]

    def approve_auction_start(self, tournament_id: int) -> TournamentAuctionState:
        state = self.get_or_create_state(tournament_id)
        state.approved_at = datetime.now(timezone.utc)
        return state

    def set_live_items(self, tournament_id: int, items: List[AuctionViewData]) -> TournamentAuctionState:
        state = self.get_or_create_state(tournament_id)
        state.live_items = items
        return state

    def render_spectator_page(self, tournament_id: int) -> str:
        state = self.get_or_create_state(tournament_id)
        if not state.is_approved:
            return self._render_waiting_page(tournament_id)
        return self._render_live_page(state)

    @staticmethod
    def _render_waiting_page(tournament_id: int) -> str:
        return f"""<!doctype html>
<html lang=\"ko\">
  <head>
    <meta charset=\"utf-8\" />
    <title>경매 대기 중</title>
  </head>
  <body>
    <h1>대회 #{tournament_id} 관람 페이지</h1>
    <p>운영진의 경매 시작 승인이 나면 자동으로 관람 화면이 열립니다.</p>
  </body>
</html>
"""

    @staticmethod
    def _render_live_page(state: TournamentAuctionState) -> str:
        rows = "\n".join(
            "<tr>"
            f"<td>{escape(item.item_name)}</td>"
            f"<td>{item.current_price:.0f}</td>"
            f"<td>{escape(item.leading_team)}</td>"
            f"<td>{item.remaining_seconds}</td>"
            "</tr>"
            for item in state.live_items
        )

        if not rows:
            rows = "<tr><td colspan=\"4\">진행 중인 경매가 없습니다.</td></tr>"

        approved_at_text = state.approved_at.isoformat() if state.approved_at else "-"

        return f"""<!doctype html>
<html lang=\"ko\">
  <head>
    <meta charset=\"utf-8\" />
    <title>실시간 경매 관람</title>
  </head>
  <body>
    <h1>대회 #{state.tournament_id} 실시간 경매</h1>
    <p>운영진 승인 시각(UTC): {approved_at_text}</p>
    <table border=\"1\" cellpadding=\"6\" cellspacing=\"0\">
      <thead>
        <tr>
          <th>매물</th>
          <th>현재가</th>
          <th>선두 팀</th>
          <th>남은 시간(초)</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </body>
</html>
"""


def create_wsgi_app(control_service: AuctionControlService):
    """의존성 없이 실행 가능한 최소 WSGI 앱.

    - GET /spectator?tournament_id=1
    - POST /admin/approve-start?tournament_id=1
    """

    def app(environ, start_response):
        path = environ.get("PATH_INFO", "")
        method = environ.get("REQUEST_METHOD", "GET").upper()
        query = parse_qs(environ.get("QUERY_STRING", ""))
        tournament_id = int(query.get("tournament_id", ["1"])[0])

        if path == "/spectator" and method == "GET":
            html = control_service.render_spectator_page(tournament_id)
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [html.encode("utf-8")]

        if path == "/admin/approve-start" and method == "POST":
            control_service.approve_auction_start(tournament_id)
            start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
            return [b"approved"]

        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"not found"]

    return app
