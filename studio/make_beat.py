import numpy as np, wave, sys
sr=44100; bpm=92; beat=60/bpm; dur=24.0
n=int(sr*dur); L=np.zeros(n); R=np.zeros(n)
rng=np.random.default_rng(7)
def add(sig,t0,g=1.0,pan=0.0):
    i=int(t0*sr)
    if i>=n: return
    s=sig[:n-i]
    L[i:i+len(s)]+=s*g*(1-max(pan,0)); R[i:i+len(s)]+=s*g*(1+min(pan,0))
def kick():
    t=np.arange(int(.35*sr))/sr; f=45+110*np.exp(-t*28)
    return np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-t*7)
def snare():
    t=np.arange(int(.22*sr))/sr
    return (rng.standard_normal(len(t))*np.exp(-t*20)*.6+np.sin(2*np.pi*190*t)*np.exp(-t*25)*.5)
def hat(o=False):
    t=np.arange(int((.18 if o else .05)*sr))/sr
    x=np.diff(rng.standard_normal(len(t)+1))
    return x*np.exp(-t*(18 if o else 70))*.35
def bass(f,d):
    t=np.arange(int(d*sr))/sr
    return np.tanh(2.2*np.sin(2*np.pi*f*t))*np.exp(-t*2.2)*np.minimum(t*200,1)*.55
def pluck(f,d=.35):
    t=np.arange(int(d*sr))/sr
    x=sum(np.sin(2*np.pi*f*k*t)/k for k in (1,2,3))
    return x*np.exp(-t*9)*.18
step=beat/4
notes=[55.0,55.0,65.41,49.0]  # A1 A1 C2 G1
arp=[220.0,261.63,329.63,261.63,392.0,329.63,261.63,220.0]
bars=int(dur/(beat*4))+1
for b in range(bars):
    t0=b*beat*4
    add(bass(notes[b%4],beat*3.6),t0,1.0)
    for s in range(16):
        ts=t0+s*step
        if s in (0,6,10): add(kick(),ts,.95)
        if s in (4,12): add(snare(),ts,.8)
        add(hat(s%4==2),ts,.8 if s%2==0 else .5,pan=.3 if s%2 else -.3)
        if s%2==0: add(pluck(arp[(s//2)%8]*(1.2247 if b%4==2 else 1)),ts,.9,pan=-.2)
m=max(abs(L).max(),abs(R).max()); L/=m; R/=m
fade=int(1.5*sr); 
# no fade here; applied per-video
out=(np.stack([L,R],1)*0.89*32767).astype(np.int16)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(out.tobytes()); w.close()
