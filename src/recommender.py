import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: float = 0.5

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file into a list of dicts with numeric fields cast to float/int."""
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a song against user preferences per the Algorithm Recipe in README.md; returns (score, reasons)."""
    favorite_genre = user_prefs.get("genre")
    favorite_mood = user_prefs.get("mood")
    target_energy = user_prefs.get("energy", 0.5)
    likes_acoustic = user_prefs.get("likes_acoustic", False)

    reasons: List[str] = []
    score = 0.0

    if favorite_genre is not None and song.get("genre") == favorite_genre:
        score += 2.0
        reasons.append(f"genre match ({song['genre']}) (+2.0)")
    else:
        reasons.append(f"genre mismatch ({song.get('genre')} vs {favorite_genre}) (+0.0)")

    if favorite_mood is not None and song.get("mood") == favorite_mood:
        score += 1.0
        reasons.append(f"mood match ({song['mood']}) (+1.0)")
    else:
        reasons.append(f"mood mismatch ({song.get('mood')} vs {favorite_mood}) (+0.0)")

    energy = song.get("energy", 0.0)
    energy_points = 1.0 * (1 - abs(energy - target_energy))
    score += energy_points
    reasons.append(
        f"energy closeness (song={energy:.2f}, target={target_energy:.2f}) (+{energy_points:.2f})"
    )

    acousticness = song.get("acousticness", 0.0)
    if likes_acoustic:
        acoustic_points = 0.5 * acousticness
        reasons.append(f"acousticness fit (likes acoustic, song={acousticness:.2f}) (+{acoustic_points:.2f})")
    else:
        acoustic_points = 0.5 * (1 - acousticness)
        reasons.append(f"acousticness fit (prefers produced sound, song={acousticness:.2f}) (+{acoustic_points:.2f})")
    score += acoustic_points

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song, then returns the top k sorted from highest to lowest score."""
    judged = [(song, *score_song(user_prefs, song)) for song in songs]
    ranked = sorted(judged, key=lambda entry: entry[1], reverse=True)
    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]
