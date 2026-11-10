import json,subprocess
tl=json.load(open('work/tl.json')); OFF=tl['OFF']; T=tl['TOTAL']; words=tl['words']
SEG=[('s1',1.24,5.92),('s2',13.27,16.88),('s3',17.36,21.24),('s4',21.71,24.72),('s5',24.78,31.20),('s6',31.75,34.88),('s7',35.28,38.60)]
def wt(seg,w):
    for a,b,x,k in words:
        if k==seg and x.strip('.,?!:').lower()==w: return a
    return OFF[seg]
S='../sfx3/'; ev=[]
def e(n,t,v,d=None): ev.append((n,max(0,t),v,d))
e('boom',0.0,0.35); e('hit',0.05,0.4); e('pop',0.1,0.3); e('pop',0.35,0.3)
e('toggle',wt('s1','completam')-0.3,0.4); e('whoosh_b',3.5-0.47,0.3); e('click',3.55,0.35); e('pop',3.6,0.3)
W={'s2':'whoosh_deep','s3':'whoosh_a','s4':'whoosh_b','s5':'whoosh_deep','s6':'whoosh_a','s7':'whoosh_b'}
PK={'whoosh_a':0.71,'whoosh_b':0.47,'whoosh_deep':0.49}
for n,w in W.items(): e(w,OFF[n]-PK[w],0.35)
for n in ['s2','s3','s5']: e('metal_rise',OFF[n]-0.63,0.2)
for n in ['s2','s3','s4','s5','s6','s7']: e('click',OFF[n]+0.08,0.4)
e('pop',wt('s2','dor')-0.1,0.35); e('pop',wt('s2','movimento')-0.1,0.35)
for i in range(6): e('pop',OFF['s3']+0.6+i*0.35,0.22)
e('success',OFF['s3']+0.6+5*0.35,0.25)
e('pop',wt('s4','sentar')-0.1,0.35)
e('pop',wt('s5','altura')-0.15,0.35); e('pop',wt('s5','técnica')-0.1,0.35)
e('whoosh_b',OFF['s5']+3.5-0.47,0.25); e('hit',wt('s5','carga'),0.35); e('success',wt('s5','carga')+0.4,0.25)
e('pop',OFF['s6']+0.6,0.35)
ty=wt('s7','força')-0.35; e('typing',ty,0.3,0.55); e('notif',ty+0.7,0.45); e('pop',ty+1.3,0.3)
inputs=['-f','lavfi','-t',str(T),'-i','anullsrc=r=48000:cl=stereo']; fl=[]; k=1; labs=[]
for n,a,b in SEG:
    d=b-a; ms=int(OFF[n]*1000)
    inputs+=['-ss',str(a),'-t',str(d),'-i','work/fl_c.wav']
    fl.append(f'[{k}]afade=t=in:d=0.04,afade=t=out:st={d-0.06}:d=0.06,adelay={ms}|{ms}[v{k}]'); labs.append(f'[v{k}]'); k+=1
for n,t,v,dd in ev:
    ms=int(t*1000); inputs+=['-i',S+n+'.wav']; tr=f'atrim=0:{dd},afade=t=out:st={max(0,dd-0.08)}:d=0.08,' if dd else ''
    fl.append(f'[{k}]aformat=channel_layouts=stereo,{tr}volume={v},adelay={ms}|{ms}[v{k}]'); labs.append(f'[v{k}]'); k+=1
fc=';'.join(fl)+';[0:a]'+''.join(labs)+f'amix=inputs={k}:normalize=0:duration=first,afade=t=out:st={T-0.3}:d=0.3,loudnorm=I=-14:TP=-1.5:LRA=9[a]'
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc,'-map','[a]','-ar','48000','work/audio4b.wav'],check=True)
print('ok',len(ev))
