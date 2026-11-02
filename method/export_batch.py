from pathlib import Path
import json,csv,io,copy,hashlib,zipfile,shutil,sys
import numpy as np,cv2,ezdxf,openpyxl
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
from skimage.measure import find_contours
import engine,parameter_tools as PT,model_export as ME
import process_masks as PM

ROOT=Path('/workspace/sem_batch2');RAW=ROOT/'raw';MASK=ROOT/'masks'
DATA=ROOT/'export/SEM_batch02';DATA.mkdir(parents=True,exist_ok=True)
PUB=Path('/workspace/double/batch_02_1-01_to_1-53');PUB.mkdir(exist_ok=True)
(PUB/'archives').mkdir(exist_ok=True)
XLS=Path('/workspace/attachments/944b1b2b-5761-43ae-b762-badfe36a03b4/1.xlsx')
RECORDS=engine.parameter_rows(XLS.read_bytes(),XLS.name)
ORIGINAL={r['原文件名']:r for r in RECORDS if r.get('原文件名')}
EFFECTIVE=copy.deepcopy(ORIGINAL)
key=next(k for k in EFFECTIVE['1-26.tif'] if PT.identify(k)=='fs_power_mw');EFFECTIVE['1-26.tif'][key]=.443
META={m['file']:m for m in json.loads((ROOT/'metadata.json').read_text())}
METHOD=json.loads((ROOT/'mask_method.json').read_text())
TRACES=np.load(ROOT/'boundary_traces.npz')
EXCLUDE={'1-01.tif','1-37.tif','1-38.tif','1-39.tif'}
H=1419
with zipfile.ZipFile('/workspace/attachments/0478a636-373d-4c59-8326-07d0966aaa29/case_002.zip') as z:
    STANDARD={Path(n).name for n in z.namelist() if not n.endswith('/')}
    REVIEW_KEYS=set(json.loads(z.read('case_002/review.json')))
    MODEL_KEYS=set(json.loads(z.read('case_002/model_input.json')))

def js(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def csvsave(p,rows,fields=None):
    if fields is None:fields=list(dict.fromkeys(k for r in rows for k in r))
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:w.writerow({k:json.dumps(r.get(k),ensure_ascii=False) if isinstance(r.get(k),(dict,list)) else r.get(k) for k in fields})
def png(p,a):Image.fromarray(a).save(p)
def image_num(n):return f'1-{n:02}.tif'
def getmask(n):return np.asarray(Image.open(MASK/f'1-{n:02}_mask.png')).copy()
def overlay(n,m):
    a=np.asarray(Image.open(RAW/image_num(n)).convert('RGB')).copy();fg=m>0
    a[fg]=(.72*a[fg]+.28*np.array([20,215,150])).astype('uint8')
    e=cv2.morphologyEx(m,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))>0;a[e]=[255,130,20]
    return a
def grid(m,nm,pt):
    cx,cy=pt;xx,yy=np.meshgrid(cx+(np.arange(100)-49.5)*20/nm,cy+(np.arange(80)-39.5)*20/nm)
    return (ndi.map_coordinates(m.astype(float),[yy,xx],order=0,mode='constant',cval=0)>127).astype('uint8')*255

def line_stats(m,nm,centers):
    stats=[];points=[];centers=list(centers)
    for i,cy in enumerate(centers,1):
        lo=max(0,round(cy)-32);hi=min(H,round(cy)+33)
        obj=m[lo:hi]>0;cols=obj.sum(axis=0);xx=np.flatnonzero(cols)
        assert xx.size,(cy,'empty line')
        left,right=int(xx.min()),int(xx.max());cx=(left+right)/2;ix=round(cx)
        if cols[ix]:ys=np.flatnonzero(obj[:,ix]);y=float((ys.min()+ys.max())/2)+lo
        else:y=float(cy)
        widths=cols[cols>0]*nm
        stats.append({'线条':i,'有效列数':int(np.count_nonzero(cols)),'长度(µm)':round(float(np.count_nonzero(cols)*nm/1000),6),
            '中位线宽(nm)':round(float(np.median(widths)),3),'平均线宽(nm)':round(float(np.mean(widths)),3),
            '左端x_px':left,'右端x_px_含':right,'水平跨度(µm)':round(float((right-left+1)*nm/1000),6),
            '间断或低置信度列数':int((right-left+1)-np.count_nonzero(cols))})
        points.append((cx,y))
    return stats,points

def exact_dxf(m,nm,centers,params):
    # Half-pixel isocontours retain the full width of thin raster objects.
    unit=nm/1000;binary=m[:H]>0;doc=ezdxf.new('R2010');doc.header['$INSUNITS']=13;ms=doc.modelspace()
    for name,color in [('SEM_OBSERVED_CONTOURS',2),('SEM_OBSERVED_CENTERLINES',3),('DESIGN_SCAN_PATH',5),('SEM_FRAME',8)]:doc.layers.new(name,dxfattribs={'color':color})
    contours=find_contours(np.pad(binary.astype('uint8'),1),.5,fully_connected='high')
    for c in contours:
        p=c-1
        if np.allclose(p[0],p[-1]):p=p[:-1]
        if len(p)<3:continue
        # Remove only exactly collinear vertices; do not smooth narrow lines.
        a=np.roll(p,1,axis=0);b=np.roll(p,-1,axis=0)
        cross=(p[:,0]-a[:,0])*(b[:,1]-p[:,1])-(p[:,1]-a[:,1])*(b[:,0]-p[:,0])
        p=p[np.abs(cross)>1e-9]
        if len(p)>=3:ms.add_lwpolyline([(float(x*unit),float((H-1-y)*unit)) for y,x in p],close=True,dxfattribs={'layer':'SEM_OBSERVED_CONTOURS'})
    for i,cy in enumerate(centers):
        lo=max(0,round(cy)-32);hi=min(H,round(cy)+33);band=binary[lo:hi];active=band.any(axis=0)
        rr=np.flatnonzero(np.diff(np.r_[False,active,False]))
        for l,r in zip(rr[::2],rr[1::2]):
            if r-l<2:continue
            pts=[(float(x*unit),float((H-1-(lo+np.flatnonzero(band[:,x]).mean()))*unit)) for x in range(l,r)]
            ms.add_lwpolyline(pts,dxfattribs={'layer':'SEM_OBSERVED_CENTERLINES'})
        y=(H-1-cy)*unit;length=params['line_length_um']
        pts=[(0,y),(length,y)] if i%2==0 else [(length,y),(0,y)]
        ms.add_lwpolyline(pts,dxfattribs={'layer':'DESIGN_SCAN_PATH'})
    ms.add_lwpolyline([(0,0),(2048*unit,0),(2048*unit,H*unit),(0,H*unit)],close=True,dxfattribs={'layer':'SEM_FRAME'})
    out=io.StringIO();doc.write(out);return out.getvalue().encode('utf-8')

models=[];mapping=[];all_stats=[];audits=[];summary=[];case_ids=[]
for index,(o,z,m) in enumerate(PM.GROUPS,2):
    if o==37:continue
    cid=f'case_{index:03}';case_ids.append(cid);folder=DATA/cid;folder.mkdir(exist_ok=True)
    on=image_num(o);zn=image_num(z) if z else '';mn=image_num(m) if m else ''
    params=copy.deepcopy(EFFECTIVE[on]);params.update(PT.canonicalize(params));params['zoom_line_id']=3 if z else None;params['scan_pattern']='待确认'
    om=getmask(o);op=META[on]['pixel_nm'];os,opts=line_stats(om,op,PM.CENTERS[o]);centers=[round(y) for x,y in opts]
    zm=None;zp=None;zs=[];zpts=[];roi=None
    if z:
        zm=getmask(z);zp=META[zn]['pixel_nm'];zy=float(np.median((TRACES[f'{z}_top']+TRACES[f'{z}_bottom'])/2))
        # Zoom can be wider than the overview strip used by line_stats.
        cols=(zm>0).sum(axis=0);xx=np.flatnonzero(cols);ix=1024;yy=np.flatnonzero(zm[:,ix])
        zpts=[(1023.5,float((yy.min()+yy.max())/2))]
        widths=cols[cols>0]*zp
        zs=[{'线条':1,'有效列数':int(len(xx)),'长度(µm)':round(float(len(xx)*zp/1000),6),
            '中位线宽(nm)':round(float(np.median(widths)),3),'平均线宽(nm)':round(float(np.mean(widths)),3),
            '左端x_px':int(xx.min()),'右端x_px_含':int(xx.max()),'水平跨度(µm)':round(float((xx.max()-xx.min()+1)*zp/1000),6),'间断或低置信度列数':int((xx.max()-xx.min()+1)-len(xx))}]
        ratio=zp/op;w=round(2048*ratio);h=round(H*ratio);cx,cy=opts[2];zcx,zcy=zpts[0]
        x0=int(np.clip(round(cx-zcx*ratio),0,2048-w));y0=int(np.clip(round(cy-zcy*ratio),0,H-h));roi=[x0,y0,x0+w,y0+h]
    used=[(o,'overview')]+([(z,'zoom')] if z else [])+([(m,'measurement')] if m else [])
    for n,role in used:
        source=RAW/image_num(n);shutil.copy2(source,folder/f'original_{role}.tif')
        mapping.append({'case_id':cid,'role':role,'original_file':image_num(n),'export_file':f'{cid}/original_{role}.tif','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
        (DATA/'image_masks').mkdir(exist_ok=True);shutil.copy2(MASK/f'1-{n:02}_mask.png',DATA/'image_masks'/f'1-{n:02}_mask.png')
    png(folder/'overview_mask.png',om);png(folder/'overview_overlay.png',overlay(o,om));png(folder/'overview_psf_grid.png',grid(om,op,opts[2]))
    if z:
        png(folder/'zoom_mask.png',zm);png(folder/'zoom_overlay.png',overlay(z,zm));png(folder/'zoom_psf_grid.png',grid(zm,zp,zpts[0]))
    (folder/'observed_contours_and_design_path.dxf').write_bytes(exact_dxf(om,op,centers,params))
    ranges={str(i):[r['左端x_px']/2048*100,(r['右端x_px_含']+1)/2048*100] for i,r in enumerate(os)}
    perimage={image_num(n):{'original':ORIGINAL[image_num(n)],'effective':EFFECTIVE[image_num(n)]} for n,role in used}
    incomplete=[]
    if not m:incomplete.append('original_measurement.tif')
    if not z:incomplete.extend(['original_zoom.tif','zoom_mask.png','zoom_overlay.png','zoom_psf_grid.png'])
    weak=[r['线条'] for r in os if r['间断或低置信度列数']>50]
    review={'overview':on,'zoom':zn,'measurement':mn,'params':params,'pairing':'本批参数表原文件名、倍率和图像内容对应；放大位置由用户确认',
        'spacing_um':params['spacing_um'],'design_count':4,'centers':centers,'line_ranges':ranges,'zoom_roi_xyxy':roi,'zoom_roi_verified':False,
        'segmentation_mode':'完整可见线体：放大图局部卡尺/图像剖面边界跟踪；整体图局部对比与连续位置约束，弱响应列保留缺失',
        'overview_nm_per_px':op,'zoom_nm_per_px':zp,'status':'自动提取完成，待实验逐像素复核','parameters_verified':False,'pairing_verified':False,
        'overview_line_stats':os,'zoom_line_stats':zs,'dataset_id':'batch02_'+cid,'mask_version':'batch02_full_visible_body',
        'parameters_by_image':perimage,'missing_expected_files':incomplete,'zoom_correspondence_confirmed_by_user':bool(z),
        'zoom_location_source':'用户确认本批仍对应整体图第三条线中间' if z else None,
        'zoom_roi_method':'第三条线可见区域中部，按双图独立TIFF刻度和线体中心估计；非独立特征精确配准' if z else None,
        'mask_shape_yx':[1536,2048],'overview_valid_image_height_px':H,'zoom_valid_image_height_px':H if z else None,
        'low_contrast_or_fragmented_overview_lines':weak,
        'width_length_definition':'宽度为垂直前景像素数；长度为有效列数乘像素尺寸，水平跨度另列。放大图长度是视野截断范围，不等于整条打印长度。',
        'dxf_coordinate_convention':'um; x=x_px*nm/1000; y=(1419-1-y_px)*nm/1000; local bottom-left valid-image origin; half-pixel closed contours preserve full raster-cell widths',
        'grid_metadata':{'shape_yx':[80,100],'step_nm':20,'overview_anchor_xy_px':list(opts[2]),'zoom_anchor_xy_px':list(zpts[0]) if z else None,'meaning':'local binary mask sampling only; not optical PSF or PDE result'},
        'review_limitations':['caliper positions serve as local seeds, not independent validation','annotation-occluded boundaries use neighboring image evidence','low-contrast overview tails and particle-contaminated portions need manual review','real scan timing and stage-to-writing registration not supplied']}
    if o==24:review['parameter_correction']={'file':'1-26.tif','field':'fs_power_mw','original':.205,'effective':.443,'authority':'explicit user confirmation'}
    model=ME.review_to_model_record(index,review,(folder/'overview_mask.png').read_bytes(),(folder/'zoom_mask.png').read_bytes() if z else None)
    model.update({'dataset_id':'batch02_'+cid,'mask_quality':'image_and_local_reference_guided_full_body_candidate_not_independent_ground_truth',
        'mask_version':review['mask_version'],'coordinate_convention':review['dxf_coordinate_convention'],
        'parameters_source_checked':True,'zoom_correspondence_confirmed_by_user':bool(z),'zoom_location_source':review['zoom_location_source'],
        'overview_valid_image_height_px':H,'zoom_valid_image_height_px':H if z else None,'grid_metadata':review['grid_metadata'],
        'missing_expected_files':incomplete,'low_contrast_or_fragmented_overview_lines':weak})
    model['needs_review']+=['mask_boundaries_not_independent_labels','scan_timing_unprovided']
    if incomplete:model['needs_review'].append('source_images_missing')
    if weak:model['needs_review'].append('low_contrast_or_fragmented_overview')
    if o==24:model['parameter_correction']=review['parameter_correction']
    model['ready_for_registration']=False;model['ready_for_training']=False
    js(folder/'review.json',review);js(folder/'model_input.json',model)
    files={p.name for p in folder.iterdir()};assert files==STANDARD-set(incomplete)
    assert REVIEW_KEYS.issubset(review) and MODEL_KEYS.issubset(model)
    doc=ezdxf.readfile(folder/'observed_contours_and_design_path.dxf');assert not doc.audit().has_errors and doc.header['$INSUNITS']==13
    polygons=[]
    for e in doc.modelspace().query('LWPOLYLINE[layer=="SEM_OBSERVED_CONTOURS"]'):
        polygons.append(np.rint(np.asarray([(p[0]/(op/1000),H-1-p[1]/(op/1000)) for p in e.get_points()])*4).astype('int32'))
    canvas=np.zeros((H*4,2048*4),np.uint8);cv2.fillPoly(canvas,polygons,1);raster=canvas[::4,::4]>0;target=om[:H]>0
    iou=float(np.count_nonzero(raster&target)/np.count_nonzero(raster|target));assert iou>.999,(cid,'DXF/mask mismatch',iou)
    for n,role in used:
        source=RAW/image_num(n);assert (folder/f'original_{role}.tif').read_bytes()==source.read_bytes()
        mm=getmask(n);assert mm.shape==(1536,2048) and set(np.unique(mm))=={0,255} and not mm[H:].any()
        if role in ['overview','zoom']:assert np.array_equal(np.asarray(Image.open(folder/f'{role}_mask.png')),mm)
    for role in ['overview']+(['zoom'] if z else []):
        im=Image.open(folder/f'{role}_overlay.png');im.load();assert im.size==(2048,1536)
        gg=np.asarray(Image.open(folder/f'{role}_psf_grid.png'));assert gg.shape==(80,100) and set(np.unique(gg)).issubset({0,255})
    for view,rows in [('overview',os),('zoom',zs)]:all_stats.extend({'case_id':cid,'view':view,**r} for r in rows)
    models.append(model);summary.append({'case_id':cid,'overview':on,'zoom':zn,'measurement':mn,'517nm_mW':params['fs_power_mw'],'671nm_mW':params['cw_power_mw'],'speed_um_s':params['speed_um_s'],
        'overview_nm_px':op,'zoom_nm_px':zp,'standard_file_count':len(files),'missing':incomplete,'review':model['needs_review']})
    archive=PUB/'archives'/f'{cid}.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as out:
        for p in sorted(folder.iterdir()):out.write(p,str(p.relative_to(DATA)))
        for n,role in used:
            p=DATA/'image_masks'/f'1-{n:02}_mask.png';out.write(p,str(p.relative_to(DATA)))
    with zipfile.ZipFile(archive) as zz:assert zz.testzip() is None
    audit={'case_id':cid,'standard_file_count':len(files),'missing_files':incomplete,'sample_filename_structure_matches_available_sources':True,
        'tiff_bytes_unchanged':True,'mask_alignment_original_size':True,'dxf_raster_iou':iou,'zip':archive.name,'zip_bytes':archive.stat().st_size,'zip_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
    audits.append(audit);print(cid,'images',len(used),'standard files',len(files),'MiB',round(archive.stat().st_size/1024**2,2),'DXF IoU',iou,flush=True)

assert len(models)==18 and len(mapping)==49
assert {r['original_file'] for r in mapping}==set(META)-EXCLUDE
assert len(list((DATA/'image_masks').glob('*.png')))==49
sources=DATA/'sources';sources.mkdir(exist_ok=True);shutil.copy2(XLS,sources/'1_original.xlsx')
wb=openpyxl.load_workbook(XLS)
for row in wb['数据填写'].iter_rows(min_row=2):
    if row[1].value=='1-26.tif':row[4].value=.443
sh=wb.create_sheet('本次用户确认修正');sh.append(['文件','字段','原值','采用值','依据']);sh.append(['1-26.tif','517nm功率(mW)',.205,.443,'用户明确确认本组0.443mW'])
wb.save(sources/'1_corrected.xlsx')
js(DATA/'user_confirmations.json',json.loads((ROOT/'user_confirmations.json').read_text()))
js(DATA/'colab_model_manifest.json',{'format_version':'7.2-compatible-batch02','cases':models})
csvsave(DATA/'colab_model_manifest.csv',models,['case_id','dataset_id','overview_file','zoom_file','measurement_file','fs_power_mw','cw_power_mw','speed_um_s','spacing_um','line_length_um','n_lines','zoom_line_id','overview_pixel_nm','zoom_pixel_nm','ready_for_training','missing_expected_files','needs_review'])
csvsave(DATA/'file_mapping.csv',mapping);csvsave(DATA/'line_measurements.csv',all_stats);csvsave(DATA/'case_summary.csv',summary)
js(DATA/'validation.json',{'checks_passed':True,'batch_id':'batch02','processed_images':49,'cases':18,'complete_cases':14,'incomplete_cases':4,
    'excluded_without_parameters':sorted(EXCLUDE),'exclusion_authority':'explicit user instruction: do not process images without parameters',
    'parameter_correction':{'file':'1-26.tif','fs_power_mw_original':.205,'fs_power_mw_effective':.443},
    'validation_scope':'source/mask integrity, schema and dimensions, archive CRC and exact raster contour consistency; not independent SEM segmentation accuracy certification','case_checks':audits})
workbook=openpyxl.Workbook();sh=workbook.active;sh.title='分组汇总'
for name,rr in [('分组汇总',summary),('逐图文件映射',mapping),('掩膜宽度与跨度',all_stats)]:
    ws=sh if name=='分组汇总' else workbook.create_sheet(name);fields=list(dict.fromkeys(k for r in rr for k in r));ws.append(fields)
    for r in rr:ws.append([json.dumps(r.get(k),ensure_ascii=False) if isinstance(r.get(k),(dict,list)) else r.get(k) for k in fields])
    ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
    for c in ws[1]:c.font=openpyxl.styles.Font(bold=True,color='FFFFFF');c.fill=openpyxl.styles.PatternFill('solid',fgColor='174B63')
    for col in ws.columns:ws.column_dimensions[col[0].column_letter].width=23
ex=workbook.create_sheet('排除与缺项');ex.append(['未处理图像','原因'])
for n in sorted(EXCLUDE):ex.append([n,'参数表无工艺参数，按用户要求不处理'])
for r in summary:
    if r['missing']:ex.append([r['case_id'],'源图缺项：'+', '.join(r['missing'])])
workbook.save(DATA/'SEM_batch02_summary.xlsx')

# Fresh previews from the final masks, without including excluded images.
preview=DATA/'previews';preview.mkdir(exist_ok=True)
over=[o for o,z,m in PM.GROUPS if o!=37];zo=[z for o,z,m in PM.GROUPS if o!=37 and z]
for title,nums,h in [('overview_review',over,450),('zoom_review',zo,240)]:
    board=Image.new('RGB',(1800,((len(nums)+1)//2)*h),'white');d=ImageDraw.Draw(board)
    for i,n in enumerate(nums):
        im=Image.open(MASK/f'1-{n:02}_overlay.jpg')
        if title=='overview_review':im=im.crop((0,280,2048,1100))
        else:
            yy=np.nonzero(getmask(n))[0];cy=int(np.median(yy));im=im.crop((0,cy-150,2048,cy+150))
        im.thumbnail((880,h-45));x=i%2*900;y=i//2*h;board.paste(im,(x,y+30));d.text((x+5,y+3),f'Batch02 1-{n:02}',fill='black',font_size=22)
    board.save(preview/f'{title}.jpg',quality=93)
method=DATA/'method';method.mkdir(exist_ok=True);shutil.copy2(ROOT/'process_masks.py',method/'process_masks.py');shutil.copy2(ROOT/'export_batch.py',method/'export_batch.py')
js(method/'mask_method.json',METHOD)

readme='''# 第二批 SEM 完整数据（本次上传的1.xlsx及三个ZIP）

本批图片与此前同名图像内容不同，使用独立目录保存。按用户确认：处理本次全部有工艺参数的图像；放大结构对应整体图第三条线中部；1-26的517nm功率统一采用0.443mW；无参数图像不处理。

实际处理 **49张原图，18组**。排除1-01、1-37、1-38、1-39。49张原始TIFF原样保留，并各有原尺寸2048×1536二值PNG掩膜；y≥1419的参数栏为背景。

## 下载完整结果

请下载下面三个完整分包，并依次解压到同一个目录，合并SEM_batch02文件夹。

'''
for i in range(1,4):readme+=f'- [完整分包{i}](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/batch_02_1-01_to_1-53/SEM_batch02_complete_part{i:02}_of_03.zip)\n'
readme+='''
## 单组下载

| 组号 | 整体图 | 放大图 | 标注图 | 下载 |
|---|---|---|---|---|
'''
for r in summary:
    cid=r['case_id'];readme+=f'| {cid} | {r["overview"]} | {r["zoom"] or "未上传"} | {r["measurement"] or "未上传"} | [ZIP](archives/{cid}.zip) |\n'
readme+='''
每个完整组沿用case_002样例的12个标准文件：3张原始TIFF、整体/放大mask及overlay PNG、2张局部网格、DXF、review.json、model_input.json。14组完整；4组按实际源图保存可用文件，不生成虚构原图或空白替代文件：

- case_006（1-14/1-15）、case_007（1-16/1-17）、case_017（1-43/1-44）未上传独立标注图，各有11个标准文件。
- case_014只有1-36整体图，未上传对应放大/标注图，有7个标准文件。
- case_015对应无参数的1-37..1-39，按用户要求排除，所以组号保留空缺。

每个单组ZIP另附该组逐图掩膜image_masks。完整分包共同含49张逐图掩膜、原/修正Excel、汇总Excel、CSV/JSON清单和叠加总览。

## 数据定义与复核

放大图通过本图/对应标注图的局部宽度种子和灰度剖面追踪上下边界，填充完整可见主体；没有标注的放大图以图像对比估计种子。标注遮挡区依邻近图像证据插值，仍含估计成分。

整体图沿四条可见目标线提取完整横截面，并按每列的局部图像响应保留低对比缺失。已知名义50µm只扩大低对比尾部的搜索范围，不用于强制补齐掩膜长度。弱尾、颗粒遮挡和间断不能仅凭自动掩膜断定是真实断口，已在needs_review中记录。

宽度按图像列的垂直前景像素数计；长度按有效列数乘像素尺寸计，水平跨度另列。放大图可见长度受视野截断，不能当作整条打印长度。每张图独立读取TIFF刻度，包括1-17、1-49和1-50的3.453nm/px。

DXF单位um，局部有效图像左下原点：x=x_px*nm/1000，y=(1419-1-y_px)*nm/1000。使用半像素闭合轮廓保留细掩膜的实际像素单元宽度；中心线在缺失处断开。50µm设计路径是名义几何，不代表实际扫描方向/时序。

PSF命名PNG是80×100、20nm步长的局部二值掩膜采样，不是光学PSF。没有复制样例的人工确认状态；标签精度、真实扫描时序和PDE配准仍需实验复核，ready_for_training=false。

validation.json检查原图字节一致性、49张掩膜尺寸/值域、按可用源图匹配样例文件名、DXF重新栅格化一致性和压缩包CRC；这些文件一致性检查不等同于独立分割精度认证。
'''
(DATA/'README.md').write_text(readme,encoding='utf-8');(PUB/'README.md').write_text(readme,encoding='utf-8')
for n in ['SEM_batch02_summary.xlsx','colab_model_manifest.json','colab_model_manifest.csv','case_summary.csv','file_mapping.csv','line_measurements.csv','validation.json','user_confirmations.json']:
    shutil.copy2(DATA/n,PUB/n)
for p in preview.iterdir():shutil.copy2(p,PUB/p.name)
only=PUB/'SEM_batch02_masks_49.zip'
with zipfile.ZipFile(only,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted((DATA/'image_masks').glob('*.png')):z.write(p,p.name)
with zipfile.ZipFile(only) as z:assert len(z.infolist())==49 and z.testzip() is None

part_records=[];seen=[]
for i in range(3):
    chosen=case_ids[i*6:(i+1)*6];allowed=set(chosen)
    names={r['original_file'] for r in mapping if r['case_id'] in allowed}
    target=PUB/f'SEM_batch02_complete_part{i+1:02}_of_03.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for p in sorted(DATA.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(DATA);first=rel.parts[0]
            include=first in allowed or (first=='image_masks' and p.name.replace('_mask.png','.tif') in names)
            if first not in set(case_ids) and first!='image_masks':include=i==0
            if include:z.write(p,str(Path(DATA.name)/rel));seen.append(str(rel))
    with zipfile.ZipFile(target) as z:assert z.testzip() is None
    assert target.stat().st_size<100*1024**2
    part_records.append({'file':target.name,'cases':chosen,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    print('COMPLETE PART',i+1,round(target.stat().st_size/1024**2,2),'MiB',flush=True)
assert sorted(seen)==sorted(str(p.relative_to(DATA)) for p in DATA.rglob('*') if p.is_file())
js(PUB/'package_integrity.json',{'parts':part_records,'all_files_covered_once':True,'case_packages':audits})
print('DONE: 49 images, 18 groups, 14 complete + 4 source-incomplete; 3 complete download parts',flush=True)
