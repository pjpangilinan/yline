import re
with open("docs/index.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace(
    '<button class="song-btn" onclick="loadSong(\'yoshi\')">\n                    <div class="title">Yoshi\'s Island</div>\n                    <div class="artist">glass beach</div>\n                </button>',
    '<button class="song-btn" onclick="loadSong(\'angel\')">\n                    <div class="title">You Are An Angel</div>\n                    <div class="artist">kate said</div>\n                </button>'
)

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)
