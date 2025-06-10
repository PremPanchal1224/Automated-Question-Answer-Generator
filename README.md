# 📘 Automated Question-Answer Generation (AQG)

The **Automated Question Generator (AQG)** is a Streamlit-based web application that intelligently extracts, summarizes, and generates meaningful questions from uploaded PDF documents. It is built to assist students, educators, and professionals by simplifying the process of information retrieval and review using advanced natural language processing techniques.

---

## 🚀 Features

- 📄 **PDF Upload & Text Extraction** – Upload academic papers, research articles, or notes in PDF format and extract content using PyPDF2.
- 🧹 **Text Preprocessing** – Cleans the extracted text for better model performance.
- ✨ **Content Summarization** – Uses the pre-trained **BART** model to generate concise and meaningful summaries.
- ❓ **Question Generation** – Employs the **T5** model to generate high-quality questions from the summarized text.
- 🛠️ **Customizable Q&A Types** – Choose between:
  - 🔹 One-word answer questions
  - 🔹 Sentence-based answer questions
- 🧠 **Iterative & Modular Design** – Supports continuous improvement based on user feedback.
- 🖥️ **User-Friendly Interface** – Built using **Streamlit** for quick deployment and ease of use.


---

## 🧰 Tech Stack

- **Frontend/UI:** Streamlit
- **Text Extraction:** PyPDF2
- **Summarization:** Facebook BART (via Hugging Face Transformers)
- **Question Generation:** T5 Model (via Hugging Face Transformers)
- **Backend Logic:** Python, Transformers, NLP utilities

---

## 🎓 Use Cases

- 📚 Students preparing for exams or quizzes  
- 🧑‍🏫 Teachers generating quick assessment questions  
- 📑 Researchers reviewing lengthy papers  
- 📊 Professionals needing quick comprehension of technical documents

---

## 🎥 Working Prototype Video

▶️ [Watch on Google Drive](https://drive.google.com/file/d/1wX2TxBFTJ4wQelOiRQnpLdQ-U6jdfHmi/view?usp=sharing)

---

## 🛠 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/PremPanchal1224/Automated-Question-Answer-Generator.git
cd Automated-Question-Answer-Generator
