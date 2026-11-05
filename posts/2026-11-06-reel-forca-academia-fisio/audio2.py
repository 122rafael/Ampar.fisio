import json,subprocess
tl=json.load(open('work/tl.json')); OFF=tl['OFF']; T=tl['TOTAL']; words=tl['words']
SEG=[('s1',2.76,8.19),('s2',8.95,12.19),('s3',13.01,19.83),('s4',21.01,25.89),('s5',27.98,32.22),('s7',32.93,37.30)]
def wt(seg,w):
    for a,b,x,k in words:
        if k==seg and x.strip('.,?!:').lower()==w: return a
    return OFF[seg]
S='../sfx3/'; ev=[]
def e(n,t,v,d=None): ev.append((n,max(0,t),v,d))
e('boom',0.0,0.35); e('hit',0.05,0.4); e('pop',0.15,0.3); e('pop',0.45,0.3)
e('whoosh_b',4.4-0.47,0.3); e('click',4.45,0.35)
W={'s2':'whoosh_deep','s3':'whoosh_a','s4':'whoosh_b','s5':'whoosh_deep','s7':'whoosh_a'}
PK={'whoosh_a':0.71,'whoosh_b':0.47,'whoosh_deep':0.49}
for n,w in W.items(): e(w,OFF[n]-PK[w],0.35)
for n in ['s2','s3','s4','s5']: e('metal_rise',OFF[n]-0.63,0.2)
for n in ['s2','s3','s4','s5','s7']: e('click',OFF[n]+0.08,0.4)
e('whoosh_a',OFF['s3']+2.6-0.71,0.25)
for w in ('cirurgia','artrose','medo'): e('pop',wt('s3',w)-0.1,0.35)
for w in ('técnica','quanto','quando'): e('pop',wt('s4',w)-0.15,0.3)
e('success',wt('s4','aumentar')+0.15,0.3)
e('success',OFF['s5']+1.5,0.3)
ty=wt('s7','força')-0.35; e('typing',ty,0.3,0.55); e('notif',ty+0.7,0.45); e('pop',ty+1.3,0.3)
inputs=['-f','lavfi','-t',str(T),'-i','anullsrc=r=48000:cl=stereo']; fl=[]; k=1; labs=[]
for n,a,b in SEG:
    d=b-a; ms=int(OFF[n]*1000)
    inputs+=['-ss',str(a),'-t',str(d),'-i','work/g2_c.wav']
    fl.append(f'[{k}]afade=t=in:d=0.04,afade=t=out:st={d-0.06}:d=0.06,adelay={ms}|{ms}[v{k}]'); labs.append(f'[v{k}]'); k+=1
for n,t,v,dd in ev:
    ms=int(t*1000); inputs+=['-i',S+n+'.wav']; tr=f'atrim=0:{dd},afade=t=out:st={max(0,dd-0.08)}:d=0.08,' if dd else ''
    fl.append(f'[{k}]aformat=channel_layouts=stereo,{tr}volume={v},adelay={ms}|{ms}[v{k}]'); labs.append(f'[v{k}]'); k+=1
fc=';'.join(fl)+';[0:a]'+''.join(labs)+f'amix=inputs={k}:normalize=0:duration=first,afade=t=out:st={T-0.3}:d=0.3,loudnorm=I=-14:TP=-1.5:LRA=9[a]'
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc,'-map','[a]','-ar','48000','work/audio2.wav'],check=True)
print('ok',len(ev))
