from pathlib import Path
import json,numpy as np,cv2
from scipy import ndimage as ndi
from skimage.segmentation import active_contour
from PIL import Image

ROOT=Path('/workspace/sem_rework');OUT=ROOT/'results'
bs=np.load(OUT/'boundaries.npz');stats=json.loads((OUT/'measurements.json').read_text())
details=[]
for n in [24,27,30,33,36,39,42,45]:
    rgb=np.asarray(Image.open(f'/workspace/sem_work/raw/1-{n:02}.tif').convert('RGB'))
    gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)[:1419]
    sm=ndi.gaussian_filter(gray.astype(float)/255,(1,1.5))
    mask=np.asarray(Image.open(OUT/f'1-{n:02}_mask.png')).copy()
    for k in range(1,5):
        r=next(v for v in stats if v['file']==f'1-{n:02}.tif' and v.get('line')==k)
        top=bs[f'{n}_line{k}_top'];bot=bs[f'{n}_line{k}_bottom']
        for side in ['left','right']:
            ex=r['x_start'] if side=='left' else r['x_end_exclusive']-1
            inner=ex+35 if side=='left' else ex-35
            yt,yb=top[inner],bot[inner]
            cy=(yt+yb)/2;half=(yb-yt)/2
            angles=np.linspace(-np.pi/2,np.pi/2,61)
            xs=inner+(-1 if side=='left' else 1)*35*np.cos(angles)
            ys=cy+half*np.sin(angles)
            lx=min(ex,inner)-15;rx=max(ex,inner)+16;ly=int(min(yt,yb))-12;ry=int(max(yt,yb))+13
            initial=np.column_stack([ys-ly,xs-lx])
            fitted=active_contour(sm[ly:ry,lx:rx],initial,alpha=.001,beta=.2,w_line=0,w_edge=100,
                gamma=.01,max_px_move=.2,max_num_iter=600,convergence=.015,boundary_condition='fixed')
            fy=fitted[:,0]+ly;fx=fitted[:,1]+lx
            # The longitudinal contrast change supplies the end location.
            # Weak SEM rims must not allow an elastic contour to retract and
            # shorten the line. Retain this observed apex as a third landmark.
            mid=len(angles)//2
            fx+=(ex-fx[mid])*np.cos(angles)**4
            fy+=(cy-fy[mid])*np.cos(angles)**6
            # Keep the fit in the observed end neighborhood and preserve its
            # attachment to the independently tracked material boundaries.
            fx=np.clip(fx,min(ex,inner)-6,max(ex,inner)+6)
            fy=np.clip(fy,ly+2,ry-3)
            if side=='left':fx=np.minimum(fx,inner)
            else:fx=np.maximum(fx,inner)
            fx[[0,-1]]=inner;fy[0]=yt;fy[-1]=yb
            fx[mid]=ex;fy[mid]=cy
            polygon=np.column_stack([fx-lx,fy-ly]).round().astype('int32')
            cap=np.zeros((ry-ly,rx-lx),np.uint8);cv2.fillPoly(cap,[polygon],255)
            if side=='left':mask[ly:ry,lx:inner+1]=cap[:,:inner-lx+1]
            else:mask[ly:ry,inner:rx]=cap[:,inner-lx:]
            details.append({'image':n,'line':k,'side':side,'initial_endpoint_x':ex,
                'method':'image-gradient active contour with fixed attachment to full-body boundary traces',
                'fitted_xy':np.column_stack([fx,fy]).tolist()})
        strip=np.zeros(mask.shape,bool)
        for x in range(2048):
            lo=max(0,int(top[x])-15);hi=min(1419,int(bot[x])+16);strip[lo:hi,x]=mask[lo:hi,x]>0
        widths=strip.sum(axis=0);xx=np.flatnonzero(widths)
        r['x_start']=int(xx.min());r['x_end_exclusive']=int(xx.max()+1)
        r['length_um']=(r['x_end_exclusive']-r['x_start'])*27.91/1000
        r['median_nm']=float(np.median(widths[widths>0])*27.91)
        r['min_nm']=float(np.min(widths[widths>0])*27.91);r['max_nm']=float(np.max(widths)*27.91)
        r['foreground_column_count']=int(np.count_nonzero(widths))
    Image.fromarray(mask).save(OUT/f'1-{n:02}_mask.png')
    ov=rgb.copy();yes=mask>0;ov[yes]=(.72*ov[yes]+.28*np.array([20,215,150])).astype('uint8')
    border=cv2.morphologyEx(mask,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))>0;ov[border]=[255,130,20]
    Image.fromarray(ov).save(OUT/f'1-{n:02}_overlay.jpg',quality=93)
    print(n,'full-body caps fitted',flush=True)
(OUT/'measurements.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
(OUT/'endcap_refinement.json').write_text(json.dumps(details,ensure_ascii=False,indent=2))
