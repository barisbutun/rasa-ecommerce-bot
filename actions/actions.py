from collections import defaultdict

import arrow
from rasa_sdk import Action, Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.interfaces import Tracker
from typing import Any, Dict, List, Text
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import jwt
import random


city_db = {

    'amsterdam': "Europe/Amsterdam"
    , 'istanbul': "Europe/Istanbul"
    , 'london': "Europe/London"
    , 'washington': "USA/Washington"

}

BACKEND_API_URL = "http://localhost:8082/api"
FRONTEND_API_URL = "http://192.168.30.16:3000"
api_key = ""

class ActionFallbackToGemini(Action):
    def name(self) -> Text:
        return "action_custom_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        import requests

        user_message = tracker.latest_message.get("text")


        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": user_message}
                    ]
                }
            ]
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=40)
            response.raise_for_status()
            data = response.json()
            content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

            if not content:
                content = "Üzgünüm, bu soruya şu anda bir yanıt veremiyorum."

        except requests.exceptions.Timeout:
            content = "Model şu anda yanıt veremiyor: Zaman aşımı oldu."
        except requests.exceptions.HTTPError as e:
            content = f"HTTP Hatası: {e.response.status_code} - {e.response.reason}"
        except Exception as e:
            content = f"Model şu anda yanıt veremiyor: {str(e)}"

        print(content)
        dispatcher.utter_message(text=content)
        return []


class Selamlama_Action(Action):
    def name(self):
        return "action_custom_selamlama"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        metadata=tracker.latest_message.get("metadata",{})
        token=metadata.get('Authorization')


        if not token:
            dispatcher.utter_message("Merhaba size nasıl yardımcı olabilirim")
            return []

        token = token.split(" ")[1]

        decoded_token = jwt.decode(token, options={"verify_signature": False})
        name = decoded_token.get("name")

        random_num=random.randint(1,3)
        if random_num==1:
            dispatcher.utter_message(f"Merhaba {name}! Sana nasıl yardımcı olabilirim")
        elif random_num==2:
            dispatcher.utter_message(f"Selam {name}! Yardımcı olabileceğim bir konu var mı?")
        else:
            dispatcher.utter_message(f"Hoş geldin {name}! Size nasıl yardımcı olabilirim bugün?")


        return []

'''class ActionSiparisDetayi(Action):
    def name(self) -> Text:
        return "action_siparis_detayi"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        siparis_no = tracker.get_slot("siparis_no")

        if not siparis_no:
            dispatcher.utter_message(text="Sipariş numaranızı anlayamadım. Lütfen tekrar eder misiniz?")
            return []

        metadata = tracker.latest_message.get("metadata", {})
        token = metadata.get("Authorization")

        if not token:
            dispatcher.utter_message(text="Yetkilendirme hatası! Token bulunamadı.")
            return []

        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        response = requests.get(f"http://localhost:8082/api/order/v1/{siparis_no}", headers=headers)


        if response.get('id')==siparis_no:
                state=response.get('delivery').get('delivery_state')
                match state:
                    case "PENDING":
                        dispatcher.utter_message("Siparişiniz hazırlık evresinde ortalama 2-3 gün içinde kargoya verilecektir")
                    case 'PROCESSING':
                        dispatcher.utter_message("Siparişiniz işleniyor ortalama 1-2 gün içinde kargoya verilecektir.")
                    case 'SHIPPED':
                        dispatcher.utter_message("Siparişiniz kargoya verilmiştir")
                    case 'IN_TRANSIT':
                        dispatcher.utter_message("Siparişiniz yola çıkmıştır")
                    case 'OUT_FOR_DELIVERY':
                        dispatcher.utter_message("Siparişiniz kurye dağıtımına çıkmıştır.Kargonuzu teslim alırken sms olarak gelen kodu kuryeye söyleyin.")
                    case 'DELIVERED':
                        dispatcher.utter_message("Siparişinizi teslim ettik iyi günlerde kullanın.")
                    case 'FAILED_DELIVERY':
                        dispatcher.utter_message("Sipatişinizle ilgili bir sorun oluştu")
                    case 'RETURNED':
                        dispatcher.utter_message("Siparişiniz iade sürecinde")
                    case 'CANCELLED':
                        dispatcher.utter_message("Siparişiniz iptal edildi")
                return[]

        dispatcher.utter_message("Sipariş numaranız bulunamadı")


        return []'''


class ActionSaatiSoyle(Action):
    def name(self):
        return "action_saati_soyle"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_place = next(tracker.get_latest_entity_values("city"), None)
        utc = arrow.now(city_db['istanbul'])

        if not current_place:
            msg = f"saat şu anda {utc.format('HH:mm')}. Özellikle bir şehir ismi belirtebilirsiniz."
            dispatcher.utter_message(text=msg)
            return []

        tz_string = city_db.get(current_place)

        if not tz_string:
            msg = f"'{current_place}' için saat bilgisi bulunamadı. Doğru yazdığınıza emin misiniz?"
            dispatcher.utter_message(text=msg)
            return []

        try:
            local_time = utc.to(tz_string).format('HH:mm')
            msg = f"Saat şu anda {current_place}'da {local_time}."
        except Exception as e:
            msg = f"Bir hata oluştu: {str(e)}"

        dispatcher.utter_message(text=msg)
        return []


class sepet_islemleri_urun_gosterme(Action):

    def name(self):
        return "sepet_islemleri_urun_gosterme"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[EventType]:
        metadata = tracker.latest_message.get("metadata", {})
        token = metadata.get("Authorization")

        if not token:
            dispatcher.utter_message(text="Yetkilendirme hatası! Token bulunamadı.")
            return []

        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        dispatcher.utter_message(
            text=f"Sepete gitmek için <a href='{FRONTEND_API_URL}/user/ShoppingCard'>tıklayın</a>")

        return []


class favori_islemleri_urun_gosterme(Action):

    def name(self):
        return "favori_islemleri_urun_gosterme"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[EventType]:
        metadata = tracker.latest_message.get("metadata", {})
        token = metadata.get("Authorization")

        if not token:
            dispatcher.utter_message(text="Yetkilendirme hatası! Token bulunamadı.")
            return []

        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

        dispatcher.utter_message(f"Favorilere gitmek için:<a href='{FRONTEND_API_URL}/user/Favorites'>tıklayın</a>")

        return []


class siparis_islemleri_urun_gosterme(Action):

    def name(self):
        return "siparis_islemleri_urun_gosterme"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[EventType]:
        metadata = tracker.latest_message.get("metadata", {})
        token = metadata.get("Authorization")

        if not token:
            dispatcher.utter_message(text="Yetkilendirme hatası! Token bulunamadı.")
            return []

        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

        dispatcher.utter_message(f"Siparişlere gitmek için:<a href='{FRONTEND_API_URL}/user/OrdersList'>tıklayın</a>")

        return []


class begenilen_urun_gosterme(Action):

    def name(self):
        return "begenilen_urun_gosterme"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[EventType]:

        metadata = tracker.latest_message.get("metadata", {})
        token = metadata.get("Authorization")

        if not token:
            dispatcher.utter_message(text="Yetkilendirme hatası! Token bulunamadı.")
            return []

        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

        try:
            response = requests.get("http://localhost:8082/api/product/top-rated", headers=headers)
            data = response.json()
            urunler = data.get("content", [])

            if not urunler:
                dispatcher.utter_message(text="Beğenilen ürün bulunmamaktadır.")
                return []

            urunler_np = np.array(urunler[:10])

            response_text = []

            for item in urunler_np:
                isim = item.get("name", "Ürün adı yok")
                id = item.get("id")
                aciklama = item.get("description", "Açıklama yok")
                fiyat = item.get("price", "Fiyat belirtilmemiş")
                puan = item.get("averageRating", "Puan yok")

                link = f"{FRONTEND_API_URL}/user/ProductDetails/{id}"
                image_url = f"http://localhost:8082/api/image/v1/{id}.jpg"

                response_text.append(
                    f"<div style='margin-bottom:20px;'>"
                    f"<img src='{image_url}' width='150'/><br>"
                    f"<b>{isim}</b><br>"
                    f"{aciklama}<br>"
                    f"Fiyat: {fiyat} ₺<br>"
                    f"Ortalama Puan: {puan}<br>"
                    f"<a href='{link}'>Ürüne Git</a>"
                    f"</div>"
                )

            response_text_str = ''.join(response_text)
            dispatcher.utter_message(response_text_str)

        except Exception as e:
            dispatcher.utter_message(text="API çağrısı başarısız oldu!")

        return []


class benzer_urun(Action):
    def name(self):
        return "actions_benzer_urun"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[EventType]:

        metadata = tracker.latest_message.get("metadata", {})
        token = metadata.get("Authorization")

        if not token:
            dispatcher.utter_message(text="Yetkilendirme hatası! Token bulunamadı.")
            return []

        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

        try:
            response_category = requests.get("http://localhost:8082/api/categories/v1")
            category_list = response_category.json()
            priority_words_cat = {cat['name'].lower(): 3 for cat in category_list}
            priority_colors = {"kırmızı", "kahverengi", "sarı", "yeşil", "mor", "siyah", "lacivert", "haki", "turuncu",
                               "mavi", "turkuaz","beyaz"}

            turkish_stop_words = [
                "ve", "fakat", "ya", "ile", "bu", "bir", "ama", "çok", "da", "de", "ki", "mi","hem",
                "ben", "sen", "o", "biz", "siz", "onlar", "istiyorum", "almak", "etmek", "için", "gibi", "daha", "en"
            ]

            response = requests.get("http://localhost:8082/api/chatbot/v1/recommend", headers=headers)
            response_all_products = requests.get("http://localhost:8082/api/product/v1/all")

            data_all_products = response_all_products.json()
            data = response.json()

            items_sources = [
                ("shoppingCartItems", 3),
                ("orders", 4),
                ("favourites", 2),
                ("reviews", 2)
            ]

            product_scores = defaultdict(float)
            product_names = {}

            def calculate_weighted_similarity(desc1, desc2, source_weight, same_count=0):
                merge = [desc1, desc2]
                vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words=turkish_stop_words)
                tfidf_matrix = vectorizer.fit_transform(merge)

                vec1 = tfidf_matrix[0].toarray()
                vec2 = tfidf_matrix[1].toarray()

                base_weight = 1.0
                if any(cat in desc1 for cat in priority_words_cat.keys()):
                    base_weight *= 3.0
                if any(color in desc1 for color in priority_colors):
                    base_weight *= 2.0

                if same_count > 0:
                    base_weight += same_count * 0.1

                vec1 *= base_weight
                vec2 *= base_weight

                cosine = cosine_similarity(vec1, vec2)[0][0]
                return cosine * source_weight

            for product in data_all_products:
                prod_id = product['id']
                product_desc = product['description'].lower()
                product_names[prod_id] = product['name']

                for source_key, weight in items_sources:
                    items = data.get(source_key, [])
                    for item in items:
                        if prod_id == item.get('id'):
                            continue
                        item_desc = item['description'].lower()
                        same_count = item.get("same_count", 0)
                        score = calculate_weighted_similarity(product_desc, item_desc, weight, same_count)
                        print(score)

                        if score > 0.5:
                            product_scores[prod_id] += score

            benzer_urunler = [
                {"id": pid, "name": product_names[pid], "score": round(score, 2)}
                for pid, score in product_scores.items()

            ]

            if not benzer_urunler:
                dispatcher.utter_message("Ürün bulunamadı.")
            else:
                order_score = np.array([urun["score"] for urun in benzer_urunler])
                sorted_indices = np.argsort(order_score)[::-1]
                benzer_urunler = [benzer_urunler[i] for i in sorted_indices]
                benzer_urunler = [urun for urun in benzer_urunler if urun["score"] > 0]
                benzer_urunler = benzer_urunler[:4]

                response_text = [f"Sizin için özel olarak oluşturduğumuz ürünler:"]
                for urun in benzer_urunler:
                    isim = urun.get("name", "Ürün adı yok")
                    id = urun.get("id")
                    benzerlik = urun.get("score", 0)
                    link = f"{FRONTEND_API_URL}/user/ProductDetails/{id}"
                    image_url = f"http://localhost:8082/api/image/v1/{id}.jpg"
                    response_text.append(
                        f"<img src='{image_url}' width='150'/><br>"
                        f"<p>{isim}<br>"
                        f"<a href='{link}'>Ürüne git</a></p>"
                        f"<br><br>"

                    )

                response_text_str = ''.join(response_text)
                dispatcher.utter_message(response_text_str)

            return []

        except Exception as e:
            dispatcher.utter_message(text=f"Hata oluştu: {str(e)}")
            return []
