# Model Card: Music Recommender Simulation

## 1. Model Name

Give your recommender a short, descriptive name.

Example: **VibeFinder 1.0**

---

## 2. Intended Use

Describe what this recommender is designed to do and who it is for.

Prompts:

- What kind of recommendations does it generate (for example, top 3 to 5 songs)
- Who is the intended audience
- What assumptions does it make about the user
- Is this for real users or classroom exploration

---

## 3. How the Model Works

Explain your scoring approach in simple language.

Prompts:

- What song features are used (genre, mood, energy, etc.)
- What user preferences are considered
- How those inputs are turned into a score
- What changed from the starter logic

Avoid code here. Explain it like you are talking to someone who does not program.

---

## 4. Data

Describe the dataset the model uses.

Prompts:

- How many songs are in `data/songs.csv`
- What genres or moods are represented
- Did you add or remove any songs
- Whose musical taste this dataset mostly reflects
- Are there parts of musical taste missing in the data

---

## 5. Strengths

Where does your recommender seem to work well?

Prompts:

- User profiles for which it gives reasonable results
- Cases where the top results felt right or matched your intuition
- Patterns your scoring seems to capture correctly
- Any benefits of the model being simple and transparent

---

## 6. Limitations and Bias

Where does the system struggle or behave unfairly?

Prompts:

- Important features it does not consider
- Genres or moods that are underrepresented
- Cases where it overfits to one preference (for example, always favoring energy)
- Whether it treats all users as if they have the same taste shape
- Ways the scoring might unintentionally favor some users over others

---

## 7. Evaluation

How did you check whether the recommender behaved as expected?

Prompts:

- Which user profiles you tested
- What you looked for in the recommendations
- What surprised you
- Any simple tests, comparisons, or reasoning checks you ran
- If relevant, how your outputs compare to recommendations from real apps

No numeric metrics are required unless you created them.

---

## 8. Future Work

If you had more time, how would you improve this recommender?

Prompts:

- Additional features or user preferences
- Better ways to explain why each recommendation was selected
- Improving diversity among top results
- Handling more complex or mixed tastes
- Support for multi-user or group recommendations

---

## 9. Personal Reflection

A few sentences about your experience.

Prompts:

- What you learned about recommender systems
- Something unexpected or interesting you discovered
- How this changed the way you think about music recommendation apps
- Where human judgment still matters even when a model seems smart
