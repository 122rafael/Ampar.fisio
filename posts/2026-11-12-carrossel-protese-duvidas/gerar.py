import subprocess,os
CH='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
HEAD=open('l2.html').read().split('</style>')[0]+'''
.q{font-family:Newsreader;font-size:76px;line-height:1.08;color:var(--ink);margin-top:10px}
.a{font-size:38px;line-height:1.45;color:#2B4436;margin-top:40px}
.a b{color:#16291f}
.alert{margin-top:34px;border:2px solid #B5683B;background:#FBF1EA;border-radius:24px;padding:24px 30px;font-size:31px;line-height:1.4;color:#5A3A22}
.disc{position:absolute;left:96px;right:96px;bottom:150px;font-size:22px;color:#7A6A4E}
.bg{position:absolute;inset:0 0 120px 0;background:url(img/omni_cover.jpg) 62% center/cover}
.veil{position:absolute;inset:0 0 120px 0;background:linear-gradient(180deg,rgba(12,26,19,.92) 0%,rgba(12,26,19,.6) 42%,rgba(12,26,19,.1) 75%)}
.ia{position:absolute;right:40px;bottom:150px;border:2px solid rgba(255,255,255,.7);border-radius:30px;padding:6px 18px;color:#fff;font-size:22px;font-weight:700;background:rgba(0,0,0,.35)}
.num{font-family:Newsreader;font-size:30px;letter-spacing:.2em;color:#B5862E}
.cta{background:#D9A441;color:#16291f;border-radius:28px;padding:30px 36px;font-weight:700;font-size:40px;line-height:1.3;margin-top:44px}
</style></head><body>'''
FOOT='<div class="foot"><div class="logo"></div><div class="brand">Ampar<b>.fisio</b></div><div class="cred">Dr. Rafael Lima<span>|</span>@fisiorafaellima</div></div></div></body></html>'
DISC='<div class="disc">Cada caso tem seu tempo, sempre com liberação do cirurgião.</div>'
def qa(n,q,a,src,extra=''):
    return HEAD+f'<div class="slide areia"><div class="n">0{n}</div><div class="pad" style="top:200px"><div class="num">DÚVIDA {n-1}</div><div class="div"></div><div class="q">{q}</div><div class="a">{a}</div>{extra}</div><div class="src" style="bottom:190px">{src}</div>{DISC}'+FOOT
S={}
S[1]=HEAD+'''<div class="slide verde"><div class="bg"></div><div class="veil"></div><div class="pad" style="top:150px"><div class="eyebrow">Semana da prótese de joelho</div><div class="div"></div>
<h1 style="font-size:104px;color:var(--cream)">5 dúvidas de quem vai colocar <span class="acc">prótese no joelho.</span></h1></div>
<div class="ia">IA</div><div class="swipe" style="color:#E7BE6A;bottom:160px;left:96px;right:auto">ARRASTA →</div>'''+FOOT
S[2]=qa(2,'Quando volta a andar?','Os primeiros passos costumam ser <b>no dia da cirurgia ou no seguinte</b>, com a equipe. Nas primeiras semanas, com andador ou muletas.<br><br>A troca para bengala e depois sem apoio <b>não é por data: é por metas</b>, como andar sem mancar, ter equilíbrio e força. Cada paciente evolui no seu ritmo.','Fonte: diretriz NICE NG157 (2020)')
S[3]=qa(3,'Dor e inchaço são normais?','<b>Sim, no começo.</b> O inchaço pode durar semanas a alguns meses e vai melhorando. Gelo e perna elevada ajudam.','Fonte: AAOS OrthoInfo',extra='<div class="alert"><b>Avise o médico se tiver:</b> piora súbita da dor, febre, vermelhidão ou secreção na cicatriz, panturrilha inchada e dura.</div>')
S[4]=qa(4,'Quanto tempo de fisioterapia?','A fase principal costuma levar <b>em média 12 semanas</b>.<br><br>Mas a melhora continua por meses depois disso, e cada pessoa tem o seu tempo.','Fonte: AAOS OrthoInfo')
S[5]=qa(5,'E a escada?','Para subir, vai primeiro a <b>perna boa</b>.<br>Para descer, vai primeiro a <b>perna operada</b>.<br><br>Corrimão sempre, um degrau de cada vez.','Fonte: AAOS OrthoInfo')
S[6]=qa(6,'Fisioterapia em casa funciona?','<b>Sim.</b> Revisões de estudos mostram resultados parecidos entre a fisioterapia em casa e a de clínica, em movimento e função.<br><br>E em casa o paciente já treina no ambiente real dele: a cama, o banheiro, a escada.','Fonte: Florez-García et al., KSSTA 2017; Zhao et al., JOSR 2023')
S[7]=HEAD+'''<div class="slide verde"><div class="n" style="color:rgba(231,190,106,.7)">07</div><div class="pad" style="top:240px"><div class="eyebrow">Guia gratuito</div><div class="div"></div>
<div class="q" style="color:var(--cream);font-size:84px">Alguém da família vai <span class="acc">operar?</span></div>
<div class="cta">Me manda JOELHO no direct que eu te mando o guia da recuperação.</div>
<p class="sub" style="color:#CFC8BA;font-size:36px;margin-top:40px">📲 Manda pra quem vai operar.</p></div>'''+DISC.replace('#7A6A4E','#AFC0B4').replace('class="disc"','class="disc" style="color:#AFC0B4"')+FOOT
for i,h in S.items():
    open(f'pk{i}.html','w').write(h)
    subprocess.run([CH,'--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars','--allow-file-access-from-files','--window-size=1080,1500','--virtual-time-budget=4000',f'--screenshot=raw_pk{i}.png',f'file://{os.getcwd()}/pk{i}.html'],capture_output=True)
from PIL import Image
ims=[]
for i in S:
    im=Image.open(f'raw_pk{i}.png').crop((0,0,1080,1350)).convert('RGB'); im.save(f'pk_{i}.jpg',quality=93); ims.append(im.resize((360,450)))
sh=Image.new('RGB',(360*7,450))
for k,im in enumerate(ims): sh.paste(im,(k*360,0))
sh.save('pk_sheet.jpg',quality=85); print('ok')
