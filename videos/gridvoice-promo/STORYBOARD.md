---
format: 1920x1080
duration: 60s
message: "Every customer call answered in seconds — 24/7, at any scale"
arc: Hook → Pain → Product intro → Proof (the call) → Scale → Breadth → CTA
audience: utility executives and customer-experience leaders
mode: autonomous
music: calm confident minimal electronic underscore, dark storm atmosphere resolving into warm assured close
---

## Video direction

- palette system: from `frame.md` — night canvas (deep storm navy) is the ground everywhere; ink-light (near-white) carries display type; electric amber is the SOLE accent and belongs to the agent — the waveform, checked rows, key stats, the lockup. Chrome/labels in mono uppercase at low opacity. Never a second accent hue; never pure #000/#fff.
- motion grammar: smooth long-tail settles (`power3` default) — no bounce, no overshoot. Every frame reveals sequentially on its VO cues with the back ~50% carrying reveals; at t=0 only what the VO is saying enters. During holds: stillness, at most subtle jitter (`sine-wave-loop`, low amplitude). The amber waveform is the recurring carrier element — it appears in Frame 3, multiplies in Frame 5, and resolves into the lockup in Frame 7.
- rhythm / held frames: Frame 2 ends on a hard still (the 47:00 counter frozen — the pain reads in silence); Frame 7's back half is the video's long calm hold. Frames 4–6 are the busy middle; Frame 3 is measured — the turn breathes.
- negative list: no robot avatars, chat-bot icons, purple-blue "AI" gradients, bokeh, stock-photo textures; no browser chrome or real cursors; no bouncy eases; no slideshow (front-load-then-freeze) and no screensaver (independently floating elements); no infinite loops, randomness, or CSS keyframe motion (seek-safe core).

## Frame 1 — 2:14 AM

- scene: Storm-dark canvas; the timestamp "2:14 AM" lands in mono chrome, then massive lowercase display type snaps in beat by beat — the storm takes Maple Street
- voiceover: "Two fourteen A-M. A storm just took the power out on Maple Street."
- duration: 4.203s
- transition_in: cut
- status: outline
- src: compositions/frames/01-hook.html
- type: hook
- persuasion: Future pacing into the viewer's worst night — pain validation by scene-setting
- beat: tension
- blueprint: kinetic-type-beats (Adapt)
- sfx: riser, impact-bass-1
- asset_candidates:

Adapt: keep the full-screen statement-build signature (each phrase its own beat onto a locked finale); the "payoff" here is a lights-out dim, not a spring-pop — tension, not triumph.
Scene 1 (0.0–1.2s): near-black storm-navy field with a faint low-opacity hairline grid (3 depth layers: grid → vignette → type plane); the mono chrome timestamp "2:14 AM" types on with a caret upper-left (type-on with caret → `discrete-text-sequence` + `context-sensitive-cursor`) as the VO speaks it — small, alone, top-third.
Scene 2 (1.2–2.6s): massive lowercase display line "a storm just took" slams in centered via kinetic beat-slam (→ `kinetic-beat-slam`), ~55% of frame width, each word on its VO beat with a long-tail settle.
Scene 3 (2.6–3.7s): "the power out on maple street." completes the statement via per-word staggered reveal (→ `dynamic-content-sequencing`); on "out," the whole canvas dims a step and the grid flickers once — the lights going out (keyword glow inverted: a dim, not a bloom → `asr-keyword-glow`).
Scene 4 (3.7–4.2s): held read in the darker state; subtle jitter only (→ `sine-wave-loop`, low amplitude).

narrativeRole: Cold-open the story on the one moment every utility is judged by. No product, no brand — just the night and the outage.
keyMessage: This is the worst night of the year, and it starts now.

## Frame 2 — The 47-minute answer

- scene: Pain statements land alone; a hold-time counter ticks upward relentlessly to 47:00 beside "your call is important to us"
- voiceover: "Six thousand customers reach for the phone. And the phone says — your estimated wait time is… forty-seven minutes."
- duration: 6.869s
- transition_in: crossfade
- status: outline
- src: compositions/frames/02-pain.html
- type: pain_point
- persuasion: Pain agitation — the institutional non-answer dramatized as a number that keeps climbing
- beat: frustration + anxiety
- blueprint: kinetic-type-beats (Adapt)
- sfx: typing, impact-bass-2
- asset_candidates:

Adapt: keep the pain-statements-landing-alone signature; the second beat is a non-text element — the wait-time counter — carrying the climax, per the bank's "a beat may be a non-text element."
Scene 1 (0.0–1.9s): on the dark field, "6,000 customers" enters as a value-scaled counter (→ `counting-dynamic-scale`) counting 0→6,000 dead-center as the VO names it, display-scale, with "reach for the phone" landing beneath in body type on its cue (per-word staggered reveal → `dynamic-content-sequencing`). Centered, ~45% of frame.
Scene 2 (1.9–3.8s): the counter demotes upward (scale-swap → `scale-swap-transition`); the mono line "your call is important to us." types on with a caret (→ `discrete-text-sequence` + `context-sensitive-cursor`), deadpan, centered — the institutional voice in institutional chrome.
Scene 3 (3.8–5.9s): as the VO reaches "forty-seven minutes," a large wait-time counter ticks 00:00 → 47:00 with value-scaled growth (→ `counting-dynamic-scale`), the digits shifting from ink-light toward a hot amber as it climbs; label "ESTIMATED WAIT" in mono chrome above it. Asymmetric 60/40 against the demoted institutional line.
Scene 4 (5.9–6.87s): hard stop at 47:00 — the frame freezes on the number, completely still (the allocated held beat; no jitter — dead stillness is the point).

narrativeRole: Agitate the known pain: storm-scale call volume meets a hold queue. The ticking counter is a non-text beat inside the type relay.
keyMessage: On the night that matters most, the old way answers with a queue.

## Frame 3 — Meet GridVoice

- scene: The dark canvas calms; a steady amber voice-waveform blooms center; "Introducing GridVoice" hard-cuts through beats and resolves on the wordmark
- voiceover: "Introducing GridVoice — the voice A-I agent built for utilities. It answers on the first ring."
- duration: 6.059s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/03-intro.html
- type: product_intro
- persuasion: Negative contrast — instant answer against the 47-minute queue we just felt
- beat: relief + curiosity
- blueprint: kinetic-type-beats (Reproduce)
- sfx: riser, chime
- asset_candidates:

Reproduce: the "Introducing…" hard-cut name-drop resolving on the brand name — with the waveform planted as the brand's mark.
Scene 1 (0.0–1.2s): the storm grid settles to a calmer, slightly lifted navy; "introducing" lands alone in display lowercase via hard-cut (→ `discrete-text-sequence`), centered.
Scene 2 (1.2–2.8s): hard-cut to "gridvoice" at full display scale (~60% width); beneath it an amber waveform draws itself stroke-by-stroke (SVG self-draw → `svg-path-draw`) — the agent's mark arrives with its name. Centered hero, 3 depth layers (grid → glow → type/waveform).
Scene 3 (2.8–4.5s): the name demotes slightly; sub-line "the voice ai agent built for utilities" reveals per-word on its VO cue (→ `dynamic-content-sequencing`) in body type beneath the waveform.
Scene 4 (4.5–6.06s): on "first ring," the waveform pulses once — its bars animate a single finite swell (live SVG internals → `svg-icon-enrichment`) with a soft ambient glow bloom behind it (→ `ambient-glow-bloom`); then the frame holds, subtle jitter at most.

narrativeRole: Name the product as the answer to the pain, and plant the waveform motif that is the agent's visual identity for the rest of the video.
keyMessage: GridVoice answers instantly — that is the whole promise.

## Frame 4 — The call, handled

- scene: The 2:14 AM call as working theater — a conversation thread builds message by message while status rows land and check off: outage confirmed on the grid map, report filed, restoration ETA delivered
- voiceover: "It confirms the outage against the live grid map. Files the report. Gives a real restoration time. Done — in under a minute."
- duration: 8s
- transition_in: crossfade
- status: outline
- src: compositions/frames/04-call.html
- type: feature_showcase
- persuasion: Show-don't-tell proof — the machine visibly does the work of the call
- beat: trust + clarity
- blueprint: agent-progress-theater (Reproduce)
- sfx: click-soft, ping, whoosh-short
- asset_candidates:

Reproduce: trigger → working theater → receipt. The trigger is the incoming call chip; the receipt is the checked task list; rows arrive and CHECK OFF as the VO names each action.
Scene 1 (0.0–1.5s): an incoming-call chip ("Incoming · 2:14 AM · Maple St") slides in from the top on a long-tail settle (spring-pop entrance, smooth register → `spring-pop-entrance`) and seats upper-left; a reconstructed dark call-panel surface fades up as the stage — asymmetric 60/40: task rail left, a stylized grid-map region right (no browser chrome). 3 depth layers (canvas → panel → chips).
Scene 2 (1.5–4.0s): as the VO names each action, status rows land one-by-one in the left rail and check off with an amber badge flip (staggered sequential reveal → `dynamic-content-sequencing`; check states → `stat-bars-and-fills` fill register): "Outage confirmed — live grid map" (a ping blooms on the map region — ambient glow bloom → `ambient-glow-bloom`), then "Report filed."
Scene 3 (4.0–6.1s): "Restoration: 3:45 AM" row lands with a keyword glow on the time (→ `asr-keyword-glow`); a small camera zoom-to-target frames the rail's bottom row (→ `coordinate-target-zoom`).
Scene 4 (6.1–8.0s): on "Done," a receipt stamp row "Resolved · 0:52" checks off; the frame settles and holds still, subtle jitter only.

narrativeRole: Prove the promise on the single call we opened with. The state mutation — rows arriving and checking off — is the demo.
keyMessage: This is not a phone menu; it resolves the call end to end.

## Frame 5 — 2:16 AM, all of them

- scene: Pull back to scale — a count-up explodes from 1 to 4,800 simultaneous calls while small waveform ticks multiply across the dark frame; "zero hold time" lands as the payoff
- voiceover: "Two sixteen A-M: four thousand eight hundred more calls. Every one answered in seconds. Zero hold time."
- duration: 6.656s
- transition_in: crossfade
- status: outline
- src: compositions/frames/05-scale.html
- type: benefit_highlight
- persuasion: Statistical proof — storm-scale capacity said as one exploding number
- beat: awe + confidence
- blueprint: dataviz-countup (Reproduce)
- sfx: riser, impact-bass-1
- asset_candidates:

Reproduce: the cold-open counter burst — one statistic explodes upward in size while satellite elements fling outward to their marks, closed by a slow lean-in.
Scene 1 (0.0–1.3s): the mono timestamp flips "2:14 AM → 2:16 AM" via hard-cut token swap (→ `discrete-text-sequence`) top-third; a single small amber waveform tick sits center — one call.
Scene 2 (1.3–3.7s): as the VO hits the number, the counter explodes 1 → 4,800 as a value-scaled counter (→ `counting-dynamic-scale`) growing to ~50% of frame; simultaneously dozens of small waveform ticks assemble outward from the center to a deterministic scatter across the field (cluster→outward expansion → `center-outward-expansion`, index-derived positions — no randomness), each tick a call being answered. Layered-depth: far ticks smaller/dimmer.
Scene 3 (3.7–5.2s): "every one answered in seconds" lands beneath the number per-word on cue (→ `dynamic-content-sequencing`).
Scene 4 (5.2–6.66s): "ZERO HOLD TIME" stamps in mono caps with a keyword glow (→ `asr-keyword-glow`) and an ambient glow bloom behind the counter (→ `ambient-glow-bloom`); slow settle, then still.

narrativeRole: Turn one handled call into thousands — the scale beat the brief asked for, proving capacity during storm events.
keyMessage: It holds up exactly when call volume goes vertical.

## Frame 6 — By morning

- scene: Timestamps advance (3:41 AM restored · 8:02 AM billing · 9:15 AM scheduling) as capability cards cascade into a grid — restoration texts, billing answers, appointments, warm handoff
- voiceover: "By morning: restoration updates, billing questions, service appointments — and a warm handoff to your team when it matters."
- duration: 7.275s
- transition_in: push-slide LEFT
- status: outline
- src: compositions/frames/06-breadth.html
- type: benefit_highlight
- persuasion: Feature-to-benefit translation — breadth shown as one accumulating morning
- beat: ease + control
- blueprint: grid-card-assemble (Reproduce)
- sfx: whoosh-short, notification
- asset_candidates:

Reproduce: the staggered-cascade card assembly, each card arriving on its VO cue rather than as one dump; the timestamps ride the cards as mono chrome.
Scene 1 (0.0–1.6s): the canvas lifts one step toward a pre-dawn navy; "by morning" lands in display lowercase upper-left (per-word reveal → `dynamic-content-sequencing`); a mono timestamp "3:41 AM" ticks in with a card "Power restored — 4 minutes early · updates texted to every caller," sliding into the first grid slot on a long-tail settle (→ `spring-pop-entrance`, smooth register).
Scene 2 (1.6–5.0s): as the VO names each capability, cards cascade into a 2×2 grid (staggered cascade → `dynamic-content-sequencing`): "8:02 AM · Billing — 'why is my bill higher?' answered from the account" then "9:15 AM · Service — technician visit booked, window confirmed." Each card: mono timestamp chrome, body-type payload, hairline border. Full-width strip evolving to grid, 3 depth layers.
Scene 3 (5.0–6.1s): the fourth card "Warm handoff — full context to your team" lands with its amber left-edge accent and a keyword glow on "your team" (→ `asr-keyword-glow`).
Scene 4 (6.1–7.28s): grid holds; subtle jitter at most.

narrativeRole: Widen from the storm story to everyday breadth — the agent is not just for outages — while keeping the night-shift timestamp motif.
keyMessage: One agent covers the whole front line, around the clock.

## Frame 7 — Every call, answered

- scene: The stage clears; the amber waveform draws itself flat into a line and assembles into the GridVoice lockup; closing claim snaps in beneath, held to the final frame
- voiceover: "Every call answered in seconds. Twenty-four seven. At any scale. GridVoice — the voice A-I agent for utilities."
- duration: 7.36s
- transition_in: zoom-through
- status: animated
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
