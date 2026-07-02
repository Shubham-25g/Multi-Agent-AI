# 🔍 Multi-Agent AI Research Assistant

A **Multi-Agent AI Research Assistant** that automates the complete research workflow using **LangChain**, **Mistral AI**, **Tavily Search**, **Trafilatura**, and **Streamlit**. The system searches the web, extracts information from multiple reliable sources, summarizes the content, generates a comprehensive research report, and evaluates the final report using an AI-powered critic agent.

---

## 🌐 Live Demo

🚀 **Application:** https://multi-agent-ai-25.streamlit.app/

📂 **GitHub Repository:** https://github.com/Shubham-25g/Multi-Agent-AI

---

# ✨ Features

### 🔎 Search Agent
- Retrieves recent and reliable information using the Tavily Search API.
- Automatically filters duplicate search results.

### 🌍 Web Scraping
- Extracts clean article content using Trafilatura.
- Detects and skips inaccessible, blocked, or low-quality pages.
- Continues searching until the desired number of high-quality sources is collected.

### 📖 Reader Agent
- Reads every scraped webpage.
- Generates structured summaries while preserving important facts, statistics, dates, and technical information.

### 📝 Writer Agent
- Combines information from multiple sources.
- Removes duplicate information.
- Produces a structured research report containing:
  - Introduction
  - Key Findings
  - Analysis
  - Conclusion
  - Sources

### 🧐 Critic Agent
- Reviews the generated report.
- Evaluates:
  - Accuracy
  - Completeness
  - Organization
  - Readability
  - Citation Quality
- Provides an overall score and constructive feedback.

### 🎨 Interactive UI
- Modern Streamlit interface
- Research progress tracking
- Search result visualization
- Source previews
- AI-generated summaries
- Downloadable research report
- Critic evaluation

---

# 🏗️ System Workflow

```text
                User Query
                     │
                     ▼
          🔎 Search Agent (Tavily)
                     │
                     ▼
          🌍 Web Scraper (Trafilatura)
                     │
                     ▼
           📖 Reader Agent (LLM)
                     │
                     ▼
         📚 Context Builder
                     │
                     ▼
           📝 Writer Agent (LLM)
                     │
                     ▼
            🧐 Critic Agent (LLM)
                     │
                     ▼
             Final Research Report
```

---

# 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| Programming Language | Python |
| Framework | Streamlit |
| AI Framework | LangChain |
| Large Language Model | Mistral AI |
| Search Engine | Tavily Search API |
| Web Scraping | Trafilatura |
| HTML Parsing | BeautifulSoup |
| HTTP Requests | Requests |
| Version Control | Git & GitHub |

---

# 📂 Project Structure

```text
Multi-Agent-AI/
│
├── app.py
├── pipeline.py
├── agents.py
├── tools.py
├── requirements.txt
│
├── workflow/
│   ├── search.py
│   ├── scraper.py
│   ├── reader.py
│   ├── context.py
│   ├── writer.py
│   ├── critic.py
│   ├── orchestrator.py
│   ├── state.py
│   └── config.py
│
└── README.md
```

---

# 🚀 Future Improvements

- PDF and DOCX report export
- Research history
- Citation formatting (APA / IEEE)
- Multiple LLM support
- Configurable search depth
- Charts and visualizations
- RAG support for custom documents
- Multi-language research

---

# 🎯 Key Learning Outcomes

This project demonstrates practical experience with:

- Multi-Agent AI Systems
- Large Language Models (LLMs)
- Prompt Engineering
- LangChain Workflows
- Web Search APIs
- Web Scraping
- Streamlit Application Development
- Modular Software Design
- Git & GitHub
- Cloud Deployment

---

# 👨‍💻 Author

**Shubham Gupta**

- GitHub: https://github.com/Shubham-25g
- LinkedIn: www.linkedin.com/in/shubhamgupta2510
- Live Demo: https://multi-agent-ai-25.streamlit.app/
