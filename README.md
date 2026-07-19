# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

- Real-world music apps like Spotify or YouTube Music work by comparing two things: what a song is (its tempo, mood, genre, energy) and what a listener tends to like (based on past listens, skips, and saves). Then turns both of those into numbers, compares them, and recommends whatever numbers line up best.
- Our simulation works the same way, just at a much smaller scale. Instead of millions of listeners' history, we use one made-up `UserProfile` and a small catalog of songs. Also we replace a neural network with a simple math formula we control ourselves.
- Each `Song` in our system carries a set of attributes that describe what it sounds like: 
  - `genre`: pop, lofi, jazz, e.g.
  - `mood`: happy, chill, intense, e.g. 
  - `energy` (how high-intensity the track feels): from 0 to 1 
  - `tempo_bpm` (how fast it is)
  - `valence` (how positive or upbeat it sounds)
  - `danceability` (how easy it is to dance to)
  - `acousticness` (how much it leans acoustic vs. produced/electronic)
  - `tempo_bpm`, `valence`, and `danceability` are captured for every song but are **not** part of the current scoring formula below — they're tracked as data now so they're available if you want to experiment with adding them later (see Experiments You Tried).
- The `UserProfile` stores what one listener is looking for: 
  - `favorite_genre` and `favorite_mood` 
  - a `target_energy` (the energy level they want, not just "high" or "low"), and whether they `likes_acoustic` sound.
  - a `target_valence` field also exists (default `0.5`) but, like the song-level attributes above, it's reserved for future use and is not part of the current scoring recipe.
- The `Recommender` scores each song against that profile.
  - `genre` and `mood` are match-based which means that a song either fits the listener's favorite or it doesn't and with `genre` weighted more heavily as the stronger taste signal.
  - `energy` is scored by closeness such that a song is rewarded for being near the user's target energy, not just for being high or low, so a listener who wants medium energy won't get handed the most intense track in the catalog.
  - `acousticness` is scored based on whether the listener said they like that sound.
  - These individual scores are combined into one weighted total per song. `genre` counts the most since it's the rarest, strongest taste signal in this catalog; `mood` and `energy` closeness form the next tier and are weighted evenly with each other; `acousticness` contributes the least since it's a softer, boolean-style preference rather than an explicit target.
- Once every song has a score, we choose recommendations by sorting all the songs from highest score to lowest and returning the top results. 
- This is why our system needs two separate ideas working together: a scoring rule that judges one song at a time, and a ranking step that looks at every song's score together to decide the final order.

### Algorithm Recipe

Each song is judged against the user's profile using four components, then the components are summed into one total score:

| Component | Type | Points | Formula |
|---|---|---|---|
| Genre match | binary | +2.0 | `2.0 if song.genre == favorite_genre else 0` |
| Mood match | binary | +1.0 | `1.0 if song.mood == favorite_mood else 0` |
| Energy closeness | continuous | up to +1.0 | `1.0 * (1 - abs(song.energy - target_energy))` |
| Acousticness fit | continuous | up to +0.5 | `0.5 * song.acousticness` if `likes_acoustic` else `0.5 * (1 - song.acousticness)` |

Max possible score: **4.5**.

If `user_prefs` doesn't specify a preference, the score falls back to a neutral default rather than erroring: a missing `genre`/`mood` simply can't earn genre/mood points (every song scores +0 on that component), a missing `energy` falls back to `target_energy = 0.5`, and a missing `likes_acoustic` defaults to `False`. This keeps `score_song` safe to call with partial profiles and means an empty `user_prefs` still ranks songs consistently by energy-closeness-to-0.5 and acousticness alone.

Genre outweighs mood (2:1) because our catalog has more distinct genres than moods, so an exact genre match is a rarer, stronger signal. Energy and acousticness are continuous rather than binary, so they add nuance without ever being able to out-weigh an explicit genre or mood match on their own.

### Expected Biases

- **Over-prioritizing genre**: because genre match is worth 2x a mood match, a song in the user's favorite genre with a totally wrong mood can still outscore a song that's a perfect mood/energy fit in a different genre. This may bury great songs that match the *feel* the listener wants just because they're shelved under a different genre label.
- **All-or-nothing penalty on genre/mood**: a song that's "close enough" (e.g. `indie pop` vs `pop`, or `relaxed` vs `chill`) gets zero credit for genre/mood, the same as a song that's a total mismatch. The system can't recognize near-miss labels.
- **Small, uneven catalog**: with only 20 songs and many singleton genres/moods, most users will get very few (sometimes zero) exact genre matches, so the ranking can end up driven mostly by energy/acousticness closeness for anyone whose favorite genre isn't well represented.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python3 -m src.main`, using the starter profile `{"genre": "pop", "mood": "happy", "energy": 0.8}`:

```
Loaded songs: 20

============================================================
Top 5 Recommendations for {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}
============================================================

1. Shake It Off by Taylor Swift — Score: 4.47
     - genre match (pop) (+2.0)
     - mood match (happy) (+1.0)
     - energy closeness (song=0.80, target=0.80) (+1.00)
     - acousticness fit (prefers produced sound, song=0.05) (+0.47)

2. Sunrise City by Neon Echo — Score: 4.39
     - genre match (pop) (+2.0)
     - mood match (happy) (+1.0)
     - energy closeness (song=0.82, target=0.80) (+0.98)
     - acousticness fit (prefers produced sound, song=0.18) (+0.41)

3. Gym Hero by Max Pulse — Score: 3.35
     - genre match (pop) (+2.0)
     - mood mismatch (intense vs happy) (+0.0)
     - energy closeness (song=0.93, target=0.80) (+0.87)
     - acousticness fit (prefers produced sound, song=0.05) (+0.47)

4. Rooftop Lights by Indigo Parade — Score: 2.29
     - genre mismatch (indie pop vs pop) (+0.0)
     - mood match (happy) (+1.0)
     - energy closeness (song=0.76, target=0.80) (+0.96)
     - acousticness fit (prefers produced sound, song=0.35) (+0.33)

5. Rebel Static by Static Front — Score: 1.38
     - genre mismatch (rock vs pop) (+0.0)
     - mood mismatch (intense vs happy) (+0.0)
     - energy closeness (song=0.88, target=0.80) (+0.92)
     - acousticness fit (prefers produced sound, song=0.08) (+0.46)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



