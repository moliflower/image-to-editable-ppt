# 使用指南

[返回中文首页](../README.zh-CN.md) · [English guide](USAGE.md) · [场景格式](../references/scene-schema.md)

本指南介绍本地工具链的使用方式。图片理解和逐元素重建由智能体完成；下面的命令用来准备图片裁片、导出场景、检查文件及渲染结果。

## Windows、macOS、Linux 通用入口

```text
python -X utf8 scripts/build_figure.py --scene build/scene.json --source reference.png --output build/figure.pptx
```

没有原图裁片时可省略 `--source`。命令按需准备裁片，然后导出一次、独立审计一次，并选择可用的渲染器。Windows 可以使用 PowerPoint；三个平台都可使用 LibreOffice 与 Poppler。安装和后端选择见[平台渲染说明](../references/rendering.md)。核心导出与审计，以及 LibreOffice 渲染均不需要 PowerShell。

查看 `render.status`：`rendered` 表示已从实际 PPTX 生成预览，`unavailable` 表示缺少渲染器，视觉检查仍未完成。`.build.json` 记录每阶段耗时。文件、尺寸、后端和预览摘要一致时复用预览；改动字体后使用 `--force-render`。缓存命中也不代表已经人工看过图片。

普通图片重建无需重复运行编辑探针、整个仓库测试或其他示例回归。这些检查用于维护导出器或调查具体故障。以下单独命令供排查和高级使用。

## 安装与目录

首次安装见[快速开始](../README.md#quick-start)。完整目录应包含：

```text
image-to-editable-ppt/
├── SKILL.md                     # 智能体工作指令
├── agents/openai.yaml           # 技能展示与调用配置
├── scripts/
│   ├── export_pptx.mjs          # 本地原生 PPTX 导出器
│   ├── image_assets.py         # 图片检查、裁片与嵌入
│   ├── audit_pptx.py           # 独立 OOXML 审计
│   ├── build_figure.py         # 跨平台统一构建入口
│   ├── render_pptx.py          # 自动选择渲染器并缓存预览
│   └── render_powerpoint.ps1   # 可选的 Windows 后端与编辑探针
├── references/                 # 场景格式与上游来源
├── vendor/figureforge/          # 固定版本的上游导出器与模板
├── examples/                   # 基础示例与复杂重建案例
├── tests/                      # 导出与审计测试
└── requirements.txt            # Pillow
```

所有示例命令都在仓库根目录执行。可先检查环境：

```bash
node --version
python --version
python -m pip install -r requirements.txt
```

需要 Node.js 18+ 和 Python 3.10+。可以在已有虚拟环境中安装 Pillow；Node 导出器不需要 `npm install`。

<a id="update"></a>

## 更新已有安装

进入已安装的 `image-to-editable-ppt` 目录，先查看本地修改：

```bash
git status --short
git pull --ff-only
python -m pip install -r requirements.txt
```

如果 `git status` 显示自行修改的技能或脚本，先保存修改再更新，不要直接覆盖。ZIP 安装可以先备份旧目录，再用完整新目录替换。示例输出建议保存在任务目录或被忽略的 `build/` 中。

## 图片到场景

把图片附在支持视觉输入的智能体会话中，显式调用 `$image-to-editable-ppt`。技能会读取图片并生成场景，每个元素使用原图像素坐标与独立 ID。

清楚说明以下要求可以减少后续返工：

- 是否严格保留原图布局、配色、字体与换行。
- 是否只允许使用这张图片，或也可以参考已有源文件。
- 哪些区域允许保留为图片，例如照片、热图、复杂插画。
- 哪些文字无法辨认，需要由你确认。

手动查看图片尺寸：

```bash
python -X utf8 scripts/image_assets.py inspect path/to/reference.png
```

放大局部供识别时，可导出裁片。下面的坐标只是示例，需要按实际图像调整：

```bash
python -X utf8 scripts/image_assets.py crop path/to/reference.png --box 100 80 300 200 --output build/detail.png
```

坐标基于处理 EXIF 方向后的图片。裁片在完整画布中的偏移需要保留，不能把裁片局部坐标直接当作原图坐标。

## 导出已有场景

使用仓库自带的基础示例：

```bash
node scripts/export_pptx.mjs --scene examples/diagram.scene.json --output build/figure.pptx
```

导出器会同时生成：

| 文件 | 用途 |
| --- | --- |
| `build/figure.pptx` | 原生可编辑幻灯片 |
| `build/figure.exported.scene.json` | 规范化后的场景，供独立审计与后续修订 |
| `build/figure.editability.json` | 对象统计、图片区域、警告与核验状态 |

导出器的初始状态为 `visualVerification: required`，因为生成文件本身不代表已完成视觉检查。

也可以直接导出复杂案例的场景：

```bash
node scripts/export_pptx.mjs --scene examples/sam2/scene.json --output build/sam2.pptx
```

公开 SAM 2 案例保留官方参考图、场景、PPTX 和来源许可证，详见[案例说明](../examples/sam2/README.md)。

## 含图片裁片的场景

场景中的照片或复杂图像区域可以用 `crop` 指定。下面的例子从原图 `(100, 200)` 截取 `180 × 120` 像素，放到相同位置：

```json
{
  "id": "sample-photo",
  "type": "image",
  "x": 100,
  "y": 200,
  "w": 180,
  "h": 120,
  "crop": {"x": 100, "y": 200, "w": 180, "h": 120},
  "assetPurpose": "photo",
  "assetDescription": "原图中的样本照片"
}
```

含 `crop` 的场景需要先准备图片，再导出：

```bash
python -X utf8 scripts/image_assets.py prepare --scene build/scene.json --source path/to/reference.png --output build/prepared.scene.json
node scripts/export_pptx.mjs --scene build/prepared.scene.json --output build/figure.pptx
```

准备脚本检查画布尺寸和裁片边界，并将 PNG 数据嵌入场景。文字、模块和箭头应按原生对象重建，不要藏进照片裁片中。

## 独立审计

审计时使用导出后的规范化场景：

```bash
python -X utf8 scripts/audit_pptx.py --pptx build/figure.pptx --scene build/figure.exported.scene.json --report build/audit.json
```

`passed: true` 表示受检的对象数量、名称、文字、两端箭头、旋转角度、虚线间距、图片像素、长宽比与包结构符合场景。它不检查整体视觉相似度，也不能代替字体和遮挡关系的视觉核对。

新裁片会自动保留来源坐标和像素摘要。可预先声明 `sourceAssets` 清单，检查是否有漏图或重复绑定；未预先声明时，清单只覆盖已经提供的裁片节点。核对原图像素时增加 `--source`：

```bash
python -X utf8 scripts/audit_pptx.py --pptx build/figure.pptx --scene build/figure.exported.scene.json --source path/to/reference.png --report build/audit.json
```

报告中的 `originalSourceVerifiedAssets` 表示通过原图核验的裁片数量，`imagesWithoutSourceProvenance` 表示没有来源记录的旧图片对象。来源核验允许图片移动、缩放和旋转，不要求其放置坐标等于原图裁切坐标。

原生线条支持 `arrowStart: true` 与 `arrow: true` 组成双端箭头，`dash: [12, 6]` 指定像素单位的虚线/间隔长度，所有对象支持 `rotation` 顺时针角度。显式字体、字号与换行保持不变，不使用浏览器 Canvas。示例见 [native-capabilities.scene.json](../examples/native-capabilities.scene.json)。

## 科研文字

科研标签可通过同一文本节点的 `runs` 混排样式，所有片段拼接后必须与 `text` 完全一致。片段继承文本框的字体、颜色和粗斜体；`baselineShift` 的 `super` / `sub` 设置上下标，不会自动缩小字号。`lineSpacing` 使用原图像素，渐变色标的 `opacity` 范围为 0–1。

```bash
node scripts/export_pptx.mjs --scene examples/scientific-text.scene.json --output build/scientific-text.pptx
python -X utf8 scripts/audit_pptx.py --pptx build/scientific-text.pptx --scene build/scientific-text.exported.scene.json
```

审计核验文件内实际保存的文字样式与渐变参数，测试还会故意篡改文件来检查能否发现错误。字段见[场景格式](../references/scene-schema.md#scientific-text-within-one-editable-box)，效果见[渲染示例](../examples/scientific-text/README.md)。字体是否安装、文字是否溢出仍须以实际渲染检查。

## 渲染已有 PPTX

```text
python -X utf8 scripts/render_pptx.py --pptx build/figure.pptx --output build/figure.png --renderer auto --width 1600
```

使用与构建命令相同的后端选择和缓存规则，渲染实际 PPTX 文件。不同字体和渲染器可能影响字距，应在最终使用的软件中核对关键排版。Windows 专用的可选编辑探针、各平台安装方法见[渲染说明](../references/rendering.md)。

## 故障排查

| 现象 | 检查与处理 |
| --- | --- |
| 技能未被发现 | 核对目录层级、自定义 `CODEX_HOME`，按客户端支持的方式重新加载技能 |
| `Cannot find module` 或导出器文件缺失 | 检查是否只复制了 `SKILL.md`，补齐整个仓库，尤其是 `vendor/figureforge/` |
| `No module named PIL` | 在实际执行脚本的 Python 环境运行 `python -m pip install -r requirements.txt` |
| Windows 输出中文或数学符号时报编码错误 | 使用文档中的 `python -X utf8 ...` 调用方式 |
| 提示先准备裁片 | 对含 `crop` 的场景运行 `image_assets.py prepare`，再导出准备后的 JSON |
| 裁片超出边界或画布尺寸不匹配 | 用 `inspect` 核对原图尺寸与 EXIF 方向，再调整场景坐标 |
| 文本溢出、字体变化 | 安装所需字体或明确设置回退字体，调整文本框后重新渲染 |
| PowerPoint COM 访问被拒绝 | 核对桌面版 PowerPoint 是否可启动，以及当前进程是否允许访问桌面 COM；受限环境可交给已授权的本机进程渲染 |
| PowerShell 阻止执行脚本 | 按所在环境允许的脚本执行方式运行；也可在 PowerPoint 中手动打开并导出图片进行核对 |
| 结构审计通过但显示不对 | 检查实际 PPTX 渲染，修正场景后重新导出；不要以审计通过替代视觉检查 |

## 继续修改

修改保留的场景后重新导出、审计和渲染。如果你已经直接编辑过 PPTX，应把修改后的文件交给智能体先检查，再决定如何同步回场景，避免旧场景覆盖新改动。

场景字段与支持边界见[格式参考](../references/scene-schema.md)，开发测试与示例提交要求见[贡献指南](../CONTRIBUTING.md)。
