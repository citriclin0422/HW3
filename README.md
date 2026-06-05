# 🎨 Cosmos 3 AI Image Studio (AI 創意繪圖板)

這是一個基於 Streamlit 開發的 AI 圖像生成應用程式（學生創新專題：高真物理影像生成學堂）。本專案支援使用高畫質物理圖像生成模型 **NVIDIA Cosmos 3** 以及 **Google Imagen 4.0** 進行影像創作，並整合了 Gemini AI 提供自動提示詞 (Prompt) 擴寫優化的功能。

## ✨ 特色功能

- **多模型支援**：
  - **Cosmos 3 Super (64B)**：透過 Hugging Face 推理伺服器生成極具物理真實性與細節的圖像。
  - **Google Imagen 4.0**：內建直接對接，快速且高品質的圖像生成體驗。
- **AI 擴寫助手**：整合 Gemini 2.5 模型，能一鍵將簡單的想法擴寫成具備光影、材質、相機透視等細節的專業級英文 Prompt。
- **自訂參數**：支援調整畫面比例 (Aspect Ratio)、提示詞相關度 (CFG Scale)、去噪步數 (Inference Steps) 及隨機種子 (Seed)。
- **現代化美觀介面**：套用毛玻璃特效 (Glassmorphism)、暗色系質感背景與漸層立體按鈕的 Streamlit UI。

## 🚀 快速開始

### 1. 安裝依賴套件

請先確認您的環境已安裝 Python，接著安裝 `requirements.txt` 中的必要套件：

```bash
pip install -r requirements.txt
```

*(如果尚未有 `requirements.txt`，請至少確保安裝以下套件：`streamlit`, `requests`, `python-dotenv`)*

### 2. 環境變數設定

本專案需要存取外部 API，請準備好以下 Token 或金鑰：

- **Hugging Face Token**：用於調用 Cosmos 3 模型。可以在介面上直接輸入，或透過 `.env` 管理。
- **Google API Key**：用於 Imagen 4.0 生成與 Gemini 提示詞優化。可以在專案根目錄建立 `.env` 檔案並加入：

```env
google_API_Key=您的_GOOGLE_API_KEY
```
*(也可以設定在 Streamlit secrets 中)*

### 3. 啟動應用程式

在終端機中執行以下指令以啟動 Streamlit 伺服器：

```bash
streamlit run app.py
```

### 4. 開始創作
1. 在左側面板選擇生成引擎 (Cosmos 3 或 Gemini)。
2. 若選擇 Cosmos 3，請確保已輸入 Hugging Face Token。
3. 在畫面中央的輸入框輸入您的想法。
4. 點擊 **「✨ AI 擴寫 (Gemini 優化)」** 讓 AI 幫您完善提示詞。
5. 點擊 **「▶️ 開始生成」**，稍候片刻即可在下方查看並下載您的作品！

### ⚠️ Hugging Face API 端點更新注意事項
Hugging Face 官方已將舊的 `api-inference.huggingface.co` 伺服器棄用並關閉。本專案已同步更新為官方最新的 Inference Providers Router 網址：
`https://router.huggingface.co/hf-inference/models/{model_id}`
若您在其他專案遇到 `Name or service not known` 錯誤，請確保已將 API 網址更新為上述新格式。

## 🛠 技術堆疊

- **前端與框架**：[Streamlit](https://streamlit.io/)
- **API 介接**：`requests`
- **環境變數管理**：`python-dotenv`
- **生成式 AI 模型**：
  - Hugging Face Inference API (NVIDIA Cosmos 3)
  - Google Generative AI (Imagen 4.0, Gemini 2.5)

## 📄 授權條款
本專案為學生創新專題展示用途。
