with open("docs/index.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace('<div class="title">You Are An Angel</div>', '<div class="title">kate said</div>')
html = html.replace('<div class="artist">kate said</div>', '<div class="artist">you are an angel</div>')

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)
    
with open("docs/app.js", "r", encoding="utf-8") as f:
    js = f.read()

js = js.replace('"artist": "kate said", "title": "you are an angel"', '"artist": "you are an angel", "title": "kate said"')

with open("docs/app.js", "w", encoding="utf-8") as f:
    f.write(js)
