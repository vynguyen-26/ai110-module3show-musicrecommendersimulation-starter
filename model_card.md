# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
**YourTaste 4.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for.   

YourTaste 4.0 takes one listener's stated taste, favorite genre, favorite mood, a target energy level, and whether they like an acoustic sound, and ranks a small fixed catalog of 20 songs to hand back the top five matches with a short explanation for each. It assumes the listener can describe their taste using those exact labels, and that the genre or mood they pick actually shows up somewhere in the catalog, since it has no way to recognize a preference it's never seen before. It also only ever handles one listener's profile at a time, so it isn't built to balance a group's shared taste or learn from someone's actual listening history the way a real streaming app would. This is a classroom project meant to show how a simple, rule-based recommender works under the hood, not a tool meant for real listeners or a production-size music catalog.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Every song in the catalog has a genre, a mood, an energy level, and how acoustic versus produced it sounds, and the listener's profile states those same four things as their preferences. The model checks each song against those preferences one at a time: a big bonus if the genre matches exactly, a smaller bonus if the mood matches exactly, a partial bonus that grows the closer the song's energy is to what the listener asked for, and a small bonus depending on whether the song leans acoustic or produced in the direction the listener said they like. All of those bonuses get added up into one overall score per song, and the recommender just sorts every song by that score and hands back the top five with a short reason attached to each. The starter code only had empty placeholders for the scoring and ranking, so I filled in all of that math myself, and later added the plain-language "Why" explanation next to each pick along with a couple of fixes so typos like a capital letter or a stray word don't throw the matching off.

---

## 4. Data  

Describe the dataset the model uses.  

The catalog has 20 songs total. I added 10 more on top of the 10 that shipped with the starter project so there'd be a wider mix of genres and moods to test against. Even so, the mix isn't even: pop and lofi have three songs each and chill is the most common mood with four, but eight different genres and eight different moods only show up on a single song each. Energy and acousticness cluster at the extremes too, plenty of mellow, low-energy acoustic songs and plenty of loud, high-energy produced ones, but almost nothing in the middle. So tastes that land in that middle ground, or that match one of the one-song genres or moods, aren't well represented, and traits like tempo, valence, and danceability are tracked in the data but never actually used in the score, so those parts of someone's taste don't factor in at all yet.

---

## 5. Strengths  

Where does your system seem to work well  

The system works best for listeners whose favorite genre and mood are well represented in the catalog: pop, lofi, rock, jazz, and ambient fans all got a genre-and-mood-matched song at the very top, in an order that felt right once we looked at the numbers behind it. The energy-closeness scoring is one pattern that captures real taste well, it doesn't just hand a medium-energy listener the loudest song in the catalog, it actually rewards whatever sits closest to the energy level they asked for. The lofi/chill and jazz/relaxed profiles, which both asked for a specific genre plus low energy and an acoustic sound, pulled up genuinely mellow, acoustic-leaning songs in first and second place, which matched our intuition about what those listeners would actually want to hear. And now that the capitalization and truthy-string issues are fixed, small typos like "Pop" instead of "pop" or answering "no" to the acoustic question no longer throw off an otherwise reasonable set of recommendations.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

One weakness I found while testing edge-case profiles is that the recommender really only works well for tastes the catalog happens to have a lot of. Eight of the thirteen genres, things like metal, reggae, k-pop, and latin, only have one song each, so a listener who prefers any of those genres can never see more than a single genre-matched recommendation no matter how their mood or energy preferences change. Meanwhile pop and lofi fans, who each have three songs to pick from, get a noticeably more varied top five. We saw this clearly when testing a metal-fan profile: "Iron Verdict" was the only song that could ever earn the genre bonus, so it kept showing up as the lone genre match no matter what else we changed about the profile. In other words, for anyone whose favorite genre isn't well represented, the system isn't really learning their taste, it's just repeatedly surfacing the one song we happened to include in that genre.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

I tested the four "normal" profiles from the sample output first, then pushed further with a handful of deliberately weird oneslike an empty profile, a genre and mood that don't exist in the catalog, a profile with mismatched capitalization, and one where the genre, mood, and energy all pulled in different directions. For each one I checked whether the top few picks actually matched what that listener asked for, and whether the score explanations lined up with the numbers. A couple things caught me off guard is typing "Pop" instead of "pop" tanked a song's score just as hard as picking a totally wrong genre, and passing `"no"` as a string for `likes_acoustic` got treated as true, since Python only checks whether the string is empty. I also compared the empty profile against the made-up "classical" genre and got back the exact same top five for both, which is what tipped me off that the system can't tell "no preference" apart from "a preference it's never seen." None of this needed formal metrics, just running the profiles and reading the explanations closely enough to catch where they didn't add up.

### Comparing profiles side by side

**Happy Pop vs. Intense Rock.** These two flip genres completely but land on similarly high-energy, produced-sounding songs, just from different genres. Since both listeners asked for high energy and didn't ask for an acoustic sound, so the "vibe" of loud and polished carries across genre, even though the actual songs are totally different.

**Happy Pop vs. Chill Acoustic Lofi.** These two are basically opposites, and the recommendations show it: Happy Pop surfaces upbeat, radio-style pop, while Chill Lofi surfaces slow, guitar-and-piano tracks. Because this listener asked for low energy and specifically said they like acoustic instruments, so the system flips its picks in the exact direction.

**Chill Acoustic Lofi vs. Relaxed Acoustic Jazz.** Different genre, different mood, but almost the same "shape" of song comes back for both such as slow, soft, acoustic. It means the system is responding to how a song *sounds* (slow and unplugged) and not just stamping a genre label on it.

**Why does "Gym Hero" keep showing up for someone who just wants Happy Pop?** "Gym Hero" is tagged as pop, so it gets the same genre credit as any other pop song, and its energy level is close to what the "happy pop" listener asked for, so it earns most of the energy points too. It only loses credit on one thing ad that is its mood since it is "intense," not "happy." Two out of three matches is still enough points to land in the top five, even though a real person would probably say "this doesn't sound happy at all, it sounds like a workout song." The system doesn't actually understand what "happy" *feels* like, it just checks if the word "happy" is written on the song's label or not, and everything else about the song can still push it up the list even when that one word doesn't match.

**Contradictory Metal/Chill vs. Intense Rock.** With Intense Rock, the genre, mood, and energy all agree with each other, so the top rock songs win by a wide margin. With the made-up "metal fan who wants something chill and quiet" profile, the one metal song in the catalog is loud and aggressive, the opposite of chill, so even with its genre bonus it actually loses to three completely different genres that fit the "chill and quiet" request better.

**Empty profile vs. "classical, euphoric" profile.** These two came back with the exact same top five, which surprised me at first. It makes sense once you realize neither "classical" nor "euphoric" appears anywhere in the song catalog, so the system quietly gives up on both of those preferences and falls back to whatever's left. To this recommender, "I have no preference" and "I really want classical music" look identical, which isn't really fair to the second listener.

**"likes_acoustic: True" vs. "likes_acoustic: 'no'" (same jazz fan, otherwise identical profile).** Both versions agree on the top two songs, since genre and mood carry those regardless of acoustic taste, but the picks below that diverge: the "True" version leans toward the more acoustic songs left in the catalog, while the "no" version leans toward the more produced ones. That makes sense, since one listener is saying they enjoy acoustic instruments and the other is saying they'd rather hear something more produced, so the ranking should split in exactly that direction once the genre and mood matches are accounted for.

**"pop, happy" vs. "Pop, Happy" (same taste, just capitalized).** Both versions return the exact same top five songs in the exact same order. That makes sense from a listener's point of view: "Pop" and "pop" describe the same genre to a person, so someone who happens to type their favorite genre with a capital letter should get treated no differently than someone who types it in lowercase.

---

## 8. Future Work  

Ideas for how you would improve the model next.   

The next step is to actually use the song data we're already collecting but not scoring on, tempo, valence, and danceability, plus the `target_valence` field already sitting unused in every user profile, since those could pick up on parts of a listener's taste the current four-part formula just misses. I'd also want to replace the all-or-nothing genre and mood matching with something that gives partial credit for close labels, so "indie pop" counts a little bit toward a "pop" preference instead of scoring exactly the same as a totally unrelated genre, and pair that with explanations that mention near-misses too, not just exact matches. For diversity, I'd add a rule that keeps one song from showing up as the only real recommendation every single time for listeners whose favorite genre only has one entry in the catalog, so the system isn't just repeating the same track as their "personalized" pick. And since real listeners rarely have one clean genre and mood, letting someone list a few genres or moods with different priorities, or mark things they specifically want to avoid, would make the profiles feel a lot more like an actual person's taste.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Building this project taught me that a recommender system is really just a scoring and ranking rule underneath, nothing mysterious, just math applied consistently to every song. I noticed my formula actually uses two different kinds of comparison: genre and mood are matched exactly and either earn full credit or none at all, while energy and acousticness are measured by how close they are, so a song doesn't need to be a perfect match to still pick up partial credit. What surprised me most was how much the results depended on having enough data behind each preference, a listener whose favorite genre only had one song in the whole catalog basically got the same recommendation every time no matter what else about their taste changed, and small formatting slips, like typing "Pop" instead of "pop", could tank an otherwise perfectly good match. That changed how I think about real apps like Spotify: they need a huge, well-balanced amount of listening data behind every genre, mood, and vibe, not just to be more accurate, but because a system this literal will keep feeding people the same narrow slice of songs whenever it doesn't have enough examples of their actual taste, which is exactly the kind of thing that would make someone stop trusting the app.
