from pathlib import Path
import json,csv,hashlib,zipfile,shutil,io
import numpy as np,cv2
from PIL import Image,ImageDraw

ROOT=Path('/workspace/sem_rework');SRC=ROOT/'results';RAW=Path('/workspace/sem_work/raw')
REPO=Path('/workspace/double');DEST=REPO/'masks_v2_1-22_to_1-45'
for name in ['masks','overlays','method']: (DEST/name).mkdir(parents=True,exist_ok=True)
overview=[24,27,30,33,36,39,42,45]
measurements=[];audit=[]
for n in range(22,46):
    p=SRC/f'1-{n:02}_mask.png';m=np.asarray(Image.open(p)).copy()
    count,labels,stats,cents=cv2.connectedComponentsWithStats((m>0).astype('uint8'))
    removed=[]
    for k in range(1,count):
        if stats[k,4]<64:removed.append(int(stats[k,4]));m[labels==k]=0
    Image.fromarray(m).save(p)
    rgb=np.asarray(Image.open(RAW/f'1-{n:02}.tif').convert('RGB'))
    ov=rgb.copy();yes=m>0;ov[yes]=(.72*ov[yes]+.28*np.array([20,215,150])).astype('uint8')
    edge=cv2.morphologyEx(m,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))>0;ov[edge]=[255,130,20]
    Image.fromarray(ov).save(SRC/f'1-{n:02}_overlay.jpg',quality=93)
    shutil.copy2(p,DEST/'masks'/p.name);shutil.copy2(SRC/f'1-{n:02}_overlay.jpg',DEST/'overlays'/f'1-{n:02}_overlay.jpg')
    assert m.shape==rgb.shape[:2]==(1536,2048)
    assert set(np.unique(m))=={0,255} and not m[1419:].any()
    count,l,st,ct=cv2.connectedComponentsWithStats((m>0).astype('uint8'))
    assert count-1==(4 if n in overview else 1),(n,count-1)
    for i,k in enumerate(sorted(range(1,count),key=lambda k:ct[k,1]),1):
        component=l==k;cols=component.sum(axis=0);xs=np.flatnonzero(cols)
        nm=27.91 if n in overview else 3.489
        measurements.append({'图像':f'1-{n:02}.tif','线条':i,'类型':'整体图' if n in overview else '放大图',
            'nm_per_px':nm,'左端x_px':int(xs.min()),'右端x_px_含':int(xs.max()),
            '水平可见跨度_um':round(float((xs.max()-xs.min()+1)*nm/1000),6),
            '中位垂直线宽_nm':round(float(np.median(cols[cols>0])*nm),3),
            '最小垂直线宽_nm_含端部':round(float(np.min(cols[cols>0])*nm),3),
            '最大垂直线宽_nm':round(float(np.max(cols)*nm),3),
            '前景面积_px':int(component.sum()),
            '边界长度说明':'两端位于画外；此处仅为可见视野跨度' if n not in overview else '原图可见端点之间的水平跨度；未强制设为50um'})
    if n not in overview:assert (m[:,0]>0).any() and (m[:,-1]>0).any()
    audit.append({'file':p.name,'source_tiff':f'1-{n:02}.tif','size_xy':[2048,1536],
        'binary_values':[0,255],'footer_black_from_y':1419,'major_components':count-1,
        'removed_disconnected_fit_fragments_area_px':removed,
        'mask_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
        'source_sha256':hashlib.sha256((RAW/f'1-{n:02}.tif').read_bytes()).hexdigest()})

for name in ['reextract.py','refine_caps_snake.py','package_v2.py','brackets.json']:
    shutil.copy2(ROOT/name,DEST/'method'/name)
shutil.copy2('/workspace/sem_work/inspection/centers.json',DEST/'method/selected_overview_centers.json')
for name in ['boundaries.npz','endcap_refinement.json']:
    shutil.copy2(SRC/name,DEST/'method'/name)
(DEST/'validation.json').write_text(json.dumps({'checks_passed':True,'image_count':24,
    'scope':'file integrity, binary format, original alignment and component checks; not independent accuracy certification',
    'images':audit},ensure_ascii=False,indent=2))
with (DEST/'widths_and_extents.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(measurements[0]));w.writeheader();w.writerows(measurements)

# Compact grouped previews: full overview and enlarged zoom crop, each with
# original SEM and revised mask overlay. Annotation sources are retained in
# their individual overlays instead of duplicated in this contact sheet.
pairs=[(24,22),(27,26),(30,28),(33,31),(36,34),(39,37),(42,40),(45,43)]
overview_board=Image.new('RGB',(1800,4*520),'white');od=ImageDraw.Draw(overview_board)
zoom_board=Image.new('RGB',(1800,8*210),'white');zd=ImageDraw.Draw(zoom_board)
for i,(on,zn) in enumerate(pairs):
    pic=Image.open(DEST/'overlays'/f'1-{on:02}_overlay.jpg').crop((0,300,2048,1100))
    pic.thumbnail((880,460));x=i%2*900;y=i//2*520;overview_board.paste(pic,(x,y+35));od.text((x+5,y+5),f'1-{on:02}: complete visible bodies / actual endpoints',fill='black',font_size=21)
    for j,path in enumerate([RAW/f'1-{zn:02}.tif',DEST/'overlays'/f'1-{zn:02}_overlay.jpg']):
        im=Image.open(path).convert('RGB').crop((0,550,2048,900));im.thumbnail((890,170));zoom_board.paste(im,(j*900,i*210+30))
        zd.text((j*900+5,i*210+4),f'1-{zn:02} '+('original' if j==0 else 're-extracted complete-body mask'),fill='black',font_size=21)
overview_board.save(DEST/'overview_review.jpg',quality=94)
zoom_board.save(DEST/'zoom_review.jpg',quality=94)

readme='''# 重新提取的完整线体掩膜：1-22 至 1-45（含 1-22）

本次只交付这 24 张原图的掩膜。用户已明确确认目标是“完整可见线体”：覆盖上、下外边界之间整个主体；整体图保留端部，放大图覆盖到画面边缘。

## 下载与查看

- [下载24张掩膜PNG（仅掩膜）](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/SEM_masks_1-22_to_1-45_v2.zip)
- [整体图叠加总览](overview_review.jpg)
- [放大图原图/掩膜对照](zoom_review.jpg)
- [逐图全尺寸叠加图](overlays)
- [逐图掩膜](masks)
- [从最终二值掩膜统计的宽度和可见跨度](widths_and_extents.csv)

## 文件格式

掩膜均为单通道 PNG，大小 **2048×1536**，与原始 TIFF 对齐，无缩放。白色255表示完整可见线体，黑色0表示背景。底部参数栏 y≥1419 置黑。

本范围有8张整体图（每张4条线）和16张放大/带测量标注图（每张1条线）。带标注图也分别输出掩膜。

## 提取方法及含义

1. 放大图使用现有测量卡尺位置作为局部上下边界种子，建立边界灰度剖面；沿整幅图做归一化剖面匹配及平滑路径跟踪，填充上下边界之间完整可见主体。
2. 宽度随图像变化，不把某个标注宽度直接铺成整幅固定宽度矩形。标注遮挡区的匹配代价从邻近可见区插值；该局部区域仍含估计成分。
3. 整体图独立追踪上下外边界，依据纵向结构对比变化寻找各条线的可见两端，再用图像梯度活动轮廓修整端部；不把名义50µm强制作为掩膜长度。弱对比端部通过端点及与主体的连接位置约束轮廓，端部仍存在像素级判断误差。
4. 移除小于64像素且与主要线体不连接的拟合碎片。未将标尺、文字或绿色卡尺识别成独立结构。

原图内已有宽度标注参与了局部定位，不能把掩膜在标注点与原标注的一致性当成独立精度验证。本次检查了全部24张二值掩膜、16张放大图视野两端以及8张整体图32条线的端部；叠加图供实验人员继续逐像素核对，不宣称为独立人工描画的真值。

CSV的宽度是沿图像列测得的垂直宽度；“水平可见跨度”是二值掩膜最左、最右前景之间的水平跨度，不是曲线弧长。放大图中的结构在画外继续，其约7.145µm跨度只代表当前视野，不能当作整条结构长度。

`method` 记录实际使用的脚本、种子/卡尺位置、逐列边界和端部拟合轮廓。原始输入保存在之前的来源包中；本次未处理1-21及更早图像，也未重生成CAD、PSF或模型训练数据。

复现顺序：使用原始TIFF运行 reextract.py → refine_caps_snake.py → package_v2.py。脚本内路径需按本机目录对应调整；`reextract.py`引用的brackets.json与selected_overview_centers.json分别为保存的卡尺位置及整体线候选中心。
'''
(DEST/'README.md').write_text(readme,encoding='utf-8')

target=REPO/'SEM_masks_1-22_to_1-45_v2.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted((DEST/'masks').glob('*.png')):z.write(p,p.name)
with zipfile.ZipFile(target) as z:
    assert len(z.infolist())==24 and z.testzip() is None
    for info in z.infolist():assert info.filename.endswith('_mask.png')
print('Packaged',target,'bytes',target.stat().st_size)
print('Validated 24 native-size binary masks, 8x4 overview objects and 16x1 zoom objects.')
