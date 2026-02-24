import streamlit as st
import sqlite3
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from geopy.geocoders import Nominatim

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

place_images = {
    "Red Fort": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Red_Fort_in_Delhi_03-2016.jpg",
    "Qutub Minar": "https://upload.wikimedia.org/wikipedia/commons/d/da/Qutub_Minar.jpg",
    "India Gate": "https://upload.wikimedia.org/wikipedia/commons/f/fc/India_Gate_in_New_Delhi.jpg",
    "Humayun's Tomb": "https://upload.wikimedia.org/wikipedia/commons/3/38/Humayun%27s_Tomb.jpg",
    "Lotus Temple": "https://upload.wikimedia.org/wikipedia/commons/f/fc/LotusDelhi.jpg",

    "Taj Mahal": "https://upload.wikimedia.org/wikipedia/commons/d/da/Taj-Mahal.jpg",
    "Agra Fort": "https://upload.wikimedia.org/wikipedia/commons/0/02/Agra_Fort.jpg",
    "Fatehpur Sikri": "https://upload.wikimedia.org/wikipedia/commons/1/12/Fatehpur_Sikri_Buland_Darwaza.jpg",

    "Amer Fort": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Amer_Fort.jpg",
    "Hawa Mahal (Palace of Winds)": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Hawa_Mahal.jpg",
    "City Palace": "https://upload.wikimedia.org/wikipedia/commons/5/5c/City_Palace_Jaipur.jpg",
    "Jantar Mantar": "https://upload.wikimedia.org/wikipedia/commons/7/79/Jantar_Mantar_Jaipur.jpg",

    "Charminar": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Charminar_Hyderabad.jpg",
    "Golconda Fort": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Golconda_Fort.jpg",
    "Ramoji Film City": "https://upload.wikimedia.org/wikipedia/commons/1/14/Ramoji_Film_City.jpg",
    "Hussain Sagar Lake": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Hussain_Sagar.jpg",

    "Lalbagh Botanical Garden": "https://upload.wikimedia.org/wikipedia/commons/2/23/Lalbagh_Glasshouse.jpg",
    "Bangalore Palace": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Bangalore_Palace.jpg",
    "Cubbon Park": "https://upload.wikimedia.org/wikipedia/commons/2/2b/Cubbon_Park.jpg",

    "Marina Beach": "https://upload.wikimedia.org/wikipedia/commons/5/57/Marina_Beach.jpg",
    "Fort St. George": "https://upload.wikimedia.org/wikipedia/commons/1/1e/Fort_St_George_Chennai.jpg",

    "Padmanabhaswamy Temple": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Padmanabhaswamy_Temple.jpg",
    "Kovalam Beach": "https://upload.wikimedia.org/wikipedia/commons/3/36/Kovalam_beach.jpg",

    "Araku Valley": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Araku_Valley.jpg",
    "Borra Caves": "https://upload.wikimedia.org/wikipedia/commons/2/21/Borra_Caves.jpg",

    "Golden Temple": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Golden_Temple.jpg",
    "Jallianwala Bagh": "https://upload.wikimedia.org/wikipedia/commons/3/31/Jallianwala_Bagh.jpg",

    "Gateway of India": "https://upload.wikimedia.org/wikipedia/commons/4/4c/Gateway_of_India.jpg",
    "Marine Drive": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Marine_Drive_Mumbai.jpg",
    "Juhu Beach": "https://upload.wikimedia.org/wikipedia/commons/5/58/Juhu_Beach.jpg",

    "Solang Valley": "https://upload.wikimedia.org/wikipedia/commons/2/2a/Solang_Valley.jpg",
    "Hadimba Devi Temple": "https://upload.wikimedia.org/wikipedia/commons/5/5f/Hadimba_Temple.jpg",

    "Pangong Lake": "https://upload.wikimedia.org/wikipedia/commons/0/0a/Pangong_Lake.jpg",
    "Shanti Stupa": "https://upload.wikimedia.org/wikipedia/commons/7/73/Shanti_Stupa_Leh.jpg",

    "The Ridge": "https://upload.wikimedia.org/wikipedia/commons/4/49/The_Ridge_Shimla.jpg",
    "Tea Gardens": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Munnar_Tea_Plantations.jpg",

    "Ooty Lake": "https://upload.wikimedia.org/wikipedia/commons/d/d5/Ooty_Lake.jpg",
    "City Palace": "https://upload.wikimedia.org/wikipedia/commons/6/6d/City_Palace_Udaipur.jpg",

    "Mysore Palace": "https://upload.wikimedia.org/wikipedia/commons/a/a4/Mysore_Palace.jpg",
    "Backwaters Houseboat Cruise": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Alleppey_Backwaters.jpg",
    "Fort Kochi": "https://upload.wikimedia.org/wikipedia/commons/4/4f/Fort_Kochi.jpg",
}
place_images = {k.strip().lower(): v for k, v in place_images.items()}

st.set_page_config(
    page_title="Bharat Yatra Sahayak",
    page_icon="🧳",
    layout="wide"
)
# --- 1. DATABASE REPAIR & INITIALIZATION ---
def init_db():

    conn = sqlite3.connect('bharat_yatra.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS tourist_places (id INTEGER PRIMARY KEY, city TEXT, place TEXT, category TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS flights (id INTEGER PRIMARY KEY, origin TEXT, destination TEXT, airline TEXT, price TEXT, link TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS hotels (id INTEGER PRIMARY KEY, city TEXT, name TEXT, price TEXT, rating TEXT, link TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS transport (id INTEGER PRIMARY KEY, type TEXT, provider TEXT, base_price TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, city TEXT, user_name TEXT, comment TEXT, rating INTEGER)')
    #users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
    )
    """ )
    cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT,
    amount INTEGER,
    method TEXT,
    transaction_id TEXT,
    status TEXT,
    date TEXT
)
""")

    
    # SELF-REPAIR: Automatically add 'link' column if it's missing from an old database
    try:
        cursor.execute("SELECT link FROM flights LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE flights ADD COLUMN link TEXT")
    try:
        cursor.execute("SELECT link FROM hotels LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE hotels ADD COLUMN link TEXT")
        
    conn.commit()
    conn.close()
init_db()
conn = sqlite3.connect('bharat_yatra.db')
if not st.session_state.logged_in:
    st.title("Tourist Login")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM users WHERE email=? AND password=?",
                (email, password)
            )
            user = cur.fetchone()

            if user:
                st.session_state.logged_in = True
                st.session_state.user_name = user[0]
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        name = st.text_input("Name")
        email_r = st.text_input("Email", key="reg_email")
        pass_r = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Register"):
            try:
                conn.execute(
                    "INSERT INTO users (name, email, password) VALUES (?,?,?)",
                    (name, email_r, pass_r)
                )
                conn.commit()
                st.success("Account created! Please login.")
            except:
                st.error("Email already exists")

    st.stop()


# --- 2. MULTILINGUAL SETUP ---
translations = {
    "English": {"nav_dash": "🏠 Dashboard", "nav_book": "✈️ Bookings", "nav_trans": "🚗 Transport", "nav_tour": "🗺️ Tourist Places","nav_food": "🍽️ Food Booking", "nav_pay": "💳 Payment", "nav_rev": "💬 Reviews", "nav_admin": "⚙️ Admin"},
    "Hindi": {"nav_dash": "🏠 डैशबोर्ड", "nav_book": "✈️ बुकिंग", "nav_trans": "🚗 परिवहन", "nav_tour": "🗺️ पर्यटन स्थल", "nav_food": "🍽️ खाना बुकिंग", "nav_pay": "💳 भुगतान", "nav_rev": "💬 समीक्षा", "nav_admin": "⚙️ एडमिन"},
    "Telugu": {"nav_dash": "🏠 డాష్‌బోర్డ్", "nav_book": "✈️ బుకింగ్స్", "nav_trans": "🚗 రవాణా", "nav_tour": "🗺️ పర్యాటక ప్రదేశాలు", 	"nav_food":"🍽️ ఆహార బుకింగ్", 	"nav_pay":"💳 పేమెంట్", "nav_rev": 	"💬 సమీక్షలు", 	"nav_admin":"⚙️ అడ్మిన్"}
}



    

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    lang = st.selectbox("Language / भाषा / భాష", ["English", "Hindi", "Telugu"])
    t = translations[lang]
    st.title("Menu")
    choice = st.radio("Navigate to:", [t["nav_dash"], t["nav_book"], t["nav_trans"], t["nav_tour"], t["nav_food"], t["nav_pay"], t["nav_rev"], t["nav_admin"]])
    st.sidebar.success(f"Welcome {st.session_state.user_name}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()


conn = sqlite3.connect('bharat_yatra.db')

# --- 4. DASHBOARD (Fixed Blank Screen) ---


if choice == t["nav_dash"]:
    st.title("🇮🇳 Bharat Yatra Sahayak")
    st.caption("Smart Travel Assistance System for Tourists")

    st.divider()

    st.subheader("📍 Live GPS Tracking")

    location = get_geolocation()

    # fallback location
    lat, lon = 17.3850, 78.4867
    city = "Hyderabad"

    if location:
        lat = location['coords']['latitude']
        lon = location['coords']['longitude']

        try:
            geolocator = Nominatim(user_agent="bharat_yatra_app")
            loc = geolocator.reverse((lat, lon), language="en", timeout=20)

            if loc and "address" in loc.raw:
                address = loc.raw["address"]
                city = address.get("city") or address.get("town") or address.get("state")

        except:
            pass


    st.success(f"📍 You are in {city}")
    st.divider()

    # Quick actions
    st.subheader("Explore Options")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🗺️ Tourist Places"):
            st.session_state.page = t["nav_tour"]
            st.rerun()

    with c2:
        if st.button("🏨 Hotels"):
            st.session_state.page = t["nav_book"]
            st.rerun()

    with c3:
        if st.button("✈️ Flights"):
            st.session_state.page = t["nav_book"]
            st.rerun()
    st.divider()


    # Map
    st.subheader("Live Location Map")

    m = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker([lat, lon], popup="You are here").add_to(m)
    st_folium(m, width=700, height=400)


    # Tourist places section
    st.subheader(f"🗺️ Tourist Places in {city}")

    places_df = pd.read_sql(
        "SELECT place, category FROM tourist_places WHERE city COLLATE NOCASE = ?",
        conn,
        params=(city,)
    )

    if not places_df.empty:
        cols = st.columns(2)
        for i, (_, row) in enumerate(places_df.iterrows()):
            with cols[i % 2]:
                st.markdown(
                    f"""
                    <div style="background:#111827;padding:15px;border-radius:12px;margin-bottom:12px;border:1px solid #1f2937;">
                        <h4>📍 {row['place']}</h4>
                        <p style="color:#9ca3af;">{row['category']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info(f"No tourist places found for {city}.")


    st.header("About Bharat Yatra Sahayak")
    st.write("""
    Bharat Yatra Sahayak is a smart travel assistance web application designed to help
    tourists explore destinations, find transport, search hotels, and discover
    tourist places across India.
    """)

    st.info("Major Project • Streamlit • SQLite • Python")

# --- 5. BOOKINGS (Fixed Hotels & DeltaGenerator Error) ---
if choice == t["nav_book"]:
    st.header(t["nav_book"])
    tab1, tab2 = st.tabs(["✈️ Flights", "🏨 Hotels"])
    with tab1:
        c1, c2 = st.columns(2)
        org = c1.text_input("From")
        dst = c2.text_input("To")

        if st.button("Search Flights"):
            if org and dst:
                import urllib.parse

                org_enc = urllib.parse.quote(org)
                dst_enc = urllib.parse.quote(dst)

                makemytrip = f"https://www.makemytrip.com/flight/search?itinerary={org_enc}-{dst_enc}"
                goibibo = f"https://www.goibibo.com/flights/{org_enc}-to-{dst_enc}/"
                indigo = "https://www.goindigo.in/"

                st.subheader("Flight Booking Platforms")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.image("assets/makemytrip.png", width=120)
                    st.link_button("MakeMyTrip", makemytrip)

                with col2:
                    st.image("assets/goibibo.png", width=120)
                    st.link_button("Goibibo", goibibo)

                with col3:
                    st.image("assets/indigo.png", width=120)
                    st.link_button("IndiGo", indigo)
            else:
                st.warning("Enter origin and destination.")


    with tab2:
        h_city = st.text_input("Enter City for Hotels")

        if st.button("Find Hotels"):
            if h_city:
                import urllib.parse

                city_enc = urllib.parse.quote(h_city)

                makemytrip = f"https://www.makemytrip.com/hotels/{city_enc}-hotels.html"
                goibibo = f"https://www.goibibo.com/hotels/find-hotels-in-{city_enc}/"
                booking = f"https://www.booking.com/searchresults.html?ss={city_enc}"

                st.subheader("Hotel Booking Platforms")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.image("assets/makemytrip.png", width=120)
                    st.link_button("MakeMyTrip", makemytrip)

                with col2:
                    st.image("assets/goibibo.png", width=120)
                    st.link_button("Goibibo", goibibo)

                with col3:
                    st.image("assets/booking.png", width=120)
                    st.link_button("Booking.com", booking)
            else:
                st.warning("Enter a city.")


# --- 6. TRANSPORT (Fixed Blank Screen & Rapido Link) ---
if choice == t["nav_trans"]:
    st.header(t["nav_trans"])
    st.write("Book a quick ride to your destination.")
    v_type = st.selectbox("Vehicle", ["Bike", "Auto", "Cab"])
    p_up = st.text_input("📍 Pickup")
    drop = st.text_input("🏁 Drop")
    if st.button(f"Search {v_type}s"):
        if p_up and drop:
            st.success(f"Rides available! Redirecting to Rapido...")
            st.link_button("Book on Rapido", "https://www.rapido.bike/")
        else:
            st.warning("Please enter both pickup and drop locations.")

# --- 7. TOURIST PLACES (Implemented) ---
elif choice == t["nav_tour"]:
    st.header(t["nav_tour"])
    st.write("Find beautiful places to visit near you.")

    cities_df = pd.read_sql(
        "SELECT DISTINCT city FROM tourist_places ORDER BY city",
        conn
    )

    search_city = st.selectbox("Select City", cities_df["city"])

    df = pd.read_sql(
        "SELECT place, category FROM tourist_places WHERE city=?",
        conn,
        params=(search_city,)
    )
    if not df.empty:
        cols = st.columns(2)

        for i, (_, row) in enumerate(df.iterrows()):
            with cols[i % 2]:

                st.markdown(f"""
            <div style="
                background:#111827;
                padding:14px;
                border-radius:12px;
                border:1px solid #1f2937;
                margin-bottom:12px;
            ">
                <h4>📍 {row['place']}</h4>
                <p style="color:#9ca3af;">{row['category']}</p>
            </div>
            """, unsafe_allow_html=True)

            import urllib.parse
            query = urllib.parse.quote(row["place"] + " " + search_city)
            maps_link = f"https://www.google.com/maps/search/?api=1&query={query}"

            st.link_button("📍 View Photos & Reviews", maps_link)
            st.divider()




    else:
        st.warning(f"No places found for {search_city}.")
# --- FOOD BOOKING ---
elif choice == t["nav_food"]:
    st.header(t["nav_food"])

    city = st.text_input("Enter City for Food Delivery")

    if st.button("Search Restaurants"):
        if city:
            import urllib.parse
            city_enc = urllib.parse.quote(city)

            zomato = f"https://www.zomato.com/{city_enc}"
            swiggy = f"https://www.swiggy.com/city/{city_enc}"

            col1, col2 = st.columns(2)

            with col1:
                st.image("assets/zomato.png", width=120)
                st.link_button("Order on Zomato", zomato)

            with col2:
                st.image("assets/swiggy.png", width=120)
                st.link_button("Order on Swiggy", swiggy)
        else:
            st.warning("Please enter a city.")


# --- PAYMENT GATEWAY ---
if choice == t["nav_pay"]:
    import random
    import string
    import datetime
    import time
    st.header("💳 Secure UPI Payment")

    amount = st.number_input("Enter Amount (₹)", min_value=1)

    method = st.selectbox(
        "Select Payment Method",
        ["UPI - Google Pay", "UPI - PhonePe", "UPI - Paytm"]
    )

    if st.button("🔐 Pay Now", use_container_width=True):

        if amount > 0:

            with st.spinner("Processing Payment..."):
                time.sleep(2)

            txn_id = "BYS" + ''.join(random.choices(string.digits, k=8))
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn.execute(
                "INSERT INTO payments (user_name, amount, method, transaction_id, status, date) VALUES (?,?,?,?,?,?)",
                (
                    st.session_state.user_name,
                    amount,
                    method,
                    txn_id,
                    "Success",
                    date
                )
            )
            conn.commit()

            st.success("Payment Successful ✅")
            st.balloons()

            st.markdown(f"""
            ### 🧾 Payment Receipt
            - Transaction ID: {txn_id}
            - Amount: ₹{amount}
            - Method: {method}
            - Date: {date}
            """)

        else:
            st.warning("Enter valid amount.")

        st.divider()
        st.subheader("📜 Payment History")

        history = pd.read_sql(
            "SELECT amount, method, transaction_id, date FROM payments WHERE user_name=?",
            conn,
            params=(st.session_state.user_name,)
        )

        if not history.empty:
            st.dataframe(history)
        else:
            st.info("No transactions yet.")

# --- 8. REVIEWS (Fixed Blank Screen) ---
if choice == t["nav_rev"]:
    st.header(t["nav_rev"])
    with st.form("new_review"):
        r_city = st.text_input("City").capitalize()
        r_user = st.text_input("Your Name")
        r_comm = st.text_area("Experience")
        r_star = st.slider("Rating", 1, 5, 5)
        if st.form_submit_button("Post Review"):
            conn.execute("INSERT INTO reviews (city, user_name, comment, rating) VALUES (?,?,?,?)", (r_city, r_user, r_comm, r_star))
            conn.commit()
            st.success("Review Added!")
    
    st.divider()
    search_rev = st.text_input("View Reviews for City").capitalize()
    if search_rev:
        rdf = pd.read_sql(f"SELECT user_name, comment, rating FROM reviews WHERE city='{search_rev}'", conn)
        for i, r in rdf.iterrows():
            st.write(f"**{r['user_name']}** | {'⭐'*r['rating']}")
            st.info(r['comment'])

# --- 8. ADMIN PANEL (Access: admin123) ---
if choice == t["nav_admin"]:
    st.header("⚙️ Admin Dashboard")
    pw = st.text_input("Access Key", type="password")
    if pw == "admin123":
        action = st.selectbox("Action", ["Add Flight", "Add Hotel", "Add Tourist Place"])
        with st.form("admin_form"):
            if action == "Add Flight":
                f1, f2, f3, f4, f5 = st.text_input("Origin"), st.text_input("Dest"), st.text_input("Airline"), st.text_input("Price"), st.text_input("Link")
                if st.form_submit_button("Save Flight"):
                    conn.execute("INSERT INTO flights (origin, destination, airline, price, link) VALUES (?,?,?,?,?)", (f1.capitalize(), f2.capitalize(), f3, f4, f5))
                    conn.commit()
                    st.success("Saved!")
            
            elif action == "Add Hotel":
                h1, h2, h3, h4, h5 = st.text_input("City"), st.text_input("Hotel Name"), st.text_input("Price"), st.text_input("Rating"), st.text_input("Link")
                if st.form_submit_button("Save Hotel"):
                    conn.execute("INSERT INTO hotels (city, name, price, rating, link) VALUES (?,?,?,?,?)", (h1.capitalize(), h2, h3, h4, h5))
                    conn.commit()
                    st.success("Hotel Saved!")

            elif action == "Add Tourist Place":
                t1, t2, t3 = st.text_input("City"), st.text_input("Place Name"), st.selectbox("Category", ["Historical", "Nature", "Religious", "Adventure", "Shopping"])
                if st.form_submit_button("Save Place"):
                    conn.execute("INSERT INTO tourist_places (city, place, category) VALUES (?,?,?)", (t1.capitalize(), t2, t3))
                    conn.commit()
                    st.success("Place Added!")

    else:
        st.error("Invalid Access Key!")
import time

def animated_response(text):
    message_placeholder = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        message_placeholder.markdown(full_text)
        time.sleep(0.01)

if choice == "🤖 Chat Assistant":
    st.markdown("""
    <h2 style="display:flex;align-items:center;">
        ⭐ Tara – Your Travel Companion
    </h2>
    """, unsafe_allow_html=True)

    st.caption("Your smart guide for exploring India 🇮🇳")


    if "tara_initialized" not in st.session_state:
        st.session_state.messages = []
        if "tara_initialized" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Hello 👋 I’m Tara, your smart travel companion! Ask me about tourist places, hotels, flights, or authentic food."
            })
        st.session_state.tara_initialized = True
        

    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        msg = user_input.lower()
        response = ""

        # Detect tourist places
        cities = pd.read_sql("SELECT DISTINCT city FROM tourist_places", conn)["city"].tolist()

        detected_city = None
        for c in cities:
            if c.lower() in msg:
                detected_city = c
                break

        # TOURIST PLACES
        if "tourist" in msg or "places" in msg or "explore" in msg:
            if detected_city:
                df = pd.read_sql(
                    "SELECT place FROM tourist_places WHERE city=?",
                    conn,
                    params=(detected_city,)
                )
                places = ", ".join(df["place"].tolist())
                response = f"🗺 Tourist places in {detected_city}: {places}"
            else:
                response = "Please mention a city to explore."

        # HOTELS
        elif "hotel" in msg:
            if detected_city:
                import urllib.parse
                city_enc = urllib.parse.quote(detected_city)
                booking = f"https://www.booking.com/searchresults.html?ss={city_enc}"
                response = f"🏨 Hotels in {detected_city}:\n\n[Book on Booking.com]({booking})"
            else:
                response = "Please mention a city for hotels."

        # FLIGHTS
        elif "flight" in msg:
            words = msg.split()
            if "from" in words and "to" in words:
                try:
                    org = words[words.index("from")+1]
                    dst = words[words.index("to")+1]

                    import urllib.parse
                    org_enc = urllib.parse.quote(org)
                    dst_enc = urllib.parse.quote(dst)

                    makemytrip = f"https://www.makemytrip.com/flight/search?itinerary={org_enc}-{dst_enc}"

                    response = f"✈ Flights from {org.title()} to {dst.title()}:\n\n[Search on MakeMyTrip]({makemytrip})"
                except:
                    response = "Please use format: Flights from CityA to CityB"
            else:
                response = "Please use format: Flights from CityA to CityB"

        # FOOD
        elif "food" in msg or "famous food" in msg:
            food_df = pd.read_sql(
                "SELECT food_name FROM city_foods WHERE city=?",
                conn,
                params=(detected_city,)
            )
            if not food_df.empty:
                foods = ", ".join(food_df["food_name"].tolist())
                response = f"🍛 Authentic foods in {detected_city}: {foods}"
            else:
                response = "No food data available for this city."

        # GPS BASED SUGGESTION
        elif "near me" in msg or "here" in msg:
            gps_city = city  # from your dashboard GPS logic
            df = pd.read_sql(
                "SELECT place FROM tourist_places WHERE city COLLATE NOCASE = ?",
                conn,
                params=(gps_city,)
            )
            if not df.empty:
                places = ", ".join(df["place"].tolist())
                response = f"📍 You are in {gps_city}. You can explore: {places}"
            else:
                response = "No data found for your current location."

        else:
            response = "I can help with tourist places, hotels, flights, or food. Try asking about a city!"

        st.session_state.messages.append({"role": "assistant", "content": response})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

conn.close()
