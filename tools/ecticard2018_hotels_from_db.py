"""Rebuild the three ECTI-CARD 2018 hotel posts that Wayback never captured,
from the site's own WordPress database, using an archived sibling post as the page template."""
import base64, html, json, os, pathlib, re, sys, urllib.parse
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
SITE = pathlib.Path(sys.argv[2])                     # docs/ecticard2018
CONTENT = SITE / "content"
TEMPLATE = CONTENT / "2017/11/03/the-park-hotel/index.html"
ABS = "http://ecticard2018.ecticard.org/content/"

posts = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
for p in posts:
    p["cats"] = [c for c in p["cats"] if c["name"] != "accomodation"]
    p["dt"] = datetime.fromisoformat(p["date"].split(".")[0])
    p["path"] = "%s/%s/" % (p["dt"].strftime("%Y/%m/%d"), p["slug"])


# ---------- shortcode rendering (only what these posts use) ----------
def autop(s):
    out = []
    for chunk in re.split(r"\n\s*\n", s.strip()):
        chunk = chunk.strip()
        if not chunk:
            continue
        if re.match(r"<(div|ul|ol|h\d|p|table)\b", chunk) and not re.search(r"\n(?!\s*<)", chunk):
            out.append(chunk)
        elif re.match(r"<(div|ul|ol|h\d|table)\b", chunk):
            # block element with loose text lines inside: keep tags, break loose lines
            out.append(re.sub(r"(?<!>)\n(?!\s*<)", "<br />\n", chunk))
        else:
            out.append("<p>" + chunk.replace("\n", "<br />\n") + "</p>")
    return "\n".join(out)


def col_class(w):
    return {"1/2": "vc_col-sm-6", "1/3": "vc_col-sm-4", "2/3": "vc_col-sm-8"}.get(w, "vc_col-sm-12")


def attrs(s):
    return dict(re.findall(r'(\w+)="([^"]*)"', s or ""))


def text_col(inner):
    return ('\n\t<div class="wpb_text_column wpb_content_element " >\n\t\t<div class="wpb_wrapper">\n\t\t\t'
            + autop(inner) + '\n\n\t\t</div>\n\t</div>\n')


def render(c):
    c = re.sub(r"\[vc_column_text\](.*?)\[/vc_column_text\]", lambda m: text_col(m.group(1)), c, flags=re.S)
    c = re.sub(r"\[vc_custom_heading ([^\]]*)\]", lambda m: (
        '<h4 style="text-align: left;font-family:Abril Fatface;font-weight:400;font-style:normal" '
        'class="vc_custom_heading" >%s</h4>' % attrs(m.group(1)).get("text", "")), c)
    c = re.sub(r"\[dt_fancy_separator[^\]]*\]",
               '<div class="hr-thin style-dotted" style="width: 80%;border-top-width: 1px;"></div>', c)
    c = re.sub(r"\[just_icon ([^\]]*)\]", lambda m: (
        '<div class="ult-just-icon-wrapper  "><div class="align-icon" style="text-align:center;">\n'
        '<div class="aio-icon none "  style="color:#333;font-size:32px;display:inline-block;">\n'
        '\t<i class="%s"></i>\n</div></div></div>' % attrs(m.group(1)).get("icon", "")), c)

    def gmaps(m):
        link = attrs(m.group(1)).get("link", "")
        frame = urllib.parse.unquote(base64.b64decode(link.split("_", 1)[1]).decode()) if "_" in link else ""
        if frame and not frame.lstrip().startswith("<iframe"):
            # the author pasted a plain Google Maps URL, which cannot be embedded: link to it instead
            frame = '<p><a href="%s" target="_blank" rel="noopener">เปิดแผนที่ใน Google Maps</a></p>\n' % html.escape(frame)
        return ('<div class="wpb_gmaps_widget wpb_content_element" >\n\t\t<div class="wpb_wrapper">\n'
                '\t\t<div class="wpb_map_wraper">\n\t\t\t%s\t\t</div>\n\t</div>\n</div>\n' % frame)
    c = re.sub(r"\[vc_gmaps ([^\]]*)\]", gmaps, c)
    c = re.sub(r"\[vc_column(?:_inner)?(?: ([^\]]*))?\]", lambda m: (
        '<div class="wpb_column vc_column_container %s"><div class="vc_column-inner "><div class="wpb_wrapper">'
        % col_class(attrs(m.group(1)).get("width"))), c)
    c = re.sub(r"\[/vc_column(?:_inner)?\]", "</div></div></div>", c)
    c = c.replace("[vc_row_inner]", '<div class="vc_row wpb_row vc_inner vc_row-fluid">').replace("[/vc_row_inner]", "</div>")
    c = re.sub(r"\[vc_row[^\]]*\]", '<div class="vc_row wpb_row vc_row-fluid">', c).replace("[/vc_row]", "</div>")
    left = re.findall(r"\[/?[a-z_]+[^\]]*\]", c)
    assert not left, left
    return c


# ---------- page assembly ----------
tpl = TEMPLATE.read_bytes().decode("utf-8")
T_TITLE = "The Park Hotel"


def cat_links(p, cls=""):
    return ", ".join('<a href="%scategory/accomodation_near_by/%s/" %s>%s</a>' % (ABS, c["slug"], cls, c["name"])
                     for c in p["cats"])


def build(p, newer, older):
    t = tpl
    t = t.replace("<title>%s &#8211;" % T_TITLE, "<title>%s &#8211;" % html.escape(p["title"]))
    t = t.replace('<meta property="og:title" content="%s" />' % T_TITLE,
                  '<meta property="og:title" content="%s" />' % html.escape(p["title"]))
    t = t.replace('<h1 class="entry-title">%s</h1>' % T_TITLE, '<h1 class="entry-title">%s</h1>' % html.escape(p["title"]))
    t = t.replace('<li class="current">%s</li>' % T_TITLE, '<li class="current">%s</li>' % html.escape(p["title"]))
    # post body: from the thumbnail block to the post meta
    a = t.index('<div class="post-thumbnail">')
    b = t.index('<div class="post-meta wf-mobile-collapsed">')
    d = p["dt"]
    fancy = ('<div class="post-thumbnail"><div class="fancy-date"><a title="%s" href="%s%s/" rel="nofollow">'
             '<span class="entry-month">%s</span><span class="entry-date updated">%d</span>'
             '<span class="entry-year">%d</span></a></div></div>'
             % (d.strftime("%I:%M %p").lstrip("0").lower(), ABS, d.strftime("%Y/%m/%d"), d.strftime("%b"), d.day, d.year))
    t = t[:a] + fancy + '<div class="entry-content">' + render(p["content"]) + "\n</div>" + t[b:]
    t = re.sub(r'<span class="category-link">Category:&nbsp;.*?</span>',
               lambda m: '<span class="category-link">Category:&nbsp;%s</span>' % cat_links(p, ""), t, count=1, flags=re.S)
    # previous (= newer) / next (= older) post links, the7 style
    def nav(cls, rel, label, q):
        if not q:
            return ""
        return ('<a class="%s" href="%s" rel="%s"><i class="fa fa-angle-%s" aria-hidden="true"></i>'
                '<span class="meta-nav" aria-hidden="true">%s</span><span class="screen-reader-text">%s post:</span>'
                '<span class="post-title h4-size">%s</span></a>'
                % (cls, ABS + q["path"], rel, "left" if label == "Previous" else "right", label, label,
                   html.escape(q["title"])))
    t = re.sub(r'<div class="nav-links">.*?</div></nav>',
               lambda m: '<div class="nav-links">%s%s</div></nav>' % (nav("nav-previous", "next", "Previous", newer),
                                                                   nav("nav-next", "prev", "Next", older)),
               t, count=1, flags=re.S)
    # the template sits in 2017/11/03/<slug>/; sibling links "../x/" must now climb to that folder
    t = re.sub(r'href="\.\./(?!\.\./)', 'href="../../../11/03/', t)
    return t


park = {"title": "The Park Hotel", "path": "2017/11/03/the-park-hotel/"}
chain = posts + [park]                     # oldest -> newest
for i, p in enumerate(posts):
    out = CONTENT / p["path"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(p, chain[i + 1], posts[i - 1] if i else None), encoding="utf-8", newline="\n")
    print("wrote", out)

# ---------- point every archived link at the new local pages ----------
targets = {ABS + p["path"]: CONTENT / p["path"] / "index.html" for p in posts + [park]}
n = 0
for f in SITE.rglob("*.html"):
    s = f.read_bytes().decode("utf-8")
    ns = s
    for url, dest in targets.items():
        rel = os.path.relpath(dest, f.parent).replace(os.sep, "/")
        ns = ns.replace(url, rel)
    if ns != s:
        f.write_bytes(ns.encode("utf-8")); n += 1
print("relinked", n, "files")
