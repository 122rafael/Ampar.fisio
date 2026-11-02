import subprocess,os
CH='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
HEAD=open('l2.html').read().split('</style>')[0]+'''
.big{font-family:Newsreader;font-size:96px;line-height:1.05}
.cta{background:#D9A441;color:#16291f;border-radius:28px;padding:34px 40px;font-weight:700;font-size:40px;line-height:1.3;margin-top:50px}
.pdf{position:absolute;right:96px;bottom:190px;width:300px;height:400px;background:#FBF7EF;border-radius:14px;box-shadow:0 30px 60px rgba(0,0,0,.45);transform:rotate(6deg);overflow:hidden}
.pdf .h{background:#16291f;height:150px;padding:28px 24px;color:#F4EEE3;font-family:Newsreader;font-size:40px;line-height:1}
.pdf .h b{color:#E7BE6A;font-weight:400}.pdf .l{height:14px;background:#E3D7C3;border-radius:7px;margin:22px 24px 0}
.bg{position:absolute;inset:0 0 120px 0;background:url(img/tapete.jpg) center/cover}
.veil{position:absolute;inset:0 0 120px 0;background:linear-gradient(180deg,rgba(12,26,19,.88) 0%,rgba(12,26,19,.55) 45%,rgba(12,26,19,.15) 75%)}
</style></head><body>'''
FOOT='<div class="foot"><div class="logo"></div><div class="brand">Ampar<b>.fisio</b></div><div class="cred">Dr. Rafael Lima<span>|</span>@fisiorafaellima</div></div></div></body></html>'
def mito(n,m,v,src):
    return HEAD+f'<div class="slide areia"><div class="n">0{n}</div><div class="pad" style="top:250px"><div class="lab m"><span class="ic">×</span>Mito</div><div class="mt">{m}</div><div class="sep"></div><div class="lab v"><span class="ic">✓</span>Verdade</div><div class="vt" style="font-size:66px">{v}</div></div><div class="src">{src}</div>'+FOOT
photo=os.path.exists('img/tapete.jpg')
S={}
S[1]=HEAD+'<div class="slide verde">'+('<div class="bg"></div><div class="veil"></div>' if photo else '')+'''<div class="pad" style="top:200px"><div class="eyebrow">Semana do equilíbrio</div><div class="div"></div>
<h1 style="font-size:122px;color:var(--cream)">4 mitos que fazem seu pai <span class="acc">cair.</span></h1></div>
<div class="swipe" style="color:#E7BE6A;bottom:170px">ARRASTA →</div>'''+FOOT
S[2]=mito(2,'Cair faz parte da idade.','O equilíbrio se treina <span class="acc">em qualquer idade</span>. Exercícios de equilíbrio reduzem as quedas em cerca de 24%.','Fonte: Sherrington et al., Cochrane Database of Systematic Reviews, 2019')
S[3]=mito(3,'Caminhar já treina o equilíbrio.','Caminhar faz bem, mas o equilíbrio melhora com <span class="acc">treino específico</span>: ficar numa perna, um pé na frente do outro.','Fonte: Sherrington et al., Cochrane, 2019 · Diretrizes Mundiais de Prevenção de Quedas, 2022')
S[4]=mito(4,'Com medo de cair, o melhor é se mexer menos.','Ficar parado enfraquece a perna e piora o equilíbrio. O caminho é <span class="acc">se mexer com segurança</span>, com orientação.','Fonte: Sherrington et al., Cochrane, 2019')
S[5]=mito(5,'Tapete solto e chinelo não fazem diferença.','Ajustes simples na casa <span class="acc">reduzem as quedas</span>, principalmente em quem já tem mais risco.','Fonte: Gillespie et al., Cochrane Database of Systematic Reviews, 2012')
S[6]=HEAD+'''<div class="slide areia"><div class="n">06</div><div class="pad" style="top:330px"><div class="eyebrow">E aí?</div><div class="div"></div>
<div class="big">Qual desses você <span class="acc">já ouviu?</span></div>
<p class="sub" style="font-size:44px;margin-top:70px">Manda pra quem cuida dos pais.</p></div>'''+FOOT
S[7]=HEAD+'''<div class="slide verde"><div class="n" style="color:rgba(231,190,106,.7)">07</div><div class="pad" style="top:200px;right:96px"><div class="eyebrow">Guia gratuito</div><div class="div"></div>
<div class="big" style="color:var(--cream);font-size:88px">Me manda <span class="acc">EQUILÍBRIO</span><br>no direct</div>
<p class="sub" style="color:#CFC8BA;font-size:40px;margin-top:40px;max-width:560px">que eu te mando o guia <b style="color:#E7BE6A">Equilíbrio em casa.</b></p></div>
<div class="pdf"><div class="h">Equilíbrio<br><b>em casa.</b></div><div class="l"></div><div class="l" style="width:60%"></div><div class="l"></div><div class="l" style="width:75%"></div><div class="l"></div><div class="l" style="width:50%"></div></div>'''+FOOT
for i,h in S.items():
    open(f'eq{i}.html','w').write(h)
    subprocess.run([CH,'--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars','--allow-file-access-from-files','--window-size=1080,1500','--virtual-time-budget=4000',f'--screenshot=raw_eq{i}.png',f'file://{os.getcwd()}/eq{i}.html'],capture_output=True)
from PIL import Image
ims=[]
for i in S:
    im=Image.open(f'raw_eq{i}.png').crop((0,0,1080,1350)).convert('RGB'); im.save(f'eq_{i}.jpg',quality=93); ims.append(im.resize((360,450)))
sh=Image.new('RGB',(360*7,450))
for k,im in enumerate(ims): sh.paste(im,(k*360,0))
sh.save('eq_sheet.jpg',quality=85); print('ok',photo)
