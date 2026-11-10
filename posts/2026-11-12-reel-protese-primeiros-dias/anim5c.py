import numpy as np, math, json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FPS=30; W,H=1080,1920; SS=2; ST=1000  # stage 1000x1000 drawn at 2x
PREVIEW=len(sys.argv)>1
GOLD=(217,164,65); GOLD2=(240,196,92); CREAM=(242,237,228); DARK=(12,26,19); GREEN=(22,41,31)
RED=(196,62,52); RED2=(232,104,86); BONE=(236,226,204); BONE2=(201,186,158); OK=(96,196,120); WARN=(226,120,92)
OF='hf/fonts/Outfit.ttf'; PF='hf/fonts/Playfair.ttf'; FK={}
def fk(sz,w=800,pf=False):
    k=(sz,w,pf)
    if k not in FK:
        f=ImageFont.truetype(PF if pf else OF,sz)
        try: f.set_variation_by_axes([w])
        except Exception: pass
        FK[k]=f
    return FK[k]
def cl(u): return min(max(u,0),1)
def ease(u): u=cl(u); return 1-(1-u)**3
def eio(u): u=cl(u); return u*u*(3-2*u)
def eback(u):
    u=cl(u); c1=1.9; c3=c1+1; return 1+c3*(u-1)**3+c1*(u-1)**2
def lerp(a,b,u): return a+(b-a)*u
def shadow(lay,r=14,a=0.75):
    sh=Image.new('RGBA',lay.size,(0,0,0,0)); sh.putalpha(lay.getchannel('A').filter(ImageFilter.GaussianBlur(r)).point(lambda v:int(v*a))); sh.alpha_composite(lay); return sh

# ---------------- timeline ----------------
SEG=[('s1',1.87,7.92,'Ela colocou a prótese há poucos dias. Olha o que a gente já treina.',(1.97,7.82)),
     ('s2',12.09,20.11,'Inchaço e dor são esperados no começo. Mexer cedo, com orientação, ajuda a recuperar o movimento.',(12.19,20.01)),
     ('s3',20.73,22.45,'O objetivo da fase',(20.83,22.39)),
     ('s3b',23.22,27.32,'é dobrar, esticar e andar com segurança.',(23.30,27.22)),
     ('s4',29.20,35.40,'Alguém da família vai operar? Me manda JOELHO que eu te mando o guia da recuperação.',(29.30,35.00))]
OFF={}; t=0
for n,a,b,_,_ in SEG: OFF[n]=t; t+=b-a
TOTAL=t
words=[]
for n,a,b,txt,(s0,s1) in SEG:
    ws=txt.split(); L=sum(len(w)+1 for w in ws); tt=s0-a+OFF[n]; span=s1-s0
    for w in ws: d=span*(len(w)+1)/L; words.append((tt,tt+d,w,n)); tt+=d
def wt(seg,word):
    for a,b,w,k in words:
        if k==seg and w.strip('.,?!:').lower()==word: return a
    return OFF[seg]
def seg_at(t):
    for n,*_ in reversed(SEG):
        if t>=OFF[n]: return n
    return 's1'
blocks=[];cur=[];sg_=None
for wd in words:
    txt=' '.join(x[2] for x in cur+[wd])
    if cur and (len(txt)>17 or wd[3]!=sg_ or len(cur)>=3 or cur[-1][2][-1] in '.:,'): blocks.append(cur); cur=[]
    cur.append(wd); sg_=wd[3]
blocks.append(cur)
KEY={'prótese','dias','treina','inchaço','dor','esperados','mexer','orientação','movimento','dobrar','esticar','andar','segurança','operar','joelho','guia'}
def caption(img,t,y=1650):
    for i,bl in enumerate(blocks):
        a0=bl[0][0]-0.05; nxt=blocks[i+1][0][0] if i+1<len(blocks) else 99
        a1=nxt-0.05 if nxt-bl[-1][1]<0.6 else bl[-1][1]+0.25
        if not(a0<=t<a1): continue
        lay=Image.new('RGBA',(W,260),(0,0,0,0)); d=ImageDraw.Draw(lay)
        fin=ease((t-a0)/0.12); items=[];tw=0
        for a,b,w,_ in bl:
            act=a<=t<b; sc=1+0.14*ease((t-a)/0.12) if act else 1
            f=fk(int(72*sc),800); wd=d.textlength(w.upper(),font=f)+(30 if act else 0); items.append((w,a,b,act,sc,wd)); tw+=wd+20
        x=(W-tw+20)/2; base=150
        for w,a,b,act,sc,wd in items:
            up=w.upper(); cx=x+wd/2
            if act:
                f=fk(int(72*sc),800); d.rounded_rectangle((x,base-74*sc,x+wd,base+22),radius=18,fill=GOLD+(255,))
                d.text((cx,base),up,font=f,fill=DARK,anchor='ms')
            else:
                k=w.strip('.,?!:').lower()
                col=(GOLD2+(255,)) if (t>=b and k in KEY) else ((255,255,255,255) if t>=b else (255,255,255,130))
                d.text((cx,base),up,font=fk(72,800),fill=col,anchor='ms',stroke_width=6,stroke_fill=(0,0,0,200))
            x+=wd+20
        if fin<1: lay.putalpha(lay.getchannel('A').point(lambda v:int(v*fin)))
        img.alpha_composite(lay,(0,y-150-int((1-fin)*20))); return

# ---------------- background ----------------
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
BGBASE=np.zeros((H,W,3),np.float32)
r=np.sqrt(((xx-W*0.5)/W)**2+((yy-H*0.42)/H)**2)
for c,(a,b) in enumerate(zip((33,64,47),(9,18,13))): BGBASE[...,c]=np.clip(a+(b-a)*np.clip(r*1.9,0,1),0,255)
grid=((np.mod(xx,60)<1.2)|(np.mod(yy,60)<1.2)).astype(np.float32)*7
BGBASE+=grid[...,None]*np.array([0.6,1.0,0.8])
rng=np.random.default_rng(4); PART=rng.random((40,4))
def background(t):
    img=Image.fromarray(np.clip(BGBASE,0,255).astype(np.uint8)).convert('RGBA')
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for x,y,s,ph in PART:
        Y=(y*H-t*30*(0.4+s))%H; X=x*W+18*math.sin(t*0.7+ph*6); rr=1.5+3*s
        d.ellipse((X-rr,Y-rr,X+rr,Y+rr),fill=GOLD+(int(40+60*s),))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))
    return img

# ---------------- stage drawing (2x) ----------------
class Stage:
    def __init__(s,cx=500,cy=500,z=1.0):
        s.im=Image.new('RGBA',(ST*SS,ST*SS),(0,0,0,0)); s.d=ImageDraw.Draw(s.im); s.cx,s.cy,s.z=cx,cy,z
    def P(s,p): return ((p[0]-s.cx)*s.z+500)*SS,((p[1]-s.cy)*s.z+500)*SS
    def R(s,v): return v*s.z*SS
    def lay(s):
        l=Image.new('RGBA',s.im.size,(0,0,0,0)); return l,ImageDraw.Draw(l)
def capsule(S,d,p1,p2,w,col):
    a=S.P(p1); b=S.P(p2); ww=S.R(w)
    d.line((a,b),fill=col,width=max(1,int(ww)))
    for q in (a,b): d.ellipse((q[0]-ww/2,q[1]-ww/2,q[0]+ww/2,q[1]+ww/2),fill=col)
def circle(S,d,p,r,fill=None,outline=None,width=1):
    q=S.P(p); rr=S.R(r); d.ellipse((q[0]-rr,q[1]-rr,q[0]+rr,q[1]+rr),fill=fill,outline=outline,width=int(width*SS))
def bone(S,p1,p2,w,glow=0,end1=1.25,end2=1.25):
    d=S.d
    capsule(S,d,p1,p2,w+8,(120,104,80,255))
    for p,e in ((p1,end1),(p2,end2)): circle(S,d,p,w*e/2+4,fill=(120,104,80,255))
    capsule(S,d,p1,p2,w,BONE2+(255,))
    for p,e in ((p1,end1),(p2,end2)): circle(S,d,p,w*e/2,fill=BONE2+(255,))
    # highlight
    ax=(p2[0]-p1[0],p2[1]-p1[1]); L=math.hypot(*ax)+1e-6; nx,ny=-ax[1]/L,ax[0]/L
    off=-w*0.18
    capsule(S,d,(p1[0]+nx*off,p1[1]+ny*off),(p2[0]+nx*off,p2[1]+ny*off),w*0.45,BONE+(255,))
    if glow>0:
        l,ld=S.lay(); capsule(S,ld,p1,p2,w+30,GOLD+(int(140*glow),)); S.im.alpha_composite(l.filter(ImageFilter.GaussianBlur(S.R(14))),(0,0))
def muscle(S,p1,p2,side,base,mus,t,act=0.0,col=RED,col2=RED2,taper=(0.06,0.9)):
    ax=(p2[0]-p1[0],p2[1]-p1[1]); L=math.hypot(*ax)+1e-6; ux,uy=ax[0]/L,ax[1]/L; nx,ny=-uy*side,ux*side
    t0,t1=taper; N=24; out=[];inn=[]
    for i in range(N+1):
        u=i/N; s=lerp(t0,t1,u); bx=p1[0]+ax[0]*s; by=p1[1]+ax[1]*s
        bulge=base*mus*(math.sin(math.pi*u)**0.75)*(1+0.06*act*math.sin(t*14))
        out.append((bx+nx*(bulge+10),by+ny*(bulge+10))); inn.append((bx+nx*6,by+ny*6))
    poly=out+inn[::-1]
    d=S.d; d.polygon([S.P(p) for p in poly],fill=(120,30,28,255))
    poly2=[(lerp(a[0],b[0],0.12),lerp(a[1],b[1],0.12)) for a,b in zip(out,[inn[len(inn)-1-k] if False else inn[k] for k in range(len(inn))])]
    out2=[(lerp(o[0],i[0],0.10),lerp(o[1],i[1],0.10)) for o,i in zip(out,inn)]
    d.polygon([S.P(p) for p in out2+inn[::-1]],fill=col+(255,))
    out3=[(lerp(o[0],i[0],0.45),lerp(o[1],i[1],0.45)) for o,i in zip(out,inn)]
    out4=[(lerp(o[0],i[0],0.25),lerp(o[1],i[1],0.25)) for o,i in zip(out,inn)]
    d.polygon([S.P(p) for p in out4[2:-2]+out3[2:-2][::-1]],fill=col2+(255,))
    # fibers
    for k in range(1,6):
        f=k/6; pts=[S.P((lerp(o[0],i[0],f),lerp(o[1],i[1],f))) for o,i in zip(out,inn)]
        d.line(pts[1:-1],fill=(255,190,170,int(70+90*act*(0.5+0.5*math.sin(t*10+k)))),width=int(S.R(2.2)))
    if act>0:
        l,ld=S.lay(); ld.polygon([S.P(p) for p in poly],fill=GOLD+(int(110*act),)); S.im.alpha_composite(l.filter(ImageFilter.GaussianBlur(S.R(16))))
    return out
def tendon(S,p1,p2,w=10):
    capsule(S,S.d,p1,p2,w,(232,220,196,255))
def leg_geom(shin_deg,thigh_deg,ankle=(560,880),L1=330,L2=320):
    a=math.radians(shin_deg); knee=(ankle[0]+L2*math.sin(a),ankle[1]-L2*math.cos(a))
    b=math.radians(thigh_deg); hip=(knee[0]-L1*math.sin(b),knee[1]-L1*math.cos(b))
    return hip,knee,ankle
def draw_leg(S,shin_deg,thigh_deg,t,mus=1.0,act=0.0,ankle=(560,880),loadarrows=0.0,knee_glow=0.0,skin=False):
    hip,knee,ank=leg_geom(shin_deg,thigh_deg,ankle)
    toe=(ank[0]+120,ank[1]+20); heel=(ank[0]-30,ank[1]+25)
    if skin:
        l,ld=S.lay()
        for p1,p2,w in ((hip,knee,170*(0.85+0.15*mus)),(knee,ank,120),(heel,toe,60)): capsule(S,ld,p1,p2,w,(242,237,228,38))
        S.im.alpha_composite(l)
        l,ld=S.lay()
        for p1,p2,w in ((hip,knee,170*(0.85+0.15*mus)),(knee,ank,120)):
            a=S.P(p1); b=S.P(p2)
        S.im.alpha_composite(l)
    # hamstring (back) and calf
    ax=(knee[0]-hip[0],knee[1]-hip[1])
    muscle(S,hip,knee,1,62,mus*0.9,t,act*0.4,col=(170,52,46),col2=(210,90,76),taper=(0.08,0.85))
    muscle(S,knee,ank,1,58,0.9+0.1*mus,t,act*0.3,col=(170,52,46),col2=(210,90,76),taper=(0.08,0.7))
    bone(S,hip,knee,46)
    bone(S,knee,ank,40,end1=1.35,end2=1.2)
    # foot bones
    capsule(S,S.d,ank,toe,26,BONE2+(255,)); capsule(S,S.d,ank,heel,30,BONE2+(255,))
    # quadriceps front
    out=muscle(S,hip,knee,-1,88,mus,t,act,taper=(0.04,0.86))
    # patella + tendon
    ax2=(ank[0]-knee[0],ank[1]-knee[1]); L=math.hypot(*ax2); u=(ax2[0]/L,ax2[1]/L); n=(u[1],-u[0])
    # front normal relative to shin: rotate thigh normal
    axh=(knee[0]-hip[0],knee[1]-hip[1]); Lh=math.hypot(*axh); nh=(-axh[1]/Lh,axh[0]/Lh)
    pat=(knee[0]-nh[0]*38+axh[0]/Lh*6,knee[1]-nh[1]*38+axh[1]/Lh*6)
    tub=(knee[0]+u[0]*85+u[1]*26,knee[1]+u[1]*85-u[0]*26)
    tendon(S,out[-3],pat,16); tendon(S,pat,tub,14)
    circle(S,S.d,pat,22,fill=(120,104,80,255)); circle(S,S.d,pat,18,fill=BONE+(255,))
    if knee_glow>0:
        l,ld=S.lay(); circle(S,ld,knee,70,fill=OK+(int(120*knee_glow),)); S.im.alpha_composite(l.filter(ImageFilter.GaussianBlur(S.R(18))))
    if loadarrows>0.02:
        for k,dx in enumerate((-40,0,40)):
            sz=loadarrows
            x=knee[0]+dx*0.8+60; y0=knee[1]-150-40*sz; y1=knee[1]-40
            l,ld=S.lay()
            ld.line((S.P((x,y0)),S.P((x,y1-22*sz))),fill=WARN+(230,),width=int(S.R(8+10*sz)))
            ld.polygon([S.P((x-18-18*sz,y1-30*sz)),S.P((x+18+18*sz,y1-30*sz)),S.P((x,y1+6))],fill=WARN+(240,))
            S.im.alpha_composite(l)
    return hip,knee,ank

def put_stage(img,S,y=300,alpha=1.0,scale=1.0):
    st=S.im.resize((int(ST*scale),int(ST*scale)),Image.LANCZOS)
    if alpha<1: st.putalpha(st.getchannel('A').point(lambda v:int(v*alpha)))
    img.alpha_composite(st,(int((W-ST*scale)/2),int(y+(1-scale)*ST/2)))

def title(img,txt,t0,t,y=210,size=64,sub=None):
    if t<t0: return
    u=ease((t-t0)/0.35); lay=Image.new('RGBA',(W,240),(0,0,0,0)); d=ImageDraw.Draw(lay)
    f=fk(size,800); tw=d.textlength(txt,font=f)
    d.rounded_rectangle(((W-tw)/2-36,30,(W+tw)/2+36,30+size+44),radius=40,fill=(10,22,16,int(220*u)),outline=GOLD+(int(255*u),),width=4)
    d.text((W/2,30+(size+44)/2),txt,font=f,fill=CREAM+(int(255*u),),anchor='mm')
    img.alpha_composite(shadow(lay,12,0.5),(0,int(y-30-(1-u)*40)))
def meter(img,label,val,t0,t,x=W-330,y=560,good_down=True,col=None):
    if t<t0: return
    u=ease((t-t0)/0.3); lay=Image.new('RGBA',(300,170),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((10,10,290,160),radius=26,fill=(10,22,16,int(215*u)),outline=(255,255,255,int(90*u)),width=2)
    d.text((150,48),label,font=fk(30,700),fill=CREAM+(int(255*u),),anchor='mm')
    d.rounded_rectangle((34,92,266,124),radius=16,fill=(255,255,255,int(40*u)))
    c=col or (OK if good_down else GOLD)
    d.rounded_rectangle((34,92,34+232*max(0.04,val),124),radius=16,fill=c+(int(255*u),))
    img.alpha_composite(lay,(x,y))

# ---------------- scenes ----------------
PAT=None
PATD=1.5
def sc_hook(img,t,lt,dur):
    global PAT
    if PAT is None:
        import cv2
        cap=cv2.VideoCapture('work/pat.mp4'); PAT=[]
        while True:
            ok,fr=cap.read()
            if not ok: break
            PAT.append(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB))
    if lt<PATD:
        fr=PAT[min(len(PAT)-1,int(lt*FPS))]
        z=1.0+0.04*lt
        pim=Image.fromarray(fr).resize((int(W*z),int(H*z)),Image.BILINEAR).crop((int(W*(z-1)/2),int(H*(z-1)/2),int(W*(z-1)/2)+W,int(H*(z-1)/2)+H)).convert('RGBA')
        img.paste(pim,(0,0))
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(lay).rectangle((0,0,W,420),fill=(0,0,0,90)); img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(60)))
        title(img,'O que a musculação faz por dentro',0.0,t,y=200,size=50)
        if lt>PATD-0.25:
            v=(lt-(PATD-0.25))/0.25; fl=Image.new('RGBA',(W,H),(255,255,255,int(160*v))); img.alpha_composite(fl)
        return
    lt=lt-PATD; dur=dur-PATD
    # squat -> stand in first second, then idle subtle, zoom to knee at end
    u=eio(lt/0.9)
    shin=lerp(38,6,u); thigh=lerp(78,4,u)
    if lt>1.1:
        dep=0.5*(1-math.cos(2*math.pi*(lt-1.1)/1.6))*0.55*(1-ease((lt-(dur-1.3))/0.4))
        shin=lerp(6,38,dep); thigh=lerp(4,78,dep); act=0.4+0.6*(1-dep)
    act=1.0 if lt<1.0 else 0.6
    zz=1.25; cx,cy=520,560
    if lt>dur-0.8:
        v=eio((lt-(dur-0.8))/0.8); zz=lerp(1.25,1.7,v)
        _,knee,_=leg_geom(shin,thigh); cx=lerp(520,knee[0],v); cy=lerp(560,knee[1],v)
    S=Stage(cx,cy,zz); draw_leg(S,shin,thigh,lt,mus=1.0,act=act)
    put_stage(img,S,y=330)
    title(img,'O que a musculação faz por dentro',0.0,t,y=200,size=50)
def sc_knee(img,t,lt,dur):
    shin,thigh=6,4; grow=ease((wt('s2','forte')-OFF['s2']-0.1+0.0 - 0 + (lt-(wt('s2','forte')-OFF['s2'])) )/1.4) if True else 0
    g=ease((lt-(wt('s2','forte')-OFF['s2']))/1.4)
    mus=1.0+0.4*g
    _,knee,_=leg_geom(shin,thigh)
    S=Stage(knee[0],knee[1]-20,1.7)
    la=lerp(1.0,0.25,ease((lt-(wt('s2','menos')-OFF['s2']))/1.0)) if lt>0.3 else 0
    draw_leg(S,shin,thigh,lt,mus=mus,act=0.6+0.4*g,loadarrows=la if lt>0.25 else 0,knee_glow=g*0.8)
    put_stage(img,S,y=330)
    title(img,'Protege a articulação',0.1+OFF['s2'],t,y=200,size=58)
    meter(img,'Carga no joelho',la if lt>0.25 else 1,OFF['s2']+0.4,t,x=60,y=1240)
    # spine inset at "coluna"
    tc=wt('s2','coluna')
    if t>=tc-0.2:
        u=ease((t-tc+0.2)/0.4); lay=Image.new('RGBA',(300,420),(0,0,0,0)); d=ImageDraw.Draw(lay)
        d.rounded_rectangle((10,10,290,410),radius=30,fill=(10,22,16,int(220*u)),outline=GOLD+(int(200*u),),width=3)
        for k in range(6):
            yv=50+k*58
            d.rounded_rectangle((110,yv,190,yv+40),radius=10,fill=BONE+(int(255*u),))
            d.rounded_rectangle((116,yv+42,184,yv+52),radius=5,fill=(120,170,200,int(220*u)))
        pul=0.6+0.4*math.sin(t*8)
        for xx_ in (60,200):
            d.rounded_rectangle((xx_,40,xx_+40,390),radius=20,fill=RED+(int(230*u),))
        d.text((150,388),'coluna',font=fk(26,700),fill=GOLD2+(int(255*u),),anchor='ms')
        g2=Image.new('RGBA',lay.size,(0,0,0,0)); ImageDraw.Draw(g2).rounded_rectangle((50,40,250,390),radius=30,fill=OK+(int(90*u*pul),))
        lay.alpha_composite(g2.filter(ImageFilter.GaussianBlur(14)))
        img.alpha_composite(shadow(lay,14,0.6),(W-340-int((1-u)*200),560))
TRAB=None
def sc_bone(img,t,lt,dur):
    global TRAB
    if TRAB is None:
        r=np.random.default_rng(9); TRAB=[]
        for k in range(260):
            x=r.uniform(170,830); y=r.uniform(440,560); a=r.uniform(0,math.pi); l=r.uniform(18,46)
            TRAB.append((x,y,x+math.cos(a)*l,y+math.sin(a)*l,r.uniform(0,1)))
    S=Stage(500,500,1.0); d=S.d
    # bone outline: shaft + epiphyses
    bone(S,(160,500),(840,500),220,end1=1.35,end2=1.35)
    # cut-away interior
    l,ld=S.lay()
    ld.rounded_rectangle((*S.P((190,420)),*S.P((810,580))),radius=int(S.R(60)),fill=(70,46,40,255))
    S.im.alpha_composite(l)
    dens=lerp(0.25,1.0,ease((lt-0.6)/(dur-1.0)))
    for x0,y0,x1,y1,rk in TRAB:
        if rk>dens: continue
        d.line((S.P((x0,y0)),S.P((x1,y1))),fill=BONE+(255,),width=int(S.R(3+4*dens)))
    # stimulus waves
    for k in range(3):
        ph=((lt-0.3)*1.1-k*0.33)%1.0
        if lt<0.3: break
        x=lerp(160,840,ph)
        l,ld=S.lay(); ld.ellipse((*S.P((x-40,380)),*S.P((x+40,620))),fill=GOLD+(int(150*(1-abs(ph-0.5)*1.6)),))
        S.im.alpha_composite(l.filter(ImageFilter.GaussianBlur(S.R(20))))
    # load arrows on top
    for x in (300,500,700):
        pr=0.5+0.5*math.sin(lt*6)
        d.polygon([S.P((x-26,250+20*pr)),S.P((x+26,250+20*pr)),S.P((x,300+20*pr))],fill=GOLD+(255,))
        d.line((S.P((x,180)),S.P((x,260+20*pr))),fill=GOLD+(255,),width=int(S.R(10)))
    d.text(S.P((500,150)),'ESTÍMULO',font=fk(int(S.R(30)),800),fill=GOLD2+(255,),anchor='mm')
    put_stage(img,S,y=330)
    title(img,'Osso mais forte',OFF['s3']+0.05,t,y=200,size=62)
    meter(img,'Densidade',dens,OFF['s3']+0.5,t,x=(W-300)//2,y=1240,col=GOLD)
GLU=None
def hexa(d,S,c,r,fill):
    pts=[S.P((c[0]+r*math.cos(math.pi/3*k+math.pi/6),c[1]+r*math.sin(math.pi/3*k+math.pi/6))) for k in range(6)]; d.polygon(pts,fill=fill)
def sc_glucose(img,t,lt,dur):
    global GLU
    if GLU is None:
        r=np.random.default_rng(5); GLU=[(r.uniform(0,1),r.uniform(170,300),r.uniform(0,1)) for _ in range(26)]
    S=Stage(500,500,1.0); d=S.d
    # vessel
    d.rounded_rectangle((*S.P((40,150)),*S.P((960,320))),radius=int(S.R(80)),fill=(110,24,30,255))
    d.rounded_rectangle((*S.P((40,175)),*S.P((960,295))),radius=int(S.R(60)),fill=(150,36,40,255))
    d.text(S.P((120,130)),'SANGUE',font=fk(int(S.R(26)),800),fill=(255,160,150,255),anchor='lm')
    # muscle cell
    contr=0.5+0.5*math.sin(lt*7)
    d.rounded_rectangle((*S.P((90,470)),*S.P((910,800))),radius=int(S.R(70)),fill=(120,30,28,255))
    d.rounded_rectangle((*S.P((105,485)),*S.P((895,785))),radius=int(S.R(60)),fill=RED+(255,))
    sp=34-8*contr
    x=130
    while x<880:
        d.line((S.P((x,500)),S.P((x,770))),fill=(255,170,150,150),width=int(S.R(4)))
        x+=sp
    d.text(S.P((120,830)),'MÚSCULO',font=fk(int(S.R(26)),800),fill=(255,160,150,255),anchor='lm')
    # doors
    dv=ease((lt-0.6)/0.4)
    doors=[220,400,580,760]
    for xd in doors:
        if dv>0: d.rounded_rectangle((*S.P((xd-28,455)),*S.P((xd+28,485))),radius=int(S.R(8)),fill=GOLD+(int(255*dv),))
    # glucose
    absorbed=0
    for i,(ph,y,sp_) in enumerate(GLU):
        x=((ph+lt*0.18*(0.6+sp_))%1.0)*920+40
        if dv>0.5 and i%2==0:
            k=(lt*0.9+sp_)%1.0; xd=doors[i%4]
            yy_=lerp(y,640,k); xx_=lerp(xd,xd+(sp_-0.5)*200,max(0,k-0.4))
            if k>0.75:
                r_=lerp(16,4,(k-0.75)/0.25); c=GOLD2
                l,ld=S.lay(); circle(S,ld,(xx_,yy_),30,fill=GOLD+(120,)); S.im.alpha_composite(l.filter(ImageFilter.GaussianBlur(S.R(10))))
                circle(S,d,(xx_,yy_),r_,fill=c+(255,))
            else: hexa(d,S,(xx_,yy_),16,(250,240,220,255))
        else: hexa(d,S,(x,y),16,(250,240,220,255))
    put_stage(img,S,y=330)
    title(img,'Ajuda a glicose',OFF['s4']+0.05,t,y=200,size=62)
    meter(img,'Açúcar no sangue',lerp(0.9,0.45,ease((lt-0.8)/2.2)),OFF['s4']+0.5,t,x=(W-300)//2,y=1240)
def sc_falls(img,t,lt,dur):
    g=ease((lt-0.6)/1.6); mus=1.0+0.45*g
    wob=(1-g)*7*math.sin(lt*9)
    S=Stage(520,560,1.25)
    hip,knee,ank=leg_geom(6+wob*0.4,4+wob)
    draw_leg(S,6+wob*0.4,4+wob,lt,mus=mus,act=0.4+0.6*g,knee_glow=g*0.6)
    put_stage(img,S,y=330)
    title(img,'Menos quedas',OFF['s5']+0.05,t,y=200,size=62)
    # gauge
    u=ease((t-OFF['s5']-0.3)/0.3)
    if u>0:
        lay=Image.new('RGBA',(340,230),(0,0,0,0)); d=ImageDraw.Draw(lay)
        d.rounded_rectangle((10,10,330,220),radius=28,fill=(10,22,16,int(215*u)),outline=(255,255,255,int(90*u)),width=2)
        d.text((170,46),'Risco de queda',font=fk(30,700),fill=CREAM+(int(255*u),),anchor='mm')
        cx,cy,rr=170,190,110
        for k,(a0,a1,c) in enumerate(((180,240,OK),(240,300,GOLD),(300,360,WARN))):
            d.arc((cx-rr,cy-rr,cx+rr,cy+rr),a0,a1,fill=c+(int(255*u),),width=22)
        ang=math.radians(lerp(330,205,g)); d.line((cx,cy,cx+math.cos(ang)*90,cy+math.sin(ang)*90),fill=CREAM+(int(255*u),),width=8)
        d.ellipse((cx-12,cy-12,cx+12,cy+12),fill=CREAM+(int(255*u),))
        img.alpha_composite(lay,(W-380,1000))
def sc_oms(img,t,lt,dur):
    lay=Image.new('RGBA',(W,1100),(0,0,0,0)); d=ImageDraw.Draw(lay)
    u=ease(lt/0.4)
    # OMS badge
    d.ellipse((W/2-110,30,W/2+110,250),fill=(10,22,16,int(230*u)),outline=GOLD+(int(255*u),),width=6)
    d.text((W/2,140),'OMS',font=fk(78,800),fill=GOLD2+(int(255*u),),anchor='mm')
    days=['S','T','Q','Q','S','S','D']; t2=wt('s6','duas')-OFF['s6']
    for i,dn in enumerate(days):
        x=W/2-3*130+i*130; y=420; v=ease((lt-0.2-i*0.05)/0.3)
        d.rounded_rectangle((x-55,y-70,x+55,y+70),radius=28,fill=(255,255,255,int(30*v)),outline=(255,255,255,int(120*v)),width=2)
        d.text((x,y-30),dn,font=fk(44,800),fill=CREAM+(int(255*v),),anchor='mm')
        if i in (1,3):
            c=ease((lt-t2-(0 if i==1 else 0.35))/0.3)
            if c>0:
                d.ellipse((x-28,y+4,x+28,y+60),fill=GOLD+(int(255*c),))
                d.line([(x-13,y+33),(x-3,y+44),(x+15,y+20)],fill=DARK+(int(255*c),),width=7,joint='curve')
    ti=wt('s6','qualquer')-OFF['s6']
    for i,a in enumerate(['20+','40+','60+','80+']):
        v=eback((lt-ti-i*0.12)/0.35) if lt>ti+i*0.12 else 0
        if v<=0: continue
        x=W/2-3*110+i*220-100+100; y=700
        f=fk(int(54*max(0.3,v)),800)
        d.rounded_rectangle((x-90,y-50,x+90,y+50),radius=50,fill=GOLD+(255,))
        d.text((x,y),a,font=f,fill=DARK,anchor='mm')
    if lt>ti: d.text((W/2,820),'anos',font=fk(38,700),fill=CREAM+(220,),anchor='mm')
    img.alpha_composite(shadow(lay,12,0.5),(0,330))
    title(img,'2x por semana',OFF['s6']+t2-0.2,t,y=200,size=62)
def sc_cta(img,t,lt,dur):
    u=ease(lt/0.35); x0,y0,w,h=250,360+int((1-u)*700),580,900
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((x0,y0,x0+w,y0+h),radius=70,fill=(11,21,16,255),outline=GOLD+(255,),width=6)
    sx,sy,sw,sh=x0+20,y0+20,w-40,h-40
    d.rounded_rectangle((sx,sy,sx+sw,sy+sh),radius=54,fill=(246,240,229,255))
    d.ellipse((sx+30,sy+40,sx+100,sy+110),fill=GREEN); d.text((sx+65,sy+76),'R',font=fk(36,800),fill=GOLD2,anchor='mm')
    d.text((sx+120,sy+62),'fisiorafaellima',font=fk(32,800),fill=GREEN,anchor='lm'); d.text((sx+120,sy+96),'Direct',font=fk(24,600),fill=(90,110,100),anchor='lm')
    d.line((sx+20,sy+140,sx+sw-20,sy+140),fill=(220,210,195),width=2)
    MSG='FORÇA'; ty=wt('s7','força')-OFF['s7']-0.3; n=int(max(0,min(len(MSG),(lt-ty)/0.12)))
    sent=lt>ty+0.9
    d.rounded_rectangle((sx+20,sy+sh-100,sx+sw-20,sy+sh-24),radius=38,fill=(255,255,255),outline=(200,190,175),width=2)
    if not sent: d.text((sx+50,sy+sh-62),MSG[:n]+('|' if int(lt*4)%2==0 else ''),font=fk(36,800),fill=GREEN,anchor='lm')
    if sent:
        v=ease((lt-ty-0.9)/0.25); bx=sx+sw-40
        d.rounded_rectangle((bx-200,sy+200,bx,sy+280),radius=40,fill=GOLD+(int(255*v),)); d.text((bx-100,sy+240),'FORÇA',font=fk(38,800),fill=DARK+(int(255*v),),anchor='mm')
    tr=wt('s7','três')-OFF['s7']
    if lt>tr:
        v=ease((lt-tr)/0.3); by=sy+320
        d.rounded_rectangle((sx+30,by,sx+sw-60,by+300),radius=30,fill=(22,41,31,int(255*v)))
        d.text((sx+60,by+40),'PDF',font=fk(26,800),fill=GOLD2+(int(255*v),),anchor='lm')
        d.text((sx+60,by+100),'Força em casa',font=fk(44,800,True),fill=CREAM+(int(255*v),),anchor='lm')
        for k,ex in enumerate(['1  Sentar e levantar','2  Ponte de quadril','3  Flexão na parede']):
            d.text((sx+60,by+165+k*40),ex,font=fk(28,600),fill=(207,200,186,int(255*v)),anchor='lm')
    sh_=Image.new('RGBA',(W,H),(0,0,0,0)); sh_.putalpha(lay.getchannel('A').filter(ImageFilter.GaussianBlur(24)).point(lambda v:int(v*0.5)))
    img.alpha_composite(sh_,(0,16)); img.alpha_composite(lay)
    title(img,'Me manda FORÇA',OFF['s7']+0.05,t,y=200,size=62)
import cv2
def pill(img,txt,t0,t,x,y,col=GOLD,fg=DARK,size=40):
    if t<t0: return
    u=eback((t-t0)/0.35) if t-t0<0.35 else 1
    f=fk(int(size*max(0.3,u)),800); lay=Image.new('RGBA',(W,140),(0,0,0,0)); d=ImageDraw.Draw(lay)
    tw=d.textlength(txt,font=f); d.rounded_rectangle((x-tw/2-30,20,x+tw/2+30,20+size+34),radius=40,fill=col+(255,))
    d.text((x,20+(size+34)/2),txt,font=f,fill=fg,anchor='mm'); img.alpha_composite(shadow(lay,10,0.5),(0,int(y)))
HF='Caveat.ttf'; HK={}
def hfont(sz,wgt=700):
    k=(sz,wgt)
    if k not in HK:
        f=ImageFont.truetype(HF,sz)
        try: f.set_variation_by_axes([wgt])
        except Exception: pass
        HK[k]=f
    return HK[k]
INK=(22,41,31); GOLDI=(196,140,40); REDI=(205,70,55); BLUEI=(70,120,170)
class Reader:
    def __init__(s,p): s.cap=cv2.VideoCapture(p); s.cache={}; s.n=int(s.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    def get(s,sec):
        idx=min(s.n-1,max(0,int(round(sec*FPS))))
        if idx in s.cache: return s.cache[idx]
        s.cap.set(cv2.CAP_PROP_POS_FRAMES,idx); ok,fr=s.cap.read()
        if not ok:
            s.cap.set(cv2.CAP_PROP_POS_FRAMES,idx-3); ok,fr=s.cap.read()
        fr=cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)
        if len(s.cache)>20: s.cache.pop(next(iter(s.cache)))
        s.cache[idx]=fr; return fr
LEG=Reader('work/legq.mp4'); LEGLEN=11.6
def legsec(s):
    s=s%(LEGLEN-0.2); return s
def leg_full(sec,z=1.0):
    fr=LEG.get(legsec(sec)); h,w=fr.shape[:2]
    cw=int(1080/z); ch=int(1920/z); cx=int(0.36*w); cy=int(0.45*h)
    x0=max(0,min(w-cw,cx-cw//2)); y0=max(0,min(h-ch,cy-ch//2))
    return cv2.resize(fr[y0:y0+ch,x0:x0+cw],(W,H),interpolation=cv2.INTER_AREA)
def leg_half(sec):
    fr=LEG.get(legsec(sec)); h,w=fr.shape[:2]
    k=1.65; cw=int(1080*k); ch=int(950*k); cx=int(0.40*w); cy=int(0.40*h)
    x0=max(0,min(w-cw,cx-cw//2)); y0=max(0,min(h-ch,cy-ch//2))
    return Image.fromarray(cv2.resize(fr[y0:y0+ch,x0:x0+cw],(W,950),interpolation=cv2.INTER_AREA)).convert('RGBA')
# ---------- whiteboard ----------
rngp=np.random.default_rng(11)
PAPER=np.full((950,W,3),(247,243,234),np.float32)
PAPER+=rngp.normal(0,3.2,(950,W,1)).astype(np.float32)
PAPER=Image.fromarray(np.clip(PAPER,0,255).astype(np.uint8)).convert('RGBA')
def plen(pts):
    return [0]+list(np.cumsum([math.hypot(pts[i+1][0]-pts[i][0],pts[i+1][1]-pts[i][1]) for i in range(len(pts)-1)]))
def partial(pts,u):
    L=plen(pts); tot=L[-1]; tgt=tot*cl(u); out=[pts[0]]
    for i in range(1,len(pts)):
        if L[i]<=tgt: out.append(pts[i])
        else:
            a=(tgt-L[i-1])/max(1e-6,L[i]-L[i-1]); out.append((lerp(pts[i-1][0],pts[i][0],a),lerp(pts[i-1][1],pts[i][1],a))); break
    return out
def jitter(pts,amp=1.6,seed=0):
    r=np.random.default_rng(seed); return [(x+r.normal(0,amp),y+r.normal(0,amp)) for x,y in pts]
def arc(cx,cy,rx,ry,a0,a1,n=40): return [(cx+rx*math.cos(math.radians(a0+(a1-a0)*i/n)),cy+ry*math.sin(math.radians(a0+(a1-a0)*i/n))) for i in range(n+1)]
def line(a,b,n=12): return [(lerp(a[0],b[0],i/n),lerp(a[1],b[1],i/n)) for i in range(n+1)]
class Board:
    def __init__(s): s.im=PAPER.copy(); s.d=ImageDraw.Draw(s.im); s.tip=None
    def stroke(s,pts,t0,dur,t,col=INK,w=7,seed=0):
        if t<t0: return
        u=(t-t0)/dur; p=partial(jitter(pts,1.2,seed),u)
        if len(p)>1: s.d.line(p,fill=col+(255,),width=w,joint='curve')
        if u<1: s.tip=p[-1]
    def text(s,txt,t0,t,xy,size=58,col=INK,cps=16,anchor='lm'):
        if t<t0: return
        n=int((t-t0)*cps); sub=txt[:n]
        if not sub: return
        f=hfont(size); s.d.text(xy,sub,font=f,fill=col+(255,),anchor=anchor)
        if n<len(txt):
            bb=s.d.textbbox(xy,sub,font=f,anchor=anchor); s.tip=(bb[2],bb[3]-size*0.25)
    def fill(s,poly,a,col):
        if a<=0: return
        l=Image.new('RGBA',s.im.size,(0,0,0,0)); ImageDraw.Draw(l).polygon(poly,fill=col+(int(255*cl(a)),)); s.im.alpha_composite(l)
def pen(img,tip,oy):
    if tip is None: return
    x,y=tip[0],tip[1]+oy
    p=Image.new('RGBA',(300,300),(0,0,0,0)); d=ImageDraw.Draw(p)
    # marker pointing down-left, tip at (40,260)
    d.polygon([(40,260),(58,226),(74,242)],fill=(30,30,30,255))
    d.polygon([(58,226),(74,242),(250,66),(234,50)],fill=INK+(255,))
    d.polygon([(234,50),(250,66),(282,34),(266,18)],fill=GOLD+(255,))
    d.line([(66,234),(242,58)],fill=(255,255,255,70),width=4)
    sh=Image.new('RGBA',(300,300),(0,0,0,0)); sh.putalpha(p.getchannel('A').filter(ImageFilter.GaussianBlur(6)).point(lambda v:int(v*0.35)))
    img.alpha_composite(sh,(int(x-40+10),int(y-260+14))); img.alpha_composite(p,(int(x-40),int(y-260)))
# knee drawing parts (board coords 1080x950)
KX,KY=330,330
FEM_L=line((KX-80,10),(KX-95,KY-70))+arc(KX,KY-60,110,80,180,90,20)[1:]
FEM_R=line((KX+80,10),(KX+95,KY-70))+arc(KX,KY-60,110,80,0,90,20)[1:]
FEMCOMP=arc(KX,KY-55,128,98,170,10,40)
INSERT=line((KX-100,KY+48),(KX+100,KY+48))
TRAY=line((KX-112,KY+66),(KX+112,KY+66))
STEM=line((KX,KY+66),(KX,KY+150))
TIB_L=line((KX-100,KY+74),(KX-70,690))
TIB_R=line((KX+100,KY+74),(KX+72,690))
PAT=arc(KX+165,KY-95,32,55,0,360,40)
SWELL=[(KX+10+235*math.cos(a)*(1+0.07*math.sin(5*a)),KY-10+185*math.sin(a)*(1+0.07*math.cos(4*a))) for a in np.linspace(0,2*math.pi,60)]
ZIG=[(KX-250,KY-150),(KX-225,KY-195),(KX-200,KY-140),(KX-175,KY-190),(KX-150,KY-135)]
BENDARC=arc(KX,KY+40,330,330,-35,40,30)
def board_explain(t,lt):
    B=Board(); T0=OFF['s2']
    def at(x): return T0+x
    B.stroke(FEM_L,at(0.05),0.6,t,seed=1); B.stroke(FEM_R,at(0.35),0.6,t,seed=2)
    B.stroke(TIB_L,at(0.7),0.5,t,seed=3); B.stroke(TIB_R,at(0.9),0.5,t,seed=4)
    B.stroke(PAT,at(1.2),0.4,t,seed=5)
    B.stroke(FEMCOMP,at(1.45),0.5,t,col=GOLDI,w=12,seed=6); B.stroke(INSERT,at(1.85),0.25,t,col=(150,150,150),w=10,seed=7)
    B.stroke(TRAY,at(2.0),0.3,t,col=GOLDI,w=12,seed=8); B.stroke(STEM,at(2.2),0.25,t,col=GOLDI,w=12,seed=9)
    pa=ease((t-at(1.7))/0.5)
    if pa>0:
        crest=arc(KX,KY-55,130,100,170,10,40)+arc(KX,KY-55,104,78,10,170,40)
        B.fill(crest,pa,(196,202,212)); B.fill(arc(KX,KY-58,124,94,150,30,20)+arc(KX,KY-58,114,86,30,150,20),pa*0.9,(240,244,250))
        B.fill([(KX-100,KY+38),(KX+100,KY+38),(KX+100,KY+56),(KX-100,KY+56)],pa,(232,238,248))
        B.fill([(KX-112,KY+58),(KX+112,KY+58),(KX+112,KY+76),(KX-112,KY+76)],pa,(186,192,204))
        B.fill([(KX-16,KY+76),(KX+16,KY+76),(KX+10,KY+150),(KX-10,KY+150)],pa,(186,192,204))
        B.stroke(crest+[crest[0]],at(1.7),0.01,t,col=(110,116,128),w=4,seed=60)
    tl_=at(2.35)
    if t>=tl_:
        u=ease((t-tl_)/0.3)
        B.stroke(line((KX+130,KY-40),(600,40)),tl_,0.3,t,col=GOLDI,w=6,seed=61)
        B.stroke(line((KX+115,KY+66),(600,40)),tl_+0.1,0.3,t,col=GOLDI,w=6,seed=62)
        if u>0.6:
            B.d.rounded_rectangle((600,0,940,86),radius=20,fill=GOLD+(255,))
            B.d.text((770,44),'PRÓTESE',font=fk(52,800),fill=DARK,anchor='mm')
        B.text('metal + plástico',tl_+0.4,t,(612,128),size=50,col=(110,116,128),cps=26)
    ti=wt('s2','inchaço')-0.2
    if t>=ti:
        a=ease((t-ti-0.8)/0.6); B.fill(SWELL,0.12*a,(120,170,215))
        B.stroke(SWELL,ti,0.8,t,col=BLUEI,w=6,seed=10)
        B.text('inchaço',ti+0.6,t,(640,230),size=64,col=BLUEI)
    td=wt('s2','dor')-0.1
    B.stroke(ZIG,td,0.35,t,col=REDI,w=8,seed=11); B.text('dor',td+0.3,t,(40,KY-230),size=64,col=REDI)
    te=wt('s2','esperados')
    B.text('esperados no começo',te,t,(640,300),size=54,col=INK,cps=22)
    tm=wt('s2','mexer')-0.1
    if t>=tm:
        B.stroke(BENDARC,tm,0.6,t,col=GOLDI,w=8,seed=12)
        p=BENDARC[-1]
        if t>tm+0.6: B.d.polygon([(p[0]-28,p[1]-6),(p[0]+8,p[1]-30),(p[0]+10,p[1]+12)],fill=GOLDI+(255,))
        B.text('mexer cedo,',tm+0.4,t,(700,450),size=60,col=INK,cps=20)
        B.text('com orientação',tm+0.9,t,(700,520),size=60,col=INK,cps=20)
    return B
ICON={}
def board_goals(t,lt):
    B=Board(); T0=OFF['s3']
    B.text('Objetivos desta fase',T0+0.05,t,(W/2,90),size=74,col=INK,cps=24,anchor='mm')
    B.stroke(line((300,140),(780,140)),T0+0.7,0.4,t,col=GOLDI,w=6,seed=20)
    items=[('dobrar',wt('s3b','dobrar')),('esticar',wt('s3b','esticar')),('andar com segurança',wt('s3b','andar'))]
    for i,(lab,tk) in enumerate(items):
        y=210+i*155; tk=tk-0.25
        box=[(120,y-45),(210,y-45),(210,y+45),(120,y+45),(120,y-45)]
        B.stroke(box,tk,0.35,t,seed=30+i)
        # doodles
        if i==0: dood=line((280,y+40),(340,y-40))+line((340,y-40),(420,y+40))[1:]
        elif i==1: dood=line((270,y+20),(430,y+20))
        else: dood=arc(300,y,18,28,0,360,20)+arc(380,y-20,18,28,0,360,20)
        B.stroke(dood,tk+0.2,0.35,t,col=GOLDI,w=8,seed=40+i)
        B.text(lab,tk+0.35,t,(470,y),size=66,col=INK,cps=20)
        chk=[(135,y),(160,y+28),(200,y-30)]
        B.stroke(chk,tk+0.9,0.25,t,col=(60,150,90),w=12,seed=50+i)
    B.text('cada caso tem seu tempo, com liberação do cirurgião',T0+1.0,t,(W/2,690),size=42,col=(110,100,85),cps=40,anchor='mm')
    return B
def split(img,t,B,vsec):
    img.paste(leg_half(vsec),(0,0)); img.paste(B.im,(0,970))
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(lay).rectangle((0,950,W,970),fill=GOLD+(255,)); img.alpha_composite(lay)
    pen(img,B.tip,970)
def tag(img,txt,y=860):
    lay=Image.new('RGBA',(W,140),(0,0,0,0)); d=ImageDraw.Draw(lay); f=fk(34,800); tw=d.textlength(txt,font=f)
    d.rounded_rectangle((40,20,40+tw+50,80),radius=30,fill=(0,0,0,150)); d.text((65,50),txt,font=f,fill=CREAM,anchor='lm'); img.alpha_composite(lay,(0,y))
def leg_fit(sec,z=1.0):
    fr=LEG.get(legsec(sec)); h,w=fr.shape[:2]
    bg=cv2.resize(fr[:,int(w*0.2):int(w*0.2)+int(h*1080/1920)],(W//4,H//4)); bg=cv2.GaussianBlur(cv2.resize(bg,(W,H)),(0,0),25); bg=(bg*0.45).astype(np.uint8)
    FW=int(1300*z); FH=int(FW*h/w); fg=cv2.resize(fr,(FW,FH),interpolation=cv2.INTER_AREA)
    x0=int(0.45*FW-540); fg=fg[:,x0:x0+1080]; y0=(H-FH)//2
    bg[y0:y0+FH]=fg; return bg
def sc1(img,t,lt,dur):
    img.paste(Image.fromarray(leg_fit(lt,1.0+0.02*lt)).convert('RGBA'),(0,0))
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rectangle((0,0,W,420),fill=(0,0,0,110)); d.rectangle((0,1460,W,H),fill=(0,0,0,150)); img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(70)))
    title(img,'Prótese de joelho, dias depois',0.0,t,y=200,size=54)
    tp=wt('s1','olha')-0.1
    if t>=tp:
        # hand-drawn circle around knee
        l=Image.new('RGBA',(W,H),(0,0,0,0)); dd=ImageDraw.Draw(l)
        u=ease((t-tp)/0.6); pts=partial(jitter(arc(400,780,170,130,200,560,60),2,3),u)
        if len(pts)>1: dd.line(pts,fill=GOLD+(255,),width=10,joint='curve')
        if u>=1: dd.text((560,630),'joelho com prótese',font=hfont(78),fill=GOLD2+(255,),anchor='lm')
        img.alpha_composite(shadow(l,8,0.5))
OMNI=Reader('work/omnip.mp4')
def board_notes(t):
    B=Board(); T0=OFF['s2']
    B.stroke(SWELLI,T0+0.3,0.6,t,col=BLUEI,w=6,seed=70); B.fill(SWELLI,0.15*ease((t-T0-0.9)/0.4),(120,170,215))
    B.text('inchaço',T0+0.5,t,(270,90),size=72,col=BLUEI,cps=18)
    B.stroke(ZIGI,wt('s2','dor')-0.1,0.35,t,col=REDI,w=9,seed=71)
    B.text('dor',wt('s2','dor')+0.1,t,(270,215),size=72,col=REDI,cps=14)
    B.text('esperados no começo',wt('s2','esperados'),t,(560,150),size=58,col=INK,cps=22)
    tm=wt('s2','mexer')-0.1
    B.stroke(ARCI,tm,0.5,t,col=GOLDI,w=9,seed=72)
    if t>tm+0.5:
        p=ARCI[-1]; B.d.polygon([(p[0]-12,p[1]-30),(p[0]+22,p[1]-4),(p[0]-18,p[1]+12)],fill=GOLDI+(255,))
    B.text('mexer cedo,',tm+0.3,t,(270,390),size=72,col=INK,cps=20)
    B.text('com orientação',tm+0.8,t,(270,470),size=72,col=INK,cps=20)
    return B
SWELLI=[(170+70*math.cos(a)*(1+0.08*math.sin(5*a)),95+55*math.sin(a)*(1+0.08*math.cos(4*a))) for a in np.linspace(0,2*math.pi,40)]
ZIGI=[(110,240),(140,190),(165,245),(195,195),(225,245)]
ARCI=arc(170,440,90,90,200,360,30)
def sc2(img,t,lt,dur):
    blurbg(img)
    fr=OMNI.get(0.5+lt); img.paste(Image.fromarray(fr).convert('RGBA'),(0,330))
    B=board_notes(t); img.paste(B.im,(0,970))
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); d.rectangle((0,950,W,970),fill=GOLD+(255,)); d.rectangle((0,326,W,330),fill=GOLD+(255,)); img.alpha_composite(lay)
    pen(img,B.tip,970)
    title(img,'Joelho com prótese',OFF['s2']+0.05,t,y=170,size=58)
    tp=OFF['s2']+4.6
    if t>=tp:
        u=ease((t-tp)/0.35); l=Image.new('RGBA',(W,H),(0,0,0,0)); dd=ImageDraw.Draw(l)
        dd.line([(600,600),(lerp(600,780,u),lerp(600,470,u))],fill=GOLD+(255,),width=6)
        dd.ellipse((580,580,620,620),outline=GOLD+(255,),width=6)
        img.alpha_composite(shadow(l,6,0.5))
        pill(img,'PRÓTESE: metal + plástico',tp,t,770,380,col=GOLD,fg=DARK,size=38)
    ia_badge(img,x=40,y=880)
def ia_badge(img,x=40,y=1530):
    lay=Image.new('RGBA',(120,60),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((4,4,116,56),radius=26,fill=(0,0,0,120),outline=(255,255,255,170),width=2)
    d.text((60,30),'IA',font=fk(28,800),fill=(255,255,255,230),anchor='mm'); img.alpha_composite(lay,(x,y))
BGB=cv2.GaussianBlur(cv2.resize(cv2.cvtColor(cv2.imread('../forca1/in3d/3d1.jpg'),cv2.COLOR_BGR2RGB),(W,H)),(0,0),20); BGB=(BGB*0.35).astype(np.uint8)
def blurbg(img): img.paste(Image.fromarray(BGB).convert('RGBA'),(0,0))
def sc3(img,t,lt,dur):
    B=board_goals(t,lt); split(img,t,B,2.0+lt); tag(img,'Fase inicial · pós-operatório',y=20)
CART=Image.open('in/cart1.jpg').convert('RGBA').resize((300,375))
def sc4(img,t,lt,dur):
    img.paste(Image.fromarray(cv2.GaussianBlur(leg_full(8.6+lt*0.3),(0,0),18)//3).convert('RGBA'),(0,0))
    title(img,'Me manda JOELHO',OFF['s4']+0.05,t,y=200,size=62)
    tq=wt('s4','alguém')-0.05
    if t>=tq: pill(img,'Alguém da família vai operar?',tq,t,W/2,330,col=GOLD,fg=DARK,size=44)
    u=ease((lt-0.4)/0.35); x0,y0,w,h=250,500+int((1-u)*900),580,860
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((x0,y0,x0+w,y0+h),radius=70,fill=(11,21,16,255),outline=GOLD+(255,),width=6)
    sx,sy,sw,sh=x0+20,y0+20,w-40,h-40
    d.rounded_rectangle((sx,sy,sx+sw,sy+sh),radius=54,fill=(246,240,229,255))
    d.ellipse((sx+30,sy+40,sx+100,sy+110),fill=GREEN); d.text((sx+65,sy+76),'R',font=fk(36,800),fill=GOLD2,anchor='mm')
    d.text((sx+120,sy+62),'fisiorafaellima',font=fk(32,800),fill=GREEN,anchor='lm'); d.text((sx+120,sy+96),'Direct',font=fk(24,600),fill=(90,110,100),anchor='lm')
    d.line((sx+20,sy+140,sx+sw-20,sy+140),fill=(220,210,195),width=2)
    MSG='JOELHO'; ty=wt('s4','joelho')-OFF['s4']-0.4; n=int(max(0,min(len(MSG),(lt-ty)/0.09)))
    sent=lt>ty+0.7
    d.rounded_rectangle((sx+20,sy+sh-100,sx+sw-20,sy+sh-24),radius=38,fill=(255,255,255),outline=(200,190,175),width=2)
    if not sent: d.text((sx+50,sy+sh-62),MSG[:n]+('|' if int(lt*4)%2==0 else ''),font=fk(36,800),fill=GREEN,anchor='lm')
    img.alpha_composite(lay)
    if sent:
        v=ease((lt-ty-0.7)/0.25); bx=sx+sw-40; l2=Image.new('RGBA',(W,H),(0,0,0,0)); d2=ImageDraw.Draw(l2)
        d2.rounded_rectangle((bx-220,sy+170,bx,sy+250),radius=40,fill=GOLD+(int(255*v),)); d2.text((bx-110,sy+210),'JOELHO',font=fk(38,800),fill=DARK+(int(255*v),),anchor='mm')
        img.alpha_composite(l2)
        if lt>ty+1.3:
            v=ease((lt-ty-1.3)/0.3); c=CART.copy(); c.putalpha(c.getchannel('A').point(lambda a:int(a*v)))
            img.alpha_composite(c,(sx+60,sy+290))
def sc3b(img,t,lt,dur): sc3(img,t,t-OFF['s3'],dur)
SC={'s1':sc1,'s2':sc2,'s3':sc3,'s3b':sc3b,'s4':sc4}
DUR={n:b-a for n,a,b,_,_ in SEG}

def frame(t):
    img=background(t); n=seg_at(t); lt=t-OFF[n]
    SC[n](img,t,lt,DUR[n])
    # loop: last 0.35s blend toward hook start
    caption(img,t,y=(1660 if n in ('s1','s2','s4') else 915))
    lay=Image.new('RGBA',(W,12),(0,0,0,0)); d=ImageDraw.Draw(lay); d.rectangle((0,0,W,6),fill=(255,255,255,50)); d.rectangle((0,0,W*t/TOTAL,6),fill=GOLD+(230,)); img.alpha_composite(lay)
    rgb=np.array(img.convert('RGB')).astype(np.float32)
    dt=min(abs(t-OFF[k]) for k in OFF if OFF[k]>0)
    if dt<0.07: rgb=rgb+(1-dt/0.07)*40
    if t>TOTAL-0.35:
        first=np.array(frame0).astype(np.float32); v=(t-(TOTAL-0.35))/0.35; rgb=rgb*(1-v)+first*v
    return np.clip(rgb,0,255).astype(np.uint8)
frame0=None
if __name__=='__main__':
    json.dump({'OFF':OFF,'TOTAL':TOTAL,'words':words},open('work/tl.json','w'),ensure_ascii=False)
    _f=frame.__globals__
    frame0=Image.fromarray(np.zeros((H,W,3),np.uint8)); frame0=Image.fromarray(frame(0.0))
    pts=[float(x) for x in sys.argv[1].split(',')] if PREVIEW else None
    proc=None
    if not PREVIEW: proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','work/video5c.mp4'],stdin=subprocess.PIPE)
    N=int(round(TOTAL*FPS))
    for fi in range(N):
        t=fi/FPS
        if PREVIEW and not any(abs(t-p)<0.5/FPS for p in pts): continue
        out=frame(t)
        if PREVIEW: Image.fromarray(out).resize((540,960)).save('work/pv_%05.2f.jpg'%t,quality=85)
        else: proc.stdin.write(out.tobytes())
    if proc: proc.stdin.close(); proc.wait()
    print('done',N,TOTAL,OFF)
