# Wicketle

A daily guess-the-IPL-player game. Every player who made an IPL playing XI from 2008 to 2026 (809 players) can be guessed.

There is one daily puzzle, in **Full Toss** mode (key `normal`) (players with 50+ IPL matches, 187 players). It has the stats, streak and archive. The other modes are **practice modes**, with a new random player every game:

| Mode | Answer pool | Players | Who you can guess |
|---|---|---|---|
| Full Toss (daily, key `normal`) | 50+ IPL matches | 187 | Full Toss players only |
| Good Length (key `medium`) | 20+ IPL matches | 348 | Good Length players only |
| Yorker (key `hard`) | every IPL player | 809 | any IPL player |
| Spot the Star | hand-picked legends in `data/iconic.txt` | 79 | Spot the Star players only |
| 2026 season | played in IPL 2026 | 202 | any IPL player |

- **Daily answer:** each day's player is an independent seeded random pick from the full Normal pool (no fixed cycle), so the same player can come up again on a later day, but never two days running. Day 0 = 23 Nov 2026 = Puzzle #1. Everyone gets the same player on the same local date.
- **Spot the Star** (mode key `iconic`): edit `data/iconic.txt` (one name per line, spelled as in `data/players.json`) and rebuild. The build stops with an error if a name isn't found.

## How it works

- **Columns** (one header row above the board; tiles show values only, and with all columns shown, phones swipe the board sideways with the name column pinned): Player (name tile: green only when correct), Country, Role, Team (last franchise), Age, Debut season, Matches, Runs, Top score, Wickets, Best bowling, Titles.
  - Age is worked out live from the birth date (age at death for deceased players, marked †). Yellow when within 2 years. A grey-blue `?` tile means one of the two players has no birth date.
- **Feedback:** green = correct, yellow = close or partly right, red = wrong. ▲/▼ shows whether the answer is higher or lower.
  - Role is yellow when roles overlap (all-rounder vs batter/bowler, keeper vs batter).
  - Team is yellow when the two players share any franchise in their careers.
  - Numbers are yellow within 2 seasons / 15 matches / 300 runs / 15 runs of the high score / 15 wickets / 1 title.
  - Best bowling is yellow with the same wicket count; ▲ means the answer's figure is better. A `*` marks a not-out high score.
- **Daily answer:** a fixed seeded shuffle of each mode's pool (different seeds per mode), indexed by days since 23 Nov 2026 (Puzzle #1). Everyone sees the same player on the same local date. Each mode cycles through its whole pool before repeating.
- **Storage:** today's guesses, stats, streaks and the colour-blind setting are saved in `localStorage`. No backend is needed.
- **Guide sections** below the board: Colour guide, How to play (step by step), What each attribute means, Tips & strategy, Rules, About.
- **Less stats switch** in the header, off by default. Off: all 12 columns show. On: Debut, Matches, Top score, Best bowling and Titles are hidden, leaving 7 tiles (Player, Country, Role, Team, Age, Runs, Wickets) that fit a phone without swiping. The choice is remembered (`crickdle:less`), and the share grid matches the columns shown.
- **Dark mode switch** in the header. It follows the device setting until pressed, then remembers the choice.
- **Extras:** share (emoji grid copied to clipboard), stats and guess distribution, unlimited Practice mode, a colour-blind palette, and light and dark themes.

## Project layout

```
index.html              the built game (single file, data inlined) — deploy this
src/template.html       page source; data is injected at /*__DATA__*/
data/stats.json         per-player stats computed from Cricsheet
data/dob_verified.tsv   birth dates for 232 players (from the 2024 player file in the IPL-DATASET repo)
data/dob_curated.tsv    birth dates added by hand: id, YYYY-MM-DD or YYYY, '?' = unsure, optional death date
data/meta.tsv           curated: cricsheet_id, full name, country, role override, "?" = name to verify
data/players.json       merged data (same as what's inlined)
scripts/build_stats.py  Cricsheet match JSON -> data/stats.json
scripts/roles.py        role inference rules (keeper / batter / bowler / all-rounder)
scripts/build_site.py   stats + meta + template -> index.html
```

## Updating after a new IPL season

1. Download `ipl_json.zip` from https://cricsheet.org/downloads/ and unzip it into a folder.
2. `python3 scripts/build_stats.py <unzipped_folder> data/stats.json`
3. `python3 scripts/build_site.py`. If new players appear, the script stops and lists the Cricsheet IDs missing from `data/meta.tsv`. Add a line for each (`id<TAB>Full Name<TAB>COUNTRY<TAB>optional role`) and run it again.

Note: adding players changes the length of the daily order, which reshuffles future answers. Keep `EPOCH` in `src/template.html` as is, and add new players after the season ends if you don't want mid-run surprises.

## Deploying

The game is a static site. Drag the folder (or just `index.html`) into Netlify Drop, Vercel, Cloudflare Pages or GitHub Pages. No build step is needed on the host.

## Data and credits

Match data comes from [Cricsheet](https://cricsheet.org), released under the Open Data Commons Attribution License (ODC-BY). Keep the credit line in the footer. Full names, countries, a few role overrides and most birth dates were added by hand. 132 birth dates are flagged `?` and 56 players have none. Rows marked `?` in `meta.tsv` are names worth double-checking.

## Publishing checklist
- Open `config.js` (in the top folder, next to `index.html`) and set `contactEmail` to show the corrections email in About, Privacy and the footers. It stays hidden while empty. `config.js` holds the settings for the home page and every game; the build only creates it if it's missing, so your settings are never overwritten.
- The About section and the footer credit Cricsheet (ODC-By) and the IPL-DATASET mirror (MIT), and state that Wicketle is unofficial and not affiliated with the IPL, BCCI or any team. Keep these when you change the page.
- Birth dates flagged `?` in `data/dob_curated.tsv` are skipped by the build, so those players show a "?" age. To restore one, put a confirmed date in `dob_verified.tsv`.
- Country flags are simplified inline SVG drawings (the `FLAG` map in the template). A new country needs a new entry there, or it shows the code without a flag.

## Site layout
- `index.html` is the home page (copied from `src/home.html`). It also holds the About and Privacy sections; the games link to them. It shows a short overview and a play button for each game.
- `player/index.html` is the Player of the Day game (built from `src/template.html`). It links back to the home page with the logo and the home icon, and accepts `?mode=normal|medium|hard|iconic|season`.
- To add a game: put it in its own folder (for example `scorecard/index.html`) and add an entry to the `GAMES` list near the top of the script in `src/home.html`. Keep localStorage keys under `crickdle:` with a prefix of your own for the new game.

## Archive
The Archive button opens a calendar of every daily puzzle since Puzzle #1 (23 Nov 2026). Tap a date to play it. The daily history is kept in `localStorage` under `crickdle:hist:normal`: one entry per puzzle day, `{g: [player ids], done, won, a: 1}` where `a` marks a game played from the archive after its day. Stats and streaks are worked out from this history and count only games played on their own day.

## Google sign-in (optional)
Sign-in uses Google Firebase (free Spark plan). It stays switched off, with no account button, until you add your project's settings.

1. Go to https://console.firebase.google.com, click **Create a project**, name it `wicketle`, and turn Google Analytics off (not needed).
2. **Build → Authentication → Get started → Sign-in method → Google → Enable**. Pick a support email and save.
3. **Authentication → Settings → Authorized domains → Add domain**: `nannukalapala2004-svg.github.io` (and your custom domain later).
4. **Build → Firestore Database → Create database**. Choose a location near your players (for India, `asia-south1` Mumbai) and start in **production mode**.
5. In Firestore, open the **Rules** tab, replace everything with the contents of `firestore.rules` from this repository, and click **Publish**.
6. **Project settings (gear icon) → General → Your apps → Web (`</>`)**. Register an app called `wicketle` (no Hosting). Copy the `firebaseConfig` object it shows.
7. Open `config.js` and replace `firebase: null` with `firebase: { ...the object you copied... }`, then publish. No rebuild is needed.

The web config (apiKey and so on) is not a secret: it only identifies the project. The Firestore rules are what keep each player's history private to them.

Each signed-in player has one document, `users/<their uid>`, holding `{hist: {<mode>: {<day>: entry}}, updated}`. On sign-in the device's history and the account's history are merged (a finished game beats an unfinished one; a game counts as daily if any device played it on its day). After that, every guess is saved to the account.

Note: saved progress uses `localStorage` keys starting `crickdle:` (the game's earlier name). They are kept on purpose so players don't lose their history; don't rename them.

## Career Path (`path/`)
A second game with two modes, each with its own daily puzzle (resets at local midnight) and unlimited practice:
- **Who's the player?** Shows an IPL legend's career path (every franchise he played for, in order, with seasons). Guess the player in 6 tries. Each guess shows that player's path coloured against the answer (green same team in the same place, yellow team in the path elsewhere, red not in the path). Wrong guesses unlock clues: country, role, matches, runs/wickets, initials.
- **Build the path.** Shows the player; fill in the franchise for each stint (seasons shown on each slot; teams that didn't play in those seasons are disabled). 6 tries, Wordle-style colours, greens carry over.

Only Spot the Star players (`data/iconic.txt`) are used, as answers and as guesses. Answers are the legends who played for 2+ franchises (66; Build the path uses those with 2–7 stints). Daily answers are seeded random picks, never the same two days running.

Data: `scripts/build_paths.py <cricsheet json dir> data/paths.json` builds each player's season-by-season franchise path (the franchise he played for each season, grouped into stints; seasons in a squad without playing aren't included). `data/flags.json` holds the flag drawings shared with Player of the Day. `scripts/build_site.py` builds `path/index.html` from `src/path.html`. Progress is stored under `crickdle:cp:` in localStorage. Google sign-in sync doesn't cover Career Path yet.

## The Over (`over/`)
Daily IPL trivia: six multiple-choice questions, one per ball of the over, the same for everyone each day (resets at local midnight), plus unlimited practice overs. After each answer the right one and a fact are shown; at the end the score (X/6), a review of all six and a share grid appear on the page.

Every question is generated from the data, never written by hand, so answers match the records the site uses. Question types: IPL champion of a season, runner-up, Player of the Match in a final, final venue, the season's top run-scorer and wicket-taker, most career runs / wickets / matches among four players, whose highest score is N, who debuted in a year, and which team a player played for in a season. A season is never asked about twice in one over.

Data: `scripts/build_trivia.py <cricsheet json dir> data/trivia.json` computes each season's champion, runner-up, final venue, final XIs, Player of the Match and the top six run-scorers and wicket-takers. Career questions use players with 50+ IPL matches. `scripts/build_site.py` builds `over/index.html` from `src/over.html`. Progress is stored under `crickdle:over:`. Season leaders were checked against the official Orange and Purple Cap winners for 2008–2025. Totals come from Cricsheet's records and can occasionally differ by one from other sites.
