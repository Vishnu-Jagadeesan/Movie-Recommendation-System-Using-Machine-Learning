# 🎬 Movie Recommendation System with Sentiment Analysis

This is a **machine learning-powered movie recommendation system** that helps users discover similar movies based on a selected title, enriched with **cast details**, **genre**, **director info**, and **user review sentiment analysis**. It uses **content-based filtering** combined with **Natural Language Processing (NLP)** techniques to personalize recommendations.

This project was **originally developed as a group academic project** and later enhanced with a production-grade deployment on [Render](https://render.com) with API security and preloading optimization.

> 📝 **Published Paper**: [Scientific.Net (2022)](https://doi.org/10.4028/p-g9ekjp)

---

## 🔗 Live Demo

🌐 [Open Preloader Page]([https://vishnu-jagadeesan.github.io/Movie-Recommendation-System/](https://vishnu-jagadeesan.github.io/Movie-Recommendation-System/)

---

## 📌 Project Highlights

- 🔍 **Content-Based Filtering** using metadata (cast, genre, director, etc.)
- 💬 **Sentiment Analysis** on live TMDb reviews using Multinomial Naive Bayes
- 🎭 Cast info with images and Wikipedia-style modal biographies
- 🧠 Auto-complete with top movie titles (AJAX-based)
- 📈 98.77% Accuracy in sentiment prediction
- 🌐 TMDb API integration for fresh movie data
- 🔐 Environment variable protection for API keys (`.env`)
- 🖼️ Responsive UI with Bootstrap, jQuery, and custom CSS
- ⏳ **Preloader support** for Render’s cold start delay (GitHub Pages loader)

---

## 🆕 What's New?

This repository includes my **upgraded version** of the original movie recommendation project:

| Feature                         | Old (Heroku)                          | New (Render + GitHub Pages)               |
|---------------------------------|----------------------------------------|-------------------------------------------|
| Deployment                      | Heroku (now deprecated)                | Render (Free Tier)                         |
| API Handling                    | Direct TMDb call from frontend         | Securely routed via Flask proxy (backend) |
| Review Sentiment Integration    | Offline/static reviews                 | Live reviews fetched from TMDb            |
| Preloader UI                    | ❌ Not included                         | ✅ GitHub-hosted animated preloader        |
| Paper Reference                 | [Published Link](https://doi.org/10.4028/p-g9ekjp) | Same                                        |

See the included [📄 PDF report](./Final%20paper%20Movie%20Recommendation%20system%20using%20Machine%20Learning_220512_142548.pdf) for a detailed breakdown of the original methodology.

---

## 🎯 Technologies Used

- **Python + Flask**
- **Natural Language Processing** (TF-IDF, Naive Bayes)
- **TMDb API**
- **HTML + Bootstrap + JS + AJAX**
- **Pickle + Pandas + Scikit-learn**
- **GitHub Pages** (for preloader)
- **Render** (deployment)

---

## 🔒 Security & Optimization

- TMDb API calls are **proxied through the backend** to prevent direct exposure of API keys.
- Uses a **`.env` file** for sensitive configurations.
- Includes a **loader page hosted on GitHub Pages** that redirects to Render app after ~6 seconds (cold start workaround).

---

## 📄 License & Use

© 2025 Vishnu Jagadeesan  
All rights reserved.

This project is a **closed academic prototype** and not open for redistribution or modification without permission.

### ❌ Restrictions

- No commercial use without approval
- No redistribution of code or design
- Not licensed for open-source contribution

---

## 📬 Contact

For academic collaboration or demo access, contact:

**Vishnu Jagadeesan**  
📧 [vishnujagadeesan10@gmail.com](mailto:vishnujagadeesan10@gmail.com)

---
