
# AI SEO Service: Full Architecture with ML-Enhanced Clustering

## 📌 Overview
Advanced AI SEO platform with optional supervised learning layer for improving clustering quality using labeled data.

---

## 🧠 High-Level Architecture

User Input → Crawl → Keywords → Embeddings → Clustering → SERP → Intent → Pages → Content

Optional ML Layer:
            ↓
   Supervised Similarity Model
            ↓
   Improved Clustering

---

## ⚙️ Core Modules

### 1. Crawling
Extract:
- URL
- Title
- Headings
- Content

---

### 2. Keyword Expansion
Generate:
- long-tail
- synonyms
- intent labels

---

### 3. Embeddings
Store vectors in pgvector.

---

### 4. Clustering
Default:
- DBSCAN (cosine similarity)

---

## 🧠 Optional Module: ML-Enhanced Clustering

### 🎯 Goal
Improve clustering using labeled data:
- keyword sets → correct clusters

---

### 📊 Dataset Preparation

Transform clusters into pairs:

Positive pairs:
- same cluster

Negative pairs:
- different clusters

Example:

{
  "query1": "math tutor online",
  "query2": "online math teacher",
  "label": 1
}

---

### 🤖 Model Options

- Sentence-BERT (fine-tuning)
- Cross-encoder (recommended)

---

### ⚙️ Pipeline

keywords
 ↓
embeddings
 ↓
candidate pairs (ANN search)
 ↓
ML similarity model
 ↓
graph clustering
 ↓
SERP validation

---

### 💡 Hybrid Strategy

1. Embeddings → recall
2. ML model → precision
3. SERP → validation

---

### 📈 Benefits

- Better intent separation
- Reduced clustering errors
- Learns from real SEO data

---

## 🔍 SERP Validation

Rule:
30%+ overlap → same intent

---

## 🎯 Intent Detection

Classify:
- informational
- commercial
- transactional
- navigational

---

## 🧩 Page Mapping

Cluster → Page

---

## ✍️ Content Generation

Generate:
- Titles
- Headings
- FAQ
- Keywords

---

## 🧱 Tech Stack

- FastAPI
- PostgreSQL + pgvector
- Python (sklearn, transformers)
- Async workers

---

## 📡 API

POST /crawl
POST /keywords
POST /cluster
POST /cluster/ml
POST /intent
POST /pages

---

## 🚀 Roadmap

v1:
- basic clustering

v2:
- SERP + intent

v3:
- ML clustering

v4:
- full automation

---

## 💡 Product Vision

AI SEO system that:
- learns from user data
- improves clustering over time
- automates SEO end-to-end

---

## ✅ Output

- semantic core
- clusters
- page structure
- content briefs
