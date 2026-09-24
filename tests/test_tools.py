import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from yline.tools.music_search import search_music

class TestTools(unittest.IsolatedAsyncioTestCase):
    @patch("httpx.AsyncClient.get")
    async def test_search_music(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "recordings": [
                {
                    "artist-credit": [{"name": "The Beatles"}],
                    "title": "Let It Be",
                    "id": "1234"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = await search_music("The Beatles Let It Be")
        self.assertEqual(result["status"], "found")
        self.assertIn("Beatles", result["results"][0]["artist"])
        self.assertIn("Let It Be", result["results"][0]["title"])

if __name__ == "__main__":
    unittest.main()
