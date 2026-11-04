import json,subprocess
tl=json.load(open('work/tl.json')); OFF=tl['OFF']; T=tl['TOTAL']; words=tl['words']
SEG=[('s1',5.70,10.32),('s2',11.36,16.65),('s3',17.76,21.67),('s4',24.96,28.20),('s5',29.47,32.79),('s6',36.20,42.95),('s7',43.33,49.15)]
def wt(seg,w):
    for a,b,x,k in words:
        if k==seg and x.strip('.,?!:').lower()==w: return a
    return OFF[seg]
S='../sfx3/'; ev=[]
def e(n,t,v,d=None): ev.append((n,max(0,t),v,d))
e('boom',0.0,0.4); e('hit',0.3,0.4); e('whoosh_b',1.5-0.47,0.35); e('hit',1.5+0.85,0.4)
W={'s2':'whoosh_deep','s3':'whoosh_a','s4':'whoosh_b','s5':'whoosh_a','s6':'whoosh_deep','s7':'whoosh_b'}
PK={'whoosh_a':0.71,'whoosh_b':0.47,'whoosh_deep':0.49}
for n,w in W.items(): e(w,OFF[n]-PK[w],0.35)
for n in ['s2','s3','s4','s5','s6']: e('metal_rise',OFF[n]-0.63,0.2)
for n in ['s2','s3','s4','s5','s6','s7']: e('click',OFF[n]+0.08,0.45)
e('riser',OFF['s1']+3.0,0.18,1.6)
e('hit',wt('s2','forte'),0.4); e('pop',OFF['s2']+0.4,0.3); e('success',wt('s2','menos')+0.6,0.25)
e('pop',wt('s2','coluna')-0.2,0.35)
e('pop',OFF['s3']+0.5,0.3); e('success',OFF['s3']+3.0,0.25)
e('pop',OFF['s4']+0.6,0.3)
e('pop',OFF['s5']+0.3,0.3); e('success',OFF['s5']+2.3,0.25)
t2=wt('s6','duas'); e('pop',t2,0.4); e('pop',t2+0.35,0.4)
ti=wt('s6','qualquer')
for i in range(4): e('pop',ti+i*0.12,0.28)
ty=wt('s7','força')-0.3; e('typing',ty,0.3,0.7); e('notif',ty+0.9,0.45); e('click',wt('s7','três'),0.4)
inputs=['-f','lavfi','-t',str(T),'-i','anullsrc=r=48000:cl=stereo']; fl=[]; k=1; labs=[]
for n,a,b in SEG:
    d=b-a; ms=int(OFF[n]*1000)
    inputs+=['-ss',str(a),'-t',str(d),'-i','work/f1_c.wav']
    fl.append(f'[{k}]afade=t=in:d=0.04,afade=t=out:st={d-0.06}:d=0.06,adelay={ms}|{ms}[v{k}]'); labs.append(f'[v{k}]'); k+=1
for n,t,v,dd in ev:
    ms=int(t*1000); inputs+=['-i',S+n+'.wav']; tr=f'atrim=0:{dd},afade=t=out:st={max(0,dd-0.08)}:d=0.08,' if dd else ''
    fl.append(f'[{k}]aformat=channel_layouts=stereo,{tr}volume={v},adelay={ms}|{ms}[v{k}]'); labs.append(f'[v{k}]'); k+=1
fc=';'.join(fl)+';[0:a]'+''.join(labs)+f'amix=inputs={k}:normalize=0:duration=first,afade=t=out:st={T-0.3}:d=0.3,loudnorm=I=-14:TP=-1.5:LRA=9[a]'
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-filter_complex',fc,'-map','[a]','-ar','48000','work/audio.wav'],check=True)
print('ok',len(ev))
