# 第二批：本次1.xlsx对应的SEM结果

已按本次确认处理 **49张有参数图像、18组数据**。1-26的517nm功率采用 **0.443mW**；无参数的1-01、1-37、1-38、1-39未处理。

**[打开第二批下载清单及说明](batch_02_1-01_to_1-53)**

完整结果分为3个独立ZIP；全部下载后解压到同一目录，合并SEM_batch02：

- [完整分包1](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/batch_02_1-01_to_1-53/SEM_batch02_complete_part01_of_03.zip)
- [完整分包2](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/batch_02_1-01_to_1-53/SEM_batch02_complete_part02_of_03.zip)
- [完整分包3](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/batch_02_1-01_to_1-53/SEM_batch02_complete_part03_of_03.zip)
- [仅49张逐图掩膜](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/batch_02_1-01_to_1-53/SEM_batch02_masks_49.zip)
- [第二批汇总Excel](batch_02_1-01_to_1-53/SEM_batch02_summary.xlsx)

14组具有样例同名的全部12个标准文件；4组缺少上传源图，按实际源图保存并标注缺项。原图、新掩膜、PNG叠加、DXF、局部掩膜网格及JSON/CSV元数据均来自本批图像。旧批次文件保留在下方链接，未覆盖或混用。

---

# 最新完整导出：1-22 至 1-45，按 case_002 样例格式

**[下载新版8组完整数据ZIP](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/SEM_cases_1-22_to_1-45_v2.zip)**

- [单组下载清单与说明](case_exports_v2_1-22_to_1-45)
- [分组、原文件名和工艺参数索引](case_exports_v2_1-22_to_1-45/colab_model_manifest.csv)
- [一致性检查结果](case_exports_v2_1-22_to_1-45/validation.json)

每组 `case_008` 至 `case_015` 都包含与上传样例同名的12个标准文件：3张原始TIFF、整体/放大新版掩膜和PNG叠加、2张局部掩膜网格、DXF、review.json、model_input.json。所有派生内容已从完整线体v2重新导出。

每个单组ZIP另外附上3张逐图掩膜；完整合包共保留24张逐图掩膜。掩膜和叠加图保持2048×1536原图画布，参数栏为黑色，有效成像高度1419在JSON中单独记录。PSF命名文件仍是局部掩膜采样，非光学PSF；未宣称可直接训练。

---

# 最新版：1-22 至 1-45 完整线体掩膜

本次重新提取了 **1-22 至 1-45（包含1-22）共24张图像** 的完整可见线体掩膜，修正此前只分出部分亮边、主体宽度不足和端点漏分的问题。

- **[下载新版24张掩膜PNG（仅掩膜ZIP）](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/SEM_masks_1-22_to_1-45_v2.zip)**
- [查看整体图叠加](masks_v2_1-22_to_1-45/overview_review.jpg)
- [查看放大图原图与掩膜对照](masks_v2_1-22_to_1-45/zoom_review.jpg)
- [查看逐图掩膜、叠加、方法和统计](masks_v2_1-22_to_1-45)

掩膜与原始TIFF尺寸一致，2048×1536；白色为完整可见线体，底部参数栏为黑色。没有重做1-21及更早图像。

**此前8个分包保留用于来源存档，其中旧版掩膜已被本次限定范围的新结果替代。请使用上方新版掩膜。**

---

# SEM 处理结果下载

本分支包含用户授权交付的 15 组 SEM 候选处理结果，共保留 45 张原始 TIFF。8 个压缩包合计约 199 MiB，覆盖完整结果的全部 292 个文件。

## 下载方法

推荐在本分支页面点击绿色 **Code → Download ZIP**，保存到电脑后解压，进入 `downloads` 目录。

也可以点击下表中的链接分别下载 8 个包。如果仓库需要登录，请使用有仓库访问权限的 GitHub 账号。

| 下载 | 大小（MiB） | 内容 |
|---|---:|---|
| [分包 1](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/downloads/SEM_complete_part_01_of_08.zip) | 19.99 | 汇总表、来源文件、全景图、第1组 |
| [分包 2](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/downloads/SEM_complete_part_02_of_08.zip) | 26.18 | 第2–3组 |
| [分包 3](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/downloads/SEM_complete_part_03_of_08.zip) | 25.4 | 第4–5组 |
| [分包 4](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/downloads/SEM_complete_part_04_of_08.zip) | 25.59 | 第6–7组 |
| [分包 5](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/downloads/SEM_complete_part_05_of_08.zip) | 25.67 | 第8–9组 |
| [分包 6](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/downloads/SEM_complete_part_06_of_08.zip) | 25.55 | 第10–11组 |
| [分包 7](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/downloads/SEM_complete_part_07_of_08.zip) | 25.39 | 第12–13组 |
| [分包 8](https://github.com/ybai2896-maker/double/raw/refs/heads/sem-results/downloads/SEM_complete_part_08_of_08.zip) | 24.91 | 第14–15组 |

这 8 个 ZIP 均可独立解压。请把它们**依次解压到同一个文件夹**，合并 `SEM_results` 目录。全部解压后，打开 `SEM_results/index.html` 浏览各组结果。

## 其他文件

- [Excel 汇总表](SEM_summary.xlsx)
- [结果总览图](all_cases_preview.jpg)
- [详细说明](README_使用说明.txt)
- [文件校验结果](validation_report.json)
- [8 个压缩包的 SHA-256](SHA256SUMS.txt)

## 本次采用的用户确认

- 所有放大结构对应整体图**第三条线的中间**，有放大图的 14 组均已记录此位置约束。
- 第 15 组的 1-43 / 1-44 / 1-45 统一采用 **517 nm 功率 0.515 mW**；原始表中的记录和修正依据均保留。

## 结果范围

每组包含原图、候选二值掩膜、叠加图、DXF、局部掩膜采样网格、审核记录和模型输入 JSON；总包还包含 CSV 索引、汇总表、来源文件和复现脚本。

掩膜为自动亮响应候选，仍需实验人员审核，未声明为人工确认标签或可直接训练的数据。文件名中的 PSF 网格只是局部二值掩膜采样，并非光学 PSF。第 1 组没有对应放大原图，未补造；第 8 组的成像平台坐标差异已标注。

本次发布仅用于用户授权的结果交付，不修改其他分支。
