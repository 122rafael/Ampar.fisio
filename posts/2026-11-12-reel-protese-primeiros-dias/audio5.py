import json,subprocess
tl=json.load(open('work/tl.json')); OFF=tl['OFF']; T=tl['TOTAL']; words=tl['words']
SEG=[('s1',1.87,7.92),('s2',12.09,20.11),('s3',20.73,22.45),('s3b',23.22,27.32),('s4',29.20,35.40)]
def wt(seg,w):
    for a,b,x,k in words:
        if k==seg and x.strip('.,?!:').lower()==w: return a
    return OFF[seg]
S='../sfx3/'; ev=[]
def e(n,t,v,d=None): ev.append((n,max(0,t),v,d))
e('boom',0.0,0.3); e('click',0.05,0.4)
tp=wt('s1','olha')-0.1; e('whoosh_b',tp-0.2,0.25); e('pop',tp+0.6,0.35)
W={'s2':'whoosh_deep','s3':'whoosh_a','s4':'whoosh_b'}; PK={'whoosh_a':0.71,'whoosh_b':0.47,'whoosh_deep':0.49}
for n,w in W.items(): e(w,OFF[n]-PK[w],0.35)
for n in ['s2','s3']: e('metal_rise',OFF[n]-0.63,0.2)
# marker drawing sounds (soft ticks) during strokes
for x in (0.05,0.35,0.7,0.9,1.2,1.45,2.0,2.2): e('typing',OFF['s2']+x,0.12,0.25)
e('pop',OFF['s2']+2.4,0.3); e('hit',OFF['s2']+2.55,0.3)
for w in ('inchaço','dor','mexer'): e('pop',wt('s2',w),0.3)
e('typing',OFF['s3']+0.05,0.15,0.6)
for w in ('dobrar','esticar','andar'): e('pop',wt('s3b',w)-0.2,0.3); e('success',wt('s3b',w)+0.65,0.22)
ty=wt('s4','joelho')-0.4; e('click',OFF['s4']+0.45,0.35); e('typing',ty,0.3,0.6); e('notif',ty+0.7,0.45); e('pop',ty+1.3,0.3)
inputs=['-f','lavfi','-t',str(T),'-i','anullsrc=r=48000:cl=stereo']; fl=[]; k=1; labs=[]
for n,a,b in SEG:
    d=b-a; ms=int(OFF[n]*1000)
    inputs+=['-ss',str(a),'-t',str(d),'-i','work/p_c.wav']
    fl.append(f'[{k}]afade=t=in:d=0.04,afade=t=out:st={d-0.06}:d=0.06,adelay={ms}|{ms}[v{k}]'); labs.append(f'[v{k}]'); k+=1
for n,t,v,dd in ev:
    ms=int(t*1000); inputs+=['-i',S+n+'.wav']; tr=f'atrim=0:{dd},afade=t=out:st={max(0,dd-0.08)}:d=0.08,' if dd else ''
    fl.append(f'[{k}]aformat=channel_layouts=stereo,{tr}volume={v},adelay={ms}|{ms}[v{k}]'); labs.append(f'[v{k}]'); k+=1
fc=';'.join(fl)+';[0:a]'+''.join(labs)+f'amix=inputs={k}:normalize=0:duration=first,afade=t=out:st={T-0.3}:d=0.3,loudnorm=I=-14:TP=-1.5:LRA=9[a]'
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc,'-map','[a]','-ar','48000','work/audio5b.wav'],check=True)
print('ok',len(ev))
