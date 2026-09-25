import unittest
from unittest.mock import AsyncMock, patch
import io
import hashlib
from PIL import Image

from yline.tools.images import download_image
from yline.tools.lyrics import parse_lrc

class TestPipelineRemediation(unittest.IsolatedAsyncioTestCase):
    
    def test_parse_lrc_filters_empty_lines_and_caps_long_gaps(self):
        sample_lrc = """
[00:05.00] Line one of lyrics
[00:10.00] 
[00:15.00] Line two after long instrumental pause
[00:35.00] Line three after a 20 second guitar solo
[00:40.00] Line four normal gap
        """.strip()
        
        parsed = parse_lrc(sample_lrc)
        
        # 1. Empty lines should be completely filtered out
        texts = [p["text"] for p in parsed]
        self.assertNotIn("", texts)
        self.assertEqual(len(parsed), 4)
        
        # 2. Line 1: start_ms=5000, next line starts at 15000 (gap=10s > 6.0s)
        # Display is capped during long instrumental gap to allow clean screen
        self.assertEqual(parsed[0]["start_ms"], 5000)
        self.assertTrue(5000 < parsed[0]["end_ms"] < 15000)
        
        # 3. Line 2: start_ms=15000, next line starts at 35000 (gap=20s > 6.0s)
        # Display is capped so it does not freeze across 20-second guitar solo
        self.assertEqual(parsed[1]["start_ms"], 15000)
        self.assertTrue(15000 < parsed[1]["end_ms"] < 35000)
        
        # 4. Line 3: start_ms=35000, next line starts at 40000 (gap=5s <= 6.0s normal gap)
        # Held until next line so subtitles don't vanish prematurely before singer finishes
        self.assertEqual(parsed[2]["start_ms"], 35000)
        self.assertEqual(parsed[2]["end_ms"], 40000)

    @patch("httpx.AsyncClient.get")
    async def test_download_image_seen_hashes_deduplication(self, mock_get):
        # Create a test image
        img = Image.new("RGB", (600, 400), color="blue")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=92)
        raw_bytes = buf.getvalue()
        
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = raw_bytes
        mock_get.return_value = mock_response
        
        seen_hashes = set()
        
        # First download: should succeed and add hash to seen_hashes
        path1 = await download_image(
            url="https://example.com/test1.jpg",
            save_path="output/test_dedup/img_001.jpg",
            min_bytes=1000,
            seen_hashes=seen_hashes
        )
        self.assertIsNotNone(path1)
        self.assertEqual(len(seen_hashes), 1)
        
        # Second download with same image content: should be rejected as duplicate
        path2 = await download_image(
            url="https://example.com/test2.jpg",
            save_path="output/test_dedup/img_002.jpg",
            min_bytes=1000,
            seen_hashes=seen_hashes
        )
        self.assertIsNone(path2)
        self.assertEqual(len(seen_hashes), 1)
        
        # Clean up created file
        import os
        if path1 and os.path.exists(path1):
            os.remove(path1)
            if os.path.exists("output/test_dedup"):
                os.rmdir("output/test_dedup")

if __name__ == "__main__":
    unittest.main()
