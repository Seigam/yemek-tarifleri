import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

STRAPI_URL = os.getenv("STRAPI_URL", "http://localhost:1337")
STRAPI_TOKEN = os.getenv("STRAPI_TOKEN", "") 

# Streamlit sayfası genel yapılandırması
st.set_page_config(page_title="Dünya Mutfakları Tarif Rehberi", page_icon="🍽️", layout="wide")

def get_headers():
    headers = {}
    if STRAPI_TOKEN:
        headers["Authorization"] = f"Bearer {STRAPI_TOKEN}"
    return headers

def fetch_cuisines(locale="tr"):
    try:
        url = f"{STRAPI_URL}/api/cuisines?locale={locale}"
        res = requests.get(url, headers=get_headers(), timeout=10)
        if res.status_code == 200:
            return res.json().get("data", [])
    except Exception as e:
        st.sidebar.error(f"Mutfaklar çekilirken hata oluştu: {e}")
    return []

def fetch_recipes(cuisine_id=None, locale="tr"):
    try:
        url = f"{STRAPI_URL}/api/recipes?populate=KapakResmi&locale={locale}"
        if cuisine_id:
            url += f"&filters[Cuisine][id][$eq]={cuisine_id}"
        res = requests.get(url, headers=get_headers(), timeout=10)
        if res.status_code == 200:
            return res.json().get("data", [])
    except Exception as e:
        st.error(f"Tarifler çekilirken hata oluştu: {e}")
    return []

# Arayüz Bileşenleri
st.title("🍽️ Dünya Mutfakları Tarif Rehberi")

# Sol Sidebar: Dil ve Mutfak Seçimi için ayrılmış alan
with st.sidebar:
    st.header("⚙️ Ayarlar / Settings")
    lang_selection = st.radio("Dil / Language", options=["Türkçe (TR)", "English (EN)"])
    locale = "en" if "EN" in lang_selection else "tr"
    
    st.subheader("🍲 Mutfak Seçimi / Cuisine")
    cuisines = fetch_cuisines(locale)
    
    cuisine_options = {"Tümü / All": None}
    for c in cuisines:
        cuisine_options[c["attributes"]["Ad"]] = c["id"]
        
    selected_cuisine_name = st.selectbox("Bir mutfak seçin / Select:", options=list(cuisine_options.keys()))
    selected_cuisine_id = cuisine_options[selected_cuisine_name]

# Ana Alan: Seçilen kriterlere uygun tariflerin listelendiği bölüm
st.subheader(f"📖 {selected_cuisine_name} Tarifleri")
recipes = fetch_recipes(selected_cuisine_id, locale)

if not recipes:
    st.info("Bu kriterlere uygun tarif bulunamadı. / No recipes found.")
else:
    # Tarifleri yan yana sütunlar (grid) halinde göstermek için 3'lü kolon yapısı
    cols = st.columns(3)
    
    for index, recipe in enumerate(recipes):
        attr = recipe.get("attributes", {})
        col = cols[index % 3]
        
        with col:
            st.markdown(f"### {attr.get('TarifAdi', 'İsimsiz Tarif')}")
            
            # Kapak Resmi Gösterimi
            media = attr.get("KapakResmi", {}).get("data")
            if media:
                img_url = media.get("attributes", {}).get("url", "")
                # Eğer URL tam yol (http ile) başlamıyorsa Strapi hostunu ekle
                if not img_url.startswith("http"):
                    img_url = STRAPI_URL + img_url
                st.image(img_url, use_container_width=True)
            else:
                st.image("https://via.placeholder.com/400x300?text=Gorsel+Yok", use_container_width=True)
            
            # Puan Değerinin Yıldız Sembolü İle Gösterimi
            st.markdown(f"**Puan:** ★ {attr.get('Puan', '-')}")
            
            # Malzemeler Özeti (İlk 100 karakter)
            malzemeler = attr.get('Malzemeler', '')
            ozet = malzemeler[:100] + "..." if len(malzemeler) > 100 else malzemeler
            st.markdown(f"**Malzemeler:** {ozet}")
            
            # Detaylar için Genişletilebilir Bölüm (Expander)
            with st.expander("Tam Yapılış / Detaylar"):
                st.markdown("**Tüm Malzemeler:**")
                st.write(malzemeler)
                st.markdown("**Yapılış:**")
                st.write(attr.get('Yapilis', ''))
