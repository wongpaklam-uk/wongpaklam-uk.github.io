#!/usr/bin/env python3
"""Download real screenshots from Apple's public app listings; never create images."""
import html,io,json,re,urllib.parse,urllib.request
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"assets"/"screenshots"
APPS={
 "downhillspotter":{"id":"6829381502","slug":"downhillspotter"},
 "metronome":{"id":"6824046685","slug":"metronome-by-berlin"}
}
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; BerlinApps/1.0)","Accept":"*/*"}
def fetch(url):
 request=urllib.request.Request(url,headers=HEADERS)
 with urllib.request.urlopen(request,timeout=25) as r:return r.read()
def trusted(url):
 p=urllib.parse.urlparse(url)
 return p.scheme=="https" and (p.hostname=="mzstatic.com" or (p.hostname or "").endswith(".mzstatic.com"))
def listing(appid):
 for country in ("gb","us"):
  try:
   data=json.loads(fetch("https://itunes.apple.com/lookup?"+urllib.parse.urlencode({"id":appid,"country":country})))
   for item in data.get("results",[]):
    if str(item.get("trackId"))==appid:yield item
  except Exception as ex:print("Lookup unavailable:",country,ex)
def markup_urls(slug,appid):
 for country in ("gb","us"):
  try:
   raw=fetch(f"https://apps.apple.com/{country}/app/{slug}/id{appid}").decode("utf-8","replace")
   raw=html.unescape(raw).replace("\\/","/").replace("\\u002F","/").replace("\\u003A",":")
   candidates=re.findall(r"https://(?:is\d+-ssl|is\d+|a\d+)\.mzstatic\.com/[^\s\"'<>\\]+",raw)
   urls=[]
   for item in candidates:
    url=item.split("&amp;")[0].rstrip(");,")
    if trusted(url) and url not in urls:urls.append(url)
   if urls:return urls
  except Exception as ex:print("HTML fallback unavailable:",ex)
 return []
def read_img(url):
 if not trusted(url):return None
 try:
  data=fetch(url)
  if len(data)<7000:return None
  with Image.open(io.BytesIO(data)) as im:
   im.verify()
  with Image.open(io.BytesIO(data)) as im:
   w,h=im.size;fmt=im.format
  if w<320 or h<400:return None
  ratio=w/max(h,1)
  if ratio<.35 or ratio>2.3:return None
  return data,ratio,{"PNG":".png","JPEG":".jpg","WEBP":".webp"}.get(fmt,".bin")
 except Exception as ex:
  print("Image skipped:",str(ex)[:75])
  return None
def main():
 manifest={}
 for key,app in APPS.items():
  phone,tablet,icon=[],[],None
  for record in listing(app["id"]):
   phone+=record.get("screenshotUrls") or []
   tablet+=record.get("ipadScreenshotUrls") or []
   icon=record.get("artworkUrl512") or icon
  if not phone and not tablet:
   for url in markup_urls(app["slug"],app["id"]):
    result=read_img(url)
    if result:
     (phone if result[1]<.72 else tablet).append(url)
  record={"iphone":[],"ipad":[]}
  for kind,urls,cap in (("iphone",phone,7),("ipad",tablet,5)):
   for url in dict.fromkeys(urls):
    if len(record[kind])>=cap:break
    image=read_img(url)
    if not image:continue
    data,ratio,ext=image
    if kind=="iphone" and ratio>=.72:continue
    path=OUT/key/(kind+"-"+str(len(record[kind])+1).zfill(2)+ext)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
    record[kind].append(path.relative_to(ROOT).as_posix())
  if record["iphone"] or record["ipad"]:manifest[key]=record
  print(key, len(record["iphone"]),"iPhone screenshots,",len(record["ipad"]),"iPad screenshots")
  if icon and trusted(icon):
   try:
    data=fetch(icon);item=read_img(icon)
    if item:
     icon_path=OUT/key/("icon"+item[2]);icon_path.parent.mkdir(parents=True,exist_ok=True);icon_path.write_bytes(data)
   except Exception as ex:print("Icon unavailable",ex)
 (ROOT/"assets").mkdir(parents=True,exist_ok=True)
 (ROOT/"assets"/"appstore-images.js").write_text("/* Actual Apple App Store screenshots, unmodified. */\nObject.assign(BERLIN_LOCAL_SCREENSHOTS, "+json.dumps(manifest,indent=2)+");\n",encoding="utf-8")
 print("Saved verified screenshot manifest for",len(manifest),"apps")
if __name__=="__main__":main()
