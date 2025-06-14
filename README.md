# 🤖 Rasa AI Chatbot for E-Commerce Platform

A Rasa-powered chatbot designed to enhance customer interaction and support within an AI-supported e-commerce platform. This chatbot provides real-time assistance, product recommendations based on user behavior, and handles common e-commerce tasks like tracking orders, managing the cart, and more.

---

## 📌 Overview / Genel Bakış

🇬🇧 This chatbot is a key component of a larger AI-supported e-commerce application. It integrates with backend services and leverages user behavior data (search history, favorites, cart, orders) to deliver personalized product recommendations and handle various customer service operations.

🇹🇷 Bu chatbot, yapay zeka destekli bir e-ticaret uygulamasının önemli bir bileşenidir. Arka uç servislerle entegre olur ve kullanıcı davranışlarını (arama geçmişi, favoriler, sepet, siparişler) analiz ederek kişiselleştirilmiş ürün önerileri sunar; aynı zamanda müşteri hizmetleri süreçlerini yönetir.

---

## 🚀 Features / Özellikler

- 💬 **Doğal Dil Anlama (NLU)** – Türkçe ve İngilizce destekli  
- 📦 **Akıllı Ürün Sorgulama ve Öneriler** – Arama geçmişi/sepet üzerinden  
- 📋 **Sepet ve Sipariş Yönetimi Diyalogları**  
- 🤝 **Özel Aksiyonlar** – REST API ile backend'e bağlanır  
- ⏱ **Bağlama Duyarlı Diyaloglar** – Önceki niyetleri hatırlama  
- ⚙️ **Modüler Domain Yapısı** – Niyetler, varlıklar, formlar, slotlar  

---

## 🧱 Tech Stack / Teknolojiler

| Katman         | Teknoloji                |
|----------------|--------------------------|
| NLU/NLG Engine | [Rasa 3.6.21](https://rasa.com) |
| Dil İşleme     | SpaCy / Regex + Özel Kurallar |
| Backend API    | Spring Boot REST         |
| Veritabanı     | PostgreSQL, Redis        |

---

## 📦 Full-Stack Repo

🔗 [https://github.com/barisbutun/Bitirme](https://github.com/barisbutun/Bitirme)

---

## 🛠️ How to Run / Nasıl Çalıştırılır

```bash
# 1. Proje klasörüne girin
cd rasa-ai-supported-ecommerce

# 2. Sanal ortam oluşturun ve etkinleştirin
python -m venv venv
source venv/bin/activate      # Windows için: venv\Scripts\activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Modeli eğitin
rasa train

# 5. API ile chatbot'u çalıştırın
rasa run --enable-api

# 6. Özel aksiyonları başlatın
rasa run actions
