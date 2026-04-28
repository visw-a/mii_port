import json
import unittest
from unittest.mock import patch

from backend.main import app
from fastapi.testclient import TestClient


class BackendApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_endpoint(self) -> None:
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['status'], 'ok')

    @patch('backend.main.urlopen')
    def test_live_endpoint_uses_quote_price(self, mock_urlopen) -> None:
        fake_payload = {
            'quoteResponse': {
                'result': [
                    {'symbol': 'AAPL', 'regularMarketPrice': 300.0, 'regularMarketChangePercent': 2.5},
                ]
            }
        }

        class _Resp:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps(fake_payload).encode('utf-8')

        mock_urlopen.return_value = _Resp()

        response = self.client.get('/api/portfolio/live')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        aapl = next(h for h in data['holdings'] if h['symbol'] == 'AAPL')
        self.assertEqual(aapl['price'], 300.0)
        self.assertEqual(aapl['dayChangePct'], 0.025)


if __name__ == '__main__':
    unittest.main()
