<div align="center">
  <img src="assets/logo_with_txt.png" width="500" alt="FreePDF">
</div>

<div align="center">
  <img src="https://img.shields.io/badge/version-5.1.0-blue" alt="version">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-AGPL3.0-green" alt="license"></a>
  <h4>
    <a href="README.md">🇨🇳 中文</a>
    <span> | </span>
    <a href="README_EN.md">🇬🇧 English</a>
  </h4>
</div>

## ⭐️ Introduction

A free PDF reader that translates PDF documents from multiple languages into Chinese and integrates large language models to perform question-answering based on the document content.

## 🏗️ Demo

[![FreePDF: Revolutionizing the way researchers read literature](https://i0.hdslb.com/bfs/new_dyn/ee3f2cef036de77d80fe4518ef350f32472442675.jpg@428w_322h_1c.avif)](https://www.bilibili.com/video/BV11EgkziEFg)

## 📦 Installation

- windows：

  - github：https://github.com/zstar1003/FreePDF/releases/download/v5.1.0/FreePDF_v5.1.0_Setup.exe

  - 百度网盘：https://pan.baidu.com/s/1Qh8Sb5XYpJWdDHXVr0vOoA?pwd=8888 (Extraction code: 8888)

- mac(arm64)：

  - github：https://github.com/zstar1003/FreePDF/releases/download/v5.1.0/FreePDF_v5.1.0_arm64.dmg

  - 百度网盘：https://pan.baidu.com/s/1Eqe1Q0_DqQ0u6_YQybD8AQ?pwd=8888 (Extraction code: 8888)

After the translation completes, two files will be generated in the same directory:

- `*-dual.pdf`: bilingual view (original + Chinese)
- `*-mono.pdf`: Chinese-only translation

## 🔧 Run from Source

Create environment:

```bash
uv venv --python 3.10
uv sync
```

Start the application:

```bash
python main.py
```

## 📥 Configuration

### Configuration File Structure and Parameters

Example config file (`pdf2zh_config.json`):

```json
{
  "models": {
    "doclayout_path": "./models/doclayout_yolo_docstructbench_imgsz1024.onnx"
  },
  "fonts": {
    "zh": "./fonts/SourceHanSerifCN-Regular.ttf",
    "ja": "./fonts/SourceHanSerifJP-Regular.ttf",
    "ko": "./fonts/SourceHanSerifKR-Regular.ttf",
    "zh-TW": "./fonts/SourceHanSerifTW-Regular.ttf",
    "default": "./fonts/GoNotoKurrent-Regular.ttf"
  },
  "translation": {
    "service": "bing", // Engine: bing, google, silicon, ollama, custom
    "lang_in": "en",   // Source language: en, zh, ja, ko, zh-TW
    "lang_out": "zh",  // Target language: same as above
    "envs": {
      // bing/google: leave empty
      // silicon example:
      //   "SILICON_API_KEY": "your API Key",
      //   "SILICON_MODEL": "Qwen/Qwen2.5-7B-Instruct"
      // ollama example:
      //   "OLLAMA_HOST": "http://127.0.0.1:11434",
      //   "OLLAMA_MODEL": "deepseek-r1:1.5b"
      // custom example:
      //   "CUSTOM_HOST": "https://api.xxx.com",
      //   "CUSTOM_KEY": "your key",
      //   "CUSTOM_MODEL": "model name"
    }
  },
  "qa_engine": {
    "service": "off", // Q&A engine: off, silicon, ollama, custom
    "envs": {
      // configure exactly as above, see examples below
    }
  },
  "qa_settings": {
    "pages": "", // Page range for Q&A, e.g. "1-5,8,10-15", empty for all
    "system_prompt": "You are a professional PDF document analysis assistant. The user has uploaded a PDF document. Please answer the user's questions based on the document content.\n\nPDF content:\n{pdf_content}\n\nNotes:\n1. Only answer based on the above PDF content\n2. If the question is unrelated, state so clearly\n3. Be accurate, detailed, and cite relevant pages\n4. Answer in Chinese\n5. Use plain text only, no markdown formatting (such as **, ##, *, - etc.), just use text to highlight key points."
  },
  "translation_enabled": true, // Enable translation
  "NOTO_FONT_PATH": "./fonts/SourceHanSerifCN-Regular.ttf", // Global font path
  "pages": "" // Global page range
}
```

#### Field Explanations
- `models.doclayout_path`: DocLayout-YOLO ONNX model path.
- `fonts`: Font paths for different languages.
- `translation.service`: Translation engine, supports bing, google, silicon, ollama, custom.
- `translation.lang_in`/`lang_out`: Source/target language, supports en, zh, ja, ko, zh-TW.
- `translation.envs`: Engine-specific API parameters. The configuration method is exactly the same as for `qa_engine.envs` below. See the examples below.
- `qa_engine.service`: Q&A engine, supports off, silicon, ollama, custom.
- `qa_engine.envs`: Engine-specific API parameters. The configuration method is exactly the same as for `translation.envs` above. See the examples below.
- `qa_settings.pages`: Page range for Q&A, e.g. "1-5,8,10-15".
- `qa_settings.system_prompt`: System prompt for Q&A, `{pdf_content}` will be replaced with the actual document content.
- `translation_enabled`: Enable translation (true/false).
- `NOTO_FONT_PATH`: Global font path.
- `pages`: Global page range.

> For both translation and Q&A, the `envs` field should be filled in exactly the same way, just use the parameters required by your selected engine. See the examples below.

#### Typical Configuration Examples
- **SiliconFlow translation/Q&A**:
  ```json
  "service": "silicon",
  "envs": {
    "SILICON_API_KEY": "your API Key",
    "SILICON_MODEL": "Qwen/Qwen2.5-7B-Instruct"
  }
  ```
- **Ollama local LLM**:
  ```json
  "service": "ollama",
  "envs": {
    "OLLAMA_HOST": "http://127.0.0.1:11434",
    "OLLAMA_MODEL": "deepseek-r1:1.5b"
  }
  ```
- **Custom OpenAI-compatible API**:
  ```json
  "service": "custom",
  "envs": {
    "CUSTOM_HOST": "https://api.xxx.com",
    "CUSTOM_KEY": "your key",
    "CUSTOM_MODEL": "model name"
  }
  ```

> It is recommended to edit the config file with Notepad/VSCode, and remember that JSON does not support comments. All comments above are for reference only.

Four translation engines are supported and can be selected in “Engine Settings”.

- Bing Translator (default)  
  Choose `bing` as the translation engine; no additional parameters are required.

- Google Translate  
  Choose `google`; no additional parameters are required.

- SiliconFlow Translator  
  Choose `silicon`; you need to configure your [SiliconFlow](https://cloud.siliconflow.cn/i/bjDoFhPf) API Key and the specific chat model.

- Ollama Translator  
  Choose `ollama`; first deploy a local chat model via Ollama, then configure the Ollama address and the specific chat model.

Five languages are currently supported (Chinese, English, Japanese, Korean, Traditional Chinese) and can be translated interchangeably.

The Q&A engine supports SiliconFlow (cloud), Ollama (local), and any other implementation compatible with the OpenAI API.

## ❓ FAQ

1. Does it support image-based PDFs, such as scanned documents?  
   **Answer:** No. The tool relies on `pdf2zh` to detect text blocks. Replacing text in image-based PDFs will cause overlapping content.

2. When using a large language model (LLM) for translation, some content remains untranslated? 
   **Answer:** Small-parameter LLMs have weak instruction-following ability. If the model ignores translation instructions, this issue can occur. When translating locally with an LLM, please ensure the model has a sufficient parameter size—7 B or larger is recommended.

3. Why is the content inside tables not translated?  
   **Answer:** Currently, pdf2zh does not support table translation. If you need this feature, check the `dev` branch of this repository, where pdf2zh_next can handle tables. However, due to its slower speed, it has not been merged into the main branch yet.

If you have other questions, feel free to submit an issue.

## 🛠️ Contributing

1. Fork this repository  
2. Clone your fork:  
   `git clone git@github.com:<your-username>/FreePDF.git`  
3. Create a local branch:  
   `git checkout -b my-branch`  
4. Commit with descriptive messages:  
   `git commit -m "A clear and descriptive commit message"`  
5. Push changes to GitHub:  
   `git push origin my-branch`  
6. Open a PR and wait for review

## 🚀 Acknowledgments

This project is based on the following open-source projects:

- [PDFMathTranslate](https://github.com/Byaidu/PDFMathTranslate)
- [DocLayout-YOLO](https://github.com/opendatalab/DocLayout-YOLO)
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt)
- [pdf.js](https://github.com/mozilla/pdf.js) 