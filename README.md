# 🎵 Music Recommender Simulation

## Project Summary

**YourTaste 4.0**, is a command-line music recommender that works off a small catalog of 20 songs. You describe your taste as a simple profile, your favorite genre, your favorite mood, how much energy you want, and whether you like an acoustic sound, and the app scores every song in the catalog against that profile using a weighted formula: genre matches count the most, mood matches count next, and energy/acoustic closeness fill in the rest. It then hands back your top 5 matches, each with a short plain-language explanation of why that song made the cut. Beyond just building the scoring logic, this project also stress-tested it with a batch of everyday and deliberately tricky profiles (typos, contradictory preferences, missing fields) to see where the recommendations held up and where they didn't, and documents both the fixes and the remaining biases in the README and the [model card](model_card.md).

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

Run `python3 -m src.main`

### `{"genre": "pop", "mood": "happy", "energy": 0.8}` (starter profile)

```
Loaded songs: 20

============================================================
Top 5 Recommendations for {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}
============================================================

1. Shake It Off by Taylor Swift — Score: 4.47
     Why: matching genre (pop) + matching mood (happy) + energy closely matches your target (0.80 vs 0.80)
       - genre match (pop) (+2.0)
       - mood match (happy) (+1.0)
       - energy closeness (song=0.80, target=0.80) (+1.00)
       - acousticness fit (prefers produced sound, song=0.05) (+0.47)

2. Sunrise City by Neon Echo — Score: 4.39
     Why: matching genre (pop) + matching mood (happy) + energy closely matches your target (0.82 vs 0.80)
       - genre match (pop) (+2.0)
       - mood match (happy) (+1.0)
       - energy closeness (song=0.82, target=0.80) (+0.98)
       - acousticness fit (prefers produced sound, song=0.18) (+0.41)

3. Gym Hero by Max Pulse — Score: 3.35
     Why: matching genre (pop) + energy closely matches your target (0.93 vs 0.80) + produced/electronic sound as you prefer (0.05)
       - genre match (pop) (+2.0)
       - mood mismatch (intense vs happy) (+0.0)
       - energy closeness (song=0.93, target=0.80) (+0.87)
       - acousticness fit (prefers produced sound, song=0.05) (+0.47)

4. Rooftop Lights by Indigo Parade — Score: 2.29
     Why: matching mood (happy) + energy closely matches your target (0.76 vs 0.80)
       - genre mismatch (indie pop vs pop) (+0.0)
       - mood match (happy) (+1.0)
       - energy closeness (song=0.76, target=0.80) (+0.96)
       - acousticness fit (prefers produced sound, song=0.35) (+0.33)

5. Rebel Static by Static Front — Score: 1.38
     Why: energy closely matches your target (0.88 vs 0.80) + produced/electronic sound as you prefer (0.08)
       - genre mismatch (rock vs pop) (+0.0)
       - mood mismatch (intense vs happy) (+0.0)
       - energy closeness (song=0.88, target=0.80) (+0.92)
       - acousticness fit (prefers produced sound, song=0.08) (+0.46)
```

Note: this profile is high-energy (0.8) with no stated acoustic preference (defaults to `likes_acoustic: False`), so it rewards loud, produced pop — the opposite end of the spectrum from the acoustic, low-energy lofi and jazz profiles below, which pull toward mellow, textured tracks instead.

### `{"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True}`

```
============================================================
Top 5 Recommendations for {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35, 'likes_acoustic': True}
============================================================

1. Library Rain by Paper Lanterns — Score: 4.43
     Why: matching genre (lofi) + matching mood (chill) + energy closely matches your target (0.35 vs 0.35)
       - genre match (lofi) (+2.0)
       - mood match (chill) (+1.0)
       - energy closeness (song=0.35, target=0.35) (+1.00)
       - acousticness fit (likes acoustic, song=0.86) (+0.43)

2. Midnight Coding by LoRoom — Score: 4.29
     Why: matching genre (lofi) + matching mood (chill) + energy closely matches your target (0.42 vs 0.35)
       - genre match (lofi) (+2.0)
       - mood match (chill) (+1.0)
       - energy closeness (song=0.42, target=0.35) (+0.93)
       - acousticness fit (likes acoustic, song=0.71) (+0.35)

3. Focus Flow by LoRoom — Score: 3.34
     Why: matching genre (lofi) + energy closely matches your target (0.40 vs 0.35) + strong acoustic feel (0.78)
       - genre match (lofi) (+2.0)
       - mood mismatch (focused vs chill) (+0.0)
       - energy closeness (song=0.40, target=0.35) (+0.95)
       - acousticness fit (likes acoustic, song=0.78) (+0.39)

4. Spacewalk Thoughts by Orbit Bloom — Score: 2.39
     Why: matching mood (chill) + energy closely matches your target (0.28 vs 0.35) + strong acoustic feel (0.92)
       - genre mismatch (ambient vs lofi) (+0.0)
       - mood match (chill) (+1.0)
       - energy closeness (song=0.28, target=0.35) (+0.93)
       - acousticness fit (likes acoustic, song=0.92) (+0.46)

5. Quiet Orbit by Orbit Bloom — Score: 2.32
     Why: matching mood (chill) + energy closely matches your target (0.22 vs 0.35) + strong acoustic feel (0.90)
       - genre mismatch (ambient vs lofi) (+0.0)
       - mood match (chill) (+1.0)
       - energy closeness (song=0.22, target=0.35) (+0.87)
       - acousticness fit (likes acoustic, song=0.90) (+0.45)
```

Note: low energy (0.35) plus `likes_acoustic: True` shifts the whole top 5 toward mellow, acoustic-leaning tracks (acousticness 0.71–0.92) — the reverse of the pop/happy profile above, and similar in shape to the jazz/relaxed profile below even though the two don't share a genre or mood.

### `{"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False}`

```
============================================================
Top 5 Recommendations for {'genre': 'rock', 'mood': 'intense', 'energy': 0.9, 'likes_acoustic': False}
============================================================

1. Storm Runner by Voltline — Score: 4.44
     Why: matching genre (rock) + matching mood (intense) + energy closely matches your target (0.91 vs 0.90)
       - genre match (rock) (+2.0)
       - mood match (intense) (+1.0)
       - energy closeness (song=0.91, target=0.90) (+0.99)
       - acousticness fit (prefers produced sound, song=0.10) (+0.45)

2. Rebel Static by Static Front — Score: 4.44
     Why: matching genre (rock) + matching mood (intense) + energy closely matches your target (0.88 vs 0.90)
       - genre match (rock) (+2.0)
       - mood match (intense) (+1.0)
       - energy closeness (song=0.88, target=0.90) (+0.98)
       - acousticness fit (prefers produced sound, song=0.08) (+0.46)

3. Gym Hero by Max Pulse — Score: 2.44
     Why: matching mood (intense) + energy closely matches your target (0.93 vs 0.90) + produced/electronic sound as you prefer (0.05)
       - genre mismatch (pop vs rock) (+0.0)
       - mood match (intense) (+1.0)
       - energy closeness (song=0.93, target=0.90) (+0.97)
       - acousticness fit (prefers produced sound, song=0.05) (+0.47)

4. Starlight Anthem by Nova Sisters — Score: 1.44
     Why: energy closely matches your target (0.88 vs 0.90) + produced/electronic sound as you prefer (0.08)
       - genre mismatch (k-pop vs rock) (+0.0)
       - mood mismatch (triumphant vs intense) (+0.0)
       - energy closeness (song=0.88, target=0.90) (+0.98)
       - acousticness fit (prefers produced sound, song=0.08) (+0.46)

5. Iron Verdict by Grave Chorus — Score: 1.41
     Why: energy closely matches your target (0.98 vs 0.90) + produced/electronic sound as you prefer (0.02)
       - genre mismatch (metal vs rock) (+0.0)
       - mood mismatch (aggressive vs intense) (+0.0)
       - energy closeness (song=0.98, target=0.90) (+0.92)
       - acousticness fit (prefers produced sound, song=0.02) (+0.49)
```

Note: this is the most extreme high-energy, non-acoustic profile (0.9, `likes_acoustic: False`) — "Storm Runner" and "Rebel Static" land within 0.00 of each other (4.44 each) because both nail genre, mood, and energy simultaneously. Nothing acoustic or mellow (like the lofi/jazz picks) comes anywhere close for this listener.

### `{"genre": "jazz", "mood": "relaxed", "energy": 0.4, "likes_acoustic": True}`

```
============================================================
Top 5 Recommendations for {'genre': 'jazz', 'mood': 'relaxed', 'energy': 0.4, 'likes_acoustic': True}
============================================================

1. Coffee Shop Stories by Slow Stereo — Score: 4.42
     Why: matching genre (jazz) + matching mood (relaxed) + energy closely matches your target (0.37 vs 0.40)
       - genre match (jazz) (+2.0)
       - mood match (relaxed) (+1.0)
       - energy closeness (song=0.37, target=0.40) (+0.97)
       - acousticness fit (likes acoustic, song=0.89) (+0.45)

2. Blue Hour Sessions by Slow Stereo — Score: 4.35
     Why: matching genre (jazz) + matching mood (relaxed) + energy closely matches your target (0.33 vs 0.40)
       - genre match (jazz) (+2.0)
       - mood match (relaxed) (+1.0)
       - energy closeness (song=0.33, target=0.40) (+0.93)
       - acousticness fit (likes acoustic, song=0.85) (+0.42)

3. Focus Flow by LoRoom — Score: 1.39
     Why: energy closely matches your target (0.40 vs 0.40) + strong acoustic feel (0.78)
       - genre mismatch (lofi vs jazz) (+0.0)
       - mood mismatch (focused vs relaxed) (+0.0)
       - energy closeness (song=0.40, target=0.40) (+1.00)
       - acousticness fit (likes acoustic, song=0.78) (+0.39)

4. Library Rain by Paper Lanterns — Score: 1.38
     Why: energy closely matches your target (0.35 vs 0.40) + strong acoustic feel (0.86)
       - genre mismatch (lofi vs jazz) (+0.0)
       - mood mismatch (chill vs relaxed) (+0.0)
       - energy closeness (song=0.35, target=0.40) (+0.95)
       - acousticness fit (likes acoustic, song=0.86) (+0.43)

5. Spacewalk Thoughts by Orbit Bloom — Score: 1.34
     Why: energy closely matches your target (0.28 vs 0.40) + strong acoustic feel (0.92)
       - genre mismatch (ambient vs jazz) (+0.0)
       - mood mismatch (chill vs relaxed) (+0.0)
       - energy closeness (song=0.28, target=0.40) (+0.88)
       - acousticness fit (likes acoustic, song=0.92) (+0.46)
```

Note: same "low energy + acoustic" shape as the lofi/chill profile above (both land in the 0.85–0.90 acousticness range), just in a different genre/mood bucket — evidence that energy and acousticness, not genre, are what make these two profiles' top picks *feel* similar to each other.

### `{"genre": "metal", "mood": "chill", "energy": 0.1, "likes_acoustic": True}` — adversarial: internal contradiction

```
============================================================
Top 5 Recommendations for {'genre': 'metal', 'mood': 'chill', 'energy': 0.1, 'likes_acoustic': True}
============================================================

1. Quiet Orbit by Orbit Bloom — Score: 2.33
     Why: matching mood (chill) + energy closely matches your target (0.22 vs 0.10) + strong acoustic feel (0.90)
       - genre mismatch (ambient vs metal) (+0.0)
       - mood match (chill) (+1.0)
       - energy closeness (song=0.22, target=0.10) (+0.88)
       - acousticness fit (likes acoustic, song=0.90) (+0.45)

2. Spacewalk Thoughts by Orbit Bloom — Score: 2.28
     Why: matching mood (chill) + energy fairly close to your target (0.28 vs 0.10) + strong acoustic feel (0.92)
       - genre mismatch (ambient vs metal) (+0.0)
       - mood match (chill) (+1.0)
       - energy closeness (song=0.28, target=0.10) (+0.82)
       - acousticness fit (likes acoustic, song=0.92) (+0.46)

3. Library Rain by Paper Lanterns — Score: 2.18
     Why: matching mood (chill) + energy fairly close to your target (0.35 vs 0.10) + strong acoustic feel (0.86)
       - genre mismatch (lofi vs metal) (+0.0)
       - mood match (chill) (+1.0)
       - energy closeness (song=0.35, target=0.10) (+0.75)
       - acousticness fit (likes acoustic, song=0.86) (+0.43)

4. Iron Verdict by Grave Chorus — Score: 2.13
     Why: matching genre (metal)
       - genre match (metal) (+2.0)
       - mood mismatch (aggressive vs chill) (+0.0)
       - energy closeness (song=0.98, target=0.10) (+0.12)
       - acousticness fit (likes acoustic, song=0.02) (+0.01)

5. Midnight Coding by LoRoom — Score: 2.04
     Why: matching mood (chill) + energy fairly close to your target (0.42 vs 0.10) + strong acoustic feel (0.71)
       - genre mismatch (lofi vs metal) (+0.0)
       - mood match (chill) (+1.0)
       - energy closeness (song=0.42, target=0.10) (+0.68)
       - acousticness fit (likes acoustic, song=0.71) (+0.35)
```

Note: the only genre-matching song ("Iron Verdict") actually ranks 4th, not 1st — its mood/energy/acoustic mismatches are severe enough that three genre-*mismatched* songs beat it. This is a useful counterexample to the assumption that genre's 2.0 weight always dominates the ranking.

### `{"genre": None, "mood": "sad", "energy": 0.9}` — adversarial: mood/energy conflict, unrepresented mood

```
============================================================
Top 5 Recommendations for {'genre': None, 'mood': 'sad', 'energy': 0.9}
============================================================

1. Gym Hero by Max Pulse — Score: 1.44
     Why: energy closely matches your target (0.93 vs 0.90) + produced/electronic sound as you prefer (0.05)
       - genre mismatch (pop vs None) (+0.0)
       - mood mismatch (intense vs sad) (+0.0)
       - energy closeness (song=0.93, target=0.90) (+0.97)
       - acousticness fit (prefers produced sound, song=0.05) (+0.47)

2. Storm Runner by Voltline — Score: 1.44
     Why: energy closely matches your target (0.91 vs 0.90) + produced/electronic sound as you prefer (0.10)
       - genre mismatch (rock vs None) (+0.0)
       - mood mismatch (intense vs sad) (+0.0)
       - energy closeness (song=0.91, target=0.90) (+0.99)
       - acousticness fit (prefers produced sound, song=0.10) (+0.45)

3. Rebel Static by Static Front — Score: 1.44
     Why: energy closely matches your target (0.88 vs 0.90) + produced/electronic sound as you prefer (0.08)
       - genre mismatch (rock vs None) (+0.0)
       - mood mismatch (intense vs sad) (+0.0)
       - energy closeness (song=0.88, target=0.90) (+0.98)
       - acousticness fit (prefers produced sound, song=0.08) (+0.46)

4. Starlight Anthem by Nova Sisters — Score: 1.44
     Why: energy closely matches your target (0.88 vs 0.90) + produced/electronic sound as you prefer (0.08)
       - genre mismatch (k-pop vs None) (+0.0)
       - mood mismatch (triumphant vs sad) (+0.0)
       - energy closeness (song=0.88, target=0.90) (+0.98)
       - acousticness fit (prefers produced sound, song=0.08) (+0.46)

5. Iron Verdict by Grave Chorus — Score: 1.41
     Why: energy closely matches your target (0.98 vs 0.90) + produced/electronic sound as you prefer (0.02)
       - genre mismatch (metal vs None) (+0.0)
       - mood mismatch (aggressive vs sad) (+0.0)
       - energy closeness (song=0.98, target=0.90) (+0.92)
       - acousticness fit (prefers produced sound, song=0.02) (+0.49)
```

Note: no song in the catalog has `mood == "sad"`, so the stated mood preference is silently ignored — the ranking is really just "give me high energy," which the system can't distinguish from a coherent profile.

### `{}` — adversarial: empty profile

```
============================================================
Top 5 Recommendations for {}
============================================================

1. Midnight Tango by Rio Sombra — Score: 1.27
     Why: energy closely matches your target (0.60 vs 0.50) + produced/electronic sound as you prefer (0.25)
       - genre mismatch (latin vs None) (+0.0)
       - mood mismatch (mysterious vs None) (+0.0)
       - energy closeness (song=0.60, target=0.50) (+0.90)
       - acousticness fit (prefers produced sound, song=0.25) (+0.38)

2. Island Time by Sunny Roots — Score: 1.23
     Why: energy closely matches your target (0.55 vs 0.50)
       - genre mismatch (reggae vs None) (+0.0)
       - mood mismatch (playful vs None) (+0.0)
       - energy closeness (song=0.55, target=0.50) (+0.95)
       - acousticness fit (prefers produced sound, song=0.45) (+0.28)

3. Shake It Off by Taylor Swift — Score: 1.17
     Why: energy fairly close to your target (0.80 vs 0.50) + produced/electronic sound as you prefer (0.05)
       - genre mismatch (pop vs None) (+0.0)
       - mood mismatch (happy vs None) (+0.0)
       - energy closeness (song=0.80, target=0.50) (+0.70)
       - acousticness fit (prefers produced sound, song=0.05) (+0.47)

4. Night Drive Loop by Neon Echo — Score: 1.14
     Why: energy fairly close to your target (0.75 vs 0.50) + produced/electronic sound as you prefer (0.22)
       - genre mismatch (synthwave vs None) (+0.0)
       - mood mismatch (moody vs None) (+0.0)
       - energy closeness (song=0.75, target=0.50) (+0.75)
       - acousticness fit (prefers produced sound, song=0.22) (+0.39)

5. Sunrise City by Neon Echo — Score: 1.09
     Why: energy fairly close to your target (0.82 vs 0.50) + produced/electronic sound as you prefer (0.18)
       - genre mismatch (pop vs None) (+0.0)
       - mood mismatch (happy vs None) (+0.0)
       - energy closeness (song=0.82, target=0.50) (+0.68)
       - acousticness fit (prefers produced sound, song=0.18) (+0.41)
```

Note: matches the documented fallback behavior exactly — with no stated preferences, ranking is driven purely by energy-closeness-to-0.5 and acousticness fit.

### `{"genre": "classical", "mood": "euphoric", "energy": 0.5}` — adversarial: unrepresented genre/mood

```
============================================================
Top 5 Recommendations for {'genre': 'classical', 'mood': 'euphoric', 'energy': 0.5}
============================================================

1. Midnight Tango by Rio Sombra — Score: 1.27
     Why: energy closely matches your target (0.60 vs 0.50) + produced/electronic sound as you prefer (0.25)
       - genre mismatch (latin vs classical) (+0.0)
       - mood mismatch (mysterious vs euphoric) (+0.0)
       - energy closeness (song=0.60, target=0.50) (+0.90)
       - acousticness fit (prefers produced sound, song=0.25) (+0.38)

2. Island Time by Sunny Roots — Score: 1.23
     Why: energy closely matches your target (0.55 vs 0.50)
       - genre mismatch (reggae vs classical) (+0.0)
       - mood mismatch (playful vs euphoric) (+0.0)
       - energy closeness (song=0.55, target=0.50) (+0.95)
       - acousticness fit (prefers produced sound, song=0.45) (+0.28)

3. Shake It Off by Taylor Swift — Score: 1.17
     Why: energy fairly close to your target (0.80 vs 0.50) + produced/electronic sound as you prefer (0.05)
       - genre mismatch (pop vs classical) (+0.0)
       - mood mismatch (happy vs euphoric) (+0.0)
       - energy closeness (song=0.80, target=0.50) (+0.70)
       - acousticness fit (prefers produced sound, song=0.05) (+0.47)

4. Night Drive Loop by Neon Echo — Score: 1.14
     Why: energy fairly close to your target (0.75 vs 0.50) + produced/electronic sound as you prefer (0.22)
       - genre mismatch (synthwave vs classical) (+0.0)
       - mood mismatch (moody vs euphoric) (+0.0)
       - energy closeness (song=0.75, target=0.50) (+0.75)
       - acousticness fit (prefers produced sound, song=0.22) (+0.39)

5. Sunrise City by Neon Echo — Score: 1.09
     Why: energy fairly close to your target (0.82 vs 0.50) + produced/electronic sound as you prefer (0.18)
       - genre mismatch (pop vs classical) (+0.0)
       - mood mismatch (happy vs euphoric) (+0.0)
       - energy closeness (song=0.82, target=0.50) (+0.68)
       - acousticness fit (prefers produced sound, song=0.18) (+0.41)
```

Note: identical ranking to the empty profile above — neither "classical" nor "euphoric" appears anywhere in the catalog, so both components are dead weight for this user; two of the four scoring dimensions are effectively invisible to them.

### `{"genre": "Pop", "mood": "Happy", "energy": 0.8}` — adversarial: case sensitivity

```
============================================================
Top 5 Recommendations for {'genre': 'Pop', 'mood': 'Happy', 'energy': 0.8}
============================================================

1. Shake It Off by Taylor Swift — Score: 4.47
     Why: matching genre (pop) + matching mood (happy) + energy closely matches your target (0.80 vs 0.80)
       - genre match (pop) (+2.0)
       - mood match (happy) (+1.0)
       - energy closeness (song=0.80, target=0.80) (+1.00)
       - acousticness fit (prefers produced sound, song=0.05) (+0.47)

2. Sunrise City by Neon Echo — Score: 4.39
     Why: matching genre (pop) + matching mood (happy) + energy closely matches your target (0.82 vs 0.80)
       - genre match (pop) (+2.0)
       - mood match (happy) (+1.0)
       - energy closeness (song=0.82, target=0.80) (+0.98)
       - acousticness fit (prefers produced sound, song=0.18) (+0.41)

3. Gym Hero by Max Pulse — Score: 3.35
     Why: matching genre (pop) + energy closely matches your target (0.93 vs 0.80) + produced/electronic sound as you prefer (0.05)
       - genre match (pop) (+2.0)
       - mood mismatch (intense vs Happy) (+0.0)
       - energy closeness (song=0.93, target=0.80) (+0.87)
       - acousticness fit (prefers produced sound, song=0.05) (+0.47)

4. Rooftop Lights by Indigo Parade — Score: 2.29
     Why: matching mood (happy) + energy closely matches your target (0.76 vs 0.80)
       - genre mismatch (indie pop vs Pop) (+0.0)
       - mood match (happy) (+1.0)
       - energy closeness (song=0.76, target=0.80) (+0.96)
       - acousticness fit (prefers produced sound, song=0.35) (+0.33)

5. Rebel Static by Static Front — Score: 1.38
     Why: energy closely matches your target (0.88 vs 0.80) + produced/electronic sound as you prefer (0.08)
       - genre mismatch (rock vs Pop) (+0.0)
       - mood mismatch (intense vs Happy) (+0.0)
       - energy closeness (song=0.88, target=0.80) (+0.92)
       - acousticness fit (prefers produced sound, song=0.08) (+0.46)
```

Note: originally, `"Shake It Off"` dropped from 4.47 to 1.48 here purely because `song.get("genre") == favorite_genre` was a case-sensitive string comparison. We fixed this by lowercasing/trimming both sides before comparing (`_normalize_label` in `score_song`), so this profile now scores *identically* to the lowercase starter profile — the top 5 above is a byte-for-byte match.

### `{"genre": "jazz", "mood": "relaxed", "energy": 0.4, "likes_acoustic": "no"}` — adversarial: non-boolean truthy value

```
============================================================
Top 5 Recommendations for {'genre': 'jazz', 'mood': 'relaxed', 'energy': 0.4, 'likes_acoustic': 'no'}
============================================================

1. Coffee Shop Stories by Slow Stereo — Score: 4.02
     Why: matching genre (jazz) + matching mood (relaxed) + energy closely matches your target (0.37 vs 0.40)
       - genre match (jazz) (+2.0)
       - mood match (relaxed) (+1.0)
       - energy closeness (song=0.37, target=0.40) (+0.97)
       - acousticness fit (prefers produced sound, song=0.89) (+0.05)

2. Blue Hour Sessions by Slow Stereo — Score: 4.00
     Why: matching genre (jazz) + matching mood (relaxed) + energy closely matches your target (0.33 vs 0.40)
       - genre match (jazz) (+2.0)
       - mood match (relaxed) (+1.0)
       - energy closeness (song=0.33, target=0.40) (+0.93)
       - acousticness fit (prefers produced sound, song=0.85) (+0.08)

3. Midnight Tango by Rio Sombra — Score: 1.18
     Why: energy fairly close to your target (0.60 vs 0.40) + produced/electronic sound as you prefer (0.25)
       - genre mismatch (latin vs jazz) (+0.0)
       - mood mismatch (mysterious vs relaxed) (+0.0)
       - energy closeness (song=0.60, target=0.40) (+0.80)
       - acousticness fit (prefers produced sound, song=0.25) (+0.38)

4. Cardigan by Taylor Swift — Score: 1.15
     Why: energy closely matches your target (0.35 vs 0.40)
       - genre mismatch (indie folk vs jazz) (+0.0)
       - mood mismatch (melancholic vs relaxed) (+0.0)
       - energy closeness (song=0.35, target=0.40) (+0.95)
       - acousticness fit (prefers produced sound, song=0.60) (+0.20)

5. Midnight Coding by LoRoom — Score: 1.12
     Why: energy closely matches your target (0.42 vs 0.40)
       - genre mismatch (lofi vs jazz) (+0.0)
       - mood mismatch (chill vs relaxed) (+0.0)
       - energy closeness (song=0.42, target=0.40) (+0.98)
       - acousticness fit (prefers produced sound, song=0.71) (+0.15)
```

Note: originally, this scored identically to `likes_acoustic: True` because Python treats the non-empty string `"no"` as truthy. We fixed it by requiring the literal boolean `True` (`user_prefs.get("likes_acoustic", False) is True`), so `"no"` now correctly falls back to "prefers produced sound." The ranking changed noticeably below the two genre-matched songs — songs 3–5 flipped from acoustic picks (Focus Flow, Library Rain, Spacewalk Thoughts) to produced-leaning ones (Midnight Tango, Cardigan, Midnight Coding), confirming the acoustic preference is now read correctly.

### `{"genre": "rock", "mood": "intense", "energy": 1.4}` — adversarial: out-of-range energy

```
============================================================
Top 5 Recommendations for {'genre': 'rock', 'mood': 'intense', 'energy': 1.4}
============================================================

1. Storm Runner by Voltline — Score: 3.96
     Why: matching genre (rock) + matching mood (intense) + produced/electronic sound as you prefer (0.10)
       - genre match (rock) (+2.0)
       - mood match (intense) (+1.0)
       - energy closeness (song=0.91, target=1.40) (+0.51)
       - acousticness fit (prefers produced sound, song=0.10) (+0.45)

2. Rebel Static by Static Front — Score: 3.94
     Why: matching genre (rock) + matching mood (intense) + produced/electronic sound as you prefer (0.08)
       - genre match (rock) (+2.0)
       - mood match (intense) (+1.0)
       - energy closeness (song=0.88, target=1.40) (+0.48)
       - acousticness fit (prefers produced sound, song=0.08) (+0.46)

3. Gym Hero by Max Pulse — Score: 2.01
     Why: matching mood (intense) + produced/electronic sound as you prefer (0.05)
       - genre mismatch (pop vs rock) (+0.0)
       - mood match (intense) (+1.0)
       - energy closeness (song=0.93, target=1.40) (+0.53)
       - acousticness fit (prefers produced sound, song=0.05) (+0.47)

4. Iron Verdict by Grave Chorus — Score: 1.07
     Why: produced/electronic sound as you prefer (0.02)
       - genre mismatch (metal vs rock) (+0.0)
       - mood mismatch (aggressive vs intense) (+0.0)
       - energy closeness (song=0.98, target=1.40) (+0.58)
       - acousticness fit (prefers produced sound, song=0.02) (+0.49)

5. Starlight Anthem by Nova Sisters — Score: 0.94
     Why: produced/electronic sound as you prefer (0.08)
       - genre mismatch (k-pop vs rock) (+0.0)
       - mood mismatch (triumphant vs intense) (+0.0)
       - energy closeness (song=0.88, target=1.40) (+0.48)
       - acousticness fit (prefers produced sound, song=0.08) (+0.46)
```

Note: `target_energy = 1.4` is outside the valid `0`–`1` range for `energy`, so `abs(song.energy - target_energy)` can exceed 1, making the energy component contribute *negative* points (visible here as it drops out of every "Why" line, since it never crosses the "notable" threshold). `score_song` has no input validation clamping `energy` to `[0, 1]`.

### `{"genre": "ambient", "mood": "chill", "energy": 0.25, "likes_acoustic": True}` — adversarial: forced near-tie

```
============================================================
Top 5 Recommendations for {'genre': 'ambient', 'mood': 'chill', 'energy': 0.25, 'likes_acoustic': True}
============================================================

1. Spacewalk Thoughts by Orbit Bloom — Score: 4.43
     Why: matching genre (ambient) + matching mood (chill) + energy closely matches your target (0.28 vs 0.25)
       - genre match (ambient) (+2.0)
       - mood match (chill) (+1.0)
       - energy closeness (song=0.28, target=0.25) (+0.97)
       - acousticness fit (likes acoustic, song=0.92) (+0.46)

2. Quiet Orbit by Orbit Bloom — Score: 4.42
     Why: matching genre (ambient) + matching mood (chill) + energy closely matches your target (0.22 vs 0.25)
       - genre match (ambient) (+2.0)
       - mood match (chill) (+1.0)
       - energy closeness (song=0.22, target=0.25) (+0.97)
       - acousticness fit (likes acoustic, song=0.90) (+0.45)

3. Library Rain by Paper Lanterns — Score: 2.33
     Why: matching mood (chill) + energy closely matches your target (0.35 vs 0.25) + strong acoustic feel (0.86)
       - genre mismatch (lofi vs ambient) (+0.0)
       - mood match (chill) (+1.0)
       - energy closeness (song=0.35, target=0.25) (+0.90)
       - acousticness fit (likes acoustic, song=0.86) (+0.43)

4. Midnight Coding by LoRoom — Score: 2.19
     Why: matching mood (chill) + energy fairly close to your target (0.42 vs 0.25) + strong acoustic feel (0.71)
       - genre mismatch (lofi vs ambient) (+0.0)
       - mood match (chill) (+1.0)
       - energy closeness (song=0.42, target=0.25) (+0.83)
       - acousticness fit (likes acoustic, song=0.71) (+0.35)

5. Wildflower Fields by Amber Hollow — Score: 1.39
     Why: energy closely matches your target (0.30 vs 0.25) + strong acoustic feel (0.88)
       - genre mismatch (folk vs ambient) (+0.0)
       - mood mismatch (dreamy vs chill) (+0.0)
       - energy closeness (song=0.30, target=0.25) (+0.95)
       - acousticness fit (likes acoustic, song=0.88) (+0.44)
```

Note: "Spacewalk Thoughts" and "Quiet Orbit" land within 0.01 of each other (4.43 vs 4.42) rather than an exact tie. If two songs ever do score identically, Python's stable sort means the one appearing first in `songs.csv` wins — an implicit, undocumented tie-break rule.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran.

### Lowering the genre weight from 2.0 to 0.5

For the starter pop/happy/0.8 profile, dropping genre from +2.0 to +0.5 let "Rooftop Lights" (indie pop, but a mood + energy match) climb past "Gym Hero" (a pop genre match with the wrong mood) into 3rd place. It is exactly the "over-prioritizing genre" bias called out earlier, and it goes away once genre isn't weighted so heavily.

But the same change did *nothing* to the rock/intense profile's top 5: "Storm Runner" and "Rebel Static" both dropped from 4.44 to 2.94, but stayed tied for 1st, because nothing else in the catalog was close enough on mood and energy to overtake them even without the genre boost. So how much lowering the genre weight changes things depends on whether a "close but wrong genre" song is waiting in the wings because it isn't an automatic fix everywhere.

### Adding valence into the score

We added a fifth component, valence closeness, using the `target_valence` field that already exists on every profile but was never scored, worth up to +0.5, the same way energy closeness works.

For the starter profile (`target_valence` defaults to 0.5), the top 4 songs didn't move, but 5th place flipped from "Rebel Static" (a moodier rock track) to "Night Drive Loop" (whose valence sits closer to neutral), result in a new song entered the top 5 purely because of the new signal. Then we reran the same profile with `target_valence: 0.3` (someone who wants a slightly less upbeat pop song), and 5th place flipped right back to "Rebel Static" which confirming the new component actually responds to what the listener says, instead of just padding every score by the same amount.

### How different user types behave

I ran a dozen profiles through the real, unmodified formula (see [Sample Recommendation Output](#sample-recommendation-output) above) already showed it clearly: listeners whose favorite genre and mood are well represented (pop, lofi, rock, jazz) get confidently differentiated top 5s, while listeners with rare or unrepresented tastes get thin, mostly default-driven results. See the "Note:" comparisons under each profile in [Sample Recommendation Output](#sample-recommendation-output) above, and the model card's [Comparing profiles side by side](model_card.md#comparing-profiles-side-by-side), for the details.

---

## Limitations and Risks

Summarize some limitations of your recommender.

- **Tiny, uneven catalog**: only 20 songs total, and 8 of the 13 genres and 8 of the 12 moods only have one song each, so most listeners get very few real genre/mood matches to draw from.
- **All-or-nothing genre/mood matching**: a "close enough" label (`indie pop` vs `pop`, `relaxed` vs `chill`) earns zero credit, the same as a totally wrong genre — the system can't recognize near-misses, only exact ones.
- **Acoustic preference is boolean, not a target**: `likes_acoustic` only rewards leaning fully acoustic or fully produced; there's no way to ask for "somewhat acoustic."
- **No real personalization or listening history**: it only ever considers one static profile per run, it doesn't learn from what you skip or replay, and it can't balance multiple listeners' tastes at once, unlike an actual streaming app.
- **Tempo, valence, and danceability aren't used**: those fields exist in the data but aren't part of the scoring formula, so real parts of a song's feel, how fast it is, how upbeat it sounds, how danceable it is, don't factor into recommendations at all right now.
- **No understanding of lyrics, language, or artist context**: it only ever compares labels and numbers, so it can't tell you why a song *sounds* the way it does or account for anything about the words, the language, or who's performing it.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Working through this project made it clear that a recommender doesn't need anything mysterious to turn data into predictions, it just needs a consistent way to compare a listener's stated preferences against a song's own attributes and add the results into a single number. Our system does that with two different styles of comparison: genre and mood are checked for an exact match and either earn full credit or nothing, while energy and acoustic sound are measured by how close they are to what the listener asked for, so a song doesn't have to be a perfect match to still score well. Once every song has a score, the actual "recommending" part is just sorting that list from highest to lowest, there's no deeper reasoning happening behind it, the ranking *is* the prediction.

That simplicity is also where bias and unfairness can quietly creep in. Because our catalog has far more songs in a few popular genres and moods than in the rest, listeners whose taste lines up with pop, lofi, chill, or intense get rich, varied recommendations, while listeners into something like metal, reggae, or k-pop get handed the same single song over and over, not because the system understands their taste, but because that's the only genre-matched option it has. We also saw how the same kind of small, invisible assumption behind fixing real bugs, treating "Pop" and "pop" as different genres, or reading a stray "no" as a "yes", could just as easily be exactly the sort of quiet unfairness a real app might ship if nobody stress-tested it with unusual profiles. It changed how I think about apps like Spotify: behind the friendly "recommended for you" screen is a system that depends entirely on having enough good data and careful matching rules for every kind of listener, not just the popular ones.


