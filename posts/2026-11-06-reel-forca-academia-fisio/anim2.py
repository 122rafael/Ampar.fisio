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
SEG=[('s1',2.76,8.19,'Academia ou fisioterapia? Na verdade, um prepara o outro.',(2.86,8.09)),
     ('s2',8.95,12.19,'A fisioterapia avalia onde está a dor e por quê.',(9.05,12.09)),
     ('s3',13.01,19.83,'Adapta o exercício pro seu corpo: depois da cirurgia, com artrose, com medo de se mexer.',(13.11,19.73)),
     ('s4',21.01,25.89,'Ensina a técnica e define quanto e quando aumentar.',(21.11,25.79)),
     ('s5',27.98,32.22,'Quando a dor está controlada, você vai pra musculação com segurança.',(28.08,32.12)),
     ('s7',32.93,37.30,'Não sabe por onde começar? Me manda FORÇA no direct!',(33.03,36.65))]
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
KEY={'academia','fisioterapia','prepara','dor','cirurgia','artrose','medo','técnica','aumentar','musculação','segurança','força'}
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
class Reader:
    def __init__(s,p): s.cap=cv2.VideoCapture(p); s.cache={}
    def get(s,sec):
        idx=max(0,int(round(sec*FPS)))
        if idx in s.cache: return s.cache[idx]
        s.cap.set(cv2.CAP_PROP_POS_FRAMES,idx); ok,fr=s.cap.read()
        if not ok:
            s.cap.set(cv2.CAP_PROP_POS_FRAMES,idx-3); ok,fr=s.cap.read()
        fr=cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)
        if len(s.cache)>30: s.cache.pop(next(iter(s.cache)))
        s.cache[idx]=fr; return fr
RD={k:Reader(f'work/{k}p.mp4') for k in ('agach','joelho','eletro')}
def vid(img,k,sec,z=1.0,cy=0.5):
    fr=RD[k].get(sec)
    if z!=1.0:
        h,w=fr.shape[:2]; nw,nh=int(w/z),int(h/z); x0=(w-nw)//2; y0=int((h-nh)*cy)
        fr=cv2.resize(fr[y0:y0+nh,x0:x0+nw],(W,H),interpolation=cv2.INTER_CUBIC)
    img.paste(Image.fromarray(fr).convert('RGBA'),(0,0))
def vign(img):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rectangle((0,0,W,420),fill=(0,0,0,110)); d.rectangle((0,1460,W,H),fill=(0,0,0,150))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(70)))
def ia_badge(img):
    lay=Image.new('RGBA',(120,60),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((4,4,116,56),radius=26,fill=(0,0,0,120),outline=(255,255,255,170),width=2)
    d.text((60,30),'IA',font=fk(28,800),fill=(255,255,255,230),anchor='mm'); img.alpha_composite(lay,(40,1530))
def pill(img,txt,t0,t,x,y,col=GOLD,fg=DARK,size=40):
    if t<t0: return
    u=eback((t-t0)/0.35) if t-t0<0.35 else 1
    f=fk(int(size*max(0.3,u)),800); lay=Image.new('RGBA',(W,140),(0,0,0,0)); d=ImageDraw.Draw(lay)
    tw=d.textlength(txt,font=f); d.rounded_rectangle((x-tw/2-30,20,x+tw/2+30,20+size+34),radius=40,fill=col+(255,))
    d.text((x,20+(size+34)/2),txt,font=f,fill=fg,anchor='mm'); img.alpha_composite(shadow(lay,10,0.5),(0,int(y)))
S3D=cv2.cvtColor(cv2.imread('in3d/3d2.jpg'),cv2.COLOR_BGR2RGB)
BG3=cv2.cvtColor(cv2.imread('in3d/3d1.jpg'),cv2.COLOR_BGR2RGB)
BGB=cv2.GaussianBlur(cv2.resize(BG3,(W,H)),(0,0),20); BGB=(BGB*0.35).astype(np.uint8)
def blurbg(img): img.paste(Image.fromarray(BGB).convert('RGBA'),(0,0))
def sc1(img,t,lt,dur):
    SPLIT=4.4
    if lt<SPLIT:
        # top: 3D still (academia) ken burns; bottom: real electrostim (fisioterapia)
        z=1.5+0.15*lt/SPLIT; h,w=S3D.shape[:2]
        cw=w/z*1.0; ch=cw*(950/1080); cx,cy=w*0.62,h*0.36
        crop=S3D[int(cy-ch/2):int(cy+ch/2),int(cx-cw/2):int(cx+cw/2)]
        top=Image.fromarray(cv2.resize(crop,(W,950),interpolation=cv2.INTER_CUBIC)).convert('RGBA')
        g=Image.new('RGBA',(W,950),(0,0,0,0)); ImageDraw.Draw(g).ellipse((380,150,820,700),fill=GOLD+(int(70+50*math.sin(lt*6)),)); top.alpha_composite(g.filter(ImageFilter.GaussianBlur(80)))
        el=RD['eletro'].get(lt); bot=Image.fromarray(el).convert('RGBA').crop((0,485,W,485+950))
        img.paste(top,(0,0)); img.paste(bot,(0,970))
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); d.rectangle((0,950,W,970),fill=GOLD+(255,)); img.alpha_composite(lay)
        pill(img,'ACADEMIA',0.15,t,250,830,col=DARK,fg=GOLD2,size=40)
        pill(img,'FISIOTERAPIA',0.45,t,W-280,975,col=GOLD,fg=DARK,size=40)
        u=eback(lt/0.4) if lt<0.4 else 1; r=70*u
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
        d.ellipse((W/2-r,960-r,W/2+r,960+r),fill=DARK+(255,),outline=GOLD+(255,),width=5); d.text((W/2,960),'VS',font=fk(int(56*u)+1,800),fill=GOLD2,anchor='mm')
        img.alpha_composite(shadow(lay,10,0.5))
        lay2=Image.new('RGBA',(120,60),(0,0,0,0)); d2=ImageDraw.Draw(lay2); d2.rounded_rectangle((4,4,116,56),radius=26,fill=(0,0,0,120),outline=(255,255,255,170),width=2); d2.text((60,30),'IA',font=fk(28,800),fill=(255,255,255,230),anchor='mm'); img.alpha_composite(lay2,(W-160,860))
        title(img,'Academia ou fisioterapia?',0.0,t,y=150,size=54)
    else:
        vid(img,'eletro',lt); vign(img)
        if lt<SPLIT+0.2: img.alpha_composite(Image.new('RGBA',(W,H),(255,255,255,int(150*(1-(lt-SPLIT)/0.2)))))
        title(img,'Um prepara o outro',SPLIT+0.05,t,y=200,size=58)
def sc2(img,t,lt,dur):
    vid(img,'joelho',1.5+lt); vign(img); ia_badge(img)
    title(img,'Avalia a dor',OFF['s2']+0.05,t,y=200,size=62)
def sc3(img,t,lt,dur):
    if lt<2.6: vid(img,'joelho',4.74+lt); vign(img); ia_badge(img)
    else:
        vid(img,'eletro',5.43+(lt-2.6)); vign(img)
        if lt<2.8: img.alpha_composite(Image.new('RGBA',(W,H),(255,255,255,int(150*(1-(lt-2.6)/0.2)))))
    title(img,'Adapta a carga',OFF['s3']+0.05,t,y=200,size=62)
    pill(img,'Pós-cirurgia',wt('s3','cirurgia')-0.1,t,W/2,1080,size=42)
    pill(img,'Artrose',wt('s3','artrose')-0.1,t,W/2,1190,size=42)
    pill(img,'Medo de se mexer',wt('s3','medo')-0.1,t,W/2,1300,size=42)
def sc4(img,t,lt,dur):
    blurbg(img)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    steps=['Técnica','Carga leve','Mais carga','Musculação']
    keys=[wt('s4','técnica'),wt('s4','quanto'),wt('s4','quando'),wt('s4','aumentar')-0.25]
    for i,(s_,k) in enumerate(zip(steps,keys)):
        x0=120+i*215; hgt=170+i*120; y1=1300; y0=y1-hgt
        v=ease((t-k+0.15)/0.35)
        d.rounded_rectangle((x0,y0,x0+195,y1),radius=22,fill=(255,255,255,30),outline=(255,255,255,90),width=2)
        if v>0:
            yy=y1-(y1-y0)*v
            d.rounded_rectangle((x0,yy,x0+195,y1),radius=22,fill=(GOLD if i<3 else OK)+(int(235*v),))
            d.text((x0+97,y0-40),s_,font=fk(34,800),fill=CREAM+(int(255*v),),anchor='mm')
            d.text((x0+97,y1-50),str(i+1),font=fk(60,800,True),fill=DARK+(int(255*v),),anchor='mm')
    # arrow
    u=ease((lt-0.3)/3.5); d.line((140,1380,140+800*u,1380),fill=GOLD2+(255,),width=8)
    if u>0.05: d.polygon([(140+800*u,1360),(140+800*u,1400),(170+800*u,1380)],fill=GOLD2+(255,))
    img.alpha_composite(shadow(lay,10,0.5))
    title(img,'Progressão segura',OFF['s4']+0.05,t,y=200,size=62)
def sc5(img,t,lt,dur):
    vid(img,'agach',5.6+lt); vign(img); ia_badge(img)
    title(img,'Musculação com segurança',OFF['s5']+0.05,t,y=200,size=56)
    if lt>1.5:
        u=ease((lt-1.5)/0.4); lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
        cx,cy=W-170,1250; r=80
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=OK+(int(235*u),)); d.line([(cx-34,cy+2),(cx-8,cy+28),(cx+38,cy-26)],fill=(255,255,255,int(255*u)),width=14,joint='curve')
        img.alpha_composite(shadow(lay,10,0.5))
def sc7(img,t,lt,dur):
    blurbg(img)
    u=ease(lt/0.35); x0,y0,w,h=250,380+int((1-u)*700),580,880
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((x0,y0,x0+w,y0+h),radius=70,fill=(11,21,16,255),outline=GOLD+(255,),width=6)
    sx,sy,sw,sh=x0+20,y0+20,w-40,h-40
    d.rounded_rectangle((sx,sy,sx+sw,sy+sh),radius=54,fill=(246,240,229,255))
    d.ellipse((sx+30,sy+40,sx+100,sy+110),fill=GREEN); d.text((sx+65,sy+76),'R',font=fk(36,800),fill=GOLD2,anchor='mm')
    d.text((sx+120,sy+62),'fisiorafaellima',font=fk(32,800),fill=GREEN,anchor='lm'); d.text((sx+120,sy+96),'Direct',font=fk(24,600),fill=(90,110,100),anchor='lm')
    d.line((sx+20,sy+140,sx+sw-20,sy+140),fill=(220,210,195),width=2)
    MSG='FORÇA'; ty=wt('s7','força')-OFF['s7']-0.35; n=int(max(0,min(len(MSG),(lt-ty)/0.1)))
    sent=lt>ty+0.7
    d.rounded_rectangle((sx+20,sy+sh-100,sx+sw-20,sy+sh-24),radius=38,fill=(255,255,255),outline=(200,190,175),width=2)
    if not sent: d.text((sx+50,sy+sh-62),MSG[:n]+('|' if int(lt*4)%2==0 else ''),font=fk(36,800),fill=GREEN,anchor='lm')
    if sent:
        v=ease((lt-ty-0.7)/0.25); bx=sx+sw-40
        d.rounded_rectangle((bx-200,sy+200,bx,sy+280),radius=40,fill=GOLD+(int(255*v),)); d.text((bx-100,sy+240),'FORÇA',font=fk(38,800),fill=DARK+(int(255*v),),anchor='mm')
        if lt>ty+1.3:
            v=ease((lt-ty-1.3)/0.3); by=sy+320
            d.rounded_rectangle((sx+30,by,sx+sw-60,by+260),radius=30,fill=(22,41,31,int(255*v)))
            d.text((sx+60,by+50),'Força em casa',font=fk(44,800,True),fill=CREAM+(int(255*v),),anchor='lm')
            for k,ex in enumerate(['1  Sentar e levantar','2  Ponte de quadril','3  Flexão na parede']):
                d.text((sx+60,by+120+k*40),ex,font=fk(28,600),fill=(207,200,186,int(255*v)),anchor='lm')
    sh_=Image.new('RGBA',(W,H),(0,0,0,0)); sh_.putalpha(lay.getchannel('A').filter(ImageFilter.GaussianBlur(24)).point(lambda v:int(v*0.5)))
    img.alpha_composite(sh_,(0,16)); img.alpha_composite(lay)
    title(img,'Me manda FORÇA',OFF['s7']+0.05,t,y=200,size=62)
DUR={n:b-a for n,a,b,_,_ in SEG}
SC={'s1':sc1,'s2':sc2,'s3':sc3,'s4':sc4,'s5':sc5,'s7':sc7}

def frame(t):
    img=background(t); n=seg_at(t); lt=t-OFF[n]
    SC[n](img,t,lt,DUR[n])
    # loop: last 0.35s blend toward hook start
    caption(img,t)
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
    if not PREVIEW: proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','work/video2.mp4'],stdin=subprocess.PIPE)
    N=int(round(TOTAL*FPS))
    for fi in range(N):
        t=fi/FPS
        if PREVIEW and not any(abs(t-p)<0.5/FPS for p in pts): continue
        out=frame(t)
        if PREVIEW: Image.fromarray(out).resize((540,960)).save('work/pv_%05.2f.jpg'%t,quality=85)
        else: proc.stdin.write(out.tobytes())
    if proc: proc.stdin.close(); proc.wait()
    print('done',N,TOTAL,OFF)
