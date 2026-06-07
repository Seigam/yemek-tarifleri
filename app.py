import os
import requests
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

# ----------------------------------------------------
# 1. Environment and Configuration Loading
# ----------------------------------------------------
# Load .env from parent directory (useful if running from within the subfolder)
parent_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(parent_env):
    load_dotenv(parent_env)
# Load .env from current directory
load_dotenv()

# Strapi Credentials
STRAPI_URL = os.getenv("STRAPI_URL", "https://yemek-tarifleri-yysj.onrender.com").rstrip("/")
STRAPI_TOKEN = os.getenv("STRAPI_API_TOKEN") or os.getenv("STRAPI_TOKEN", "")

# Page Configuration
st.set_page_config(
    page_title="Dünya Mutfakları Tarif Rehberi | World Recipes",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# 2. Styling (CSS Injection for Premium Aesthetics)
# ----------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Typography */
    html, body, [class*="css"], .stMarkdown, p, div, span, h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* Hero Banner Area */
    .hero-container {
        background: linear-gradient(135deg, #FF4B4B 0%, #FF8533 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 30px rgba(255, 75, 75, 0.15);
    }
    
    .hero-title {
        font-weight: 700;
        font-size: 2.8rem !important;
        margin: 0 !important;
        letter-spacing: -0.5px;
        color: white !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .hero-subtitle {
        font-weight: 300;
        font-size: 1.25rem !important;
        margin-top: 0.75rem !important;
        opacity: 0.95;
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Recipe Card Wrapper (Native Streamlit Column Styling) */
    .recipe-card-box {
        background-color: #ffffff;
        border-radius: 16px;
        border: 1px solid #eef2f6;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .recipe-card-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(255, 75, 75, 0.12);
        border-color: rgba(255, 133, 51, 0.4);
    }
    
    /* Badges & Tags */
    .badge-row {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
        margin: 0.5rem 0 1rem 0;
    }
    
    .badge-cuisine {
        background: #FFF0E6;
        color: #FF6600;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-rating {
        background: #E8F5E9;
        color: #2E7D32;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-date {
        background: #F0F4F8;
        color: #4A5568;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
    }

    /* Dark Mode overrides via Media Query */
    @media (prefers-color-scheme: dark) {
        .recipe-card-box {
            background-color: #18191f;
            border-color: #2a2c35;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        .recipe-card-box:hover {
            box-shadow: 0 12px 30px rgba(255, 75, 75, 0.2);
            border-color: rgba(255, 133, 51, 0.6);
        }
        .badge-cuisine {
            background: #2c1d11;
            color: #ff9955;
        }
        .badge-rating {
            background: #122c15;
            color: #81c784;
        }
        .badge-date {
            background: #232731;
            color: #cbd5e0;
        }
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. Multilingual Translations Dictionary
# ----------------------------------------------------
TRANSLATIONS = {
    "tr": {
        "title": "Dünya Mutfakları Tarif Rehberi",
        "subtitle": "Yapay zeka görselleri ve nefis tariflerle mutfak yolculuğu",
        "lang_select": "Dil Seçimi / Language Selection",
        "cuisine_select": "Mutfak Seçimi",
        "all_cuisines": "Tümü",
        "search_placeholder": "Tarif adı veya malzeme ara...",
        "rating_filter": "Minimum Puan (Filtre)",
        "recipes_found": "tarif listelendi.",
        "no_recipes": "Aradığınız kriterlere uygun tarif bulunamadı.",
        "ingredients": "Malzemeler",
        "directions": "Yapılış Adımları",
        "expand_btn": "Tarif Detayını Göster",
        "refresh_btn": "Verileri Güncelle",
        "rating": "Puan",
        "date_added": "Ekleme",
        "dev_console": "Geliştirici Konsolu",
        "api_status": "API Durumu",
        "token_status": "Token Durumu",
        "active": "Aktif",
        "inactive": "Pasif",
        "connected": "Bağlandı",
        "disconnected": "Bağlantı Yok",
        "cuisine_fallback": "Türk Mutfağı"
    },
    "en": {
        "title": "World Flavors Recipe Guide",
        "subtitle": "A culinary journey with AI-generated visuals & delicious recipes",
        "lang_select": "Dil Seçimi / Language Selection",
        "cuisine_select": "Cuisine",
        "all_cuisines": "All",
        "search_placeholder": "Search by title or ingredients...",
        "rating_filter": "Minimum Rating",
        "recipes_found": "recipes found.",
        "no_recipes": "No recipes found matching your criteria.",
        "ingredients": "Ingredients",
        "directions": "Directions / Steps",
        "expand_btn": "Show Full Recipe",
        "refresh_btn": "Refresh Data",
        "rating": "Rating",
        "date_added": "Added",
        "dev_console": "Developer Console",
        "api_status": "API Status",
        "token_status": "Token Status",
        "active": "Active",
        "inactive": "Inactive",
        "connected": "Connected",
        "disconnected": "Disconnected",
        "cuisine_fallback": "Turkish Cuisine"
    }
}

CUISINE_MAP = {
    "Türk Mutfağı": "Turkish Cuisine",
    "İtalyan Mutfağı": "Italian Cuisine",
    "Fransız Mutfağı": "French Cuisine",
    "Meksika Mutfağı": "Mexican Cuisine",
    "Çin Mutfağı": "Chinese Cuisine",
    "Hint Mutfağı": "Indian Cuisine",
    "Japon Mutfağı": "Japanese Cuisine"
}

# ----------------------------------------------------
# 4. Helper Functions
# ----------------------------------------------------
def get_headers():
    headers = {}
    if STRAPI_TOKEN:
        headers["Authorization"] = f"Bearer {STRAPI_TOKEN}"
    return headers

def extract_text_from_blocks(blocks):
    if not blocks:
        return ""
    if isinstance(blocks, str):
        return blocks
    
    text = ""
    for block in blocks:
        if isinstance(block, dict) and block.get("type") == "paragraph":
            for child in block.get("children", []):
                text += child.get("text", "")
            text += "\n"
    return text.strip()

def format_date(date_str):
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return dt.strftime("%d.%m.%Y")
    except:
        return date_str

# ----------------------------------------------------
# 5. Data Fetching with Cache & English Fallback
# ----------------------------------------------------
@st.cache_data(ttl=120)
def fetch_raw_recipes(locale):
    try:
        # Fetching published entries with populate=* to get media and relation fields
        url = f"{STRAPI_URL}/api/recipes?locale={locale}&populate=*&pagination[limit]=100"
        res = requests.get(url, headers=get_headers(), timeout=15)
        if res.status_code == 200:
            return res.json().get("data", [])
        else:
            st.sidebar.error(f"Strapi API HTTP {res.status_code}")
    except Exception as e:
        st.sidebar.error(f"API Connection Error: {e}")
    return []

@st.cache_data(ttl=120)
def fetch_raw_cuisines():
    try:
        url = f"{STRAPI_URL}/api/cuisines?locale=tr&populate=*&pagination[limit]=100"
        res = requests.get(url, headers=get_headers(), timeout=15)
        if res.status_code == 200:
            return res.json().get("data", [])
    except Exception as e:
        pass
    return []

def get_recipes(locale):
    # Fetch TR recipes to build the fallback map (since Turkish contains complete info)
    tr_recipes = fetch_raw_recipes("tr")
    
    tr_map = {}
    for r in tr_recipes:
        doc_id = r.get("documentId")
        if doc_id:
            tr_map[doc_id] = r
            
    if locale == "tr":
        return tr_recipes
        
    # If English, fetch EN recipes and fallback to TR properties if empty
    en_recipes = fetch_raw_recipes("en")
    enriched_recipes = []
    
    for r in en_recipes:
        doc_id = r.get("documentId")
        tr_counterpart = tr_map.get(doc_id) if doc_id else None
        
        # Fallback Image
        if not r.get("KapakResmi") and tr_counterpart:
            r["KapakResmi"] = tr_counterpart.get("KapakResmi")
            
        # Fallback Puan
        if (r.get("Puan") is None or r.get("Puan") == "") and tr_counterpart:
            r["Puan"] = tr_counterpart.get("Puan")
            
        # Fallback cuisines
        if not r.get("cuisines") and tr_counterpart:
            r["cuisines"] = tr_counterpart.get("cuisines")
            
        # Fallback dates if missing
        if tr_counterpart:
            if not r.get("createdAt"):
                r["createdAt"] = tr_counterpart.get("createdAt")
            if not r.get("updatedAt"):
                r["updatedAt"] = tr_counterpart.get("updatedAt")
                
        enriched_recipes.append(r)
        
    return enriched_recipes

# ----------------------------------------------------
# 6. Sidebar Controls
# ----------------------------------------------------
with st.sidebar:
    # App Logo / Title
    st.markdown("<h2 style='text-align: center; color: #FF5A36;'>🍽️ Yemek Dünyası</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 1. Language Toggle
    st.subheader("🌐 Dil / Language")
    lang_selection = st.radio(
        "Select language:",
        options=["Türkçe (TR)", "English (EN)"],
        label_visibility="collapsed"
    )
    locale = "en" if "EN" in lang_selection else "tr"
    t = TRANSLATIONS[locale]
    
    st.markdown("---")
    
    # 2. Cuisine Selector
    st.subheader(f"🍲 {t['cuisine_select']}")
    raw_cuisines = fetch_raw_cuisines()
    
    # Build cuisine options mapping ID -> Name
    cuisine_options = {t["all_cuisines"]: None}
    for c in raw_cuisines:
        name_tr = c.get("Ad", "Bilinmeyen")
        # Map to English if locale is EN
        display_name = CUISINE_MAP.get(name_tr, name_tr) if locale == "en" else name_tr
        cuisine_options[display_name] = c.get("id")
        
    selected_cuisine_name = st.selectbox(
        "Select cuisine:",
        options=list(cuisine_options.keys()),
        label_visibility="collapsed"
    )
    selected_cuisine_id = cuisine_options[selected_cuisine_name]
    
    # 3. Rating Slider
    st.subheader(f"⭐ {t['rating_filter']}")
    min_rating = st.slider("Min rating", min_value=0.0, max_value=10.0, value=0.0, step=0.5, label_visibility="collapsed")
    
    # 4. Refresh Button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(f"🔄 {t['refresh_btn']}", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # 5. Developer Debug Console
    with st.expander(f"🛠️ {t['dev_console']}", expanded=False):
        st.markdown(f"**URL:** `{STRAPI_URL}`")
        st.markdown(f"**Token:** `{'***' + STRAPI_TOKEN[-8:] if STRAPI_TOKEN else t['inactive']}`")
        
        # Test connection
        conn_status = t['disconnected']
        try:
            test_res = requests.get(f"{STRAPI_URL}/api/recipes?pagination[limit]=1", headers=get_headers(), timeout=5)
            if test_res.status_code == 200:
                conn_status = f"🟢 {t['connected']} (HTTP 200)"
            else:
                conn_status = f"🔴 HTTP {test_res.status_code}"
        except Exception as e:
            conn_status = f"🔴 {t['disconnected']}: {str(e)[:40]}..."
            
        st.markdown(f"**{t['api_status']}:** {conn_status}")

# ----------------------------------------------------
# 7. Main View Design
# ----------------------------------------------------
# Hero Header Banner
st.markdown(f"""
<div class="hero-container">
    <h1 class="hero-title">🍽️ {t['title']}</h1>
    <p class="hero-subtitle">{t['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

# Search Bar
search_query = st.text_input("Search", placeholder=t["search_placeholder"], label_visibility="collapsed")

# Fetch and enrich recipes
recipes = get_recipes(locale)

# Apply Filters
filtered_recipes = []
for r in recipes:
    # 1. Title or ingredients text search match
    title = r.get("TarifAdi", "").lower()
    materials = extract_text_from_blocks(r.get("Malzemeler", [])).lower()
    
    if search_query and (search_query.lower() not in title and search_query.lower() not in materials):
        continue
        
    # 2. Rating match
    rating = r.get("Puan")
    rating_val = float(rating) if rating is not None else 0.0
    if rating_val < min_rating:
        continue
        
    # 3. Cuisine match
    if selected_cuisine_id is not None:
        cuisines_list = r.get("cuisines", [])
        if isinstance(cuisines_list, list):
            c_ids = [c.get("id") for c in cuisines_list if isinstance(c, dict)]
        elif isinstance(cuisines_list, dict):
            c_ids = [cuisines_list.get("id")]
        else:
            c_ids = []
            
        if selected_cuisine_id not in c_ids:
            continue
            
    filtered_recipes.append(r)

# Display result summary
st.markdown(f"**{len(filtered_recipes)}** {t['recipes_found']}")

# ----------------------------------------------------
# 8. Recipe Grid Layout
# ----------------------------------------------------
if not filtered_recipes:
    st.info(t["no_recipes"])
else:
    # 3 columns responsive grid
    cols = st.columns(3)
    
    for idx, recipe in enumerate(filtered_recipes):
        col = cols[idx % 3]
        
        with col:
            # Build wrapper card container using custom HTML class
            st.markdown('<div class="recipe-card-box">', unsafe_allow_html=True)
            
            # Card Header Badge (Cuisine name)
            cuisines = recipe.get("cuisines", [])
            cuisine_name = ""
            if isinstance(cuisines, list) and len(cuisines) > 0:
                cuisine_name_tr = cuisines[0].get("Ad", "")
                cuisine_name = CUISINE_MAP.get(cuisine_name_tr, cuisine_name_tr) if locale == "en" else cuisine_name_tr
            else:
                cuisine_name = t["cuisine_fallback"]
                
            st.markdown(f'<span class="badge-cuisine">🍲 {cuisine_name}</span>', unsafe_allow_html=True)
            
            # Recipe Title
            st.markdown(f"### {recipe.get('TarifAdi', 'İsimsiz Tarif')}")
            
            # Cover Image
            media = recipe.get("KapakResmi")
            img_url = None
            if isinstance(media, dict) and media.get("url"):
                img_url = media.get("url")
            elif isinstance(media, dict) and media.get("data") and isinstance(media["data"], dict):
                img_url = media["data"].get("attributes", {}).get("url") or media["data"].get("url")
                
            if img_url:
                if not img_url.startswith("http"):
                    img_url = STRAPI_URL + img_url
            else:
                img_url = "https://images.unsplash.com/photo-1495521821757-a1efb6729352?auto=format&fit=crop&w=800&q=80"
                
            st.image(img_url, use_container_width=True)
            
            # Metadata Row (Rating & Date)
            rating = recipe.get("Puan")
            rating_str = f"★ {rating}/10" if rating else "★ -/10"
            date_str = format_date(recipe.get("createdAt", ""))
            
            st.markdown(f"""
            <div class="badge-row">
                <span class="badge-rating">{rating_str}</span>
                <span class="badge-date">📅 {t['date_added']}: {date_str}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Extract ingredients summary
            materials_str = extract_text_from_blocks(recipe.get("Malzemeler", []))
            directions_str = extract_text_from_blocks(recipe.get("Yapilis", []))
            
            summary = materials_str[:90] + "..." if len(materials_str) > 90 else materials_str
            st.markdown(f"**{t['ingredients']}:** {summary}")
            
            # Expander for Full recipe details
            with st.expander(t["expand_btn"]):
                st.markdown(f"### 📋 {t['ingredients']}")
                st.write(materials_str)
                st.markdown(f"### 🍳 {t['directions']}")
                st.write(directions_str)
                
            st.markdown('</div>', unsafe_allow_html=True)
