# Svaha: Update Log

#### Created at: 1:37 AM on November 18, 2025 at Home

---

### 1:39 AM | November 18, 2025 | Tuesday | Home

## KivyMD vs Flutter for Backtesting MVP

<u>KivyMD</u>
**Pros**

1. Faster to prototype, frictionliess integration with python backend
2. Useful for future python application ideas (of which there are always plenty)
3. local sqlite db usage
4. Easy files IO integration
5. will have UI perfected when it's time for flutter

**Cons**

1. Will have to repeat the whole UI process for flutter final product (but works out since we might have had to build a new project anyway to remove artefacts)
2. Never done before
   2.1. But same goes for Flutter. Last used properly in 2021, so long forgotten.
   2.2. All heavy-lifting will be done by Gemini anyway. So what gives.

<u>Flutter</u>
**Pros**

1. One time coding.
2. Practice of syntax while building.

**Cons**

1. Artefacts from development and trial periods might persist in polished contruction.
2. File IO integration is much harder, and has always been a pain since forever.
3. Will have to account for firestore 1.**COSTS** and 2. Integration Time
4. Now that development is local instead of Google IDX, doesn't entirely make sence if iPad is not the main device anymore.
   4.1. iPad has just as much free space as Mac SSD.
   4.2. Mac SSD can expand if ever needed with 1. Dock and 2. Extra SSD.
   4.3. Can't expand at all if iPad ever runs out of space.
5. iPad is much more complicated setup anyway because of Swift integration.

### Decision: Settled on KivyMD

---

---

### 5:35 PM | November 18, 2025 | Tuesday | Home

## Started working on Python MVP

1. Updated new code structure to github
2. Made skeleton project for KivyMD
3. Subscribed to Zerodha Historical API
4. Integrated Zerodha API with project
5. integrated auto-project restart in project on code-changes without restarting debug session
6. Persisting Zerodha login across debug sessions
