SEM结果包使用说明
=================

一、范围与来源
本包根据用户本次上传的1.1.zip、1.2.zip、1.3.zip中的45张原始TIFF，以及1.2.xlsx工艺参数表生成。
沿用case_002.zip样例的文件组织与V7.5工具的真实响应分割算法。
样例来自不同实验：其1-02/1-03/1-04命名、0.205 mW和60 um/s等参数未套用到本次结果。
原始TIFF没有重采样或改写；SHA-256保存在file_mapping.csv和validation_report.json。
14组有整体/放大/标注图，另1组只有整体及标注图，外加1张低倍全景，合计45张原图均保留。

二、用户已确认的事项
1. case_015的1-43/1-44/1-45均采用517 nm功率0.515 mW。
   原表1-45记录0.443 mW；已另存原表、修正表及parameter_corrections.json。
2. 所有放大结构均位于对应整体图第三条线中间。
   有放大图的14组zoom_line_id=3；红框按第三条线有效中段和独立TIFF刻度计算。
   亮响应中心与图像中心存在偏移，红框纵向位置已考虑放大图实际亮响应中心偏移。
   中点由整组线条纹理端点估计；case_006左半段弱，采用可见右端点加50 um名义设计线长估计中点。
   每组的估计依据保存在zoom_horizontal_midpoint_details。此项为几何估计，未宣称SIFT已经实现特征精确配准。

三、怎样查看
解压SEM_results.zip后，直接打开index.html可浏览各组预览及文件链接。
SEM_summary.xlsx：实验分组、功率、速度、倍率刻度、文件对应、候选线宽及用户确认修正。
all_45_images_contact.jpg：45张原图缩略图，便于查找；不得用缩略图替代原图测量。
all_cases_preview.jpg：所有实验组的整体、放大及掩膜叠加总览。

四、各case文件
original_overview.tif       整体SEM原图，字节级保留
original_zoom.tif           放大SEM原图，字节级保留（case_001缺失，未伪造）
original_measurement.tif    带原有测量标注的图，字节级保留
overview_mask.png          整体二值掩膜：0背景、255亮响应候选
zoom_mask.png              放大二值掩膜（有放大图时）
overview_overlay.png       整体SEM与绿色候选掩膜叠加
zoom_overlay.png           放大SEM与绿色候选掩膜叠加（有放大图时）
observed_contours_and_design_path.dxf  轮廓、分段中心线、名义设计路径和视野框
overview_psf_grid.png       20 nm间距、80行x100列的局部二值掩膜采样
zoom_psf_grid.png           同上，采样放大掩膜（有放大图时）
review.json                参数、候选分割设置、线宽统计、位置来源与复核状态
model_input.json           与样例字段兼容的模型数据描述，附来源与复核标记
parameters_by_image.json   每张图参数原值及本次采用值
grid_metadata.json         采样间距、中心点、局部物理范围
roi_candidates.json        用户确认的第三条线中部约束和自动特征匹配诊断
roi_candidates_overview.png  整体图上的第三条线中部红框
line_measurements.csv       该组候选掩膜线宽及有效列长度
preview.jpg                该组快速预览

五、坐标、算法与数据含义
原图2048x1536；掩膜和叠加图2048x1419，剔除底部117行SEM参数栏；原图上方图像坐标未缩放。
原始Image Pixel Size分别读取：整体27.91 nm/px、放大3.489 nm/px、全景279.1 nm/px。
图像坐标x向右、y向下。DXF单位um，局部左下角原点：x=x_px*nm/1000，y=(1419-1-y_px)*nm/1000。
DXF图层：SEM_OBSERVED_CONTOURS、SEM_OBSERVED_CENTERLINES、DESIGN_SCAN_PATH、SEM_FRAME。
DESIGN_SCAN_PATH仅为50 um名义几何，按交替方向绘制以兼容工具，真实扫描方向和开关时序尚未提供。
SEM平台坐标并不等于激光写入坐标，未计算二者变换。

沿用V7.5 advanced.evidence_mask：亮线、灵敏度1.2、最小纵向段7 px、无断口填补；整体最大半宽450 nm，放大350 nm。
中心线由图像候选峰并结合5 um周期和图像检查选定。四条线为可见候选数，不替代实际设计记录。
掩膜是局部亮响应候选，可能漏分弱线、含背景纹理或只覆盖结构亮边；不等于全部材料区域的精确边界。
保留低置信度空白而不桥接断口；空白可能是真实断裂，也可能是低对比度，需看原图复核。
line_measurements.csv的宽度是候选掩膜宽度，长度是有效列总数乘像素尺寸，既非连通线段总弧长，也非端到端长度。
测量图原有标注仅作局部参考，不强行用它们生成固定宽度掩膜。

PSF文件名沿用样例，但它们只是2.0x1.6 um局部二值掩膜网格，不是光学PSF、PDE计算或配准后八通道训练数据。
每张网格锚点在grid_metadata.json记录；整体默认在第三条可见线前景中部取样，避免四条线平均中心落入空白。
原始工具的默认采样使用全体掩膜质心；此处改成单条线局部前景锚点，其他采样尺寸/步长保持一致。

六、待复核事项
所有输出保留自动候选状态，未复制样例的“人工已确认”，也未声称可直接训练。
掩膜、真实扫描方式和时序仍需实验人员确认；所有组ready_for_training=false。
zoom_line_id=3来自用户；zoom_roi_verified=false表示尚无独立特征精确配准，不能误解为线号仍未知。
case_001：1-02为整体图，1-03为其标注图，两者均27.91 nm/px；没有对应放大图，未将其他功率组的放大图挪用。
case_008：1-24整体图与1-22/1-23放大图SEM Stage Y相差约7.6 um，保留用户位置约束与原始元数据，建议额外核查。
1-01为低倍全景且无工艺参数，原样放在context，不冒充单一实验组。
未包含工艺表引用但本次ZIP未上传的1-46至1-53图像，也未补造这些结果。

七、总清单与复现
colab_model_manifest.csv/.json：各组模型输入索引，含needs_review。
reviewed_summary.csv：为兼容工具沿用文件名，其行内容明确是自动候选，非“已经人工审核”。
file_mapping.csv：每张处理原图到输出文件的对应、像素尺寸、逐图采用参数与SHA-256。
validation_report.json：原图一致性、所有PNG可读性、二值值域、尺寸、DXF图层/单位/审计及清单完整性检查结果。
sources/：原始工艺表、用户确认后的修正表、未修改的V7.5工具ZIP及原始case_002样例ZIP。
reproducibility/：实际批处理脚本、人工核对的线中心和依赖版本。复现时需修改脚本中的本机绝对路径到相应文件位置。

版本说明：这是可供浏览、CAD检查和人工审核的完整候选结果包，尚不是实验人员已审核的训练标签集。
