"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def print_recommendations(user_prefs, songs, k=5) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=k)

    print("\n" + "=" * 60)
    print(f"Top {len(recommendations)} Recommendations for {user_prefs}")
    print("=" * 60)
    for rank, (song, score, short_explanation, detailed_reasons) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} by {song['artist']} — Score: {score:.2f}")
        print(f"     Why: {short_explanation}")
        for reason in detailed_reasons.split("; "):
            print(f"       - {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Starter example profile
    starter_profile = {"genre": "pop", "mood": "happy", "energy": 0.8}

    # Additional profiles covering different genres, moods, energy levels, and acoustic preference
    lofi_chill_profile = {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True}
    rock_intense_profile = {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False}
    jazz_relaxed_profile = {"genre": "jazz", "mood": "relaxed", "energy": 0.4, "likes_acoustic": True}

    # Adversarial / edge case profiles — designed to probe or "trick" the scoring logic
    contradictory_profile = {"genre": "metal", "mood": "chill", "energy": 0.1, "likes_acoustic": True}
    mood_energy_conflict_profile = {"genre": None, "mood": "sad", "energy": 0.9}
    empty_profile = {}
    unrepresented_profile = {"genre": "classical", "mood": "euphoric", "energy": 0.5}
    case_sensitivity_profile = {"genre": "Pop", "mood": "Happy", "energy": 0.8}
    non_boolean_acoustic_profile = {"genre": "jazz", "mood": "relaxed", "energy": 0.4, "likes_acoustic": "no"}
    out_of_range_energy_profile = {"genre": "rock", "mood": "intense", "energy": 1.4}
    tie_profile = {"genre": "ambient", "mood": "chill", "energy": 0.25, "likes_acoustic": True}

    for user_prefs in (
        starter_profile,
        lofi_chill_profile,
        rock_intense_profile,
        jazz_relaxed_profile,
        contradictory_profile,
        mood_energy_conflict_profile,
        empty_profile,
        unrepresented_profile,
        case_sensitivity_profile,
        non_boolean_acoustic_profile,
        out_of_range_energy_profile,
        tie_profile,
    ):
        print_recommendations(user_prefs, songs, k=5)


if __name__ == "__main__":
    main()
