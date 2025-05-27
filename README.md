# 🎬 SmartClip — AI-Powered TikTok Clip Generator

**AutoReel** is a powerful Python-based automation tool that transforms full-length movies into short, engaging TikTok-style clips — complete with multi-language subtitles, audio transcriptions, and smart slicing logic.

This project was built to streamline content creation for short-form platforms like TikTok, YouTube Shorts, and Instagram Reels.

---

## 🚀 Key Features

- 🎞️ **Automatic video segmentation** into viral-ready clips
- 🧠 **Dual transcription engine** using Deepgram and AssemblyAI with fallback logic
- 🌐 **Multi-language subtitle support**
- 🎥 **Auto rendering** with subtitles embedded
- ⚙️ **Error-tolerant modular design** with robust exception handling

---

## 🧰 Tech Stack

| Category      | Tech                               |
|---------------|------------------------------------|
| Language      | Python                             |
| Video Editing | MoviePy, ImageIO-FFMPEG            |
| Subtitles     | PySRT                              |
| Transcription | Deepgram API, AssemblyAI, OpenAI   |
| Env Mgmt      | python-dotenv                      |
| UI/CLI        | tqdm (progress bars)               |

---

## 📁 Project Structure

SmartClip/
├── source/ # Main source code
│ ├── main.py
│ ├── transcribe.py
│ ├── subtitle_generator.py
│ ├── render.py
│ ├── utils.py
├── requirements.txt
├── .gitignore
└── README.md

---

📦 Installation

git clone https://github.com/jrwdev/SmartClip.git
cd SmartClip
pip install -r requirements.txt

**Add a .env file with your API keys:**
DEEPGRAM_API_KEY=your_key
ASSEMBLYAI_API_KEY=your_key
OPENAI_API_KEY=your_key

---

⚡ Usage

```python main.py path/to/movie.mp4```

---

💡 Why It Matters

Creating engaging TikTok content from long videos is time-consuming. AutoReel automates the process using AI-based transcription and smart editing tools, helping creators and agencies produce consistent content at scale.

---

🔐 Security

All API keys are loaded from .env

.gitignore excludes sensitive files

No secrets are pushed to version control

---

📄 License

**MIT License** — feel free to use and extend this tool.

---

🤝 Let's Connect

Developed by jrwdev — feel free to fork, contribute, or reach out for collaboration.

---