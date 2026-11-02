# 第二批 SEM 完整结果：单文件夹下载版

本文件夹包含本次有工艺参数的49张原图和18组完整可用数据。下载ZIP并解压后，即可在这个文件夹内查看全部结果。

## 内容

- case_002 至 case_020：分组原图、完整线体掩膜、PNG叠加、DXF、局部掩膜网格、review.json及model_input.json；case_015按用户要求排除。
- image_masks：49张与原始TIFF对齐的2048×1536二值掩膜。
- SEM_batch02_summary.xlsx：分组、工艺参数、图像对应、线宽和可见跨度、缺项。
- sources：原始1.xlsx和按用户确认修正后的1_corrected.xlsx。
- colab_model_manifest.csv/.json、file_mapping.csv、line_measurements.csv、validation.json：索引、统计及一致性检查。
- previews：整体图与放大图的掩膜叠加总览。

## 已应用的确认

1-26.tif的517nm功率采用0.443mW，原记录0.205mW保留在原表和修正记录中。无参数的1-01、1-37、1-38、1-39未处理。放大结构按用户确认对应整体图第三条线中部。

14组具有样例的全部12个标准文件。case_006、case_007、case_017缺少独立标注图，各有11个标准文件；case_014只有1-36整体图，有7个标准文件。缺失源图未补造，详情见各组JSON和汇总表。

掩膜使用完整可见线体定义。低对比尾部、颗粒遮挡和标注遮挡区域仍需实验复核。PSF命名图只是局部二值掩膜采样，不是光学PSF；未宣称训练就绪。详见各组review.json和needs_review。
