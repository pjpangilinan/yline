with open("docs/index.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace('<script src="app.js?v=6"></script>', '<script src="app.js?v=7"></script>')

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)
