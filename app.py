from flask import Flask, render_template, request, jsonify
import random
import time
import requests
import urllib.parse

app = Flask(__name__)

# --- Mock ML Model Setup ---
# In a real scenario, you would load your model and vectorizer here:
# import pickle
# model = pickle.load(open('model/model.pkl', 'rb'))
# vectorizer = pickle.load(open('model/vectorizer.pkl', 'rb'))

MOODS = ['Happy', 'Sad', 'Angry', 'Relaxed', 'Excited', 'Romantic', 'Stressed']

MOCK_SONGS = {
    'Happy': [
        {'title': 'Walking on Sunshine', 'artist': 'Katrina & The Waves', 'genre': 'Pop', 'duration': '3:56', 'cover': 'https://placehold.co/100x100/FFD700/000?text=Happy'},
        {'title': 'Happy', 'artist': 'Pharrell Williams', 'genre': 'Pop', 'duration': '3:52', 'cover': 'https://placehold.co/100x100/FFD700/000?text=Happy'},
        {'title': 'Don\'t Stop Me Now', 'artist': 'Queen', 'genre': 'Rock', 'duration': '3:29', 'cover': 'https://placehold.co/100x100/FFD700/000?text=Happy'},
        {'title': 'Good Vibrations', 'artist': 'The Beach Boys', 'genre': 'Pop', 'duration': '3:35', 'cover': 'https://placehold.co/100x100/FFD700/000?text=Happy'},
        {'title': 'Uptown Funk', 'artist': 'Mark Ronson ft. Bruno Mars', 'genre': 'Funk', 'duration': '4:30', 'cover': 'https://placehold.co/100x100/FFD700/000?text=Happy'},
        {'title': 'I Gotta Feeling', 'artist': 'Black Eyed Peas', 'genre': 'Pop', 'duration': '4:49', 'cover': 'https://placehold.co/100x100/FFD700/000?text=Happy'},
        {'title': 'Levitating', 'artist': 'Dua Lipa', 'genre': 'Pop', 'duration': '3:23', 'cover': 'https://placehold.co/100x100/FFD700/000?text=Happy'},
        {'title': 'Can\'t Stop the Feeling!', 'artist': 'Justin Timberlake', 'genre': 'Pop', 'duration': '3:56', 'cover': 'https://placehold.co/100x100/FFD700/000?text=Happy'},
        {'title': 'Dancing Queen', 'artist': 'ABBA', 'genre': 'Pop', 'duration': '3:51', 'cover': 'https://placehold.co/100x100/FFD700/000?text=Happy'},
        {'title': 'Shake It Off', 'artist': 'Taylor Swift', 'genre': 'Pop', 'duration': '3:39', 'cover': 'https://placehold.co/100x100/FFD700/000?text=Happy'},
    ],
    'Sad': [
        {'title': 'Someone Like You', 'artist': 'Adele', 'genre': 'Pop', 'duration': '4:45', 'cover': 'https://placehold.co/100x100/0000FF/FFF?text=Sad'},
        {'title': 'Fix You', 'artist': 'Coldplay', 'genre': 'Alternative', 'duration': '4:55', 'cover': 'https://placehold.co/100x100/0000FF/FFF?text=Sad'},
        {'title': 'Let Her Go', 'artist': 'Passenger', 'genre': 'Folk', 'duration': '4:12', 'cover': 'https://placehold.co/100x100/0000FF/FFF?text=Sad'},
        {'title': 'Hurt', 'artist': 'Johnny Cash', 'genre': 'Country', 'duration': '3:38', 'cover': 'https://placehold.co/100x100/0000FF/FFF?text=Sad'},
        {'title': 'The Sound of Silence', 'artist': 'Simon & Garfunkel', 'genre': 'Folk', 'duration': '3:05', 'cover': 'https://placehold.co/100x100/0000FF/FFF?text=Sad'},
        {'title': 'Say Something', 'artist': 'A Great Big World', 'genre': 'Pop', 'duration': '3:49', 'cover': 'https://placehold.co/100x100/0000FF/FFF?text=Sad'},
        {'title': 'Creep', 'artist': 'Radiohead', 'genre': 'Alternative', 'duration': '3:55', 'cover': 'https://placehold.co/100x100/0000FF/FFF?text=Sad'},
        {'title': 'Skinny Love', 'artist': 'Bon Iver', 'genre': 'Indie', 'duration': '3:59', 'cover': 'https://placehold.co/100x100/0000FF/FFF?text=Sad'},
        {'title': 'Breathe Me', 'artist': 'Sia', 'genre': 'Pop', 'duration': '4:34', 'cover': 'https://placehold.co/100x100/0000FF/FFF?text=Sad'},
        {'title': 'Tears in Heaven', 'artist': 'Eric Clapton', 'genre': 'Rock', 'duration': '4:33', 'cover': 'https://placehold.co/100x100/0000FF/FFF?text=Sad'},
    ],
    'Angry': [
        {'title': 'Break Stuff', 'artist': 'Limp Bizkit', 'genre': 'Nu Metal', 'duration': '2:46', 'cover': 'https://placehold.co/100x100/FF0000/FFF?text=Angry'},
        {'title': 'Killing In The Name', 'artist': 'Rage Against The Machine', 'genre': 'Metal', 'duration': '5:14', 'cover': 'https://placehold.co/100x100/FF0000/FFF?text=Angry'},
        {'title': 'Chop Suey!', 'artist': 'System Of A Down', 'genre': 'Metal', 'duration': '3:30', 'cover': 'https://placehold.co/100x100/FF0000/FFF?text=Angry'},
        {'title': 'Given Up', 'artist': 'Linkin Park', 'genre': 'Rock', 'duration': '3:09', 'cover': 'https://placehold.co/100x100/FF0000/FFF?text=Angry'},
        {'title': 'Before I Forget', 'artist': 'Slipknot', 'genre': 'Metal', 'duration': '4:38', 'cover': 'https://placehold.co/100x100/FF0000/FFF?text=Angry'},
        {'title': 'Smells Like Teen Spirit', 'artist': 'Nirvana', 'genre': 'Grunge', 'duration': '5:01', 'cover': 'https://placehold.co/100x100/FF0000/FFF?text=Angry'},
        {'title': 'Walk', 'artist': 'Pantera', 'genre': 'Metal', 'duration': '5:15', 'cover': 'https://placehold.co/100x100/FF0000/FFF?text=Angry'},
        {'title': 'Duality', 'artist': 'Slipknot', 'genre': 'Metal', 'duration': '4:12', 'cover': 'https://placehold.co/100x100/FF0000/FFF?text=Angry'},
        {'title': 'Down with the Sickness', 'artist': 'Disturbed', 'genre': 'Metal', 'duration': '4:38', 'cover': 'https://placehold.co/100x100/FF0000/FFF?text=Angry'},
        {'title': 'Basket Case', 'artist': 'Green Day', 'genre': 'Punk', 'duration': '3:01', 'cover': 'https://placehold.co/100x100/FF0000/FFF?text=Angry'},
    ],
    'Relaxed': [
        {'title': 'Weightless', 'artist': 'Marconi Union', 'genre': 'Ambient', 'duration': '8:08', 'cover': 'https://placehold.co/100x100/008000/FFF?text=Relaxed'},
        {'title': 'Clair de Lune', 'artist': 'Claude Debussy', 'genre': 'Classical', 'duration': '5:05', 'cover': 'https://placehold.co/100x100/008000/FFF?text=Relaxed'},
        {'title': 'Watermark', 'artist': 'Enya', 'genre': 'New Age', 'duration': '2:26', 'cover': 'https://placehold.co/100x100/008000/FFF?text=Relaxed'},
        {'title': 'Breathe', 'artist': 'Pink Floyd', 'genre': 'Rock', 'duration': '2:49', 'cover': 'https://placehold.co/100x100/008000/FFF?text=Relaxed'},
        {'title': 'Sunset Lover', 'artist': 'Petit Biscuit', 'genre': 'Electronic', 'duration': '3:57', 'cover': 'https://placehold.co/100x100/008000/FFF?text=Relaxed'},
        {'title': 'Teardrop', 'artist': 'Massive Attack', 'genre': 'Electronic', 'duration': '5:29', 'cover': 'https://placehold.co/100x100/008000/FFF?text=Relaxed'},
        {'title': 'Aruarian Dance', 'artist': 'Nujabes', 'genre': 'Lo-Fi', 'duration': '4:10', 'cover': 'https://placehold.co/100x100/008000/FFF?text=Relaxed'},
        {'title': 'Porcelain', 'artist': 'Moby', 'genre': 'Electronic', 'duration': '4:01', 'cover': 'https://placehold.co/100x100/008000/FFF?text=Relaxed'},
        {'title': 'Orinoco Flow', 'artist': 'Enya', 'genre': 'New Age', 'duration': '4:26', 'cover': 'https://placehold.co/100x100/008000/FFF?text=Relaxed'},
        {'title': 'Gymnopédie No.1', 'artist': 'Erik Satie', 'genre': 'Classical', 'duration': '3:25', 'cover': 'https://placehold.co/100x100/008000/FFF?text=Relaxed'},
    ],
    'Excited': [
        {'title': 'Blinding Lights', 'artist': 'The Weeknd', 'genre': 'Synth-Pop', 'duration': '3:20', 'cover': 'https://placehold.co/100x100/FFA500/000?text=Excited'},
        {'title': 'Can\'t Hold Us', 'artist': 'Macklemore & Ryan Lewis', 'genre': 'Hip Hop', 'duration': '4:18', 'cover': 'https://placehold.co/100x100/FFA500/000?text=Excited'},
        {'title': 'Levels', 'artist': 'Avicii', 'genre': 'EDM', 'duration': '3:19', 'cover': 'https://placehold.co/100x100/FFA500/000?text=Excited'},
        {'title': 'Mr. Brightside', 'artist': 'The Killers', 'genre': 'Rock', 'duration': '3:42', 'cover': 'https://placehold.co/100x100/FFA500/000?text=Excited'},
        {'title': 'Titanium', 'artist': 'David Guetta ft. Sia', 'genre': 'EDM', 'duration': '4:05', 'cover': 'https://placehold.co/100x100/FFA500/000?text=Excited'},
        {'title': 'Wake Me Up', 'artist': 'Avicii', 'genre': 'EDM', 'duration': '4:07', 'cover': 'https://placehold.co/100x100/FFA500/000?text=Excited'},
        {'title': 'Party Rock Anthem', 'artist': 'LMFAO', 'genre': 'Electronic', 'duration': '4:22', 'cover': 'https://placehold.co/100x100/FFA500/000?text=Excited'},
        {'title': 'Don\'t You Worry Child', 'artist': 'Swedish House Mafia', 'genre': 'EDM', 'duration': '3:32', 'cover': 'https://placehold.co/100x100/FFA500/000?text=Excited'},
        {'title': 'Lean On', 'artist': 'Major Lazer', 'genre': 'EDM', 'duration': '2:56', 'cover': 'https://placehold.co/100x100/FFA500/000?text=Excited'},
        {'title': 'Feel So Close', 'artist': 'Calvin Harris', 'genre': 'EDM', 'duration': '3:26', 'cover': 'https://placehold.co/100x100/FFA500/000?text=Excited'},
    ],
    'Romantic': [
        {'title': 'Perfect', 'artist': 'Ed Sheeran', 'genre': 'Pop', 'duration': '4:23', 'cover': 'https://placehold.co/100x100/FFC0CB/000?text=Romantic'},
        {'title': 'All of Me', 'artist': 'John Legend', 'genre': 'R&B', 'duration': '4:29', 'cover': 'https://placehold.co/100x100/FFC0CB/000?text=Romantic'},
        {'title': 'Make You Feel My Love', 'artist': 'Adele', 'genre': 'Pop', 'duration': '3:32', 'cover': 'https://placehold.co/100x100/FFC0CB/000?text=Romantic'},
        {'title': 'A Thousand Years', 'artist': 'Christina Perri', 'genre': 'Pop', 'duration': '4:45', 'cover': 'https://placehold.co/100x100/FFC0CB/000?text=Romantic'},
        {'title': 'Thinking Out Loud', 'artist': 'Ed Sheeran', 'genre': 'Pop', 'duration': '4:41', 'cover': 'https://placehold.co/100x100/FFC0CB/000?text=Romantic'},
        {'title': 'At Last', 'artist': 'Etta James', 'genre': 'R&B', 'duration': '3:00', 'cover': 'https://placehold.co/100x100/FFC0CB/000?text=Romantic'},
        {'title': 'Just the Way You Are', 'artist': 'Bruno Mars', 'genre': 'Pop', 'duration': '3:40', 'cover': 'https://placehold.co/100x100/FFC0CB/000?text=Romantic'},
        {'title': 'Can\'t Help Falling In Love', 'artist': 'Elvis Presley', 'genre': 'Pop', 'duration': '2:59', 'cover': 'https://placehold.co/100x100/FFC0CB/000?text=Romantic'},
        {'title': 'Endless Love', 'artist': 'Lionel Richie & Diana Ross', 'genre': 'Pop', 'duration': '4:28', 'cover': 'https://placehold.co/100x100/FFC0CB/000?text=Romantic'},
        {'title': 'I Will Always Love You', 'artist': 'Whitney Houston', 'genre': 'Pop', 'duration': '4:31', 'cover': 'https://placehold.co/100x100/FFC0CB/000?text=Romantic'},
    ],
    'Stressed': [
        {'title': 'Under Pressure', 'artist': 'Queen & David Bowie', 'genre': 'Rock', 'duration': '4:08', 'cover': 'https://placehold.co/100x100/800080/FFF?text=Stressed'},
        {'title': 'Stressed Out', 'artist': 'Twenty One Pilots', 'genre': 'Alternative', 'duration': '3:22', 'cover': 'https://placehold.co/100x100/800080/FFF?text=Stressed'},
        {'title': 'Help!', 'artist': 'The Beatles', 'genre': 'Rock', 'duration': '2:18', 'cover': 'https://placehold.co/100x100/800080/FFF?text=Stressed'},
        {'title': 'Numb', 'artist': 'Linkin Park', 'genre': 'Rock', 'duration': '3:07', 'cover': 'https://placehold.co/100x100/800080/FFF?text=Stressed'},
        {'title': 'Boulevard of Broken Dreams', 'artist': 'Green Day', 'genre': 'Punk', 'duration': '4:20', 'cover': 'https://placehold.co/100x100/800080/FFF?text=Stressed'},
        {'title': 'Wake Me Up When September Ends', 'artist': 'Green Day', 'genre': 'Punk', 'duration': '4:45', 'cover': 'https://placehold.co/100x100/800080/FFF?text=Stressed'},
        {'title': 'In the End', 'artist': 'Linkin Park', 'genre': 'Rock', 'duration': '3:36', 'cover': 'https://placehold.co/100x100/800080/FFF?text=Stressed'},
        {'title': 'Losing My Religion', 'artist': 'R.E.M.', 'genre': 'Alternative', 'duration': '4:26', 'cover': 'https://placehold.co/100x100/800080/FFF?text=Stressed'},
        {'title': 'Everybody Hurts', 'artist': 'R.E.M.', 'genre': 'Alternative', 'duration': '5:17', 'cover': 'https://placehold.co/100x100/800080/FFF?text=Stressed'},
        {'title': 'Mad World', 'artist': 'Gary Jules', 'genre': 'Alternative', 'duration': '3:03', 'cover': 'https://placehold.co/100x100/800080/FFF?text=Stressed'},
    ]
}

DESCRIPTIONS = {
    'Happy': 'You seem cheerful and energetic today. Keep spreading that positivity!',
    'Sad': 'You seem a bit down. It\'s okay to feel sad sometimes. Here\'s some music that might help.',
    'Angry': 'You seem frustrated or angry. Let it out with these powerful tracks.',
    'Relaxed': 'You seem very calm and at peace. Enjoy these soothing tunes.',
    'Excited': 'You are radiating energy! Let\'s keep the momentum going.',
    'Romantic': 'Love is in the air. Enjoy these beautiful romantic melodies.',
    'Stressed': 'You seem stressed. Take a deep breath and let this music help you unwind.'
}

WELLNESS = {
    'Happy': 'Keep doing what you\'re doing! Maybe share your joy with a friend.',
    'Sad': 'Take a short walk or treat yourself to something nice today.',
    'Angry': 'Try some deep breathing exercises or a quick workout.',
    'Relaxed': 'Maintain this state by reading a book or enjoying a warm cup of tea.',
    'Excited': 'Channel this energy into a creative project or physical activity.',
    'Romantic': 'Plan a special evening or simply express your feelings to someone.',
    'Stressed': 'Step away from your screen, drink some water, and rest your eyes.'
}

EMOJIS = {
    'Happy': '😊',
    'Sad': '😢',
    'Angry': '😡',
    'Relaxed': '😌',
    'Excited': '🤩',
    'Romantic': '💖',
    'Stressed': '😫'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict_page')
def predict_page():
    return render_template('predict.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/instant_songs', methods=['GET'])
def instant_songs():
    # Gather all songs from all moods
    all_songs = []
    for mood_songs in MOCK_SONGS.values():
        all_songs.extend(mood_songs)
    
    # Pick 20 random songs
    random.shuffle(all_songs)
    selected_songs = all_songs[:20]
    
    import urllib.parse
    for s in selected_songs:
        query = urllib.parse.quote_plus(f"{s['title']} {s['artist']}")
        s['url'] = f"https://www.youtube.com/results?search_query={query}"
        
        if 'placehold' in s['cover']:
            try:
                itunes_url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=1"
                res = requests.get(itunes_url, timeout=2).json()
                if res['resultCount'] > 0:
                    s['cover'] = res['results'][0]['artworkUrl100'].replace('100x100bb', '300x300bb')
            except:
                s['cover'] = 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&h=300&fit=crop'
                
    return jsonify({'songs': selected_songs})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
        
    # Mocking prediction delay
    time.sleep(1.5)
    
    # --- Real Model Prediction ---
    # In a real app, you would do:
    # vector = vectorizer.transform([text])
    # prediction = model.predict(vector)[0]
    # prob = model.predict_proba(vector)[0]
    # confidence = max(prob) * 100
    # mood = MOODS[prediction] # assuming prediction is index or string
    
    # --- Keyword-Based Mood Detection ---
    text_lower = text.lower()
    if any(w in text_lower for w in ['happy', 'joy', 'great', 'awesome', 'good', 'aced', 'smile']): mood = 'Happy'
    elif any(w in text_lower for w in ['sad', 'depressed', 'down', 'cry', 'unhappy', 'bad']): mood = 'Sad'
    elif any(w in text_lower for w in ['angry', 'mad', 'frustrated', 'annoyed', 'furious', 'hate']): mood = 'Angry'
    elif any(w in text_lower for w in ['relax', 'chill', 'calm', 'peace', 'tired', 'sleep']): mood = 'Relaxed'
    elif any(w in text_lower for w in ['excited', 'thrilled', 'pumped', 'eager', 'can\'t wait']): mood = 'Excited'
    elif any(w in text_lower for w in ['love', 'romantic', 'sweet', 'heart', 'date']): mood = 'Romantic'
    elif any(w in text_lower for w in ['stress', 'exam', 'work', 'pressure', 'anxious', 'worried']): mood = 'Stressed'
    else: mood = 'Happy' # Default
    
    confidence = round(random.uniform(85.0, 98.9), 1)
    
    # Randomly select 10 songs for the mood (or all if < 10)
    songs = MOCK_SONGS.get(mood, [])
    random.shuffle(songs)
    recommended_songs = songs[:10]
    
    for s in recommended_songs:
        query = urllib.parse.quote_plus(f"{s['title']} {s['artist']}")
        s['url'] = f"https://www.youtube.com/results?search_query={query}"
        
        # Fetch real thumbnail from iTunes API if not already fetched
        if 'placehold' in s['cover']:
            try:
                itunes_url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=1"
                res = requests.get(itunes_url, timeout=2).json()
                if res['resultCount'] > 0:
                    s['cover'] = res['results'][0]['artworkUrl100'].replace('100x100bb', '300x300bb')
            except:
                s['cover'] = 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&h=300&fit=crop'
    
    response = {
        'mood': mood,
        'emoji': EMOJIS.get(mood, '😐'),
        'confidence_score': confidence,
        'description': DESCRIPTIONS.get(mood, ''),
        'wellness_suggestion': WELLNESS.get(mood, ''),
        'songs': recommended_songs
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
