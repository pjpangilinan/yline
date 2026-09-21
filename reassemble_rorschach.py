import json
import asyncio
from yline.agents.video_assembler import video_assembler_node

async def fix_rorschach():
    print("Loading state...")
    with open("output/rorschach_blots_by_the_ridleys_state.json", "r", encoding="utf-8") as f:
        state = json.load(f)
    
    # Add 3000 ms offset
    offset_ms = 3000
    for line in state["lyrics"]:
        line["start_ms"] += offset_ms
        line["end_ms"] += offset_ms
        
    print("Re-assembling video with +3s offset...")
    res = await video_assembler_node(state)
    print("Result:", res)
    
    # Save the fixed state just in case
    with open("output/rorschach_blots_by_the_ridleys_state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

asyncio.run(fix_rorschach())
