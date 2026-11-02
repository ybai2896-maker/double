from pathlib import Path
import json,csv,io,zipfile,shutil
import numpy as np,cv2
from scipy import ndimage as ndi
from scipy.signal import find_peaks
from PIL import Image,ImageDraw

ROOT=Path('/workspace/sem_rework');RAW=Path('/workspace/sem_work/raw')
OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
PAIRS={22:23,26:25,28:29,31:32,34:35,37:38,40:41,43:44}
OVERVIEW={24:22,27:26,30:28,33:31,36:34,39:37,42:40,45:43}
REFERENCE_NM={22:502.4,26:509.4,28:488.5,31:334.9,34:467.5,37:328,40:314,43:300.1}
BRACKETS=json.loads((ROOT/'brackets.json').read_text())
CENTERS=json.loads(Path('/workspace/sem_work/inspection/centers.json').read_text())

def load(n):return np.asarray(Image.open(RAW/f'1-{n:02}.tif').convert('RGB'))

def seam(cost,step=2,penalty=.025):
    h,w=cost.shape;acc=cost[:,0].copy();back=np.zeros((h,w),np.int8)
    shifts=np.arange(-step,step+1)
    for x in range(1,w):
        options=[]
        for d in shifts:
            q=np.full(h,np.inf)
            if d<0:q[-d:]=acc[:d]
            elif d>0:q[:-d]=acc[d:]
            else:q=acc.copy()
            options.append(q+penalty*d*d)
        choices=np.stack(options);best=np.argmin(choices,axis=0)
        acc=cost[:,x]+np.min(choices,axis=0);back[:,x]=shifts[best]
    path=np.zeros(w,int);path[-1]=np.argmin(acc)
    for x in range(w-1,0,-1):path[x-1]=path[x]+back[path[x],x]
    return path

def track(gray,target,template,xref,radius=50,invalid=None,anchor=True,below=None,width_bounds=None):
    half=len(template)//2;lo=max(half,int(target-radius));hi=min(gray.shape[0]-half-1,int(target+radius))
    strip=np.ascontiguousarray(gray[lo-half:hi+half+1],np.float32)
    templ=np.ascontiguousarray(template.reshape(-1,1),np.float32)
    response=cv2.matchTemplate(strip,templ,cv2.TM_CCOEFF_NORMED)
    ys=np.arange(lo,hi+1)
    cost=-3*response+.06*((ys[:,None]-target)/radius)**2
    if invalid:
        a,b=invalid
        for y in range(cost.shape[0]):cost[y,a:b]=np.interp(np.arange(a,b),[a-1,b],[cost[y,a-1],cost[y,b]])
    if anchor:
        # The supplied SEM caliper is a local boundary seed, not a fixed width.
        xs=np.arange(gray.shape[1]);weight=np.exp(-.5*((xs-xref)/35)**2)
        cost+=.6*((ys[:,None]-target)/8)**2*weight
    if below is not None:
        mn,mx=width_bounds
        distance=below[None,:]-ys[:,None]
        cost[(distance<mn)|(distance>mx)]=1e6
    path=seam(cost)+lo
    return ndi.gaussian_filter1d(path.astype(float),1.3),response

def zoom_masks(clean,ann):
    rgb=load(clean);gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)[:1419].astype(np.float32)
    smooth=ndi.gaussian_filter(gray,(1.3,5))
    b=BRACKETS[f'1-{clean:02}.tif']['brackets'][0]
    xref=b['x']+b['width']/2
    upper=b['y']+1.5;lower=b['y']+b['height']-2.5
    profiles=[]
    for y in [upper,lower]:
        yy=int(round(y));profiles.append(np.mean(smooth[yy-25:yy+26,int(xref)-12:int(xref)+13],axis=1))
    outputs={}
    for n in [clean,ann]:
        rgb=load(n);a=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)[:1419].astype(float)
        sm=ndi.gaussian_filter(a,(1.3,5))
        invalid=(max(1,b['x']-110),min(2047,b['x']+b['width']+110)) if n==ann else None
        top,_=track(sm,upper,profiles[0],xref,50,invalid)
        bot,_=track(sm,lower,profiles[1],xref,50,invalid)
        mask=np.zeros(rgb.shape[:2],np.uint8)
        for x in range(a.shape[1]):mask[int(round(top[x])):int(round(bot[x])),x]=255
        outputs[n]={'mask':mask,'top':top,'bottom':bot,'pixel_nm':3.489,'xref':xref,
                    'caliper_top':upper,'caliper_bottom':lower,'kind':'zoom','boundary_source':clean}
    return outputs

def overview_mask(n,zoom_result):
    rgb=load(n);a=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)[:1419].astype(np.float32)
    sm=ndi.gaussian_filter(a,(.8,2.5));nm=27.91
    mask=np.zeros(rgb.shape[:2],np.uint8);lines=[]
    estimated=np.median(zoom_result['bottom']-zoom_result['top'])*3.489/nm
    gy=ndi.gaussian_filter1d(np.mean(sm[:,850:1200],axis=1),.7,order=1)
    for i,center in enumerate(CENTERS[f'1-{n:02}.tif']):
        # Last darkward transition below the bright lower rim.
        ids=np.arange(center-4,center+13);by=int(ids[np.argmin(gy[ids])])
        ty_est=by-estimated
        p=np.mean(sm[:,850:1200],axis=1)
        # Search the upper outer trough, including double-rim cross sections.
        # A narrow window can incorrectly select the inter-rim trough (1-33 L1).
        ids=np.arange(int(ty_est-13),int(ty_est+11));ty=int(ids[np.argmin(p[ids])])
        templates=[np.mean(sm[y-5:y+6,980:1060],axis=1) for y in [ty,by]]
        bot,_=track(sm,by,templates[1],1024,radius=32,anchor=False)
        top,_=track(sm,ty,templates[0],1024,radius=40,anchor=False,below=bot,width_bounds=(max(4,estimated*.5),estimated*1.7+3))
        # Columnwise structural contrast over the complete cross section.
        energy=[]
        hp=a-ndi.gaussian_filter(a,(12,1))
        for x in range(2048):
            t=int(top[x]);b=int(bot[x]);energy.append(np.mean(np.abs(hp[max(0,t-3):b+4,x])))
        energy=ndi.gaussian_filter1d(np.asarray(energy),3)
        bg=float(np.median(np.r_[energy[:40],energy[-30:]]));signal=float(np.quantile(energy[250:1800],.6))
        active=energy>bg+.07*(signal-bg)
        runs=np.flatnonzero(np.diff(np.r_[False,active,False]));intervals=[(int(l),int(r)) for l,r in zip(runs[::2],runs[1::2]) if r-l>70]
        if not intervals:raise RuntimeError(f'Cannot find endpoints for {n} line {i}')
        left,right=max(intervals,key=lambda p:p[1]-p[0])
        for x in range(left,right):
            t,b=top[x],bot[x]
            if b>t:mask[int(round(t)):int(round(b)),x]=255
        lines.append({'line':i+1,'top':top,'bottom':bot,'left':left,'right':right,'initial_top':ty,'initial_bottom':by})
    return {'mask':mask,'lines':lines,'pixel_nm':nm,'kind':'overview'}

def visualize(n,r):
    rgb=load(n);mask=r['mask'];a=rgb.copy()
    # Lower alpha leaves the original material texture visible for inspection.
    yes=mask>0;a[yes]=(.72*a[yes]+.28*np.array([20,215,150])).astype('uint8')
    edge=cv2.morphologyEx(mask,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))>0
    a[edge]=[255,130,20]
    Image.fromarray(mask).save(OUT/f'1-{n:02}_mask.png')
    Image.fromarray(a).save(OUT/f'1-{n:02}_overlay.jpg',quality=93)
    return a

if __name__=='__main__':
    results={}
    for clean,ann in PAIRS.items():
        got=zoom_masks(clean,ann);results.update(got)
        for n,r in got.items():visualize(n,r)
    for n,z in OVERVIEW.items():results[n]=overview_mask(n,results[z])
    stats=[]
    for n,r in sorted(results.items()):
        visualize(n,r)
        if r['kind']=='zoom':
            widths=(r['bottom']-r['top'])*r['pixel_nm'];ref=REFERENCE_NM[n if n in PAIRS else next(c for c,a in PAIRS.items() if a==n)]
            rec={'file':f'1-{n:02}.tif','kind':'zoom','median_nm':float(np.median(widths)),'min_nm':float(np.min(widths)),'max_nm':float(np.max(widths)),
                 'caliper_width_nm':ref,'width_at_caliper_nm':float(widths[round(r['xref'])]),'x_start':0,'x_end_exclusive':2048}
            stats.append(rec);print(rec,flush=True)
        else:
            for line in r['lines']:
                widths=(line['bottom']-line['top'])[line['left']:line['right']]*r['pixel_nm']
                rec={'file':f'1-{n:02}.tif','kind':'overview','line':line['line'],'median_nm':float(np.median(widths)),
                     'min_nm':float(np.min(widths)),'max_nm':float(np.max(widths)),
                     'x_start':line['left'],'x_end_exclusive':line['right'],'length_um':(line['right']-line['left'])*r['pixel_nm']/1000}
                stats.append(rec);print(rec,flush=True)
    (OUT/'measurements.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
    # Save numeric boundaries for full-resolution inspection and reproducibility.
    arrays={}
    for n,r in results.items():
        if r['kind']=='zoom':arrays[f'{n}_top']=r['top'];arrays[f'{n}_bottom']=r['bottom']
        else:
            for l in r['lines']:
                arrays[f'{n}_line{l["line"]}_top']=l['top'];arrays[f'{n}_line{l["line"]}_bottom']=l['bottom']
    np.savez_compressed(OUT/'boundaries.npz',**arrays)
