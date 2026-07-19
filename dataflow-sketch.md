# Data Flow Sketch: Input → Process → Output

Planning sketch for `src/recommender.py` before implementation. Traces how a
single song moves from the CSV to a ranked recommendation list.

```mermaid
flowchart TD
    A["INPUT: user_prefs dict<br/>{genre, mood, energy, likes_acoustic}"] --> L

    CSV["data/songs.csv<br/>(20 rows)"] --> LS["load_songs(csv_path)<br/>→ List[Dict], numeric strings cast to float"]
    LS --> L{{"LOOP: for each song dict"}}
    A -.->|same prefs, reused each iteration| L

    L --> S1["score_song(user_prefs, song)"]

    subgraph judge [" judge ONE song "]
        G["genre match? +2.0 / +0"]
        M["mood match? +1.0 / +0"]
        E["energy closeness: +1.0 x (1 - |diff|)"]
        AC["acousticness fit: +0.5 scaled"]
        G --> SUM["sum → score"]
        M --> SUM
        E --> SUM
        AC --> SUM
        SUM --> REASONS["reasons list, e.g. 'genre matches pop'"]
    end

    S1 --> judge
    judge --> OUT1["(song, score, reasons)"]
    OUT1 --> ACC[("accumulate into results list")]
    ACC -->|next song| L

    L -->|all 20 scored| SORT["sort by score, descending"]
    SORT --> SLICE["take top k"]
    SLICE --> OUTPUT["OUTPUT: recommend_songs()<br/>List[(song, score, explanation)]"]
    OUTPUT --> PRINT["main.py prints title, score, 'Because: ...'"]
```

## Single-song trace

Sunrise City's CSV row (`pop, happy, energy=0.82, acousticness=0.18`) is
loaded as a dict, enters the loop, and is judged by `score_song`:

- genre: `pop == pop` → **+2.0**
- mood: `happy == happy` → **+1.0**
- energy closeness: `1 - |0.82 - 0.80|` → **+0.98**
- acousticness: low acousticness + `likes_acoustic=False` → **+0.41**
- total → **4.39**, with a `reasons` list explaining each component

That `(song, score, reasons)` tuple is appended to a results list alongside
the other 19 songs' tuples.

## Key point

`score_song` only ever sees **one song at a time** — it has no idea what the
other songs scored. Sorting/ranking is a separate second pass that can't
start until *every* song has a tuple in hand. That's the "judge one → rank
all" split described in the algorithm recipe.

## Weighting scheme (see prior discussion)

| Component | Type | Points | Formula |
|---|---|---|---|
| Genre match | binary | +2.0 | `2.0 if song.genre == favorite_genre else 0` |
| Mood match | binary | +1.0 | `1.0 if song.mood == favorite_mood else 0` |
| Energy closeness | continuous | up to +1.0 | `1.0 * (1 - abs(song.energy - target_energy))` |
| Acousticness fit | continuous | up to +0.5 | `0.5 * song.acousticness` if `likes_acoustic` else `0.5 * (1 - song.acousticness)` |

Max possible score: **4.5**.
