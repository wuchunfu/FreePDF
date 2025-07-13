<div align="center">
  <img src="assets/logo_with_txt.png" width="500" alt="FreePDF">
</div>

<div align="center">
  <img src="https://img.shields.io/badge/version-5.0.0-blue" alt="version">
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

[![FreePDF: Revolutionizing the way researchers read literature](https://i0.hdslb.com/bfs/archive/4a93b27eb529d8d4422fc6a8e43d3f081e851f05.jpg@672w_378h_1c.avif)](https://www.bilibili.com/video/BV11EgkziEFg)

## 📦 Installation

- windows：

  - github：https://github.com/zstar1003/FreePDF/releases/download/v5.0.0/FreePDF_v5.0.0_Setup.exe

  - 百度网盘：https://pan.baidu.com/s/1Qh8Sb5XYpJWdDHXVr0vOoA?pwd=8888 (Extraction code: 8888)

- mac(arm64)：

  - github：https://github.com/zstar1003/FreePDF/releases/download/v5.0.0/FreePDF_v5.0.0_arm64.dmg

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