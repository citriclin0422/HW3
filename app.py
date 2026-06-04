import streamlit as st
import requests
import os
import time
import base64
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

# Streamlit App Configuration
st.set_page_config(
    page_title="Cosmos 3 AI Image Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS for Premium Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main App Background */
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #151520 100%);
        color: #f0f0f0;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: rgba(30, 30, 45, 0.6);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Primary Button styling */
    .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #ff7eb3, #ff758c) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(255, 117, 140, 0.4) !important;
        transition: all 0.3s ease !important;
        font-weight: 600 !important;
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(255, 117, 140, 0.6) !important;
    }
    
    /* Secondary Button styling */
    .stButton>button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #e0e0e0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #ff758c !important;
        box-shadow: 0 0 0 1px #ff758c !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        background: -webkit-linear-gradient(45deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State variables if they don't exist
if "history" not in st.session_state:
    st.session_state.history = []
if "prompt" not in st.session_state:
    st.session_state.prompt = ""

# Sidebar: Configuration
with st.sidebar:
    st.title("⚙️ 1. 設定引擎與權杖")
    
    engine = st.radio(
        "選擇生成模型:",
        options=["cosmos3", "gemini"],
        format_func=lambda x: "Cosmos 3 Super (64B) [HF]" if x == "cosmos3" else "Imagen 4.0 [Google]"
    )
    
    hf_token = ""
    if engine == "cosmos3":
        st.markdown("### Hugging Face 設定")
        hf_token = st.text_input(
            "Hugging Face Token", 
            type="password",
            help="Your token is kept secure and only used for the HF inference API."
        )
        if not hf_token:
            st.warning("⚠️ 請輸入 Hugging Face Token 以使用 Cosmos 3 模型。")
        else:
            st.success("✅ Token 已配置")
            
        st.markdown("---")
        st.markdown("### 進階參數微調")
        
        # Dimensions logic based on aspect ratio
        aspect_ratio = st.selectbox(
            "畫面比例 (Aspect Ratio)",
            options=["1:1", "16:9", "9:16"],
            format_func=lambda x: "1:1 正方形" if x == "1:1" else "16:9 寬螢幕" if x == "16:9" else "9:16 肖像畫"
        )
        
        guidance_scale = st.slider(
            "提示詞相關度 (CFG Guidance Scale)",
            min_value=1.0, max_value=20.0, value=7.0, step=0.5
        )
        
        inference_steps = st.slider(
            "去噪步數 (Inference Steps)",
            min_value=10, max_value=50, value=25, step=1
        )
        
        seed = st.number_input(
            "隨機種子 (Seed, -1 為隨機)",
            value=-1, step=1
        )
        
        negative_prompt = st.text_input(
            "負向提示詞 (Negative Prompt)",
            value="blurry, low quality, distorted, bad physics, text, watermark"
        )
        
    else:
        st.info("ℹ️ Gemini 內建沙盒引擎運作中。本應用已安全對接 Imagen 4.0，無需額外 Token 即可體驗。")

# Main Content
st.title("🎨 Cosmos 3 AI 創意繪圖板")
st.markdown("學生創新專題：高真物理影像生成學堂")

st.markdown("### ✨ 2. 輸入繪圖提示詞")

# We use session_state for prompt so the AI Expansion can update it
user_prompt = st.text_area(
    "描述您想要生成的圖像：",
    value=st.session_state.prompt,
    height=150,
    placeholder="例如：An advanced industrial robotic arm assembling an electric vehicle battery..."
)

# Helper function to get Google API Key
def get_google_api_key():
    # Check Streamlit secrets first, then OS environ
    try:
        if "google_API_Key" in st.secrets:
            return st.secrets["google_API_Key"]
    except Exception:
        pass
    
    return os.environ.get("google_API_Key", "")

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("✨ AI 擴寫 (Gemini 優化)", use_container_width=True):
        api_key = get_google_api_key()
        if not api_key:
            st.error("找不到 Google API Key。請設定環境變數 `google_API_Key`。")
        elif not user_prompt.strip():
            st.error("請先輸入基本的提示詞構想！")
        else:
            with st.spinner("Gemini 正在擴寫您的提示詞..."):
                try:
                    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
                    system_prompt = """你是一個專業的 AI 繪圖 Prompt 提示詞優化專家。
請將用戶輸入的簡單想法或提示詞，擴寫為適合 NVIDIA Cosmos 3 超高畫質物理圖像生成模型使用的詳細英文 Prompt。
Cosmos 3 是一個物理真實性極高、世界模擬能力極強的模型，特別擅長細節、材質、物理光學、空間感。
請輸出一個高水準的結構化英文 Prompt，包含：主體(Subject)、物理細節(Physical details)、光影(Lighting)、材質與質地(Textures & Materials)、相機透視(Camera perspective)。
注意：請直接輸出最終的英文 Prompt 內容即可，千萬不要包含任何額外的解釋、引言、Markdown 標籤或符號。"""
                    
                    payload = {
                        "contents": [{"parts": [{"text": f"請優化以下提示詞：\n\"{user_prompt}\""}]}],
                        "systemInstruction": {"parts": [{"text": system_prompt}]}
                    }
                    
                    response = requests.post(
                        endpoint, 
                        headers={"Content-Type": "application/json"},
                        json=payload,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        enhanced_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if enhanced_text:
                            st.session_state.prompt = enhanced_text.strip()
                            st.success("✨ Prompt 優化成功！已自動填入輸入框。(如未自動更新，請複製下方文字)")
                            st.code(enhanced_text.strip(), language="text")
                        else:
                            st.error("無法解析優化後的提示詞。")
                    else:
                        st.error(f"擴寫失敗: HTTP {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"發生錯誤: {str(e)}")

st.markdown("---")

if st.button("▶️ 開始生成", type="primary", use_container_width=True):
    if not user_prompt.strip():
        st.error("請輸入提示詞！")
    else:
        # Cosmos 3 (Hugging Face)
        if engine == "cosmos3":
            if not hf_token.strip():
                st.error("請先在左側設定 Hugging Face Token！")
            else:
                with st.spinner("正在呼叫 Hugging Face 推理伺服器..."):
                    width, height = 1024, 1024
                    if aspect_ratio == "16:9":
                        width, height = 1024, 576
                    elif aspect_ratio == "9:16":
                        width, height = 576, 1024
                        
                    hf_payload = {
                        "inputs": user_prompt,
                        "parameters": {
                            "negative_prompt": negative_prompt,
                            "guidance_scale": guidance_scale,
                            "num_inference_steps": inference_steps,
                            "width": width,
                            "height": height,
                            "seed": seed if seed != -1 else int(time.time())
                        }
                    }
                    
                    try:
                        response = requests.post(
                            "https://api-inference.huggingface.co/models/nvidia/Cosmos3-Super-Text2Image",
                            headers={
                                "Authorization": f"Bearer {hf_token.strip()}",
                                "Content-Type": "application/json"
                            },
                            json=hf_payload,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            image_bytes = response.content
                            st.session_state.history.insert(0, {
                                "id": f"gen-{int(time.time())}",
                                "prompt": user_prompt,
                                "engine": "Cosmos 3",
                                "aspect_ratio": aspect_ratio,
                                "image_bytes": image_bytes,
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                            })
                            st.success("🎨 Cosmos 3 圖像生成成功！")
                        else:
                            st.error(f"Hugging Face 回傳錯誤 (HTTP {response.status_code}): {response.text}")
                    except Exception as e:
                        st.error(f"發生錯誤: {str(e)}")
                        
        # Imagen 4.0 (Gemini)
        elif engine == "gemini":
            api_key = get_google_api_key()
            if not api_key:
                st.error("找不到 Google API Key。")
            else:
                with st.spinner("正在呼叫 Google Imagen 4.0 生成伺服器..."):
                    try:
                        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={api_key}"
                        payload = {
                            "instances": [{"prompt": user_prompt}],
                            "parameters": {"sampleCount": 1}
                        }
                        
                        response = requests.post(
                            endpoint,
                            headers={"Content-Type": "application/json"},
                            json=payload,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            base64_data = data.get("predictions", [{}])[0].get("bytesBase64Encoded", "")
                            if base64_data:
                                image_bytes = base64.b64decode(base64_data)
                                st.session_state.history.insert(0, {
                                    "id": f"gen-{int(time.time())}",
                                    "prompt": user_prompt,
                                    "engine": "Imagen 4.0",
                                    "aspect_ratio": "1:1",
                                    "image_bytes": image_bytes,
                                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                                })
                                st.success("🎨 Gemini Imagen 圖像生成成功！")
                            else:
                                st.error("未接收到有效的圖像編碼數據。")
                        else:
                            st.error(f"Google API 回傳錯誤 (HTTP {response.status_code}): {response.text}")
                    except Exception as e:
                        st.error(f"發生錯誤: {str(e)}")

# Display Generated Images History
if st.session_state.history:
    st.markdown("### 🖼️ 歷史生成結果")
    for item in st.session_state.history:
        st.markdown(f"**提示詞:** `{item['prompt']}`")
        st.markdown(f"**模型:** `{item['engine']}` | **比例:** `{item['aspect_ratio']}` | **時間:** `{item['timestamp']}`")
        
        st.image(item["image_bytes"], use_container_width=True)
        
        # Download button
        st.download_button(
            label="下載圖片",
            data=item["image_bytes"],
            file_name=f"cosmos3-{item['id']}.png",
            mime="image/png",
            key=f"dl_{item['id']}"
        )
        st.markdown("---")
else:
    st.info("準備就緒，等候指令... 請在上方輸入提示詞並點擊開始生成！")
