# 第二批 SEM 完整数据（本次上传的1.xlsx及三个ZIP）

本批图片与此前同名图像内容不同，使用独立目录保存。按用户确认：处理本次全部有工艺参数的图像；放大结构对应整体图第三条线中部；1-26的517nm功率统一采用0.443mW；无参数图像不处理。

实际处理 **49张原图，18组**。排除1-01、1-37、1-38、1-39。49张原始TIFF原样保留，并各有原尺寸2048×1536二值PNG掩膜；y≥1419的参数栏为背景。

## 下载完整结果

请下载下面三个完整分包，并依次解压到同一个目录，合并SEM_batch02文件夹。

- [完整分包1](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/batch_02_1-01_to_1-53/SEM_batch02_complete_part01_of_03.zip)
- [完整分包2](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/batch_02_1-01_to_1-53/SEM_batch02_complete_part02_of_03.zip)
- [完整分包3](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/batch_02_1-01_to_1-53/SEM_batch02_complete_part03_of_03.zip)

## 单组下载

| 组号 | 整体图 | 放大图 | 标注图 | 下载 |
|---|---|---|---|---|
| case_002 | 1-02.tif | 1-03.tif | 1-04.tif | [ZIP](archives/case_002.zip) |
| case_003 | 1-05.tif | 1-06.tif | 1-07.tif | [ZIP](archives/case_003.zip) |
| case_004 | 1-08.tif | 1-09.tif | 1-10.tif | [ZIP](archives/case_004.zip) |
| case_005 | 1-11.tif | 1-12.tif | 1-13.tif | [ZIP](archives/case_005.zip) |
| case_006 | 1-14.tif | 1-15.tif | 未上传 | [ZIP](archives/case_006.zip) |
| case_007 | 1-16.tif | 1-17.tif | 未上传 | [ZIP](archives/case_007.zip) |
| case_008 | 1-18.tif | 1-19.tif | 1-20.tif | [ZIP](archives/case_008.zip) |
| case_009 | 1-21.tif | 1-22.tif | 1-23.tif | [ZIP](archives/case_009.zip) |
| case_010 | 1-24.tif | 1-25.tif | 1-26.tif | [ZIP](archives/case_010.zip) |
| case_011 | 1-27.tif | 1-28.tif | 1-29.tif | [ZIP](archives/case_011.zip) |
| case_012 | 1-30.tif | 1-31.tif | 1-32.tif | [ZIP](archives/case_012.zip) |
| case_013 | 1-33.tif | 1-34.tif | 1-35.tif | [ZIP](archives/case_013.zip) |
| case_014 | 1-36.tif | 未上传 | 未上传 | [ZIP](archives/case_014.zip) |
| case_016 | 1-40.tif | 1-41.tif | 1-42.tif | [ZIP](archives/case_016.zip) |
| case_017 | 1-43.tif | 1-44.tif | 未上传 | [ZIP](archives/case_017.zip) |
| case_018 | 1-45.tif | 1-46.tif | 1-47.tif | [ZIP](archives/case_018.zip) |
| case_019 | 1-48.tif | 1-49.tif | 1-50.tif | [ZIP](archives/case_019.zip) |
| case_020 | 1-51.tif | 1-52.tif | 1-53.tif | [ZIP](archives/case_020.zip) |

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
