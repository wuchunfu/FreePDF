<div align="center">
  <img src="assets/logo_with_txt.png" width="500" alt="FreePDF">
</div>

<div align="center">
  <img src="https://img.shields.io/badge/version-5.1.0-blue" alt="version">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-AGPL3.0-green" alt="License"></a>
  <h4>
    <a href="README.md">🇨🇳 Chinese</a>
    <span> | </span>
    <a href="README_EN.md">🇬🇧 English</a>
  </h4>
</div>

## ⭐️ Introduction

A free PDF document reader that supports converting PDF documents in various languages into Chinese, and supports access to large models for question and answer based on document content.


## 🏗️ Effect demonstration

[![FreePDF: Subverting the way researchers read literature](https://i0.hdslb.com/bfs/new_dyn/ee3f2cef036de77d80fe4518ef350f32472442675.jpg@428w_322h_1c.avif)](https://www.bilibili.com/video/BV11EgkziEFg)


## 📦 How to use

- windows:

  - github: https://github.com/zstar1003/FreePDF/releases/download/v5.1.0/FreePDF_v5.1.0_Setup.exe

  - Baidu Netdisk: https://pan.baidu.com/s/1Q4wyrLXQDovLmeBP4aP4Zw?pwd=8888 Extraction code: 8888

- mac(arm64)：

  - github: [https://github.com/zstar1003/FreePDF/releases/download/v5.1.0/FreePDF_v5.1.0_macOS.dmg](https://github.com/zstar1003/FreePDF/releases/download/v5.1.0/FreePDF_v5.1.0_macOS.dmg)

  - HomeBrew: run `brew install freepdf`

The translated PDF file will be generated in its corresponding directory `-mono.pdf` (translation file)

## 🔧 Source code startup

Configuration environment:

```bash
uv sync
```

Start the application:

```bash
python main.py
```


## 📥 Configuration instructions

### Configuration file structure and parameter description

Configuration file (pdf2zh_config.json) example:

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
    "service": "bing", // Translation engine, optional: bing, google, silicon, ollama, custom
    "lang_in": "en", // Source language, optional: en, zh, ja, ko, zh-TW
    "lang_out": "zh", // target language, same as above
    "envs": {
      // bing/google does not require configuration
      //silicon example:
      // "SILICON_API_KEY": "Your API Key",
      // "SILICON_MODEL": "Qwen/Qwen2.5-7B-Instruct"
      // ollama example:
      // "OLLAMA_HOST": "http://127.0.0.1:11434",
      // "OLLAMA_MODEL": "deepseek-r1:1.5b"
      // Custom example:
      // "CUSTOM_HOST": "https://api.xxx.com",
      // "CUSTOM_KEY": "Your Key",
      // "CUSTOM_MODEL": "Model name"
    }
  },
  "qa_engine": {
    "service": "Close", // Question and answer engine, optional: close, silicon, ollama, custom
    "envs": {
      //Configuration method is the same as above
    }
  },
  "qa_settings": {
    "pages": "", // Limit the PDF page range for question and answer analysis, the format is such as "1-5,8,10-15", leave blank to indicate all pages
    "system_prompt": "You are a professional PDF document analysis assistant. The user uploaded a PDF document and you need to answer the user's questions based on the document content.\n\nThe content of the PDF document is as follows:\n{pdf_content}\n\nPlease note:\n1. Please answer the question based only on the content of the above PDF document\n2. If the question has nothing to do with the document content, please explain clearly\n3. The answer must be accurate and detailed, and cite the relevant page information\n4. Answer in Chinese\n"
  },
  "translation_enabled": true, // Whether to enable translation
  "NOTO_FONT_PATH": "./fonts/SourceHanSerifCN-Regular.ttf", // Global font path (
  "pages": "" // Global page scope
}
```

#### Field description
- `models.doclayout_path`: DocLayout-YOLO ONNX model path.
- `fonts`: PDF rendering font path for each language.
- `translation.service`: translation engine, supports bing, google, silicon, ollama, and customization.
- `translation.lang_in`/`lang_out`: source/target language, supports en (English), zh (Chinese), ja (Japanese), ko (Korean), zh-TW (Traditional Chinese).
- `translation.envs`: API parameters of different translation engines. The configuration method is exactly the same as `qa_engine.envs` below. For details, see the typical configuration example below.
- `qa_engine.service`: Question and answer engine, supports shutdown, silicon, ollama, and customization.
- `qa_engine.envs`: API parameters of different question and answer engines. The configuration method is exactly the same as `translation.envs` above. For details, see the typical configuration example below.
- `qa_settings.pages`: The range of PDF pages analyzed during Q&A, in a format such as "1-5,8,10-15".
- `qa_settings.system_prompt`: Question and answer system prompt word, {pdf_content} placeholder represents the specific document content.
- `translation_enabled`: Whether to enable translation (true/false).
- `NOTO_FONT_PATH`: global font path.
- `pages`: global page scope.

#### Typical configuration example
- **Silicon Mobile Translation/Q&A**:
  ```json
  "service": "silicon",
  "envs": {
    "SILICON_API_KEY": "Your API Key",
    "SILICON_MODEL": "Qwen/Qwen2.5-7B-Instruct"
  }
  ```
- **Ollama local large model**:
  ```json
  "service": "ollama",
  "envs": {
    "OLLAMA_HOST": "http://127.0.0.1:11434",
    "OLLAMA_MODEL": "deepseek-r1:1.5b"
  }
  ```
- **Custom OpenAI Compatible API**:
  ```json
  "service": "custom",
  "envs": {
    "CUSTOM_HOST": "https://api.xxx.com",
    "CUSTOM_KEY": "Your Key",
    "CUSTOM_MODEL": "Model name"
  }
  ```

> Whether it is translation or Q&A, the envs field is filled in exactly the same way. You only need to fill in the corresponding parameters according to the selected engine.
> It is recommended to use Notepad/VSCode to edit the configuration file. Note that the JSON format cannot have comments. All comments are for reference only.

Four optional translation engines are supported:

- Bing Translate (default)
  
  Select the translation engine as bing, no additional parameters are required

- Google Translate
  
  Select the translation engine as google, no additional parameters are required

- Silicon Translator
  
  If the translation engine is selected as silicon, additional configuration of [Silicon Flow](https://cloud.siliconflow.cn/i/bjDoFhPf) API Key and specific chat model is required.

- Ollama translation

  Select the translation engine as ollama, first deploy the local chat model through ollama, and configure the ollama address and specific chat model.

Supports mutual translation between five languages: Chinese, English, Japanese, Korean, and Traditional Chinese.

The question and answer engine supports silicon-based flow (online), ollama (local) and other custom methods that comply with the `OpenAi API`.



## ❓ FAQ

1. Does it support image-based PDFs, such as scanned documents?    
  **Answer:** Not supported. Essentially, `pdf2zh` is used to detect the content of text blocks and then translate and replace them. Picture types cannot be directly replaced, which will cause the content to overlap and overlap.

2. When using large model translation, some content is not translated?  
  **Answer:** The large model with low number of parameters has poor ability to follow instructions. If it is translated, it may not be completely obedient, which will cause this phenomenon. Therefore, when using a large model for local translation, it is necessary to ensure that the large model itself has a certain parameter scale, and it is recommended to exceed 7B.

3. The content in the form is not translated?  
  **Answer:** pdf2zh does not currently support table content translation. If you need to translate tables, you can check the `dev` branch of this warehouse and use `pdf2zh_next` for translation. However, due to the slow speed, it has not been merged into the main branch.

4. The engine configuration file in the software cannot be saved?  
  **Answer:** Under the default scaling of some models, the saved configuration button cannot be displayed. You can modify the screen resolution or scaling ratio and try again. You can also refer to the instructions above and directly edit the configuration file `pdf2zh_config.json` in the software installation path.

If you have other questions, please submit an issue or directly contact my WeChat account zstar1003 to report the problem.

## 🛠️ How to contribute

1. Fork this GitHub repository
2. Clone the fork locally:
`git clone git@github.com:<your username>/FreePDF.git`
3. Create a local branch:
`git checkout -b my-branch`
4. Submitted information must include sufficient description:
`git commit -m 'The submission message must contain sufficient description'`
5. Push changes to GitHub (including necessary commit information):
`git push origin my-branch`
6. Submit PR and wait for review

## 🚀 Acknowledgments

This project is developed based on the following open source projects:

- [PDFMathTranslate](https://github.com/Byaidu/PDFMathTranslate)

- [DocLayout-YOLO](https://github.com/opendatalab/DocLayout-YOLO)

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt)

- [pdf.js](https://github.com/mozilla/pdf.js)