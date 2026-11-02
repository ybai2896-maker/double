# 1-22 至 1-45：按 case_002 样例保存的完整新版数据

共8组（case_008–case_015）、24张原始TIFF。沿用本批次原有组号，掩膜采用完整可见线体v2，不混用先前亮边候选结果。

## 下载

**[下载8组完整合包](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/SEM_cases_1-22_to_1-45_v2.zip)**，或选择下表单组ZIP。

| 分组 | 整体图 | 放大图 | 标注图 | 单组ZIP |
|---|---|---|---|---|
| case_008 | 1-24.tif | 1-22.tif | 1-23.tif | [下载](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/case_exports_v2_1-22_to_1-45/archives/case_008_v2.zip) |
| case_009 | 1-27.tif | 1-26.tif | 1-25.tif | [下载](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/case_exports_v2_1-22_to_1-45/archives/case_009_v2.zip) |
| case_010 | 1-30.tif | 1-28.tif | 1-29.tif | [下载](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/case_exports_v2_1-22_to_1-45/archives/case_010_v2.zip) |
| case_011 | 1-33.tif | 1-31.tif | 1-32.tif | [下载](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/case_exports_v2_1-22_to_1-45/archives/case_011_v2.zip) |
| case_012 | 1-36.tif | 1-34.tif | 1-35.tif | [下载](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/case_exports_v2_1-22_to_1-45/archives/case_012_v2.zip) |
| case_013 | 1-39.tif | 1-37.tif | 1-38.tif | [下载](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/case_exports_v2_1-22_to_1-45/archives/case_013_v2.zip) |
| case_014 | 1-42.tif | 1-40.tif | 1-41.tif | [下载](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/case_exports_v2_1-22_to_1-45/archives/case_014_v2.zip) |
| case_015 | 1-45.tif | 1-43.tif | 1-44.tif | [下载](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/case_exports_v2_1-22_to_1-45/archives/case_015_v2.zip) |

## 与上传样例一致的12个标准文件

每个 `case_NNN/` 目录严格包含：

```
model_input.json
observed_contours_and_design_path.dxf
original_measurement.tif
original_overview.tif
original_zoom.tif
overview_mask.png
overview_overlay.png
overview_psf_grid.png
review.json
zoom_mask.png
zoom_overlay.png
zoom_psf_grid.png
```

每个单组ZIP另外附有 `image_masks/`，保留这一组3张原图各自的新版掩膜，因此带测量标注图的掩膜也不会遗漏。整体合包的 `image_masks/` 共24张PNG。

## 新掩膜及派生数据

- 标准目录的两张掩膜与已发布完整线体v2逐像素一致；24张原始TIFF字节级保留。
- 两张叠加图重新生成为PNG；DXF、局部采样网格、review/model JSON中的线宽和可见跨度均从新版掩膜重新计算。
- 掩膜和叠加图保持原始2048×1536画布，参数栏 y≥1419 为背景；JSON写入实际画布尺寸，并另记有效成像高度1419。样例中的1419高掩膜是裁去参数栏的版本，此处保留本次已确认的原图对齐方式。
- 放大区域按用户确认的第三条线中部、整体/放大独立TIFF像素尺寸和新版完整线体中心重新换算。
- case_015 517nm功率统一0.515mW，保留原表0.443mW到采用0.515mW的修正记录。
- 工艺字段使用本次1.2.xlsx的数据；未复制样例另一实验的0.205mW、60um/s或“人工已确认”状态。

DXF单位um，局部有效成像区左下角原点：x=x_px*nm/1000，y=(1419-1-y_px)*nm/1000。DXF的名义50um设计路径不是实际扫描时序。PSF命名文件为80×100、20nm步长的局部二值掩膜采样，不是实测光学PSF。

掩膜来自参考卡尺位置引导的图像边界提取；弱对比端部和标注遮挡区仍有估计成分。用户确认了线体范围及第三条线中部对应，尚无独立逐像素标签审核、真实扫描时序和PDE配准；因此ready_for_training保持false。

`validation.json` 记录标准文件名/JSON字段完整性、原图与新掩膜一致性、PNG/网格尺寸以及DXF重新栅格化后与新版掩膜的重叠检查。
