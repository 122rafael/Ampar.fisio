import numpy as np, wave
from scipy import signal
SR=48000; rng=np.random.default_rng(7)
def T(d): return np.arange(int(SR*d))/SR
def bp(x,lo,hi,o=2): return signal.sosfilt(signal.butter(o,[lo,hi],'band',fs=SR,output='sos'),x)
def lp(x,f,o=2): return signal.sosfilt(signal.butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return signal.sosfilt(signal.butter(o,f,'high',fs=SR,output='sos'),x)
def env(t,a,d): return np.clip(t/a,0,1)*np.exp(-np.maximum(t-a,0)*d)
def ir(dur=1.2,decay=4.0,bright=5000):
    t=T(dur); n=rng.standard_normal((len(t),2))
    for c in range(2): n[:,c]=lp(n[:,c],bright)*np.exp(-t*decay)
    n[:int(0.008*SR)]*=0; return n/np.abs(n).sum(0)*30
def verb(x,mix=0.25,**k):
    if x.ndim==1: x=np.stack([x,x],1)
    r=ir(**k); y=np.stack([signal.fftconvolve(x[:,c],r[:,c])[:len(x)+len(r)-1] for c in range(2)],1)
    out=np.zeros_like(y); out[:len(x)]=x*(1-mix); out+=y*mix; return out
def st(x,w=0.0):
    if x.ndim==2: return x
    d=int(abs(w)*0.012*SR); a=np.concatenate([np.zeros(d),x])[:len(x)]
    return np.stack([x,a],1) if w>=0 else np.stack([a,x],1)
def save(n,x,peak=0.85):
    if x.ndim==1: x=np.stack([x,x],1)
    # trim tail
    e=np.abs(x).max(1); idx=np.where(e>e.max()*0.002)[0]; x=x[:idx[-1]+int(0.03*SR)] if len(idx) else x
    f=np.linspace(1,0,min(len(x),int(0.02*SR))); x[-len(f):]*=f[:,None]
    x=x/np.abs(x).max()*peak
    w=wave.open(n+'.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes()); w.close()

# 1 keyboard key (thocky mechanical, warm)
def key(seed,dur=0.09):
    r=np.random.default_rng(seed); t=T(dur)
    click=bp(r.standard_normal(len(t)),1800+r.uniform(-300,300),4200,2)*np.exp(-t*420)
    body=np.sin(2*np.pi*(r.uniform(190,260))*t)*np.exp(-t*90)
    clack=bp(r.standard_normal(len(t)),600,1500)*np.exp(-np.maximum(t-0.012,0)*260)*(t>0.012)
    return lp(0.55*click+0.9*body+0.45*clack,7000)
for i in range(6): save(f'key{i+1}',verb(key(i),0.08,dur=0.25,decay=25,bright=4000),0.6)
# typing burst demo
out=np.zeros(int(SR*1.6))
tt=0.05
for i in range(14):
    k=key(100+i); s=int(tt*SR); out[s:s+len(k)]+=k*rng.uniform(0.7,1.0); tt+=rng.uniform(0.07,0.12)
save('typing',verb(out,0.08,dur=0.25,decay=25,bright=4000),0.7)
# 2 mouse click (card open)
t=T(0.12); c=lambda d: bp(rng.standard_normal(len(t)),2000,5000)*np.exp(-np.maximum(t-d,0)*600)*(t>=d)+0.6*np.sin(2*np.pi*420*t)*np.exp(-np.maximum(t-d,0)*160)*(t>=d)
save('click',lp(c(0.0)+0.55*c(0.055),7500),0.6)
# 3 whoosh 1 (fast air, pan L->R)
def whoosh(d,lo0,lo1,hi0,hi1,peak=0.5,pan=True,sub=0):
    t=T(d); n=rng.standard_normal(len(t)); y=np.zeros(len(t)); blk=256
    for i in range(0,len(t),blk):
        u=i/len(t); lo=lo0+(lo1-lo0)*u; hi=hi0+(hi1-hi0)*u
        pass
    # time-varying via STFT-ish: sum of fixed bands weighted by moving center
    bands=[(80,200),(200,400),(400,800),(800,1600),(1600,3200),(3200,6000)]
    u=t/d; e=np.where(u<peak,(u/peak)**2,((1-u)/(1-peak))**1.6)
    ctr=np.interp(u,[0,peak,1],[np.log2(lo0),np.log2(hi0),np.log2(lo1)])
    for lo,hi in bands:
        c=np.log2(np.sqrt(lo*hi)); wgt=np.exp(-((ctr-c)**2)/0.9); y+=bp(n,lo,hi)*wgt
    y*=e
    if sub: y+=sub*np.sin(2*np.pi*np.cumsum(55+40*e)/SR)*e
    if pan:
        p=u; L=y*np.cos(p*np.pi/2*0.8+0.2); R=y*np.sin(p*np.pi/2*0.8+0.2); return np.stack([L,R],1)
    return y
save('whoosh1',verb(whoosh(0.45,300,250,2600,0,0.55),0.15,dur=0.6,decay=8))
save('whoosh2',verb(whoosh(0.8,200,150,1800,0,0.6),0.2,dur=0.8,decay=6))
save('deep_whoosh',verb(whoosh(0.9,90,70,700,0,0.62,sub=0.6),0.2,dur=0.9,decay=5,bright=2500))
# reverse swell (reverse reverb into cut)
t=T(0.9); tone=sum(a*np.sin(2*np.pi*f*t) for f,a in [(220,1),(330,0.5),(440,0.3)])*np.exp(-t*3)
r=verb(tone,0.8,dur=1.4,decay=3,bright=3000)[::-1]; save('reverse_swell',r)
# 4 metallic rise: inharmonic bell partials rising, tremolo, crescendo
d=1.4; t=T(d); u=t/d; f0=180*2**(u*1.0); ph=2*np.pi*np.cumsum(f0)/SR
x=sum(a*np.sin(ph*r_) for r_,a in [(1,1),(2.76,0.5),(5.40,0.28),(8.93,0.14),(1.5,0.35)])
x*= (u**2.2)*(1+0.25*np.sin(2*np.pi*(6+10*u)*t)); x+=0.5*bp(rng.standard_normal(len(t)),2000,7000)*u**3
x=lp(x,7000); x[int(len(x)*0.97):]*=np.linspace(1,0,len(x)-int(len(x)*0.97))
save('metallic_rise',verb(st(x,0.6),0.3,dur=1.2,decay=4,bright=6000))
# 5 downer: pitch drop
d=1.0; t=T(d); f=500*np.exp(-t*4.5)+45; ph=2*np.pi*np.cumsum(f)/SR
x=(np.sin(ph)+0.3*np.sin(2*ph)+0.15*np.sin(3*ph))*env(t,0.01,2.8)+0.25*lp(rng.standard_normal(len(t)),1200)*np.exp(-t*5)
save('downer',verb(lp(x,4000),0.25,dur=1.2,decay=4,bright=3000))
# 6 boom: cinematic sub boom
d=2.0; t=T(d); f=70*np.exp(-t*3)+38; x=np.sin(2*np.pi*np.cumsum(f)/SR)*env(t,0.005,2.2)+0.5*lp(rng.standard_normal(len(t)),500)*env(t,0.002,10)
save('boom',verb(x,0.3,dur=2.0,decay=2.5,bright=1500))
# 7 hit: punchy impact
d=1.2; t=T(d); x=np.sin(2*np.pi*np.cumsum(95*np.exp(-t*8)+55)/SR)*env(t,0.002,7)+0.7*bp(rng.standard_normal(len(t)),300,3000)*env(t,0.001,30)+0.3*bp(rng.standard_normal(len(t)),3000,8000)*env(t,0.001,60)
save('hit',verb(x,0.3,dur=1.5,decay=3,bright=4000))
# 8 notification: two warm mallet tones (original)
def mallet(f,d=0.7):
    t=T(d); return (np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*f*3.98*t)*np.exp(-t*20))*env(t,0.003,7)
a=mallet(784); b=mallet(1175); y=np.zeros(int(SR*1.0)); y[:len(a)]+=a; s=int(0.13*SR); y[s:s+len(b)]+=0.85*b
save('notification',verb(lp(y,6000),0.2,dur=0.8,decay=6,bright=5000),0.7)
# 9 toggle: tick-tock
t=T(0.18); k=lambda f,d: (np.sin(2*np.pi*f*t)*np.exp(-np.maximum(t-d,0)*120)+0.4*bp(rng.standard_normal(len(t)),1500,4000)*np.exp(-np.maximum(t-d,0)*500))*(t>=d)
save('toggle',lp(k(900,0)+0.9*k(1250,0.06),7000),0.6)
# 10 camera shutter
t=T(0.3); sh=lambda d: bp(rng.standard_normal(len(t)),1000,6000)*np.exp(-np.maximum(t-d,0)*180)*(t>=d)
save('shutter',lp(sh(0)+0.8*sh(0.09)+0.3*np.sin(2*np.pi*300*t)*np.exp(-t*60),8000),0.6)
# 11 heartbeat
t=T(1.0); hb=lambda d,a: a*np.sin(2*np.pi*55*(t-d))*np.exp(-np.maximum(t-d,0)*14)*(t>=d)
save('heartbeat',lp(hb(0,1)+hb(0.22,0.7),200))
# 12 glitch
t=T(0.35); x=np.sign(np.sin(2*np.pi*np.repeat(rng.uniform(200,900,12),len(t)//12+1)[:len(t)]*t))*0.4+0.6*bp(rng.standard_normal(len(t)),800,5000)
gate=np.repeat(rng.integers(0,2,40),len(t)//40+1)[:len(t)]; x*=gate
save('glitch',lp(x*np.exp(-t*3),6000),0.5)
# 13 success chime (soft check)
y=np.zeros(int(SR*1.3))
for i,f in enumerate([523.25,659.25,783.99]):
    m=mallet(f,1.0); s=int(i*0.07*SR); y[s:s+len(m)]+=m[:len(y)-s]
save('success',verb(lp(y,5000),0.25,dur=1.0,decay=4,bright=4000),0.7)
# 14 pop (soft UI bubble)
t=T(0.18); f=300+500*np.exp(-t*60); x=np.sin(2*np.pi*np.cumsum(f)/SR)*env(t,0.002,30)
save('pop',lp(x,5000),0.6)
print('ok')
