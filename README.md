# 🧠 Agentic Viral Video Orchestrator (AVVO)

### A Self-Optimizing, Multi-Agent AI System for Trend Discovery, Video Generation, and Autonomous Publishing

---

## 🎬 Live Demo  
▶️ **Watch here:** [https://youtu.be/ZyP000IhtPc](https://youtu.be/ZyP000IhtPc)

---

## 📘 Overview

**AVVO (Agentic Viral Video Orchestrator)** is an **AI-powered multi-agent automation system** that autonomously **discovers viral trends**, **creates short-form video content**, **publishes across social platforms**, and **learns from audience engagement** to improve future outputs.

It blends **Generative AI**, **automation engineering**, and **reinforcement optimization** into a unified platform — the kind of system that powers viral content pipelines for media teams like **Viralish**.

---

## 🧩 Core Architecture

AVVO runs on **seven AI agents**, coordinated through **FastAPI**, **Celery**, and **Redis** for distributed orchestration. Each agent handles a key stage of the AI video pipeline.

| Agent | Function | Key Integrations |
|--------|-----------|------------------|
| **1. Trend Discovery Agent** | Scans TikTok, YouTube Shorts, and Instagram Reels for emerging trends using virality scoring. | Gemini 2.5-Flash, FAISS, Speech-to-Text |
| **2. Story Ideation Agent** | Converts trending topics into structured video scripts. | Gemini AI, JSON prompt templates |
| **3. Video Generation Agent** | Produces short-form videos with scene orchestration, voiceovers, and sound design. | Vertex AI Veo, Google TTS, FFmpeg |
| **4. Optimization & Feedback Agent** | Tracks engagement and optimizes prompt logic using reinforcement learning. | Contextual Bandit Model, Pandas |
| **5. Publisher Agent** | Automates cross-platform posting using Buffer and Zapier. | Buffer API, Cloudinary, Zapier Webhooks |
| **6. Brand Safety Agent** | Ensures ethical and brand-safe video generation. | Gemini AI Classifier |
| **7. Documentation Agent** | Automatically documents changes, updates, and runs. | Markdown + PostgreSQL |

---

## ⚙️ Tech Stack

### **Backend**
- **FastAPI (Python 3.12)** – RESTful API gateway and orchestration layer  
- **Celery + Redis** – Task queue and async job execution for distributed AI agents  
- **PostgreSQL** – Structured data storage for users, trends, and analytics  
- **FAISS Vector Database** – Semantic trend clustering and retrieval  
- **LangChain + Gemini API** – Agentic reasoning and content ideation  
- **Zapier Webhooks** – Event-driven communication for publishing automation  

### **Frontend**
- **React 19.2 + TypeScript** – Frontend interface and dashboards  
- **TailwindCSS + Shadcn/UI** – Responsive design and UI components  
- **Recharts** – Interactive analytics and visualization  

### **Cloud & DevOps**
- **Docker + Docker Compose** – Containerized microservices  
- **AWS / GCP** – Cloud infrastructure for scaling  
- **GitHub Actions** – CI/CD automation pipeline  

### **Media & Automation**
- **Cloudinary** – Video storage, transformation, and public URL generation  
- **Zapier Webhooks** – Connects backend to Buffer and analytics feedback  
- **Buffer API** – Automated social media posting to TikTok, YouTube, and Instagram  
- **FFmpeg + OpenCV** – Video editing, stitching, and compression  

---

## 🧠 End-to-End Logic Flow

### 1️⃣ Trend Discovery
- Scheduled **Celery jobs** crawl and analyze TikTok, YouTube Shorts, and Instagram posts.  
- Virality signals (views, comments, keywords) are vectorized with **FAISS**.  
- **Gemini AI** scores each trend (1–100) and ranks by predicted viral potential.  

### 2️⃣ Story Ideation
- Selected trends are passed to **Gemini 2.5-flash** for story scripting.  
- AI generates multi-scene scripts with hooks, CTAs, and timestamps.  
- Scripts are stored in **PostgreSQL** and versioned by the Documentation Agent.

### 3️⃣ Video Generation
- Each script is processed by the **Dynamic Shot Orchestrator** (Python).  
- Video scenes are generated using **Vertex AI Veo**, **Google Text-to-Speech**, and **AI music generation**.  
- Final outputs are stitched with **FFmpeg** and uploaded to **Cloudinary**, generating a public CDN URL.

### 4️⃣ Automated Publishing (Buffer + Zapier + Cloudinary)
- Once Cloudinary returns a video URL, the backend triggers a **Zapier webhook**.  
- Zapier receives metadata (video title, caption, tags, and public URL).  
- Zapier triggers **Buffer API**, which schedules and posts videos automatically to:
  - **TikTok**
  - **YouTube Shorts**
  - **Instagram Reels**  
- Publishing confirmations are logged in **PostgreSQL**, ensuring version control and traceability.

### 5️⃣ Feedback & Optimization
- Platform analytics APIs send post-performance data (views, likes, CTR) back via Zapier.  
- The **Optimization Agent** applies a contextual bandit learning algorithm to improve:
  - Hook structure
  - Caption tone
  - Music and pacing
  - Visual consistency  
- The system **learns and updates its strategy autonomously** over time.

---

## 🧮 System Architecture Diagram

```mermaid
flowchart TD

A[Trend Discovery Agent] --> B[Story Ideation Agent]
B --> C[Video Generation Agent]
C --> D[Cloudinary - Upload & CDN]
D --> E[Zapier Webhook Trigger]
E --> F[Buffer API - Auto Publishing]
F --> G[Social Media Platforms]
G --> H[Feedback & Optimization Agent]
H --> A

subgraph Backend Infrastructure
  I[Redis - Queue]
  J[Celery Workers - Async Tasks]
  K[PostgreSQL - Structured Storage]
  L[FAISS - Vector Index]
end

A --> I
B --> J
C --> L
H --> K
