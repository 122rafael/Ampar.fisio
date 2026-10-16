# Nano Banana: python3 nb.py MODEL OUT.png "prompt" [ratio]
import sys,json,base64,urllib.request
model,out,prompt=sys.argv[1],sys.argv[2],sys.argv[3]
ratio=sys.argv[4] if len(sys.argv)>4 else "4:5"
body={"contents":[{"parts":[{"text":prompt}]}],
      "generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":ratio}}}
req=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
try:
    d=json.load(urllib.request.urlopen(req,timeout=180))
except urllib.error.HTTPError as e:
    err=json.load(e); print("ERR",err["error"]["status"],err["error"]["message"][:300]); sys.exit(1)
for c in d.get("candidates",[]):
    for p in c.get("content",{}).get("parts",[]):
        if "inlineData" in p:
            open(out,"wb").write(base64.b64decode(p["inlineData"]["data"])); print("saved",out); sys.exit(0)
print("NOIMG",json.dumps(d)[:400]); sys.exit(1)
