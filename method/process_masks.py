from pathlib import Path
import json,ast,numpy as np,cv2
from PIL import Image,ImageDraw
from scipy import ndimage as ndi

ROOT=Path('/workspace/sem_batch2');RAW=ROOT/'raw';OUT=ROOT/'masks';OUT.mkdir(exist_ok=True)
META={int(m['file'][2:4]):m for m in json.loads((ROOT/'metadata.json').read_text())}
BRACKETS=json.loads((ROOT/'brackets.json').read_text())
GROUPS=[(2,3,4),(5,6,7),(8,9,10),(11,12,13),(14,15,None),(16,17,None),
    (18,19,20),(21,22,23),(24,25,26),(27,28,29),(30,31,32),(33,34,35),
    (36,None,None),(37,38,39),(40,41,42),(43,44,None),(45,46,47),(48,49,50),(51,52,53)]
CENTERS={2:[484,665,845,1025],5:[422,602,783,963],8:[360,540,721,901],11:[400,580,761,941],
    14:[424,604,785,965],16:[428,608,789,969],18:[392,572,752,932],21:[410,590,770,952],
    24:[449,629,810,990],27:[471,651,832,1012],30:[417,598,779,959],33:[390,571,751,931],
    36:[428,609,789,970],37:[575,647,719,790,862,934],40:[434,614,794,974],43:[396,576,756,936],
    45:[455,636,816,997],48:[421,601,784,965],51:[387,567,748,930]}
# Reuse the already-reviewed numerical path tracker, not prior images or masks.
tree=ast.parse(Path('/workspace/sem_rework/reextract.py').read_text())
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('seam','track')]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'path_tracker','exec'))

def rgb(n):return np.asarray(Image.open(RAW/f'1-{n:02}.tif').convert('RGB'))
def save(n,m):
    assert m.shape==(1536,2048) and not m[1419:].any()
    Image.fromarray(m).save(OUT/f'1-{n:02}_mask.png')
    a=rgb(n).copy();fg=m>0;a[fg]=(.72*a[fg]+.28*np.array([20,215,150])).astype('uint8')
    b=cv2.morphologyEx(m,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))>0;a[b]=[255,130,20]
    Image.fromarray(a).save(OUT/f'1-{n:02}_overlay.jpg',quality=92)

def zoom(clean,ann):
    a=cv2.cvtColor(rgb(clean),cv2.COLOR_RGB2GRAY)[:1419].astype(float);sm=ndi.gaussian_filter(a,(.8,3))
    boxes=[b for b in BRACKETS.get(str(ann),[]) if b['width']>=60] if ann else []
    if boxes:
        box=max(boxes,key=lambda b:b['width']);top,bot=box['top'],box['bottom'];xref=box['x']+box['width']/2
        source='SEM caliper location seed on corresponding annotation image'
    else:
        p=ndi.gaussian_filter1d(np.median(sm[:,300:1750],axis=1),1)
        response=p-ndi.gaussian_filter1d(p,45);peak=int(np.argmax(response[150:1250]))+150
        bg=float(np.median(np.r_[p[peak-65:peak-40],p[peak+40:peak+65]]));threshold=bg+.30*(p[peak]-bg)
        top=peak
        while top>0 and p[top]>=threshold:top-=1
        bot=peak
        while bot<len(p)-1 and p[bot]>=threshold:bot+=1
        top+=.5;bot-=.5;xref=1024;source='image contrast boundary estimate; no caliper supplied'
    width=bot-top;half=max(5,min(25,int(width*.6)));radius=max(9,min(35,int(width*.45+5)))
    profiles=[np.mean(sm[round(y)-half:round(y)+half+1,round(xref)-10:round(xref)+11],axis=1) for y in [top,bot]]
    results={}
    for n in [clean]+([ann] if ann else []):
        a=cv2.cvtColor(rgb(n),cv2.COLOR_RGB2GRAY)[:1419].astype(float);s=ndi.gaussian_filter(a,(.8,3))
        invalid=(max(1,box['x']-110),min(2047,box['x']+box['width']+110)) if boxes and n==ann else None
        b,_=track(s,bot,profiles[1],xref,radius,invalid)
        t,_=track(s,top,profiles[0],xref,radius,invalid,below=b,width_bounds=(max(3,width*.40),width*2.2+3))
        m=np.zeros((1536,2048),np.uint8)
        for x in range(2048):m[int(round(t[x])):int(round(b[x])),x]=255
        save(n,m);results[n]={'top':t,'bottom':b,'seed_top':top,'seed_bottom':bot,'xref':xref,'source':source,'caliper_file':ann}
        print('ZOOM',n,'median width nm',round(float(np.median(b-t)*META[n]['pixel_nm']),2),source,flush=True)
    return results

def overview(n):
    a=cv2.cvtColor(rgb(n),cv2.COLOR_RGB2GRAY)[:1419].astype(float);sm=ndi.gaussian_filter(a,(.7,4.0))
    cs=CENTERS[n];traces=[];contrasts=[];backgrounds=[];noises=[]
    for cy in cs:
        lo,hi=cy-22,cy+23;band=sm[lo:hi]
        bg=(np.median(sm[cy-34:cy-25],axis=0)+np.median(sm[cy+25:cy+34],axis=0))*.5
        signal=band-bg[None,:]
        denom=max(2,float(np.quantile(signal[:,300:1750],.98)))
        cost=-signal/denom+.20*((np.arange(lo,hi)[:,None]-cy)/8)**2
        center=seam(cost,step=1,penalty=.10)+lo
        center=ndi.gaussian_filter1d(center.astype(float),1)
        ctr=np.rint(center).astype(int);peak=sm[ctr,np.arange(2048)]
        contrast=peak-bg
        noise=float(np.median(np.abs(sm[cy-34:cy-25]-np.median(sm[cy-34:cy-25],axis=0))))/0.6745
        traces.append(center);contrasts.append(contrast);backgrounds.append(bg);noises.append(noise)
    # Locate the common printed field from multiple observed ridges, not a
    # fixed nominal design length. Per-line presence below still allows gaps.
    field=ndi.gaussian_filter1d(np.mean(contrasts,axis=0),3)
    base=float(np.median(np.r_[field[:40],field[-35:]]));height=float(np.quantile(field[250:1800],.65))
    # Weak printed tails can be much fainter than the beginning. A relative
    # 13% gate would shorten them; use the shared multi-line evidence only as
    # a broad field window, leaving presence decisions to individual pixels.
    hit=field>base+max(.20,.025*(height-base))
    rr=np.flatnonzero(np.diff(np.r_[False,hit,False]));runs=[(int(l),int(r)) for l,r in zip(rr[::2],rr[1::2]) if r-l>200]
    if not runs:raise RuntimeError(f'Cannot identify overview extent for {n}')
    left,right=max(runs,key=lambda p:p[1]-p[0]);left=max(35,left-20);right=min(2013,right+20)
    # Nominal length broadens the SEARCH ONLY when a tail has low contrast.
    # It never creates foreground; each column still needs image evidence.
    nominal=round(float(META[n]['params'][7])*1000/META[n]['pixel_nm'])
    right=min(2013,max(right,left+nominal+60))
    mask=np.zeros((1536,2048),np.uint8);line_masks=[]
    for i,cy in enumerate(cs):
        ctr=np.rint(traces[i]).astype(int);bg=backgrounds[i];contrast=contrasts[i];noise=noises[i]
        present=ndi.gaussian_filter1d(contrast,.8)>max(1.5,noise*2.3)
        obj=np.zeros((1536,2048),np.uint8)
        for x in range(left,right):
            if not present[x]:continue
            y=ctr[x];threshold=bg[x]+.30*contrast[x]
            t=y;b=y
            while t>cy-22 and sm[t-1,x]>threshold:t-=1
            while b<cy+22 and sm[b+1,x]>threshold:b+=1
            if b-t+1>8 and contrast[x]<max(3.5,noise*3.5):continue
            # Binary full visible cross-section, including cap taper.
            obj[t:b+1,x]=255
        count,labels,st,cent=cv2.connectedComponentsWithStats((obj>0).astype('uint8'))
        for k in range(1,count):
            if st[k,4]<9 or st[k,2]<3:obj[labels==k]=0
        mask=np.maximum(mask,obj);line_masks.append(obj)
    save(n,mask)
    print('OVERVIEW',n,'lines',len(cs),'field',left,right,'areas',[int(np.count_nonzero(m)) for m in line_masks],flush=True)
    return {'centers':cs,'field_x':[left,right],'traces':traces,'noise_estimates':noises}

if __name__=='__main__':
    metadata={};arrays={}
    for o,z,m in GROUPS:
        if o==37:continue
        if z:
            rr=zoom(z,m)
            for n,r in rr.items():
                arrays[f'{n}_top']=r.pop('top');arrays[f'{n}_bottom']=r.pop('bottom');metadata[str(n)]=r
        r=overview(o)
        for i,t in enumerate(r.pop('traces')):arrays[f'{o}_line{i+1}_center']=t
        metadata[str(o)]=r
    np.savez_compressed(ROOT/'boundary_traces.npz',**arrays)
    (ROOT/'mask_method.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
    assert len(list(OUT.glob('*_mask.png')))==49
    print('MASKS COMPLETE: 49 parameterized images; 1-01 and 1-37..1-39 excluded by user',flush=True)
