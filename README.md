<div align="center">

<img alt="GOOSE Logo" src="img/GOOSE.webp" width=50% />

# GOOSE 🪿

**O**pens work**O**ut for **S**EU und**E**rgraduates

![GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)
[![Tests](https://github.com/leostudiooo/GOOSE/actions/workflows/python-test.yml/badge.svg)](https://github.com/leostudiooo/GOOSE/actions/workflows/python-test.yml)
![GitHub Stars](https://img.shields.io/github/stars/leostudiooo/GOOSE.svg?style=social)

</div>

## 🪿 关于

GOOSE 是一个开源 Python 项目，旨在帮助 SEU 的本科生更好地进行课外锻炼。它提供了一个简单易用的界面，允许用户记录和跟踪他们的锻炼进度。GOOSE 通过将数据直接上传到服务器，避免了需要使用官方小程序进行打卡上传的麻烦。只需在本地运行 GOOSE，进行一些简单的配置，就可以轻松地将锻炼数据上传到服务器。

GOOSE 是自由软件，遵循 [GPLv3 许可证](LICENSE)。你可以自由地使用、修改和分发它。我们鼓励用户参与到项目中来，提出建议和贡献代码。

<img width="682" alt="TUI 运行截图" src="https://github.com/user-attachments/assets/c7075b42-a695-478d-b804-3a813d273958" />

> 💡 **自由软件意味着**
>
> - 免费：你可以免费使用它，无需向任何人支付任何费用。
> - 开源：你可以查看源代码，了解它是如何工作的。
> - 可修改：你可以根据自己的需要修改源代码，添加新功能或修复错误。
> - 可分发：你可以将修改后的版本分发给其他人，分享你的改进。

### 为什么叫 GOOSE？

> GOOSE 不仅是个名字。它是一种精神、一种态度，是……一个递归缩写，就像 "GNU is Not Unix" 或者 "Wine Is Not an Emulator" 一样。

GOOSE 的全称是 "**G**OOSE **O**pens work**O**ut for **S**EU und**E**rgraduates"。

当然，也可以有其他的解释：

- **G**OOSE **O**rchestrates work**O**ut of **S**EU, **E**xclaim!
- **G**ood s**O**lution for work**O**uts in **SE**U
- **G**OOSE **O**ffers **O**pen-**S**ource **E**mpowerment
- **G**OOSE **O**pen **O**utdoor **S**ports for **E**veryone
- **G**OOSE **O**pen, **O**ffended by **S**EU **E**xercise
- **G**OOSE **O**pposes **O**verpriced **S**EU **E**xercise

或者任何你能想到的其他解释：因为 GOOSE 是自由的，我们希望你对它的理解和使用也能是自由的；更进一步地，我们希望这只大鹅能帮助你找到自由。

### 图标/吉祥物

GOOSE 的图标由 GOOSE 五个字母变形而来，绘制了一只张开翅膀的大鹅（虽然它看起来更像一只鸭子），配色灵感则来自于 SEU 的校徽。~~两个 O 组成的脚上色像药丸才不是 SEU 吃枣药丸的意思。~~

如果你有更好的设计，欢迎提交 PR！我们会考虑将其纳入项目中。

### 相关工具

- [PRTS](https://github.com/leostudiooo/PRTS) 是用于编辑路径点的网页工具。可以直接访问 [prts.烫烫烫的锟斤拷.top](https://prts.烫烫烫的锟斤拷.top) 使用。

### 关于防止滥用的考量

为了防止滥用，我们暂时通过以下的方式来提高使用门槛，请理解。
- 暂不考虑提供预构建的可执行文件，用户需要自己安装 Python 和依赖；
- 部分配置项需要自行寻找获取方法（见 [配置](#配置) 一节）。

## 🌲 结构

```
.
├── LICENSE
├── README.md
├── requirements.txt
├── GOOSE.py
├── config/
├── img/
├── resources/
│   ├── boundaries/
│   └── default_tracks/
├── src/
│   ├── infrastructure/
│   │   └── model_storage/
│   ├── model/
│   │   └── track/
│   ├── service/
│   └── ui/
│       ├── cli/
│       └── tui/
└── tests/
```

- `config`：配置文件目录，包含系统配置、用户配置和路线信息。
- `img`：图片资源目录。
- `resources`：资源目录，包含默认轨迹和边界文件（可用于在 [PRTS](https://github.com/leostudiooo/PRTS) 中使用）。
- `src`：源代码目录，包含基础设施、模型、服务和用户界面模块。
- `tests`：测试目录。
- `requirements.txt`：Python 依赖文件，包含项目所需的所有 Python 库。
- `GOOSE.py`：主程序文件，运行该文件即可启动 GOOSE。

## 💻 使用

### 运行环境

- Python 3.9+（未在更低版本上测试）和 pip
- Windows/macOS（未在 Linux 上测试，但理论上可以运行）

### 安装和运行

1. 将仓库 clone 到本地

   ```sh
   git clone https://github.com/leostudiooo/GOOSE.git
   ```

   或者你偏好的其他任何方式。然后进入目录：

   ```sh
   cd GOOSE
   ```

2. 安装依赖（推荐使用虚拟环境）

   ```sh
   pip install -r requirements.txt
   ```

   推荐使用 [uv](https://github.com/astral-sh/uv) 作为包管理器：

   ```sh
    uv venv .venv --python=3.9 && source .venv/bin/activate && uv sync
    ```

3. 运行

   ```sh
   python GOOSE.py
   ```

   或者如果你在 macOS/Linux 上也可以先

   ```sh
   chmod +x GOOSE.py
   ```
   然后直接运行

   ```sh
   ./GOOSE.py
   ```

   就可以进入 TUI 使用了。

### 配置

运行后会自动创建 `config/user.yaml` 文件，你也可以直接在 TUI 中进行配置。

> **⚠️ 注意**
> 
> 这里的内容仅供理解配置项的意义。实际操作中，你应当在 TUI 中填写表单进行配置，而不是手动修改配置文件。动手能力强的用户可忽略此提示。

```yaml
# 用户登录信息
token: valid.eyJ1c2VyaWQiOiAiMTIzIn0.token

# 用户偏好配置
date_time: 2025-03-19 21:01:50
start_image: "path/to/start/image.jpg"
finish_image: "path/to/finish/image.jpg"
route: 梅园田径场

# 使用自定义轨迹，可从 PRTS 生成；禁用时使用路线默认轨迹
custom_track: 
  enable: false
  file_path: "resources/my_tracks/track.json"
```

- `token`：需要在小程序中获取。为防止滥用，请自行寻找获取方法。
- `date_time`：锻炼时间，格式为 `YYYY-MM-DD HH:MM:SS`，创建时为示例时间，可在 TUI 中使用“现在”按钮获取当前时间。
- `start_image`：开始锻炼时的图片路径。
- `finish_image`：结束锻炼时的图片路径。
- `route`：锻炼的路线名称，默认为“梅园田径场”，可在 TUI 中选择，`config/route_info.yaml` 中有所有可选路线。
- `custom_track`：自定义轨迹，禁用时使用路线默认轨迹。`enable` 为 `true` 时，`file_path` 为自定义轨迹文件路径，格式为 JSON，使用 [PRTS](https://github.com/leostudiooo/PRTS) 生成。`enable` 为 `false` 时，使用默认轨迹。

> **⚠️ 注意**
>
> 为了降低被服务器检测到重复轨迹的风险，您应当在 PRTS 创建独一无二的自定义轨迹文件，在此处开启自定义轨迹使用。所需规则文件（即电子围栏边界）在 resource 目录下。

系统配置和路线信息在 `config/system.yaml` 和 `config/route_info.yaml` 中，普通用户无需修改。系统配置包括服务器地址、请求头等信息，路线信息包括所有可选路线的名称和默认轨迹文件路径。

## 🛠️ 贡献

我们欢迎任何形式的贡献，包括但不限于：
- 提交 [议题](https://github.com/leostudiooo/GOOSE/issues)
  - Bug 报告
  - 功能请求
  - 使用建议
- 创建 [拉取请求](https://github.com/leostudiooo/GOOSE/pulls)
  - Bug 修复
  - 功能实现
  - 文档更新

期待你的参与！

## 📜 声明

本项目遵循 [GPLv3 许可](LICENSE)。这主要意味着以下几点：
- 你可以自由使用、修改和分发本项目的代码。
- 你可以在任何地方使用本项目的代码，但如果你修改了代码并分发了修改后的版本，你必须在同样的许可下分发，也就是说你必须在 GPLv3 下开源你的修改。

我们反对使用本项目获取任何形式的商业利益，包括但不限于：
- 使用本项目提供收费的服务；
- 将本项目的代码或修改后的代码作为商业产品出售；
- 等等。

跑操系统属于公共资源，利用公共资源牟取商业利益是不道德的。

**软件按“原样”（as-is）提供，不附带任何明示或暗示的担保，包括但不限于对特定用途适用性的担保。作者不对因使用本软件产生的任何直接或间接损失、数据丢失、法律责任或其他风险承担责任。**

**本项目基于学习和研究目的开发。软件不对用户上传数据的真实性、准确性、完整性和合法性负责。用户应对其上传的数据承担全部责任，确保其符合实际情况。**

## 📖 参考

- [Token 结构](https://xn--huu92dpwpaa217f909c.top/posts/wechat-miniapp-token)
