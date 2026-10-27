import numpy as np, wave
SR=48000
def save(n,x):
    x=x/np.max(np.abs(x))*0.8; x=np.stack([x,x],1)
    w=wave.open(n+'.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes()); w.close()
def t(d): return np.arange(int(SR*d))/SR
def lp(x,fc):
    a=np.exp(-2*np.pi*fc/SR); y=np.zeros_like(x); s=0
    for i,v in enumerate(x): s=(1-a)*v+a*s; y[i]=s
    return y
def lp3(x,fc): return lp(lp(lp(x,fc),fc),fc)
def att(tt,a): return np.clip(tt/a,0,1)
# marimba-like soft pop (wood mallet, low)
tt=t(0.45); f=392
x=(np.sin(2*np.pi*f*tt)*np.exp(-tt*11)+0.35*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*40)+0.2*np.sin(2*np.pi*f*0.5*tt)*np.exp(-tt*8))*att(tt,0.004)
save('m_pop',x)
tt=t(0.45); f=294
save('m_pop_lo',(np.sin(2*np.pi*f*tt)*np.exp(-tt*10)+0.3*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*38))*att(tt,0.004))
# warm tick: short wood knock
tt=t(0.09); x=(np.sin(2*np.pi*620*tt)*np.exp(-tt*70)+0.12*lp3(np.random.randn(len(tt)),1200)*np.exp(-tt*120))*att(tt,0.002)
save('m_tick',x)
# soft low chime (bell, rounded)
tt=t(1.6); x=np.zeros_like(tt)
for f,a,dk in [(523.25,1,2.6),(783.99,0.45,3.5),(1046.5,0.18,5),(261.63,0.35,2.2)]: x+=a*np.sin(2*np.pi*f*tt)*np.exp(-tt*dk)
save('m_chime',lp(x*att(tt,0.012),2500))
# soft whoosh: pink-ish noise, swelling, lowpassed
tt=t(0.6); n=np.random.randn(len(tt)); env=np.sin(np.pi*np.clip(tt/0.6,0,1))**2
a=lp3(n,500)*env; b=lp3(n,1100)*env*np.clip(tt/0.6,0,1)
save('m_whoosh',a+0.6*b)
# soft thump (sub)
tt=t(0.5); f=70*np.exp(-tt*4)+45; ph=2*np.pi*np.cumsum(f)/SR
save('m_thump',np.sin(ph)*np.exp(-tt*9)*att(tt,0.003))
# soft swell-rise for speed ramp
tt=t(0.9); n=np.random.randn(len(tt)); env=(tt/0.9)**2
save('m_rise',lp3(n,450)*env)
