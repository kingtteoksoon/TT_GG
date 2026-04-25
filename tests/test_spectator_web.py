import unittest

from src.spectator_web import AuctionControlService, AuctionViewData


class SpectatorWebTests(unittest.TestCase):
    def test_spectator_page_hidden_before_admin_approval(self):
        service = AuctionControlService()
        html = service.render_spectator_page(7)

        self.assertIn("관람 페이지", html)
        self.assertIn("경매 시작 승인", html)
        self.assertNotIn("실시간 경매", html)

    def test_spectator_page_visible_after_admin_approval(self):
        service = AuctionControlService()
        service.approve_auction_start(7)
        service.set_live_items(
            7,
            [AuctionViewData(item_name="플레이어A", current_price=1200, leading_team="TeamX", remaining_seconds=15)],
        )

        html = service.render_spectator_page(7)

        self.assertIn("실시간 경매", html)
        self.assertIn("플레이어A", html)
        self.assertIn("TeamX", html)


if __name__ == "__main__":
    unittest.main()
