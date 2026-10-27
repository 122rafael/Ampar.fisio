import subprocess
CH='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
FOOT='<div class="foot"><div class="logo"></div><div class="brand">Ampar<b>.fisio</b></div><div class="cred">Dr. Rafael Lima<span>|</span>CREFITO 3 · 329642</div></div>'
CSS='''<style>
.n{font-family:Newsreader;font-size:28px;letter-spacing:.2em;color:#9A7A45;position:absolute;right:96px;top:110px}
.verde .n{color:rgba(231,190,106,.7)}
.list{display:flex;flex-direction:column;gap:30px;margin-top:8px}
.it{display:flex;gap:28px;align-items:flex-start}
.b{flex:none;width:58px;height:58px;border-radius:50%;background:#16291f;color:#E7BE6A;font-family:Newsreader;font-size:32px;display:flex;align-items:center;justify-content:center;margin-top:2px}
.verde .b{background:#D9A441;color:#16291f}
.it h3{font-family:Montserrat;font-weight:700;font-size:33px;line-height:1.2;color:#16291f}
.verde .it h3{color:#F4EEE3}
.it p{font-family:Montserrat;font-weight:400;font-size:28px;line-height:1.4;color:#3A5245;margin-top:6px}
.verde .it p{color:#CFC8BA}
.alert .b{background:#B5683B;color:#fff}
.note{position:absolute;left:96px;right:96px;bottom:160px;font-size:24px;line-height:1.45;color:#5B6B60;border-top:1px solid rgba(154,122,69,.45);padding-top:22px}
.verde .note{color:#AFC0B4;border-color:rgba(217,164,65,.35)}
.tag{display:inline-block;background:#B5683B;color:#fff;font-weight:700;font-size:26px;letter-spacing:.06em;padding:12px 24px;border-radius:40px;margin-top:6px}
</style>'''
def page(cls,body): return f'<html><head><meta charset="utf-8"><link rel="stylesheet" href="base.css">{CSS}</head><body><div class="slide {cls}">{body}{FOOT}</div></body></html>'
def items(L,alert=False):
    return '<div class="list'+(' alert' if alert else '')+'">'+''.join(f'<div class="it"><div class="b">{i+1}</div><div><h3>{t}</h3><p>{d}</p></div></div>' for i,(t,d) in enumerate(L))+'</div>'
def head(n,eb,title,top=120): return f'<div class="n">{n:02d}/10</div><div class="pad" style="top:{top}px"><div class="eyebrow">{eb}</div><div class="div"></div><h2 style="font-size:68px;margin-bottom:46px">{title}</h2>'
S=[]
S.append(page('verde','''<div class="pad" style="top:250px"><div class="eyebrow">Guia de orientações</div><div class="div"></div>
<h1 style="font-size:118px;color:var(--cream)">Seu novo<br><span class="acc">joelho.</span></h1>
<p class="sub" style="color:#CFC8BA;font-size:40px;margin-top:50px">O que esperar e como se cuidar na recuperação da prótese total de joelho.</p>
<p style="margin-top:80px;font-size:26px;letter-spacing:.18em;color:#E7BE6A;font-weight:600">ARRASTE PARA O LADO →</p></div>'''))
S.append(page('areia',head(2,'Etapas','Como é a recuperação')+items([
 ('Primeiros dias, no hospital','A equipe ajuda você a se levantar e dar os primeiros passos logo no dia da cirurgia ou no dia seguinte.'),
 ('Primeiras semanas, em casa','Fase de controlar dor e inchaço, voltar a andar com apoio e retomar a rotina aos poucos.'),
 ('Meses seguintes','Força, equilíbrio e confiança continuam melhorando por meses. Cada pessoa tem o seu ritmo.'),
])+'</div><div class="note">A fisioterapia acompanha você em todas essas etapas, desde o começo.</div>'))
S.append(page('areia',head(3,'Dor e inchaço','São esperados, e têm controle')+items([
 ('Gelo, sempre com um pano','Em média 15 a 20 minutos, nunca direto na pele. Ajuda na dor e no inchaço.'),
 ('Perna elevada e esticada','Ao descansar, apoie a perna da panturrilha ao calcanhar, um pouco acima da altura do quadril.'),
 ('Remédios no horário certo','Tome exatamente como o médico prescreveu. Não espere a dor ficar forte.'),
 ('Movimento faz parte','Ficar parado por muito tempo aumenta a rigidez. Alterne descanso e movimento ao longo do dia.'),
])+'</div>'))
S.append(page('verde',head(4,'Regra de ouro','Joelho <span class="acc">esticado</span> é prioridade',150)+items([
 ('Nada de travesseiro embaixo do joelho','Ele parece confortável, mas deixa o joelho dobrado e dificulta esticar depois.'),
 ('Apoio na panturrilha e no calcanhar','Se quiser elevar a perna, o apoio vai embaixo da panturrilha, com o joelho reto.'),
 ('Troque de posição com frequência','Evite passar horas seguidas sentada com o joelho dobrado.'),
])+'</div>'))
S.append(page('areia',head(5,'A cirurgia','Cuidados com o curativo e a circulação')+items([
 ('Curativo limpo e seco','Só molhe ou troque quando a equipe liberar. Não mexa nos pontos.'),
 ('Meias e remédios para circulação','Use exatamente como prescrito pelo médico, pelo tempo indicado.'),
 ('Mexa os pés e caminhe','Movimentar os pés e andar várias vezes ao dia ajuda o sangue a circular.'),
 ('Beba água e coma bem','Hidratação, proteína e sono ajudam na cicatrização e na energia para a reabilitação.'),
])+'</div>'))
S.append(page('areia',head(6,'Dia a dia','Movimente-se com segurança')+items([
 ('Use o apoio indicado','Andador ou muletas até a equipe liberar a troca. Não tenha pressa para largar.'),
 ('Levante em etapas','Sente na beira da cama, espere alguns segundos e só depois fique de pé.'),
 ('Cadeira firme, com braços','Evite sofás baixos e fundos. Use os braços da cadeira para sentar e levantar.'),
 ('Escada com corrimão','Para subir, vai primeiro a perna boa. Para descer, vai primeiro a perna operada.'),
])+'</div>'))
S.append(page('areia',head(7,'Casa preparada','Antes de voltar para casa')+items([
 ('Caminho livre','Tire tapetes soltos, fios e móveis do caminho entre o quarto, o banheiro e a sala.'),
 ('Luz à noite','Deixe uma luz acesa ou um abajur no caminho até o banheiro.'),
 ('Banheiro seguro','Cadeira de banho, tapete antiderrapante e, se possível, barra de apoio.'),
 ('Tudo ao alcance','Deixe o que usa todo dia entre a altura da cintura e do ombro.'),
 ('Alguém por perto','Nos primeiros dias, é importante ter alguém em casa para ajudar.'),
])+'</div>'))
S.append(page('areia',head(8,'Liberação','Converse antes com a equipe')+'''<p style="font-size:31px;line-height:1.45;color:#3A5245;margin-top:-10px">Cada cirurgia e cada pessoa têm um tempo diferente. Só retome estas atividades com a liberação do seu cirurgião:</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:44px">'''+''.join(f'<div style="background:#16291f;color:#F4EEE3;border-radius:22px;padding:28px 30px;font-size:30px;font-weight:600">{x}</div>' for x in ['Dirigir','Voltar ao trabalho','Viagens longas','Ajoelhar','Atividade física','Molhar a cicatriz'])+'</div></div>'))
S.append(page('areia',head(9,'Sinais de alerta','Avise a equipe médica se tiver:')+items([
 ('Febre de 38 °C ou mais','Ou calafrios.'),
 ('Mudança na cicatriz','Vermelhidão, calor, secreção, mau cheiro ou abertura nos pontos.'),
 ('Dor ou inchaço na panturrilha','Principalmente se a batata da perna ficar dura, quente ou vermelha.'),
 ('Dor que piora muito','E não melhora com os remédios prescritos.'),
 ('Queda','Mesmo que pareça leve.'),
],alert=True)+'<div class="tag">Falta de ar ou dor no peito: ligue 192 (SAMU)</div></div>'))
S.append(page('verde','''<div class="n">10/10</div><div class="pad" style="top:220px"><div class="eyebrow">Você não está sozinha</div><div class="div"></div>
<h2 style="font-size:84px;color:var(--cream)">Cada semana é um passo. <span class="acc">Vamos juntos.</span></h2>
<p class="sub" style="color:#CFC8BA;font-size:36px">Ficou com alguma dúvida? Me chame. Estou acompanhando a sua recuperação.</p>
<p style="margin-top:56px;font-size:30px;color:#E7BE6A;font-weight:600">Dr. Rafael Lima · Fisioterapeuta</p>
<p style="margin-top:10px;font-size:26px;color:#CFC8BA">Fisioterapia domiciliar · @fisiorafaellima</p></div>
<div class="note">Estas orientações são gerais e complementam as do seu cirurgião. Em caso de diferença, siga a equipe médica.<br>Baseado em: NICE NG157 (Joint replacement, 2020) e AAOS OrthoInfo (Total Knee Replacement).</div>'''))
for i,h in enumerate(S,1):
    open(f'c{i}.html','w').write(h)
    subprocess.run([CH,'--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars','--allow-file-access-from-files','--window-size=1080,1500','--virtual-time-budget=4000',f'--screenshot=raw_c{i}.png',f'file://{__import__("os").getcwd()}/c{i}.html'],capture_output=True)
from PIL import Image
ims=[]
for i in range(1,11):
    im=Image.open(f'raw_c{i}.png').crop((0,0,1080,1350)).convert('RGB'); im.save(f'cart_{i:02d}.jpg',quality=93); ims.append(im.resize((432,540)))
sh=Image.new('RGB',(432*5,540*2))
for k,im in enumerate(ims): sh.paste(im,((k%5)*432,(k//5)*540))
sh.save('cart_sheet.jpg',quality=85)
print('ok')
