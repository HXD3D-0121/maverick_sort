# Maverick-SORT — 部署标准化指南

> **目标**：无论在本地 Windows 电脑、同学电脑、还是 Streamlit Cloud，上传即用，双击即跑，不依赖手动激活 venv。

---

## 一、问题根因

当前你在 PowerShell 中直接打 `streamlit run ...`，调用的是**系统 Python**（没有装 `huggingface_hub` / `transformers` / `torch`），导致 Copilot 和 AI 功能全部离线。

**早上能跑的原因**：你当时激活了 `.venv`，Streamlit 用的是虚拟环境里的 Python。

**换电脑/Cloud 会失效的原因**：每台电脑的 Python 环境不同，不能指望系统自带这些包。

---

## 二、本地运行方案（Windows，双击启动）

### 2.1 方案 A：批处理文件双击启动（推荐）

已创建 `run_app.bat`，双击即可运行，自动使用 `.venv` 中的 Python：

```bat
@echo off
cd /d "%~dp0"
.venv\Scripts\streamlit.exe run streamlit_app_pro_v5.py
```

**使用方法**：
1. 打开项目文件夹
2. **双击 `run_app.bat`**
3. 浏览器自动打开 `http://localhost:8501`

### 2.2 方案 B：PowerShell 一键启动器

已创建 `run_app.ps1`，在 PowerShell 中右键"使用 PowerShell 运行"：

```powershell
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $projectRoot
& ".venv\Scripts\streamlit.exe" "run" "streamlit_app_pro_v5.py"
```

### 2.3 方案 C：VS Code 终端（已激活 venv）

如果你习惯用 VS Code：
1. `Ctrl + Shift + P` → `Python: Select Interpreter`
2. 选择 `./.venv/Scripts/python.exe`
3. 在 VS Code 终端中运行：
   ```bash
   streamlit run streamlit_app_pro_v5.py
   ```

---

## 三、Streamlit Cloud 部署方案（分享给教授）

### 3.1 上传前检查清单

| 检查项 | 状态 | 说明 |
|--------|------|------|
| `requirements.txt` 包含所有依赖 | ✅ | 已包含 `huggingface_hub`, `transformers`, `torch`, `sentence-transformers`, `faiss-cpu` |
| `.gitignore` 排除敏感文件 | ✅ | `.venv/`, `.env` 已排除 |
| `hf_integration/` 模块已提交 | ✅ | 9 个文件都在 Git 跟踪中 |
| 入口文件已指定 | ✅ | `streamlit_app_pro_v5.py` |
| Secrets 配置待完成 | ⏳ | 见 3.2 节 |

### 3.2 Streamlit Cloud Secrets 配置（关键）

上传代码到 GitHub 后，在 Streamlit Cloud 部署页面：

1. 点击 **App 右上角 ⋮ → Settings → Secrets**
2. 添加以下 TOML 格式配置：

```toml
HF_TOKEN = "hf_YOUR_TOKEN_HERE"
```

> ⚠️ **不要**把 Token 直接写在代码里或提交 `.env` 文件！Streamlit Cloud 通过 Secrets 注入环境变量，`config.py` 会优先读取 `st.secrets`。

### 3.3 部署步骤

```
1. 确保所有代码已 push 到 GitHub（main 分支）
2. 访问 https://share.streamlit.io/
3. 点击 "New app"
4. 选择你的 GitHub repo 和分支
5. Main file path 填：streamlit_app_pro_v5.py
6. 点击 Deploy
7. 部署完成后，进入 App → Settings → Secrets，添加 HF_TOKEN
8. 重启 App（Reboot）
```

### 3.4 部署后验证

打开 Cloud 链接后，检查 Copilot 状态：
- 侧边栏 Maverick Copilot 显示 **🟢 Online** → 部署成功
- 显示 **🟡 Offline** → 检查 Secrets 中 HF_TOKEN 是否配置正确

---

## 四、代码层面的健壮性保障

### 4.1 三级 Token 解析（已实现）

`hf_integration/config.py` 的解析优先级：

```
1. st.secrets["HF_TOKEN"]          ← Streamlit Cloud 生产环境
2. os.environ["HF_TOKEN"]           ← Docker / CI / 手动 export
3. 项目根目录 .env 文件              ← 本地开发
4. None → 回退到本地模型 / 规则模板   ← 离线兜底
```

### 4.2 三级 LLM 降级（已实现）

```
Tier 1: HF Inference API (Qwen2.5-7B)   ← 需要 HF_TOKEN + 联网
Tier 2: Local transformers (Qwen2.5-1.5B) ← 需要 torch + transformers
Tier 3: Rule-based fallback             ← 始终可用，预置文案
```

### 4.3 依赖缺失时的友好提示（已增强）

如果 Cloud 环境中某个包安装失败，`try_import_hf()` 会捕获完整 traceback 并显示在 UI 中，而不是笼统的 "Offline"。

---

## 五、常见问题排查

### Q1: 本地双击 run_app.bat 后闪退？

**原因**：`.venv` 目录不存在或损坏。  
**修复**：
```bash
# 在项目根目录运行
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### Q2: Cloud 部署后 Copilot 显示 Offline？

**排查步骤**：
1. 确认 Secrets 中已添加 `HF_TOKEN`
2. 确认 Token 有效（没有过期或被撤销）
3. 检查 Cloud 日志（App 页面右下角 → Manage app → Logs）
4. 查看是否有 `ImportError` 或 `ModuleNotFoundError`

### Q3: 想在本地也走 `.env` 文件，不想每次配 Secrets？

**方法**：在项目根目录创建 `.env` 文件（已被 `.gitignore` 排除，不会误提交）：

```
HF_TOKEN=hf_YOUR_TOKEN_HERE
```

`config.py` 会自动读取。

### Q4: 分享给教授时需要给他 Token 吗？

**不需要**。Cloud 部署后，Token 存在 Cloud Secrets 中，教授打开链接即可使用，看不到也接触不到 Token。

---

## 六、文件清单（部署相关）

| 文件 | 作用 | 是否提交 Git |
|------|------|-------------|
| `requirements.txt` | 依赖清单 | ✅ 必须提交 |
| `streamlit_app_pro_v5.py` | Pro 版入口 | ✅ 必须提交 |
| `hf_integration/` | AI 模块 | ✅ 必须提交 |
| `page_modules/` | 页面模块 | ✅ 必须提交 |
| `run_app.bat` | Windows 双击启动 | ✅ 建议提交 |
| `run_app.ps1` | PowerShell 启动 | ✅ 建议提交 |
| `.env` | 本地 Token（可选） | ❌ 已 gitignore |
| `.venv/` | 虚拟环境 | ❌ 已 gitignore |

---

> **文档版本**：v1.0  
> **最后更新**：2026/06/08
