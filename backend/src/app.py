import json
import os
import urllib.request
import boto3

GHOST_URL = "https://pratika.dataiesb.com"
GHOST_API_KEY = os.environ["GHOST_API_KEY"]
S3_BUCKET = os.environ["S3_BUCKET"]
CF_DISTRIBUTION = os.environ["CF_DISTRIBUTION"]
AUTHOR_SLUG = "jornageo"


def get_posts():
    url = f"{GHOST_URL}/ghost/api/content/posts/?key={GHOST_API_KEY}&include=tags,authors&formats=html&limit=all&filter=authors.slug:{AUTHOR_SLUG}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read()).get('posts', [])


def fix_urls(text):
    return text.replace('http://app.dataiesb.com', 'https://pratika.dataiesb.com').replace('http://pratika.dataiesb.com', 'https://pratika.dataiesb.com')


def build_page(post):
    title = post['title']
    html_content = fix_urls(post['html'])
    img = fix_urls(post.get('feature_image', '') or '')
    img_tag = f'<img src="{img}" style="max-width:100%;border-radius:8px;margin:1rem 0">' if img else ''
    date = post.get('published_at', '')[:10]
    author = post.get('primary_author', {}).get('name', '') if post.get('primary_author') else ''

    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} - JornaGEO</title>
<link rel="stylesheet" href="/styles.css">
<style>
.post-container{{max-width:800px;margin:100px auto 2rem;padding:0 20px}}
.post-header h1{{color:var(--primary-color);font-size:2rem;margin-bottom:0.5rem}}
.post-meta{{color:var(--text-light);font-size:0.9rem;margin-bottom:1.5rem}}
.post-body{{line-height:1.8;font-size:1.05rem}}
.post-body img{{max-width:100%;border-radius:8px;margin:1rem 0}}
.back-link{{display:inline-block;margin-top:2rem;color:var(--primary-color);text-decoration:none;font-weight:600}}
.back-link:hover{{text-decoration:underline}}
</style>
</head>
<body>
<nav class="navbar"><div class="nav-container"><div class="nav-logo"><a href="https://jornageo.dataiesb.com" style="color:var(--primary-color);font-weight:700;font-size:1.3rem;text-decoration:none">JornaGEO</a></div><ul class="nav-menu"><li><a href="https://jornageo.dataiesb.com">Início</a></li><li><a href="https://jornageo.dataiesb.com/#about">Sobre</a></li><li><a href="https://jornageo.dataiesb.com/#schedule">Programação</a></li></ul></div></nav>
<div class="post-container">
<div class="post-header"><h1>{title}</h1><p class="post-meta">{date} {("&middot; " + author) if author else ""}</p>{img_tag}</div>
<div class="post-body">{html_content}</div>
<a href="https://jornageo.dataiesb.com" class="back-link">&larr; Voltar ao JornaGEO</a>
</div>
</body>
</html>'''


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    cf = boto3.client('cloudfront')

    posts = get_posts()
    paths = []

    for post in posts:
        slug = post['slug']
        html = build_page(post)
        s3.put_object(Bucket=S3_BUCKET, Key=f"{slug}/index.html", Body=html.encode(), ContentType='text/html')
        paths.append(f"/{slug}/*")

    # Update news section in homepage
    news_html = ''
    for i, post in enumerate(posts):
        slug = post['slug']
        title = post['title']
        date = post.get('published_at', '')[:10]
        excerpt = post.get('excerpt', '')[:120]
        img = fix_urls(post.get('feature_image', '') or '')
        img_tag = f'<img src="{img}" style="width:100%;border-radius:8px;margin-bottom:0.5rem">' if img else ''
        news_html += f'<a href="/{slug}/" style="text-decoration:none;color:inherit"><div style="background:var(--bg-light);border-left:4px solid var(--primary-color);padding:1rem;margin:1rem 0;border-radius:4px">{img_tag}<h3 style="color:var(--primary-color)">{title}</h3><p style="color:var(--text-light);font-size:0.85rem">{date}</p><p>{excerpt}</p></div></a>'

    if news_html:
        try:
            obj = s3.get_object(Bucket=S3_BUCKET, Key='index.html')
            homepage = obj['Body'].read().decode()
            import re
            pattern = r'(<!--GHOST-NEWS-START-->).*?(<!--GHOST-NEWS-END-->)'
            if re.search(pattern, homepage, re.DOTALL):
                homepage = re.sub(pattern, r'\1\n' + news_html + r'\2', homepage, flags=re.DOTALL)
                s3.put_object(Bucket=S3_BUCKET, Key='index.html', Body=homepage.encode(), ContentType='text/html')
                paths.append('/index.html')
                paths.append('/')
        except Exception as e:
            print(f"Homepage update skipped: {e}")

    if paths:
        cf.create_invalidation(
            DistributionId=CF_DISTRIBUTION,
            InvalidationBatch={'Paths': {'Quantity': len(paths), 'Items': paths}, 'CallerReference': str(hash(str(paths)))}
        )

    return {'statusCode': 200, 'body': json.dumps(f'Synced {len(posts)} jornageo posts')}
