import json,subprocess
tl=json.load(open('work/tl.json')); OFF=tl['OFF']; T=tl['TOTAL']; words=tl['words']
SEG=[('s1',1.90,6.15),('s2',6.45,13.70),('s2b',16.13,21.33),('s3',21.78,27.00),('s4',27.71,33.08),('s5',35.47,42.20)]
def wt(seg,w):
    for a,b,x,k in words:
        if k==seg and x.strip('.,?!:').lower()==w: return a
    return OFF[seg]
S='../sfx3/'; ev=[]
def e(n,t,v,d=None): ev.append((n,max(0,t),v,d))
e('boom',0.0,0.3); e('hit',0.4,0.35)
for i in range(3): e('pop',1.2+i*0.5,0.3)
W={'s2':'whoosh_deep','s2b':'whoosh_a','s3':'whoosh_b','s4':'whoosh_deep','s5':'whoosh_a'}; PK={'whoosh_a':0.71,'whoosh_b':0.47,'whoosh_deep':0.49}
for n,w in W.items(): e(w,OFF[n]-PK[w],0.35)
for n in ['s2','s3','s4']: e('metal_rise',OFF[n]-0.63,0.2); e('click',OFF[n]+0.08,0.4)
for n in ['s2','s2b','s3','s4']: e('typing',OFF[n]+0.05,0.12,1.2)
ts=wt('s2','segura')
for k in range(5): e('m_tick' if False else 'click',ts+k*0.44,0.18)
e('success',ts+2.3,0.25)
e('toggle',wt('s2b','acordar')-0.05,0.45); e('success',wt('s2b','acordar')+0.3,0.25)
e('pop',wt('s4','esticado')-0.2,0.3)
e('click',OFF['s5']+0.1,0.35); ty=wt('s5','joelho')-0.4; e('typing',ty,0.3,0.6); e('notif',ty+0.7,0.45); e('pop',ty+1.2,0.3)
inputs=['-f','lavfi','-t',str(T),'-i','anullsrc=r=48000:cl=stereo']; fl=[]; k=1; labs=[]
for n,a,b in SEG:
    d=b-a; ms=int(OFF[n]*1000)
    inputs+=['-ss',str(a),'-t',str(d),'-i','work/v_c.wav']
    fl.append(f'[{k}]afade=t=in:d=0.04,afade=t=out:st={d-0.06}:d=0.06,adelay={ms}|{ms}[v{k}]'); labs.append(f'[v{k}]'); k+=1
for n,t,v,dd in ev:
    ms=int(t*1000); inputs+=['-i',S+n+'.wav']; tr=f'atrim=0:{dd},afade=t=out:st={max(0,dd-0.08)}:d=0.08,' if dd else ''
    fl.append(f'[{k}]aformat=channel_layouts=stereo,{tr}volume={v},adelay={ms}|{ms}[v{k}]'); labs.append(f'[v{k}]'); k+=1
fc=';'.join(fl)+';[0:a]'+''.join(labs)+f'amix=inputs={k}:normalize=0:duration=first,afade=t=out:st={T-0.3}:d=0.3,loudnorm=I=-14:TP=-1.5:LRA=9[a]'
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc,'-map','[a]','-ar','48000','work/audio6.wav'],check=True)
print('ok',len(ev))
