import sqlite3
import pandas as pd
from io import StringIO

data = """City,Top Tourist Places
New Delhi,"Red Fort, Qutub Minar, India Gate, Humayun's Tomb, Lotus Temple"
Agra,"Taj Mahal, Agra Fort, Fatehpur Sikri, Mehtab Bagh"
Jaipur,"Amer Fort, Hawa Mahal (Palace of Winds), City Palace, Jantar Mantar"
Hyderabad,"Charminar, Golconda Fort, Ramoji Film City, Hussain Sagar Lake"
Banglore,"Lalbagh Botanical Garden, Bangalore Palace, Cubbon Park, Bannerghatta National Park"
Chennai,"Marina Beach, Fort St. George, Kapaleeshwarar Temple, Santhome Cathedral"
Trivandrum,"Padmanabhaswamy Temple, Kovalam Beach, Napier Museum, Veli Tourist Village"
Vishakhapatnam,"Rama Krishna Beach, Araku Valley, Kailasagiri, Borra Caves"
Varanasi,"Kashi Vishwanath Temple, Dashashwamedh Ghat (Ganga Aarti), Sarnath"
Amritsar,"Golden Temple, Wagah Border, Jallianwala Bagh"
Rishikesh,"Laxman Jhula, Triveni Ghat, Beatles Ashram, Parmarth Niketan"
Ayodhya,"Ram Mandir, Hanuman Garhi, Sarayu River Ghats"
North Goa,"Baga Beach, Calangute Beach, Fort Aguada, Anjuna Flea Market"
South Goa,"Palolem Beach, Colva Beach, Dudhsagar Falls, Old Goa Churches"
Pondicherry,"White Town (French Quarter), Auroville, Promenade Beach"
Mumbai,"Gateway of India, Marine Drive, Elephanta Caves, Juhu Beach"
North Goa,"Baga Beach, Calangute Beach, Fort Aguada, Anjuna Flea Market"
South Goa,"Palolem Beach, Colva Beach, Dudhsagar Falls, Old Goa Churches"
Pondicherry,"White Town (French Quarter), Auroville, Promenade Beach"
Mumbai,"Gateway of India, Marine Drive, Elephanta Caves, Juhu Beach"
Manali,"Rohtang Pass, Solang Valley, Hadimba Devi Temple, Old Manali"
Leh (Ladakh),"Pangong Lake, Nubra Valley, Shanti Stupa, Khardung La Pass"
Shimla,"The Ridge, Mall Road, Jakhoo Temple, Kufri"
Munnar,"Tea Gardens, Eravikulam National Park, Mattupetty Dam"
Ooty,"Ooty Lake, Botanical Garden, Doddabetta Peak, Toy Train"
Udaipur,"City Palace, Lake Pichola (Boat Ride), Jag Mandir, Saheliyon-ki-Bari"
Mysore,"Mysore Palace, Chamundi Hill, Brindavan Gardens"
Alleppey,"Backwaters Houseboat Cruise, Marari Beach, Pathiramanal Island"
Kochi,"Fort Kochi, Chinese Fishing Nets, Mattancherry Palace"
"""

def infer_category(place_name):
    p = place_name.lower()
    if any(x in p for x in ['fort', 'palace', 'tomb', 'temple', 'church', 'mandir', 'ashram', 'stupa', 'historic', 'gate', 'minar']):
        return "Historical"
    elif any(x in p for x in ['beach', 'lake', 'falls', 'river', 'garden', 'park', 'valley', 'pass', 'peak', 'hill', 'dam']):
        return "Nature"
    elif any(x in p for x in ['market', 'mall', 'bazaar']):
        return "Shopping"
    elif any(x in p for x in ['adventure', 'trek', 'ride']):
        return "Adventure"
    return "Tourist Attraction"

def seed_db():
    # Clean up data: remove empty lines and repeated headers
    lines = [line for line in data.split('\n') if line.strip() and not line.startswith('City')]
    # Reassemble consistent CSV for easier manual parsing or pandas
    # Actually, simpler to just parse line by line since it is CSV-like
    
    conn = sqlite3.connect('bharat_yatra.db')
    cursor = conn.cursor()
    
    count = 0
    import csv
    reader = csv.reader(lines)
    
    for row in reader:
        if not row: continue
        city = row[0].strip()
        if city == 'City': continue # Skip header if it slipped through
            
        places_str = row[1]
        # Split places by comma
        places = [p.strip() for p in places_str.split(',')]
        
        for place in places:
            if not place: continue
            category = infer_category(place)
            
            # Check if exists to avoid duplicates
            cursor.execute("SELECT id FROM tourist_places WHERE city=? AND place=?", (city, place))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO tourist_places (city, place, category) VALUES (?, ?, ?)", (city, place, category))
                count += 1
                print(f"Added: {city} - {place} ({category})")
    
    conn.commit()
    conn.close()
    print(f"Successfully added {count} tourist places.")

if __name__ == "__main__":
    seed_db()
