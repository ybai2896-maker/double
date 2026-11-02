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
