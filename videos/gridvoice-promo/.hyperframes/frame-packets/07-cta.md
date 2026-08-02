# Frame packet: 07-cta

## Project inputs

- Project: /home/user/Development/videos/gridvoice-promo
- Design tokens: /home/user/Development/videos/gridvoice-promo/frame.md
- RULES_DIR: /root/.claude/skills/hyperframes-animation/rules

## Assigned storyboard block

## Frame 7 — Every call, answered

- scene: The stage clears; the amber waveform draws itself flat into a line and assembles into the GridVoice lockup; closing claim snaps in beneath, held to the final frame
- voiceover: "Every call answered in seconds. Twenty-four seven. At any scale. GridVoice — the voice A-I agent for utilities."
- duration: 7.36s
- transition_in: zoom-through
- status: outline
- src: compositions/frames/07-cta.html
- type: cta
- persuasion: Value stacking on the rule of three, sealed by the brand lockup
- beat: inevitability + motivation
- blueprint: logo-assemble-lockup (Reproduce)
- sfx: impact-bass-2, chime
- asset_candidates:

Reproduce: elements clear the stage, then the mark draws itself on and the wordmark completes the lockup — extended with the closing claim as kinetic beats before the build.
Scene 1 (0.0–2.6s): on the deep night canvas, the closing claims snap in centered, beat by beat, each replacing the last via hard-cut (kinetic beat-slam → `kinetic-beat-slam`): "every call answered in seconds." → "24/7." → "at any scale." — each a full display-scale statement on its VO cue.
Scene 2 (2.6–5.0s): the last claim clears; the amber waveform draws itself dead-center (SVG self-draw → `svg-path-draw`), pulses once (live SVG internals → `svg-icon-enrichment`), then settles flat into a horizontal line that becomes the underline of the "gridvoice" wordmark as it assembles above (scale-swap handoff → `scale-swap-transition`) — the agent's voice resolving into the brand. Centered lockup, ~45% width, glow bloom behind (→ `ambient-glow-bloom`).
Scene 3 (5.0–7.36s): tagline "the voice ai agent for utilities" reveals per-word beneath (→ `dynamic-content-sequencing`); the lockup holds to the final frame — the video's long calm hold, subtle jitter only.

narrativeRole: Land the message verbatim and resolve the waveform motif into the brand mark — the calm close the whole video has been earning.
keyMessage: Every call answered in seconds — 24/7, at any scale. GridVoice.

## Selected motion rule: ambient-glow-bloom

---
name: ambient-glow-bloom
description: Un-triggered soft radial glow that blooms in behind a hero element and holds with a bounded idle breathe, or a single-pass traveling sweep across a surface. No click, no word-sync — it just blooms. Finite, deterministic, seek-safe.
metadata:
  tags: glow, bloom, ambient, radial, sweep, hero, presence, finite, un-triggered
---

# Ambient Glow Bloom

A soft radial glow that **blooms in behind a hero element** (card, logo, metric) and holds, giving it presence. Unlike `press-release-spring`'s click-triggered burst or `asr-keyword-glow`'s word-timed envelope, this glow is **un-triggered** — it blooms on the hero's settle and stays lit. Two forms: a **hero bloom** that swells behind a settling element then breathes, and a **traveling sweep** that translates a soft highlight across a surface exactly once.

## How It Works

A radial-gradient layer sits **behind** the hero (glow `z-index: 1`, hero `z-index: 2` — a glow in front occludes it), starting at `opacity: 0`. Over the bloom-in window it ramps `opacity: 0 → peak` with a gentle `scale` swell, timed so `BLOOM_START + BLOOM_DUR` lands on the hero's settle — glow and hero resolve as ONE beat ("powering on"), never glow-then-card. After bloom-in:

1. **Hero bloom** — a **bounded idle breathe** during the hold: a finite `ease: "none"` tween advances a `phase` proxy and `onUpdate` nudges opacity + scale a hair around peak (never a `yoyo` loop). `sin(0) = 0` → the breathe starts exactly at the bloom's resting state.
2. **Traveling sweep** — a narrow highlight band at one edge translates **once** across to the other (`x` off-surface to off-surface), clipped to the surface (`overflow: hidden`). One pass, no return — a repeating sweep reads as a loading shimmer, not a reveal accent (the shimmer-sweep variation below is the sanctioned exception).

Peak opacity stays restrained (**≤ 0.45 hard ceiling**) so the glow gives presence without washing the frame; the glow color is **darker + more saturated** than the element it backs (a same-hue, same-lightness glow disappears into the surface).

## Recipe

```html
<!-- inside a standard scene clip -->
<div class="bloom-stage">
  <div class="bloom-glow" id="bloom-glow"></div>
  <!-- z-index: 1; inset: GLOW_INSET (negative); background: {glowGradient} -->
  <div class="hero-card" id="hero-card">{HeroLabel}</div>
  <!-- z-index: 2 -->
</div>
<!-- sweep form: <div class="sweep" id="sweep"> inside the overflow:hidden surface -->
```

```js
// ── Form A: HERO BLOOM ── bloom in soft, landing on the hero's settle.
tl.fromTo(
  "#bloom-glow",
  { opacity: 0, scale: GLOW_START_SCALE },
  { opacity: GLOW_PEAK_OPACITY, scale: 1, duration: BLOOM_DUR, ease: "power2.out" },
  BLOOM_START,
);
// Bounded breathe during the hold — finite phase tween, NOT a yoyo loop.
const glow = document.getElementById("bloom-glow");
const phase = { p: 0 };
tl.to(
  phase,
  {
    p: Math.PI * 2 * BREATHE_CYCLES,
    duration: BREATHE_DUR,
    ease: "none",
    onUpdate: () => {
      const s = Math.sin(phase.p);
      glow.style.opacity = String(GLOW_PEAK_OPACITY + s * OPACITY_AMP);
      glow.style.transform = `scale(${1 + s * SCALE_AMP})`;
    },
  },
  BLOOM_START + BLOOM_DUR,
);

// ── Form B: TRAVELING SWEEP ── one finite pass, constant glide.
tl.fromTo(
  "#sweep",
  { x: SWEEP_START_X, opacity: 0 },
  { x: SWEEP_END_X, opacity: SWEEP_PEAK_OPACITY, duration: SWEEP_DUR, ease: "none" },
  SWEEP_START,
);
tl.to("#sweep", { opacity: 0, duration: SWEEP_FADE_DUR, ease: "power1.in" }, SWEEP_FADE_START);
```

## Variations

- **Bloom-and-hold** — for scenes <3s or a hero with its own idle, skip the breathe: the single `fromTo` is the whole recipe.
- **Pulse-on-arrival** — bloom slightly PAST peak (`GLOW_OVERSHOOT_OPACITY`, `scale: 1.06`), then a second adjacent tween eases down to a steady hold — one breath punctuating the landing, no ongoing loop.
- **Multi-hero relay** — stagger per-glow `BLOOM_START` by ~0.15–0.3s across a row; shrink `OPACITY_AMP` / `SCALE_AMP` per the `/√N` rule below.
- **Diagonal raked sweep** — angle `{sweepGradient}` (~105°) across a wordmark: the classic one-pass logo sheen. Narrower `SWEEP_WIDTH`, higher `SWEEP_PEAK_OPACITY`.

### Shimmer sweep (text-clipped status-phrase working-state)

The sweep re-aimed **inside type**: a soft highlight gradient clipped into a status phrase ("Thinking…", "Analyzing dataset…") via `background-clip: text` travels left→right through the letterforms — the grey-on-grey shimmer that says _still working_. Unlike every other form here it legitimately **repeats while the status is live**: the repetition is diegetic working-state, not idle wobble (same defense as a blinking caret — the motion performs status). Two things keep it honest: it is **bounded** (one finite tween whose pass count is computed from the status window, never `repeat: -1`), and it is **killed at resolve** — the moment the status completes, the shimmer stops dead; a shimmer surviving into the answer beat turns a working indicator into decoration.

```js
// Status shimmer — N passes as ONE bounded tween. Killed at resolve.
const status = document.getElementById("status-phrase");
// CSS on #status-phrase: background: {shimmerGradient}; background-size: 300% 100%;
// -webkit-background-clip: text; background-clip: text; color: transparent;
const shimmer = { p: 0 };
const PASSES = Math.round(STATUS_DUR / PASS_PERIOD); // whole passes, computed up front
tl.to(
  shimmer,
  {
    p: PASSES,
    duration: STATUS_DUR,
    ease: "none",
    onUpdate: () => {
      const t = shimmer.p % 1; // 0→1 within each pass; percent axis inverted → left→right travel
      status.style.backgroundPosition = `${(1 - t) * 100}% 50%`;
    },
  },
  STATUS_START,
);
tl.set(status, { backgroundPosition: "100% 50%" }, STATUS_START + STATUS_DUR); // resolve: dead.
```

Keep it a whisper: `{shimmerGradient}` is the status text's own grey with one slightly-lighter band (highlight stop a step above the base, nothing near white); `background-size` ~300% keeps the band narrow in the glyphs; `PASS_PERIOD` 1.2–1.8s — slower reads as a sheen accent, faster as a spinner. Whole-number `PASSES` lands the band at its start position exactly at the kill frame, so the `tl.set` is visually a no-op. This is the working-state cousin of `gradient-text-sweep`: reach **here** when the sweep _means_ "in progress," **there** when the gradient is the typographic treatment itself.

## Values

| token                   | range / default                                        | notes                                                                      |
| ----------------------- | ------------------------------------------------------ | -------------------------------------------------------------------------- |
| GLOW_PEAK_OPACITY       | 0.15 (subtle) → 0.30 (default) → **0.45 hard ceiling** | higher washes the frame; a glow you consciously notice is too strong       |
| GLOW_INSET              | −200 to −450px (1920×1080)                             | negative so the halo extends past the hero; too small reads as a tight rim |
| GLOW_START_SCALE        | 0.80–1.0                                               | ≤1.0 — grow into place, never shrink                                       |
| BLOOM_DUR / BLOOM_START | 0.6–1.4s                                               | `BLOOM_START + BLOOM_DUR` ≈ the hero's settle frame                        |
| OPACITY_AMP / SCALE_AMP | 0.02–0.05 / 0.01–0.03 default                          | `PEAK + OPACITY_AMP ≤ 0.45`; push only when the glow is the sole motion    |
| BREATHE_CYCLES          | period 2.5–4s per breath                               | glow breathes slower than element breathing                                |
| SWEEP_WIDTH             | 15–35% of surface (grid) / 8–15% (wordmark)            |                                                                            |
| SWEEP_DUR               | 0.8–1.6s                                               | one deliberate pass — slow enough to read as light                         |
| SWEEP_PEAK_OPACITY      | 0.10 → 0.25 (default) → 0.40                           | same ≤ ~0.45 wash limit; tight sweeps tolerate the high end                |
| SWEEP_START_X / END_X   | fully off-surface both ends                            | no visible spawn/despawn mid-surface; fade reaches 0 as the band clears    |
| PASS_PERIOD (shimmer)   | 1.2–1.8s                                               | with whole-number PASSES                                                   |

## Critical Constraints

- **Glow peak opacity ≤ 0.45** — including breathe amplitude; default to the LOW end (0.15–0.30).
- **Glow behind, hero in front**; glow color darker + more saturated than the hero surface.
- **Land glow and hero as one beat** — before or after reads as two separate events.
- **Breathe is bounded, sweep is one pass** — the only sanctioned repetition is the shimmer sweep, bounded and killed at resolve.
- **Concurrent halos compound** — per-glow amps ≤ default `/√N`, stagger breathe periods (2.6s / 2.9s / 3.3s) so they don't pulse in lockstep.
- **Don't combine a `boxShadow` glow on the hero with this halo layer** — they compete and read muddy; the glow lives on the dedicated layer.

## See also

`sine-wave-loop` (hero breathes on scale/y while the glow breathes on opacity, out of phase) · `press-release-spring` (the click-triggered sibling — never both behind one element) · `counting-dynamic-scale` / `stat-bars-and-fills` (bloom behind a landing stat) · `center-outward-expansion` (sweep across the assembled grid) · `gradient-text-sweep` (the design-beat gradient counterpart).

## Selected motion rule: dynamic-content-sequencing

---
name: dynamic-content-sequencing
description: Auto-calculate timeline start/end times from content length + per-item duration config — longer content gets more screen time without hardcoded numbers.
metadata:
  tags: timeline, sequencing, dynamic, duration, content-aware, utility
---

# Dynamic Content Sequencing

A utility pattern (not a motion rule in itself) for scenes that show a SEQUENCE of items (cards, phrases, stats): each item's duration is computed from its content length + per-item config, and the sequencer assigns absolute start/end times automatically — no hardcoded offsets per item. Distinct from [discrete-text-sequence](discrete-text-sequence.md) (one text element changing states) — this rule swaps between distinct content blocks.

## How It Works

A content array of `{ eyebrow, title, body, speedFactor, hold }` entries is reduced once at build time into a flat `TIMELINE` of `{ …entry, start, end }` — duration per entry is `BASE_DURATION + body.length × SEC_PER_CHAR + hold`, so longer text earns more reading time. A single linear driver's `onUpdate` reverse-searches the active entry and swaps the DOM **only on transitions** (a `lastTitle` guard — per-frame `textContent` writes flicker in render); an optional progress bar fills 0→100% across the whole run.

## Recipe

```html
<!-- inside a standard scene clip (hyperframes-core) -->
<div class="display">
  <div class="eyebrow" id="eyebrow"></div>
  <div class="title" id="title"></div>
  <div class="body" id="body"></div>
  <div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
</div>
```

```css
.body {
  min-height: 160px; /* reserve space — content height varies; without this, layout jumps */
}
.progress-fill {
  height: 100%;
  width: 0%;
}
```

```js
// N entries, each with its own pacing (optionally a speedFactor multiplier);
// the final entry uses a larger hold (closing beat).
const CONTENT = [
  { eyebrow: "{eyebrow1}", title: "{title1}", body: "{body1}", hold: HOLD_MID },
  // …
  { eyebrow: "{eyebrowN}", title: "{titleN}", body: "{bodyN}", hold: HOLD_FINAL },
];

// Pre-compute absolute start/end ONCE — never in onUpdate.
let cumulative = 0;
const TIMELINE = CONTENT.map((entry) => {
  const dur = BASE_DURATION + entry.body.length * SEC_PER_CHAR + entry.hold;
  const start = cumulative;
  cumulative += dur;
  return { ...entry, start, end: cumulative };
});

function entryAt(time) {
  for (let i = TIMELINE.length - 1; i >= 0; i--) {
    if (time >= TIMELINE[i].start) return TIMELINE[i];
  }
  return TIMELINE[0];
}

const eyebrowEl = document.getElementById("eyebrow");
const titleEl = document.getElementById("title");
const bodyEl = document.getElementById("body");
const progressEl = document.getElementById("progress-fill");

const TOTAL_DURATION = cumulative + TAIL_PAD;
const driver = { t: 0 };
let lastTitle = "";

tl.to(
  driver,
  {
    t: TOTAL_DURATION,
    duration: TOTAL_DURATION,
    ease: "none",
    onUpdate: () => {
      const entry = entryAt(driver.t);
      // Swap content only on transitions — no per-frame DOM thrash
      if (entry.title !== lastTitle) {
        eyebrowEl.textContent = entry.eyebrow;
        titleEl.textContent = entry.title;
        bodyEl.textContent = entry.body;
        lastTitle = entry.title;
      }
      progressEl.style.width = `${(driver.t / TOTAL_DURATION) * 100}%`;
    },
  },
  0,
);
```

## Variations

- **Crossfade between items** — return BOTH adjacent entries during an overlap window (`time ≥ e.start − overlap && time ≤ e.end + overlap`, overlap ≈ 0.3s) and render them with opacities computed from distance to the boundary.
- **Per-item motion variation** — map an `entry.style` key to an existing rule per chapter (e.g. `3d-text-depth-layers` → `hacker-flip-3d` → `counting-dynamic-scale`); the sequencer only orchestrates timing.
- **Auto-extend composition duration** — you can set `data-duration` from the computed `TOTAL_DURATION` in script, but HF reads `data-duration` at composition load and setting it after init may not take effect — author the duration manually from a rough total.

### Accelerating cadence (geometric hold decay)

For rhetorical escalation — "everyone says…", a roll-call, a praise flurry — the beat grid itself accelerates: early entries hold ~1s (read speed), then windows shrink geometrically into a ~0.15–0.3s flurry, braking on an emphasis state before the resolve. The acceleration is pre-computed into the same flat `TIMELINE` — still content-driven, still deterministic, no speed-up tween anywhere:

```js
// Geometric decay on the hold, clamped at a flurry floor; the brake state holds longest.
const HOLDS = CONTENT.map((entry, i) => Math.max(FLURRY_FLOOR, HOLD_START * Math.pow(DECAY, i)));
HOLDS[CONTENT.length - 1] = HOLD_FINAL;

let cumulative = 0;
const TIMELINE = CONTENT.map((entry, i) => {
  // Past ~0.5s states are glanced as motion texture, not read —
  // drop the per-char term or you never reach flurry speed.
  const readable = HOLDS[i] >= READ_THRESHOLD;
  const dur = HOLDS[i] + (readable ? entry.body.length * SEC_PER_CHAR : 0);
  const start = cumulative;
  cumulative += dur;
  return { ...entry, start, end: cumulative };
});
```

Worked example — **praise-chip flurry**: ~16 short quotes hard-cut through a chip beside a pinned wordmark. First 3 states at `HOLD_START = 1.0` (each reads fully); `DECAY = 0.8` shrinks every following window until `FLURRY_FLOOR = 0.2` catches it (≈12 states over ~2.5s — a churn of acclaim, individually glanced); the longest phrase takes `HOLD_FINAL ≈ 1.6` as the brake before the closing lockup.

Values: `HOLD_START` 0.8–1.2s; `DECAY` 0.75–0.88 (higher = longer runway before the flurry bites); `FLURRY_FLOOR` 0.15–0.3s (below ~0.15s swaps strobe); `READ_THRESHOLD` ~0.5s; brake ≥ 4× the floor or the stop doesn't register as a beat. The 3–6 entry guidance relaxes here — 12–18 states are legal precisely because flurry states aren't individually read. The hard-cut discipline (`lastTitle` guard, instant swaps) is what lets 0.2s states render clean.

## Values

| token         | range                 | notes                                                                                                                 |
| ------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------- |
| BASE_DURATION | 0.6–1.5s              | minimum per entry regardless of length — even one-word entries get read time                                          |
| SEC_PER_CHAR  | 0.03–0.06 s/char      | ≈17–33 chars/sec; uniform across the sequence so the pace reads as one engine; lean high for wide-character languages |
| HOLD_MID      | 0.5–1.0s              | dwell on a non-final entry; `< HOLD_FINAL`                                                                            |
| HOLD_FINAL    | 1.0–2.0s              | climax dwell — must exceed HOLD_MID by a clear margin so the close reads as a beat                                    |
| SPEED_FACTOR  | 0.5–2.0 (default 1.0) | per-entry only; if every entry shares a factor, fold it into SEC_PER_CHAR                                             |
| TAIL_PAD      | 0.0–1.0s              | quiet beat after the last entry; prefer 0 when the next composition owns the breath                                   |
| CONTENT N     | 3–6 entries           | <3 isn't a sequence; >6 drags (accelerating cadence relaxes this — see above)                                         |

Reference: `../../examples/messaging-multi-phrase.html`.

## Critical Constraints

- **Pre-compute the TIMELINE once at build** — never recompute in `onUpdate`; the reverse search over the flat array is the whole per-frame cost.
- **DOM swap only on entry transition** (`lastTitle`/key guard) — per-frame `textContent` assignment flickers in HF render.
- **`min-height` on the body element** — without reservation, downstream elements (progress bar, brand) jitter as content height varies.
- **Sequential only** — for parallel tracks use a different reduction.
- **Titles fit one line at the chosen size; bodies fit inside `min-height` after wrapping.**

## See also

`discrete-text-sequence` (per-entry typewriter on the body) · `context-sensitive-cursor` (cursor color per chapter) · `vertical-spring-ticker` (animated word swap instead of hard cut) · `scale-swap-transition` (visual morph between entries).

## Selected motion rule: kinetic-beat-slam

---
name: kinetic-beat-slam
description: Percussive kinetic typography — short phrases slam in on a steady beat with distinct per-phrase entrances, optional rhythm chrome (metronome ticks, beat bar), then a locked finale.
metadata:
  tags: text, kinetic, typography, beat, rhythm, slam, percussive, punchy
---

# Kinetic Beat Slam

Short phrases hit one at a time on a **steady beat**, each with a _different_ entrance, then stack into a locked finale — the recipe for "punchy / rhythmic" text-forward pieces (taglines, manifestos, hype intros). The difference between generic and rhythmic is (1) one shared **onset array** driving every element, (2) **distinct** entrances per phrase rather than one reused helper, and (3) optional **rhythm chrome** that visibly keeps the beat.

## How It Works

A single tempo grid — `PULSE` seconds per sub-beat, `BEATS = [t0, t1, t2, …]` on that grid — is the rhythmic spine; every phrase entrance, accent, and chrome tick reads its time from it, so the piece locks to one pulse instead of drifting hand-tuned offsets. Each phrase gets a different transform axis (scale+blur slam / side snap / rise+rotate) with short attacks (0.35–0.6s on the hit), then the stack holds with a finite low-amplitude breath.

## Recipe

```html
<!-- inside a standard scene clip (hyperframes-core) -->
<div class="kbs-stage">
  <div class="kbs-line" id="p1"><span class="verb">Notice</span> more.</div>
  <div class="kbs-line" id="p2"><span class="verb">Decide</span> faster.</div>
  <div class="kbs-line" id="p3"><span class="verb">Act</span> now.</div>
</div>
<!-- optional rhythm chrome -->
<div class="kbs-metronome" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>
```

```css
.kbs-stage {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 120px 160px; /* title-safe margin */
}
.kbs-line {
  font-family: "Archivo Black", "League Gothic", sans-serif; /* embedded display face */
  font-size: 150px;
  line-height: 0.96;
  letter-spacing: -0.03em;
  color: #f5f5f5;
}
.kbs-line .verb {
  color: #ff5b2e; /* exactly one accent hue */
}
.kbs-metronome {
  position: absolute;
  bottom: 64px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 14px;
}
.kbs-metronome i {
  width: 6px;
  height: 28px;
  background: #ff5b2e;
  opacity: 0.25;
}
```

```js
// ONE tempo grid drives everything — phrases AND the metronome read it.
const PULSE = 0.4; // seconds per sub-beat
const BEATS = [PULSE * 1, PULSE * 5, PULSE * 9]; // phrase onsets, on the grid

// Distinct entrances per phrase (NOT one reused helper).
tl.fromTo(
  "#p1",
  { scale: 1.5, filter: "blur(16px)", opacity: 0 },
  { scale: 1, filter: "blur(0px)", opacity: 1, duration: 0.5, ease: "power4.out" },
  BEATS[0],
);
tl.fromTo(
  "#p2",
  { x: -320, opacity: 0 },
  { x: 0, opacity: 1, duration: 0.45, ease: "expo.out" },
  BEATS[1],
);
tl.fromTo(
  "#p3",
  { y: 90, rotation: 6, opacity: 0 },
  { y: 0, rotation: 0, opacity: 1, duration: 0.55, ease: "circ.out" },
  BEATS[2],
);

// Rhythm chrome: each tick flashes on the SAME grid, not a magic offset.
gsap.utils.toArray(".kbs-metronome i").forEach((tick, i) => {
  tl.to(tick, { opacity: 1, duration: 0.08, yoyo: true, repeat: 1, ease: "none" }, PULSE * (i + 1));
});

// Finale hold: floor (not ceil) so the repeat never overshoots data-duration;
// max(0,…) so a short hold never yields a negative repeat (GSAP reads negative as -1 = infinite).
const holdStart = BEATS[2] + 0.7,
  cycle = 1.6,
  holdDur = SCENE_DURATION - holdStart;
tl.to(
  ".kbs-stage",
  {
    scale: 1.01,
    duration: cycle / 2,
    ease: "sine.inOut",
    yoyo: true,
    repeat: Math.max(0, Math.floor(holdDur / cycle) - 1),
  },
  holdStart,
);
```

## Variations

- **Entrance easing by attack character** — `power4.out` hard slam ⭐ default hit · `expo.out` hardest snap (side-snaps, whip-ins) · `back.out(2)` overshoot pop (accents only, not body words) · `circ.out` heavy rise with momentum. Use **at least 3 distinct easings** across the piece.
- **Rhythm chrome alternatives** — a center beat bar or a `// label` monospace tag pulsing on-beat instead of the 5-tick metronome; mark any decorative that must survive a shader transition per `../../transitions/overview.md`.
- **Finale dressing** — stack + accent underline sweep ([css-marker-patterns](css-marker-patterns.md)); don't just leave the last phrase sitting.

## Values

| token             | range                | notes                                                                                        |
| ----------------- | -------------------- | -------------------------------------------------------------------------------------------- |
| BEATS spacing     | 1.2–1.8s             | <0.8s frantic, >2.5s loses the pulse; keep spacing even — it's a beat                        |
| entrance duration | 0.35–0.6s            | the hit must resolve before the next beat; exits ≤0.25s                                      |
| accent hue        | exactly 1            | the verbs; the rest mono white / near-black                                                  |
| display face      | 150px+, heavy weight | Archivo Black / League Gothic / Oswald — see `hyperframes-creative/references/typography.md` |

## Critical Constraints

- **One beat array, not scattered offsets** — every element times off `BEATS[]` / `PULSE`; this is the single biggest lever for "rhythmic".
- **Different entrance per phrase** — a reused `punchIn()` for all lines is the flat-but-competent tell. Vary the motion axis, reuse the ease _family_.
- **Finale repeat math**: `repeat: Math.max(0, Math.floor(dur / cycle) - 1)` — `Math.ceil` overshoots `data-duration` and trips the `gsap_repeat_ceil_overshoot` lint rule; a negative repeat is read by GSAP as `-1` (infinite).
- **No banned exit animations between scenes** — in a montage the _transition_ is the exit (`../../transitions/overview.md`); only a final scene may fade out.
- **Display font must be embedded** or it silently falls back at render — Anton / Bebas-as-literal are NOT embedded (`Bebas Neue` aliases to League Gothic; verify in `typography.md`).

## See also

`3d-text-depth-layers` (extruded depth on the slammed words) · `css-marker-patterns` (finale underline/circle) · `sine-wave-loop` (the finale breath) · `../adapters/gsap-easing-and-stagger.md` (easing vocabulary).

## Selected motion rule: scale-swap-transition

---
name: scale-swap-transition
description: Coordinated shrink-out + spring pop-in morph-like transition between two elements — no SVG path interpolation needed.
metadata:
  tags: transition, morph, scale, swap, spring, pop
---

# Scale-Swap Transition

Simulates a "morph" between two DOM elements by overlapping exit and entrance scale animations. Lighter weight than [card-morph-anchor.md](card-morph-anchor.md) (which morphs container dimensions — use that for SHAPE changes; this rule is for SAME-shape state swaps) and easier than SVG path interpolation.

At a single trigger, two coordinated tweens fire:

1. **Outgoing**: scale `1.0 → EXIT_SCALE` + opacity `1 → 0`, fast `power2.in` (rushing away).
2. **Incoming**: scale `EXIT_SCALE → 1.0` + opacity `0 → 1`, `back.out(BOUNCE_FACTOR)` (arriving with weight).

A small `OVERLAP` window during which both are mid-tween creates the morph illusion; the incoming sits on top via z-index so the outgoing's fade-tail doesn't bleed through.

## Recipe

```html
<!-- Both cards position: absolute; inset: 0 in one fixed-size wrapper — same
     footprint, same transform-origin: 50% 50%. Incoming starts opacity: 0,
     transform: scale(EXIT_SCALE), z-index above the outgoing. -->
<div class="swap-wrap">
  <div class="card outgoing" id="outgoing">{outgoingIcon} {outgoingLabel}</div>
  <div class="card incoming" id="incoming">
    {incomingIcon} {incomingLabel}
    <div class="sub" id="sub">{incomingSubline}</div>
  </div>
</div>
```

```js
// Outgoing: shrink + fade fast
tl.to(
  "#outgoing",
  { scale: EXIT_SCALE, opacity: 0, duration: EXIT_DUR, ease: "power2.in" },
  TRIGGER,
);

// Incoming: pops in with overshoot, starting OVERLAP before the exit finishes
tl.to(
  "#incoming",
  { scale: 1.0, opacity: 1, duration: ENTER_DUR, ease: `back.out(${BOUNCE_FACTOR})` },
  TRIGGER + EXIT_DUR - OVERLAP,
);

// Inner content reveals AFTER the incoming settles
tl.fromTo(
  "#sub",
  { opacity: 0, y: SUB_REVEAL_Y_PX },
  { opacity: 1, y: 0, duration: SUB_REVEAL_DUR, ease: "power3.out" },
  TRIGGER + EXIT_DUR + SUB_REVEAL_DELAY,
);
```

## Variations

- **Delayed inner content reveal** — the classic pattern above: morph the container, then reveal inner text once it settles; the 0.2–0.4 s gap lets the eye land on the new shape before reading.
- **Triple swap (3-state cycle)** — chain A→B→C with triggers `TRIGGER_AB` / `TRIGGER_BC`; each transition is its own tween pair, the previous incoming becoming the next outgoing. State-evolution narratives (early → mid → final labels).
- **Color-shift transition (no scale)** — for a flat morph between same-shape states, drop the scale and keep opacity + a brief background hue tween; less dramatic, more product-UI tone.

## Values

| token            | range                                 | notes                                                                                                  |
| ---------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| TRIGGER          | ≥ outgoing settled + a presence-dwell | the outgoing must "land" before transforming                                                           |
| EXIT_DUR         | 0.3–0.5 s                             |                                                                                                        |
| ENTER_DUR        | 0.45–0.7 s                            | longer than `EXIT_DUR` so the overshoot can settle                                                     |
| OVERLAP          | 0.1–0.2 s                             | >0.3 s both are clearly visible together (no morph); <0.05 s leaves a visible empty gap                |
| EXIT_SCALE       | 0.6–0.8                               | smaller exits feel dramatic but risk reading as "vanish" instead of "morph"                            |
| BOUNCE_FACTOR    | 1.4 soft · 1.8 firm · 2.2 cartoony    |                                                                                                        |
| SUB_REVEAL_DELAY | 0.2–0.4 s                             | reveals during the morph compete with the swap for attention                                           |
| BRAND_REVEAL_AT  | < TRIGGER                             | context (brand, eyebrow) sets the stage early; revealed AT the swap it competes with the headline beat |

## Critical Constraints

- **Incoming z-index ABOVE outgoing** — otherwise the outgoing's fade-tail (opacity 0.3–0.5) bleeds through and double-exposes the frame.
- **Both elements share `transform-origin: 50% 50%`** — different origins make the morph read as one thing teleporting elsewhere.
- **Bouncy ease ONLY on the incoming** — outgoing `power2.in`, incoming `back.out`; reversed, the swap feels mechanical.
- **Both cards `position: absolute; inset: 0`** in the same fixed-size wrapper (sized to fit both states; the wrap never resizes).
- **Don't `display: none` the outgoing** after the fade — leave it at `opacity: 0` so layout doesn't reflow.
- **Inner content reveals after the container settles**; **climax dwell ≥ 1 s** after the final state + subline land.

## See also

`press-release-spring` (a button press TRIGGERS the swap — cause and effect) · `card-morph-anchor` (shape-changing alternative) · `reactive-displacement` (when the replacement should read as a causal collision) · `sine-wave-loop` (idle breathing on the final state).

## Selected motion rule: svg-icon-enrichment

---
name: svg-icon-enrichment
description: Animate internal SVG elements (rotating hands, opening blades, pulsing dots, dash flows) to make icons feel alive without replacing them.
metadata:
  tags: svg, icon, animation, internal, micro-animation, pulse, rotation
---

# SVG Icon Enrichment

Treats an SVG icon as a composition of animated PARTS, not an opaque image. Each meaningful internal element (a clock hand, scissor blade, recording dot, data line) gets its own micro-animation, targeted by id. Distinct from [svg-path-draw](svg-path-draw.md) (which animates the OUTLINE drawing) — enrichment animates INTERNAL PARTS, ideally after the outline has drawn.

Four signature patterns:

| Pattern     | Use For                            | Math                                  | Tip                                |
| ----------- | ---------------------------------- | ------------------------------------- | ---------------------------------- |
| Rotation    | Clock, gear, loader, dial          | `rotate(deg cx cy)` attribute, linear | see the transform-center gotcha    |
| Oscillation | Scissors, wings, toggle            | `rotate(±sin·amp)` on opposing groups | opposite signs on the two parts    |
| Pulse       | Recording dot, heart, notification | `scale(1 + sin·amp)` + opacity        | ring lags dot by π/2 for ripple    |
| Dash flow   | Cutting line, data stream          | `strokeDashoffset` linear via time    | negative for L→R, positive for R→L |

## ❗ The transform-center gotcha

**For rotation around an explicit point inside an SVG, use the SVG `transform` ATTRIBUTE, not CSS transform**: `el.setAttribute("transform", `rotate(${deg} ${cx} ${cy})`)`. The CSS combination `transform: rotate(...)` + `transform-origin: 60px 60px` + `transform-box: fill-box` interprets the origin in the element's OWN **bbox-local** coordinates, NOT viewBox coordinates. For a thin `<line>` (whose bbox is the line's narrow envelope), `60 60` bbox-local is a point OUTSIDE the line — the hand flies along an off-center arc instead of rotating in place. Same trap for small inner shapes (a dot circle whose bbox is the small circle, not the full viewBox).

**Scaling around a center point**: same attribute route — `el.setAttribute("transform", `translate(${cx} ${cy}) scale(${s}) translate(-${cx} -${cy})`)`.

## Recipe

```html
<!-- inside a standard scene clip — named children are the animation targets -->
<svg class="icon-svg" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
  <circle cx="60" cy="60" r="50" fill="none" stroke="{accentColor}" stroke-width="6" />
  <line
    id="hand-min"
    x1="60"
    y1="60"
    x2="60"
    y2="22"
    stroke="{textColor}"
    stroke-width="6"
    stroke-linecap="round"
  />
  <line
    id="hand-sec"
    x1="60"
    y1="60"
    x2="60"
    y2="30"
    stroke="{recordColor}"
    stroke-width="3"
    stroke-linecap="round"
  />
  <circle cx="60" cy="60" r="6" fill="{textColor}" />
</svg>
<!-- pulse icon: #rec-ring + #rec-dot circles; dash-flow: a <line> with stroke-dasharray="14 12" -->
```

```js
// Pattern 1 — Rotation. Proxy tween → SVG transform attribute (explicit center, see gotcha).
const hand = document.getElementById("hand-min");
const minState = { deg: 0 };
tl.to(
  minState,
  {
    deg: 360 * MIN_REVOLUTIONS,
    duration: TOTAL_DURATION,
    ease: "none", // linear motion is the point
    onUpdate: () => hand.setAttribute("transform", `rotate(${minState.deg} 60 60)`),
  },
  0,
);
// second hand: same shape with SEC_REVOLUTIONS (visibly faster).

// Pattern 3 — Pulse. One phase proxy drives dot + ring, ring offset by π/2.
const dot = document.getElementById("rec-dot");
const ring = document.getElementById("rec-ring");
const pulse = { p: 0 };
tl.to(
  pulse,
  {
    p: Math.PI * 2 * PULSE_CYCLES,
    duration: TOTAL_DURATION,
    ease: "none", // sine handles the curve
    onUpdate: () => {
      const sD = 1 + Math.sin(pulse.p) * PULSE_DOT_AMP;
      const sR = 1 + Math.sin(pulse.p + Math.PI / 2) * PULSE_RING_AMP;
      dot.setAttribute("transform", `translate(60 60) scale(${sD}) translate(-60 -60)`);
      ring.setAttribute("transform", `translate(60 60) scale(${sR}) translate(-60 -60)`);
      ring.style.opacity = String(
        PULSE_RING_OPACITY_BASE + Math.sin(pulse.p) * PULSE_RING_OPACITY_AMP,
      );
    },
  },
  0,
);

// Pattern 4 — Dash flow. Linear offset tween on a dashed stroke.
const flowState = { offset: 0 };
tl.to(
  flowState,
  {
    offset: DASH_FLOW_TOTAL_OFFSET, // negative = L→R
    duration: TOTAL_DURATION,
    ease: "none",
    onUpdate: () => {
      document.getElementById("data-flow").style.strokeDashoffset = String(flowState.offset);
    },
  },
  0,
);
```

## Variations

- **Stroke draw → enrichment chain** — draw the outline first via [svg-path-draw](svg-path-draw.md) (phase 1, `0 → OUTLINE_DUR`), then start enrichment at `OUTLINE_DUR`: the icon "wakes up" after assembly.
- **Per-icon entry stagger** — for a row of icons, each icon's enrichment starts as it fades in, not synchronized.

## Values

| token                           | range                | notes                                                                                           |
| ------------------------------- | -------------------- | ----------------------------------------------------------------------------------------------- |
| MIN_REVOLUTIONS                 | 0.5–2.0              | avoid integer revolutions if the end frame is visible (lands back at start)                     |
| SEC_REVOLUTIONS                 | 4–10                 | > MIN × 3 or the speed difference doesn't read                                                  |
| PULSE_CYCLES                    | 2–4 over a 3–5s comp | ≥5 reads as anxious flicker; ≤1 reads as forgotten                                              |
| PULSE_DOT_AMP                   | 0.05–0.20            | 0.05 = breathing; 0.20 = throbbing                                                              |
| PULSE_RING_AMP                  | 0.04–0.12            | must be < PULSE_DOT_AMP or the ring overshadows the dot                                         |
| PULSE_RING_OPACITY_BASE / \_AMP | 0.4–0.6 / 0.3–0.5    | BASE − AMP ≥ 0 and BASE + AMP ≤ 1                                                               |
| DASH_FLOW_TOTAL_OFFSET          | ±100–400             | must be an integer multiple of the dash period (dash + gap) or the end frame shows a phase jump |

## Critical Constraints

- **The transform-center gotcha above** — SVG `transform` attribute for any rotation/scale around an explicit interior point; never CSS `transform-origin` + `transform-box: fill-box` on thin lines or small inner shapes.
- **No `requestAnimationFrame`** — like CSS animation, it desyncs from HF's frame-by-frame seek; continuous motion lives inside the timeline as linear proxy tweens.
- **Amplitudes subtle** — icons are decorative, not headlines; calibrate rotation speed against composition length, not absolute time.
- **Phase-offset the parts** — minute vs second hand at different speeds, ring lagging dot by π/2. Pure sync looks mechanical.
- **`stroke-linecap: round`** on flowing/dashed lines for clean dash edges.
- **Climax dwell ≥1s** — if the enrichment is the headline beat, the composition continues ≥1s after the most dramatic moment.

## See also

`svg-path-draw` (outline draws first, enrichment second) · `orbit-3d-entry` (orbiting items are enriched icons) · `sine-wave-loop` (the whole icon floats while internal parts animate).

## Selected motion rule: svg-path-draw

---
name: svg-path-draw
description: Animate SVG paths drawing progressively using stroke-dasharray and stroke-dashoffset.
metadata:
  tags: svg, stroke, draw, path, reveal, icon, vector
---

# SVG Path Draw

Reveals an SVG shape by animating its stroke as if a pen were tracing it. Two stroke properties together: **`stroke-dasharray = <pathLength>`** makes the entire path one dash; **`stroke-dashoffset`** starts at the path length (dash shifted fully out of view → invisible) and tweens to `0` (fully drawn). The length comes from the DOM API `path.getTotalLength()` — measured, never guessed.

Works on anything with a stroke: `<path>`, `<circle>`, `<rect>`, `<line>`, `<polyline>`, `<polygon>`, `<ellipse>`.

## Recipe

```html
<!-- inside a standard scene clip -->
<svg class="logo-mark" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <path id="bar-left" d="M 60 40 L 60 160" />
  <path id="bar-right" d="M 140 40 L 140 160" />
  <path id="bar-mid" d="M 60 100 L 140 100" />
</svg>
```

```css
.logo-mark path {
  fill: none; /* outline-only draw — a fill would appear immediately and ruin the reveal */
  stroke: {accentColor};
  stroke-width: 12;
  stroke-linecap: round; /* softer endpoints */
  stroke-linejoin: round;
}
```

```js
// Setup: measure each path and set its dash pattern. Real measured geometry, not a magic number.
document.querySelectorAll(".logo-mark path").forEach((p) => {
  const len = p.getTotalLength();
  p.style.strokeDasharray = `${len}`;
  p.style.strokeDashoffset = `${len}`;
});

// Stagger draws so the eye reads continuous motion — each segment starts at
// ~70-80% of the previous segment's duration, before it finishes.
tl.to(
  "#bar-left",
  { strokeDashoffset: 0, duration: SEGMENT_DRAW_DUR, ease: "power2.out" },
  SEG_1_START,
);
tl.to(
  "#bar-right",
  { strokeDashoffset: 0, duration: SEGMENT_DRAW_DUR, ease: "power2.out" },
  SEG_2_START,
);
tl.to(
  "#bar-mid",
  { strokeDashoffset: 0, duration: FINAL_SEGMENT_DUR, ease: "power2.out" },
  SEG_3_START,
);

// Companion wordmark fades in only after the last stroke settles.
tl.to(
  ".brand-line",
  { opacity: 1, duration: BRAND_FADE_DUR, ease: "power1.out" },
  BRAND_FADE_START,
);
```

## Variations

- **Ring starting at 12 o'clock** — `<circle>` / `<rect>` strokes start at 3 o'clock by default; rotate the element `-90deg` so a progress ring draws from the top:

```html
<circle
  cx="100"
  cy="100"
  r="60"
  id="ring"
  style="transform-origin: 100px 100px; transform: rotate(-90deg)"
/>
```

- **Linear (constant-speed) draw** — `ease: "none"` for a steady-rate "real pen" trace.
- **Draw then fill** — for filled shapes, tween `fillOpacity: 0 → 1` AFTER the stroke completes (requires `fill-opacity: 0` initially and a real `fill` in CSS):

```js
tl.to(
  "#path",
  { strokeDashoffset: 0, duration: SEGMENT_DRAW_DUR, ease: "power2.out" },
  SEG_1_START,
);
tl.to(
  "#path",
  { fillOpacity: 1, duration: FILL_FADE_DUR, ease: "power1.out" },
  SEG_1_START + SEGMENT_DRAW_DUR,
);
```

## Values

| token             | range                                   | notes                                                                                              |
| ----------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------- |
| SEGMENT_DRAW_DUR  | 0.3–0.8s                                | fast snap vs deliberate pen trace; >~1s feels sluggish for a logo reveal                           |
| FINAL_SEGMENT_DUR | 60–80% of SEGMENT_DRAW_DUR              | proportional to segment length — a short connector at full duration reads slower than its siblings |
| SEG_N_START       | previous start + 70–80% of its duration | reads as continuous motion, not N isolated animations                                              |
| SEG_1_START       | 0–0.4s                                  | a small ~0.2s lead-in lets the viewer settle before motion                                         |
| BRAND_FADE_START  | ≥ last stroke end (+ ~0.2s beat)        | earlier and the wordmark competes with the draw                                                    |
| BRAND_FADE_DUR    | 0.3–0.8s                                | snap (urgent) vs glide (premium)                                                                   |

Ease families are discrete choices: **stroke draws** use `power2.out` (a hand lifting at end of stroke) or `none` for constant speed — never `back.out` / `elastic.out` (pens don't bounce). **Fades** use `power1.out`.

## Critical Constraints

- **`fill: none`** for outline-only draws — otherwise the fill appears immediately.
- **Dasharray/dashoffset = the measured `getTotalLength()`**, set at setup; requires the SVG in the DOM (inline SVG is fine; a loaded `<image>` SVG is not).
- **Complex paths**: if `getTotalLength()` looks wrong, overestimate slightly (`len * 1.05`) — too large is invisible at animation start; too small clips the end.
- **Stagger multi-path draws at ~70–80%** of the previous segment's duration.

## See also

`svg-icon-enrichment` (internal parts animate after the outline draws) · `counting-dynamic-scale` (stroke draws an icon while a number counts up) · `hacker-flip-3d` (logo draws, wordmark decodes beneath).
