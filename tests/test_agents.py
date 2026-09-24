import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from yline.state import PipelineState
from yline.agents.song_resolver import song_resolver_node

class TestAgents(unittest.IsolatedAsyncioTestCase):

    async def test_song_resolver_bypass(self):
        state = {"song_query": "The Ridleys Rorschach Blots", "errors": []}
        res = await song_resolver_node(state)
        self.assertIn("song_metadata", res)
        self.assertEqual(res["song_metadata"]["artist"], "The Ridleys")
        self.assertEqual(res["song_metadata"]["title"], "Rorschach Blots")
        self.assertEqual(res["song_metadata"]["year"], 2021)

if __name__ == "__main__":
    unittest.main()
