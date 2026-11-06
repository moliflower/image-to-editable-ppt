<div align="center">

# Image to Editable PowerPoint

**把流程图、科研框架图和架构图，重建成可以继续修改的 PowerPoint。**

[![Checks](https://github.com/moliflower/image-to-editable-ppt/actions/workflows/test.yml/badge.svg)](https://github.com/moliflower/image-to-editable-ppt/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-2563eb.svg)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-7c3aed.svg)](SKILL.md)

[English](README.md) · **简体中文**

[效果展示](#showcase) · [安装](#installation) · [使用](#usage) · [更新](#update)

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

## 功能

- 文字、形状、矩阵与箭头分别可编辑。
- 保留参考图的布局、文字与配色。
- 支持混合文字样式和科研上下标。
- 输出可编辑 PowerPoint 文件与渲染预览。

<a id="quick-start"></a>
<a id="installation"></a>

## 安装

### 让你的 agent 安装

把这段话发给 agent：

```text
帮我按仓库里的 INSTALL.md 安装这个技能：
https://github.com/moliflower/image-to-editable-ppt
```

安装配置交给 agent 完成。[给 agent 的安装指南 →](INSTALL.md)

<details>
<summary>手动安装</summary>

在所用客户端的技能目录下执行：

```bash
git clone https://github.com/moliflower/image-to-editable-ppt.git
cd image-to-editable-ppt
python -m pip install -r requirements.txt
```

需要 Node.js 18+ 和 Python 3.10+。[预览配置](references/rendering.md)。

</details>

<a id="usage"></a>

## 使用

附上图片，说一句：

```text
把这张图片转成 PPT。
```

你会得到可编辑的 PowerPoint 文件和预览图。

<a id="update"></a>

## 更新

告诉 agent：

```text
帮我更新 image-to-editable-ppt 技能。
```

或在技能目录下执行：

```bash
git pull
```

## 可编辑范围

文字、规则图形与连接路径都是独立的 PowerPoint 对象。照片和复杂插画保留为独立图片。公式与位图图表重建为文字和几何，不恢复原始数据。

## 参与贡献

欢迎提交 Issue 和 PR！无论是报告问题、提出建议，还是贡献改进，都欢迎参与。

[提交 Issue](https://github.com/moliflower/image-to-editable-ppt/issues) · [提交 PR](https://github.com/moliflower/image-to-editable-ppt/pulls)

## 致谢

基于 [FigureForge](https://github.com/qwdwqfwq/topconf-paper-figure-gallery) 构建。[MIT License](LICENSE) · [上游来源与许可](vendor/figureforge/UPSTREAM.md)。

展示图来源：[PosDiffNet](https://github.com/moliflower/image-to-editable-ppt/blob/8230cbdffb3158fa165c0fe07a8962faeb071e3d/examples/posdiffnet/SOURCE.md)、[RepoMaster](https://github.com/moliflower/image-to-editable-ppt/blob/8230cbdffb3158fa165c0fe07a8962faeb071e3d/examples/repomaster/SOURCE.md)、[SAM 2](https://github.com/moliflower/image-to-editable-ppt/blob/8230cbdffb3158fa165c0fe07a8962faeb071e3d/examples/sam2/NOTICE.md)。原图权利归各自权利人。
