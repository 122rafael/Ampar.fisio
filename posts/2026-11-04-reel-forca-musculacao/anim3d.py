import sys, math, subprocess, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
import anim as A
from anim import W,H,FPS,GOLD,GOLD2,CREAM,OK,WARN,DARK,ease,eio,cl,lerp,title,meter,wt,OFF,TOTAL,shadow,fk

# 3D stills: upscale 2x of fit size for crisp zooms
S0=1080/572
BASE={}
for i in range(1,7):
    im=cv2.imread(f'in3d/3d{i}.jpg')
    big=cv2.resize(im,(2160,int(1024*S0*2)),interpolation=cv2.INTER_LANCZOS4)
    big=cv2.addWeighted(big,1.35,cv2.GaussianBlur(big,(0,0),2.2),-0.35,0)  # light unsharp
    BASE[i]=big
FC=(540,860)
def kb(i,z,c):
    """render still i at zoom z (1 = fit width) with src point c at frame point FC"""
    s=S0*z; s2=z/2  # base is 2x of fit
    M=np.float32([[s2,0,FC[0]-c[0]*s],[0,s2,FC[1]-c[1]*s]])
    fr=cv2.warpAffine(BASE[i],M,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    return fr,(lambda p:(FC[0]+(p[0]-c[0])*s,FC[1]+(p[1]-c[1])*s)),s
def to_img(fr): return Image.fromarray(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)).convert('RGBA')
def glow(img,p,r,col,a):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=col+(int(255*cl(a)),))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(r*0.45)))
def vign(img):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rectangle((0,0,W,430),fill=(0,0,0,110)); d.rectangle((0,1460,W,H),fill=(0,0,0,150))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(70)))
def paste_frame(img,fr): img.paste(to_img(fr),(0,0))

def sc_hook(img,t,lt,dur):
    if lt<A.PATD:
        A.sc_hook(img,t,lt,dur); return
    l=lt-A.PATD; d=dur-A.PATD
    if l<d-0.9:
        z=lerp(1.2,1.4,eio(l/(d-0.9)))
        fr,P,s=kb(2,z,(330,430)); paste_frame(img,fr)
        glow(img,P((385,330)),140*z,GOLD,0.35+0.25*math.sin(l*6))
    else:
        v=eio((l-(d-0.9))/0.9)
        fa,_,_=kb(2,1.4,(330,430)); fb,_,_=kb(1,lerp(1.4,1.9,v),(lerp(330,305,v),lerp(430,520,v)))
        paste_frame(img,cv2.addWeighted(fa,1-min(1,v*1.6),fb,min(1,v*1.6),0))
    vign(img)
    if l<0.25: img.alpha_composite(Image.new('RGBA',(W,H),(255,255,255,int(160*(1-l/0.25)))))
    title(img,'O que a musculação faz por dentro',0.0,t,y=200,size=50)

def arrows(img,p,sz,n=3,gap=70):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for k in range(n):
        x=p[0]+(k-(n-1)/2)*gap; y1=p[1]-40; y0=y1-120-60*sz
        d.line((x,y0,x,y1-24*sz),fill=WARN+(235,),width=int(8+10*sz))
        d.polygon([(x-18-18*sz,y1-34*sz),(x+18+18*sz,y1-34*sz),(x,y1+6)],fill=WARN+(245,))
    img.alpha_composite(shadow(lay,8,0.5))
def sc_knee(img,t,lt,dur):
    z=lerp(1.9,2.05,lt/dur)
    fr,P,s=kb(1,z,(305,520)); paste_frame(img,fr)
    g=ease((lt-(wt('s2','forte')-OFF['s2']))/1.4)
    glow(img,P((330,330)),190,GOLD,0.15+0.35*g*(0.75+0.25*math.sin(lt*7)))
    la=lerp(1.0,0.25,ease((lt-(wt('s2','menos')-OFF['s2']))/1.0))
    glow(img,P((300,545)),120,OK,0.55*g)
    if lt>0.25: arrows(img,(P((300,545))[0]+170,P((300,545))[1]),la)
    vign(img)
    title(img,'Protege a articulação',0.1+OFF['s2'],t,y=200,size=58)
    meter(img,'Carga no joelho',la if lt>0.25 else 1,OFF['s2']+0.4,t,x=60,y=1240)
    tc=wt('s2','coluna')
    if t>=tc-0.2:
        u=ease((t-tc+0.2)/0.35)
        sp=cv2.resize(BASE[6],(360,int(360*BASE[6].shape[0]/BASE[6].shape[1])),interpolation=cv2.INTER_AREA)[60:560]
        card=to_img(sp); m=Image.new('L',card.size,0); ImageDraw.Draw(m).rounded_rectangle((0,0,card.size[0]-1,card.size[1]-1),radius=34,fill=int(255*u)); card.putalpha(m)
        bd=Image.new('RGBA',(card.size[0]+8,card.size[1]+8),(0,0,0,0)); ImageDraw.Draw(bd).rounded_rectangle((0,0,card.size[0]+7,card.size[1]+7),radius=38,outline=GOLD+(int(255*u),),width=4)
        bd.alpha_composite(card,(4,4))
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); lay.alpha_composite(bd,(W-bd.size[0]-50+int((1-u)*300),520))
        img.alpha_composite(shadow(lay,16,0.6))
        pul=0.5+0.5*math.sin(t*8); glow(img,(W-50-bd.size[0]/2,520+bd.size[1]/2),120,OK,0.25*u*pul)

def sc_bone(img,t,lt,dur):
    z=lerp(1.05,1.25,lt/dur)
    fr,P,s=kb(3,z,(290,470))
    dens=lerp(0.25,1.0,ease((lt-0.6)/(dur-1.0)))
    paste_frame(img,fr)
    for k in range(3):
        if lt<0.3: break
        ph=((lt-0.3)*0.9-k*0.33)%1.0
        p=P((lerp(40,560,ph),480)); glow(img,p,110,GOLD,0.55*(1-abs(ph-0.5)*1.6))
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for k in range(3):
        x=P((150+k*150,0))[0]; pr=0.5+0.5*math.sin(lt*6); yb=P((0,330))[1]
        d.line((x,yb-150,x,yb-30+16*pr),fill=GOLD+(255,),width=10)
        d.polygon([(x-26,yb-40+16*pr),(x+26,yb-40+16*pr),(x,yb+10+16*pr)],fill=GOLD+(255,))
    d.text((W/2,P((0,330))[1]-185),'ESTÍMULO',font=fk(34,800),fill=GOLD2,anchor='mm')
    img.alpha_composite(shadow(lay,8,0.5))
    vign(img)
    title(img,'Osso mais forte',OFF['s3']+0.05,t,y=200,size=62)
    meter(img,'Densidade',dens,OFF['s3']+0.5,t,x=(W-300)//2,y=1240,col=GOLD)
RNG=np.random.default_rng(3); GP=RNG.random((70,3))
def sc_glucose(img,t,lt,dur):
    z=lerp(1.0,1.18,lt/dur)
    fr,P,s=kb(4,z,(286,560)); paste_frame(img,fr)
    # golden particles flowing along the capillary then out into fibers
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for u0,side,sp in GP:
        ph=(u0+lt*0.22*(0.6+sp))%1.0
        sx=lerp(500,30,ph); sy=lerp(0,1024,ph)
        out=cl((lt-0.8)/1.5)*(0.5+0.5*math.sin(ph*20+sp*9))
        off=(side-0.5)*2*90*out
        p=P((sx+off,sy+off*0.4)); r=4+5*sp
        d.ellipse((p[0]-r*2.2,p[1]-r*2.2,p[0]+r*2.2,p[1]+r*2.2),fill=GOLD+(70,))
        d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=GOLD2+(255,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))
    vign(img)
    title(img,'Ajuda a glicose',OFF['s4']+0.05,t,y=200,size=62)
    meter(img,'Açúcar no sangue',lerp(0.9,0.45,ease((lt-0.8)/2.2)),OFF['s4']+0.5,t,x=(W-300)//2,y=1240)
def sc_falls(img,t,lt,dur):
    z=lerp(1.0,1.12,lt/dur)
    fr,P,s=kb(5,z,(300,560)); paste_frame(img,fr)
    g=ease((lt-0.5)/1.6)
    for p,r in (((270,620),150),((330,700),130),((260,850),110)):
        glow(img,P(p),r,GOLD,0.18+0.3*g*(0.7+0.3*math.sin(lt*6)))
    vign(img)
    title(img,'Menos quedas',OFF['s5']+0.05,t,y=200,size=62)
    u=ease((t-OFF['s5']-0.3)/0.3)
    if u>0:
        lay=Image.new('RGBA',(340,230),(0,0,0,0)); d=ImageDraw.Draw(lay)
        d.rounded_rectangle((10,10,330,220),radius=28,fill=(10,22,16,int(215*u)),outline=(255,255,255,int(90*u)),width=2)
        d.text((170,46),'Risco de queda',font=fk(30,700),fill=CREAM+(int(255*u),),anchor='mm')
        cx,cy,rr=170,190,110
        for a0,a1,c in ((180,240,OK),(240,300,GOLD),(300,360,WARN)): d.arc((cx-rr,cy-rr,cx+rr,cy+rr),a0,a1,fill=c+(int(255*u),),width=22)
        ang=math.radians(lerp(330,205,g)); d.line((cx,cy,cx+math.cos(ang)*90,cy+math.sin(ang)*90),fill=CREAM+(int(255*u),),width=8)
        d.ellipse((cx-12,cy-12,cx+12,cy+12),fill=CREAM+(int(255*u),))
        img.alpha_composite(lay,(W-380,1180))
def soft_bg(i):
    fr,_,_=kb(i,1.1,(300,520)); fr=cv2.GaussianBlur(fr,(0,0),18); fr=(fr*0.35).astype(np.uint8); return fr
BG1=None
def sc_oms(img,t,lt,dur):
    global BG1
    if BG1 is None: BG1=soft_bg(1)
    paste_frame(img,BG1); A.sc_oms(img,t,lt,dur)
def sc_cta(img,t,lt,dur):
    global BG1
    if BG1 is None: BG1=soft_bg(1)
    paste_frame(img,BG1); A.sc_cta(img,t,lt,dur)
A.SC.update({'s1':sc_hook,'s2':sc_knee,'s3':sc_bone,'s4':sc_glucose,'s5':sc_falls,'s6':sc_oms,'s7':sc_cta})

if __name__=='__main__':
    PREVIEW=len(sys.argv)>1
    A.frame0=Image.fromarray(A.frame(0.0))
    pts=[float(x) for x in sys.argv[1].split(',')] if PREVIEW else None
    proc=None
    if not PREVIEW: proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','work/video3d.mp4'],stdin=subprocess.PIPE)
    N=int(round(TOTAL*FPS))
    for fi in range(N):
        t=fi/FPS
        if PREVIEW and not any(abs(t-p)<0.5/FPS for p in pts): continue
        out=A.frame(t)
        if PREVIEW: Image.fromarray(out).resize((540,960)).save('work/pv3_%05.2f.jpg'%t,quality=85)
        else: proc.stdin.write(out.tobytes())
    if proc: proc.stdin.close(); proc.wait()
    print('done',N)
