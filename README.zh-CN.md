<div align="center">

# Image to Editable PowerPoint

**把流程图、科研框架图和架构图，重建成可以继续修改的 PowerPoint。**

由视觉智能体理解原图，使用本地 FigureForge 导出器生成原生文字框、形状与箭头。

[![Checks](https://github.com/moliflower/image-to-editable-ppt/actions/workflows/test.yml/badge.svg)](https://github.com/moliflower/image-to-editable-ppt/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-2563eb.svg)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-7c3aed.svg)](SKILL.md)

[English](README.md) · **简体中文**

[效果展示](#showcase) · [快速开始](#quick-start) · [如何工作](#how-it-works) · [常见问题](#faq) · [参与贡献](https://github.com/moliflower/image-to-editable-ppt/blob/main/.github/CONTRIBUTING.md)

</div>

---

<a id="showcase"></a>

## 从图片到可编辑 PowerPoint

### PosDiffNet · AAAI 2024

特征张量、相似度矩阵与注意力路径。参考 She 等人的 [PosDiffNet 论文 Figure 1](https://doi.org/10.1609/aaai.v38i1.27775) 重建。

**完整重建效果**

![PosDiffNet：由可编辑 PowerPoint 文件渲染的完整重建图](https://raw.githubusercontent.com/moliflower/image-to-editable-ppt/8230cbdffb3158fa165c0fe07a8962faeb071e3d/examples/posdiffnet/preview.png)

**在 PowerPoint 中选中全部对象**

![真实 PowerPoint 截图：PosDiffNet 的 478 个对象全部选中](https://raw.githubusercontent.com/moliflower/image-to-editable-ppt/8230cbdffb3158fa165c0fe07a8962faeb071e3d/docs/assets/posdiffnet-all-selected.png)

478 个独立对象，文字、矩阵单元格、特征块的各个面和路径均可编辑；仅三处点云视图保留为图片。

### RepoMaster · NeurIPS 2025

代码树、依赖图与循环工作流。参考 Wang 等人的 [RepoMaster 论文 Figure 1](https://arxiv.org/abs/2505.21577) 重建。

**完整重建效果**

![RepoMaster：由可编辑 PowerPoint 文件渲染的完整重建图](https://raw.githubusercontent.com/moliflower/image-to-editable-ppt/8230cbdffb3158fa165c0fe07a8962faeb071e3d/examples/repomaster/preview.png)

**在 PowerPoint 中选中全部对象**

![真实 PowerPoint 截图：RepoMaster 的 353 个对象全部选中](https://raw.githubusercontent.com/moliflower/image-to-editable-ppt/8230cbdffb3158fa165c0fe07a8962faeb071e3d/docs/assets/repomaster-all-selected.png)

353 个独立对象，文字、图节点、模块与连接路径均可编辑；16 个复杂标志与插画保留为独立图片。

### 直接看编辑过程 · SAM 2

在桌面 PowerPoint 中选中文字、修改标签、移动模块，再单独选中箭头。

![SAM 2 的真实 PowerPoint 编辑过程：选择文字、修改标签、移动模块和选择箭头](https://raw.githubusercontent.com/moliflower/image-to-editable-ppt/8230cbdffb3158fa165c0fe07a8962faeb071e3d/docs/assets/powerpoint-editing.gif)

选中状态截图和动图均来自真实 PowerPoint 界面。展示素材独立托管，不随技能安装。

## 技能能做什么

- 将文字、模块、矩阵与箭头重建为独立 PowerPoint 对象。
- 根据原图保留文字、长宽比、布局和连接关系。
- 支持混合文字样式、上下标、渐变、自定义虚线与旋转图形。
- 将照片与复杂插画保留为独立裁片，并核验来源像素。
- 本地导出、独立审计，并用可用的 Office 后端渲染实际 PPTX。

图片理解由当前视觉智能体完成。本地导出器不需要额外视觉 API Key、GPU、npm 包或浏览器 Canvas。

<a id="quick-start"></a>

## 快速开始

### 安装技能

**[下载技能 ZIP](https://github.com/moliflower/image-to-editable-ppt/archive/refs/heads/main.zip)**，将其中目录解压并命名为 `image-to-editable-ppt/`，放入所用客户端的技能目录。ZIP 只包含运行文件、技能说明和许可证，不包含测试、CI 配置及演示文件。

如果使用 Git，在客户端的技能目录下执行：

```text
git clone --depth 1 --single-branch --branch main https://github.com/moliflower/image-to-editable-ppt.git image-to-editable-ppt
python -m pip install -r image-to-editable-ppt/requirements.txt
```

使用 ZIP 安装时，也在技能文件夹的上一级执行同一条 `pip install` 命令。Codex 通常使用 `~/.codex/skills`，设置了 `CODEX_HOME` 时使用 `<CODEX_HOME>/skills`。避免额外嵌套一层 `image-to-editable-ppt-main/`。

浅克隆命令不会下载历史版本中的展示素材。Git 工作区还保留少量维护测试，安装 ZIP 会自动排除它们。

### 环境要求

| 依赖 | 用途 |
| --- | --- |
| 支持图片输入与 Skill 的智能体 | 理解原图并构建重建场景 |
| Node.js 18+ | 生成原生 PPTX |
| Python 3.10+ 与 Pillow | 准备图片裁片并审计导出文件 |
| LibreOffice + Poppler，或 Windows 上的 Microsoft PowerPoint | 可选：生成实际 PPTX 预览 |

**Windows、macOS、Linux** 均可导出与审计，不依赖 Office 或 PowerShell。LibreOffice 渲染也支持三个平台。参见[渲染后端配置](references/rendering.md)。

### 附上图片并提出要求

```text
使用 $image-to-editable-ppt 把这张图转成可编辑 PPT。
保留原图文字、长宽比和布局，让文字、模块与箭头可以分别修改。
完成后给我 PPTX 和从该文件实际渲染的预览图。
```

通常得到一份单页 PPTX，以及可用渲染器生成的预览；场景 JSON 保留用于修订。交付时会说明保留为位图的区域、识别不确定处和未完成的视觉核验。

<a id="update"></a>

### 更新

Git 安装在技能目录内执行 `git pull --ff-only`，再执行 `python -m pip install -r requirements.txt`。ZIP 安装可用新包替换旧技能目录，先保留自己修改过的内容。任务产物建议放在技能目录以外。

<a id="how-it-works"></a>

## 如何工作

1. 查看原图，提前确认密集区域和不清楚的标注。
2. 以图片像素为坐标，结合可复用科研组件建立独立对象。
3. 导出一次、独立审计一次，并渲染实际 PPTX。
4. 检查渲染 PNG，修正实质问题，然后交付。

常规核验不需要 Computer Use、桌面点击或录屏。上面的真实界面素材用于效果展示。原图字体和用户指定字体优先；没有额外要求时，英文科研标签与数学文字默认使用 Times New Roman。

## 可编辑范围与限制

| 原图内容 | 输出与限制 |
| --- | --- |
| 文字、几何模块、矩阵 | 原生文字与形状；字体替换可能影响间距 |
| 直线、曲线与箭头 | 原生路径；移动模块时不会自动重新连接 |
| 照片、热图、复杂插画 | 独立图片；内部仍为像素 |
| 公式与位图数据图表 | 可编辑文字或几何；不恢复原生公式结构和原始数据 |

低分辨率、遮挡和特殊字形需要额外检查。单个成功案例不代表任意图片都能像素级一致。当前按一张图重建一页 PPT，不附带无人值守批量识图服务。

## 安装包里有什么

```text
image-to-editable-ppt/
├── SKILL.md                 智能体执行流程
├── agents/                  技能发现信息
├── scripts/                 导出、审计、渲染和科研组件
├── references/              场景格式、组件用法、渲染说明
├── vendor/figureforge/      本地导出器、模板与上游许可
└── requirements.txt         Python 依赖
```

包内另有 README 和许可证。`references/` 只有三份供智能体按需查阅的操作说明，不是论文参考图片。展示图片、示例 PPTX、重建场景、测试报告和调研笔记均不随技能安装。

已有场景 JSON 需要手动排查时，可在技能目录运行：

```text
python -X utf8 scripts/build_figure.py --scene /path/to/scene.json --source /path/to/reference.png --output /path/to/figure.pptx
```

没有原图裁片时省略 `--source`。详细参数见[场景格式](references/scene-schema.md)、[科研组件](references/components.md)和[渲染选项](references/rendering.md)。

<a id="faq"></a>

## 常见问题

**可以只分享 `SKILL.md` 吗？** 应分享安装 ZIP。技能指令依赖随包提供的脚本、参考说明与本地导出器。

**为什么技能没有被识别？** 确认客户端技能目录下直接存在 `image-to-editable-ppt/SKILL.md`。按客户端支持的方式重新加载技能，或在新会话中明确调用该技能。

**本地导出会上传图片吗？** 随包脚本不发送网络请求。智能体客户端如何处理图片取决于该客户端；README 的展示素材由页面查看器单独加载。

## 维护与来源

Git 仓库保留维护测试和 CI，安装 ZIP 会排除这些文件。[贡献说明](https://github.com/moliflower/image-to-editable-ppt/blob/main/.github/CONTRIBUTING.md) · [问题反馈](https://github.com/moliflower/image-to-editable-ppt/issues)。

原生导出基于 [FigureForge](https://github.com/qwdwqfwq/topconf-paper-figure-gallery)，保留其[许可证](vendor/figureforge/LICENSE)和[固定版本及适配记录](vendor/figureforge/UPSTREAM.md)。技能指令和封装代码使用 [MIT License](LICENSE)。

展示素材仍保留原始权利：[PosDiffNet](https://github.com/moliflower/image-to-editable-ppt/blob/8230cbdffb3158fa165c0fe07a8962faeb071e3d/examples/posdiffnet/SOURCE.md)、[RepoMaster](https://github.com/moliflower/image-to-editable-ppt/blob/8230cbdffb3158fa165c0fe07a8962faeb071e3d/examples/repomaster/SOURCE.md)、[SAM 2](https://github.com/moliflower/image-to-editable-ppt/blob/8230cbdffb3158fa165c0fe07a8962faeb071e3d/examples/sam2/NOTICE.md)。这些固定版本的素材及来源说明独立托管，不属于安装包内容。
