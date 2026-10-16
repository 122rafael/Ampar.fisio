FOOT='<div class="foot"><div class="logo"></div><div class="brand">Ampar<b>.fisio</b></div><div class="cred">Dr. Rafael Lima<span>|</span>@fisiorafaellima</div></div>'
def page(img,veil,body,extra=''):
    return f'''<html><head><meta charset="utf-8"><link rel="stylesheet" href="base.css"><style>
.bg{{position:absolute;inset:0 0 120px 0;background:url({img}) center/cover}}
.veil{{position:absolute;inset:0 0 120px 0;background:{veil}}}
.n{{font-family:Newsreader;font-size:30px;letter-spacing:.2em;color:#9A7A45;position:absolute;right:96px;top:120px}}
{extra}</style></head><body><div class="slide areia"><div class="bg"></div><div class="veil"></div>{body}{FOOT}</div></body></html>'''
TOP='linear-gradient(180deg,rgba(246,240,229,.78) 0%,rgba(246,240,229,.45) 32%,rgba(246,240,229,0) 52%)'
LEFT='linear-gradient(90deg,rgba(246,240,229,.7) 0%,rgba(246,240,229,.35) 45%,rgba(246,240,229,0) 65%)'
S={
's1':page('img/c1.png',TOP,'''<div class="pad" style="top:120px"><div class="eyebrow">Prevenção 40+</div><div class="div"></div>
<h1 style="font-size:104px">Músculo é o seu<br>plano de<br><span class="acc">aposentadoria.</span></h1></div>
<div class="swipe" style="color:#F4EEE3;bottom:160px">ARRASTA →</div>'''),
's2':page('img/c2.png',LEFT,'''<div class="n">02</div><div class="pad" style="top:300px;right:440px"><div class="div" style="margin-top:0"></div>
<h2 style="font-size:76px">Com os anos, perdemos massa e força muscular.</h2>
<p class="sub" style="margin-top:60px">Tem nome:</p><h2 class="acc" style="font-size:92px;margin-top:4px">sarcopenia.</h2></div>'''),
's3':page('img/c3.png',LEFT,'''<div class="n">03</div><div class="pad" style="top:240px;right:470px"><div class="div" style="margin-top:0"></div>
<h2 style="font-size:76px">Ela não aparece no espelho.</h2>
<p class="sub" style="margin-top:48px">Aparece na escada,<br>na mala, no levantar<br>do sofá.</p></div>'''),
's4':page('img/c4.png',TOP,'''<div class="n">04</div><div class="pad" style="top:200px;right:200px"><div class="div" style="margin-top:0"></div>
<h2 style="font-size:76px">A principal forma de prevenir não é remédio.</h2>
<h2 class="acc" style="font-size:76px;margin-top:30px">É treino de força bem orientado.</h2></div>'''),
's5':page('img/c5.png',LEFT,'''<div class="n">05</div><div class="pad" style="top:150px;right:500px"><div class="div" style="margin-top:0"></div>
<h2 style="font-size:64px">Começar depois dos 40, 50 ou 60 ainda funciona.</h2>
<h2 class="acc" style="font-size:64px;margin-top:26px">O corpo responde.</h2></div>'''),
}
for k,v in S.items(): open(k+'.html','w').write(v)
