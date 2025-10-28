# 🧠 Agentic Viral Video Orchestrator (AVVO)

### A Self-Optimizing, Multi-Agent AI System for Trend Discovery, Video Generation, and Autonomous Publishing

---

## 📘 Overview

**AVVO** (Agentic Viral Video Orchestrator) is an **AI-driven, agentic automation system** designed to autonomously **discover viral trends**, **generate short-form video content**, **publish across multiple social platforms**, and **learn from performance feedback** to optimize future outputs.

This project integrates **Generative AI**, **automation engineering**, and **agentic system design** to create a *living, self-improving video ecosystem*—ideal for media companies, growth teams, and AI-first content studios such as **Viralish**.

---

## 🧩 Core Architecture

AVVO is composed of **six collaborative AI agents**, each orchestrated through asynchronous pipelines, REST APIs, and event-driven tasks using **FastAPI**, **Celery**, and **Redis**.

| Agent | Responsibility | Key Tools / APIs |
|--------|----------------|------------------|
| **Trend Discovery Agent** | Scans TikTok, YouTube Shorts, and Instagram Reels for emerging trends. | BeautifulSoup, ScraperAPI, OpenAI Embeddings |
| **Story Ideation Agent** | Generates script outlines, hooks, and storytelling angles. | GPT-4, LangChain, FAISS |
| **Video Generation Agent** | Produces videos using multimodal AI tools. | RunwayML, Sora, Pika Labs, ElevenLabs |
| **Feedback & Optimization Agent** | Analyzes engagement metrics and refines pipelines. | Pandas, FastAPI, LangSmith |
| **Publisher Agent** | Automates video publishing to social platforms. | Cloudinary, Zapier Webhooks, Buffer API |
| **Documentation & Versioning Layer** | Logs all versions, iterations, and datasets for reproducibility. | PostgreSQL, Notion API |

---

## ⚙️ Tech Stack

### **Backend**
- **FastAPI (Python)** — Lightweight REST framework for AI and automation pipelines.  
- **Celery + Redis** — Distributed task queues and asynchronous job scheduling.  
- **PostgreSQL** — Persistent relational data storage for trends, scripts, and logs.  
- **FAISS** — Vector database for semantic search and similarity clustering.  
- **LangChain + OpenAI APIs** — LLM-driven reasoning, prompt chaining, and tool orchestration.  
- **Zapier Webhooks** — Event-based communication with publishing and analytics services.

### **Frontend**
- **React + Next.js** — Dashboard for monitoring AI agents, tasks, and trends.  
- **TailwindCSS + Shadcn/UI** — Modern, responsive UI components.  
- **Recharts** — Interactive data visualization for engagement metrics and trend tracking.

### **Cloud & DevOps**
- **Docker + Kubernetes** — Containerized, scalable deployment.  
- **AWS / GCP** — Cloud infrastructure for hosting, storage, and compute scaling.  
- **GitHub Actions** — CI/CD pipelines for testing and continuous deployment.  

### **Media & Automation**
- **Cloudinary** — Media storage and automatic CDN generation for videos.  
- **Buffer API** — Scheduled posting to TikTok, YouTube Shorts, and Instagram Reels.  
- **Zapier Webhooks** — Middleware layer for integrating publishing and feedback events.

---

## 🧠 Logic Flow

### 1️⃣ Trend Discovery
- **Celery** triggers scheduled crawlers across TikTok, YouTube Shorts, and Reels.  
- Metadata (hashtags, views, captions) is embedded using **OpenAI embeddings**.  
- Trends are clustered via **FAISS** and ranked using a **LangChain reasoning chain**.  
- Top-performing topics are stored in **PostgreSQL** for script generation.

### 2️⃣ Story Ideation
- The **Ideation Agent** uses GPT-4 to generate scripts and storyboards.  
- Each script is evaluated for engagement, clarity, and keyword potential.  
- High-performing scripts are queued for production by **Celery workers**.

### 3️⃣ Video Generation
- **RunwayML**, **Sora**, and **Pika Labs APIs** generate the video clips.  
- **ElevenLabs** produces voiceovers and sound design.  
- Final outputs are uploaded to **Cloudinary**, which returns public CDN URLs.

### 4️⃣ Automated Publishing
- Once a video is uploaded, the backend emits a **Zapier webhook** event.  
- Zapier receives metadata (title, hashtags, URL) and triggers **Buffer** for posting.  
- Buffer schedules or publishes instantly to **TikTok**, **YouTube Shorts**, and **Instagram Reels**.  
- Posting confirmations are logged in **PostgreSQL** for version tracking.

### 5️⃣ Feedback & Optimization
- Engagement metrics (views, likes, shares, CTR) are fetched from platform APIs.  
- Data is stored and processed by the **Optimization Agent**.  
- The agent updates the **prompt weights and discovery criteria**, creating a continuous improvement loop.

---

## 🧮 System Architecture Diagram

```mermaid
flowchart TD

A[Trend Discovery Agent] --> B[Story Ideation Agent]
B --> C[Video Generation Agent]
C --> D[Cloudinary Upload]
D --> E[Zapier Webhook Event]
E --> F[Buffer API - Automated Posting]
F --> G[Platform Analytics APIs]
G --> H[Feedback & Optimization Agent]
H --> A

subgraph Infrastructure
  I[Redis - Task Queue]
  J[Celery Workers]
  K[PostgreSQL - Data Store]
  L[FAISS - Vector DB]
end

A --> I
B --> J
C --> L
H --> K
