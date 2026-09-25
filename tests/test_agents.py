import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from yline.state import PipelineState
from yline.agents.song_resolver import song_resolver_node

class TestAgents(unittest.IsolatedAsyncioTestCase):

    @patch("yline.agents.song_resolver.ChatGroq")
    async def test_song_resolver_node(self, mock_chat_groq):
        # Mock LLM instance and its ainvoke returning return_song tool call
        mock_llm_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.tool_calls = [{
            "name": "return_song",
            "args": {
                "artist": "The Ridleys",
                "title": "Rorschach Blots",
                "album": "Until I Reach The Sun Vol. 2",
                "year": 2021,
                "musicbrainz_id": "none"
            },
            "id": "call_123"
        }]
        mock_response.response_metadata = {
            "token_usage": {"prompt_tokens": 100, "completion_tokens": 50}
        }
        mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_groq.return_value = mock_llm_instance

        state = {"song_query": "The Ridleys Rorschach Blots", "errors": []}
        res = await song_resolver_node(state)
        self.assertIn("song_metadata", res)
        self.assertEqual(res["song_metadata"]["artist"], "The Ridleys")
        self.assertEqual(res["song_metadata"]["title"], "Rorschach Blots")
        self.assertEqual(res["song_metadata"]["year"], 2021)

if __name__ == "__main__":
    unittest.main()
