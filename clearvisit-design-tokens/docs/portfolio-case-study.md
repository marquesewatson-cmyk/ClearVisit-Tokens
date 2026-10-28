# Portfolio case study outline: ClearVisit design tokens

**How to use this.** Each section has suggested copy, the visuals to show, the decisions worth explaining, and the evidence that would strengthen it. Copy is written in first person for you to edit. Anything in *[brackets]* is yours to fill in. Every claim is labelled:

- **Done**: exists and was verified in this project
- **Concept**: designed but not built into a real product
- **Proposed**: future validation that has not happened

Do not add research findings, collaborators, metrics or adoption that didn't happen. The strongest version of this case study is honest about being a self-initiated concept with a rigorous technical core.

---

## 1. Project overview

**Copy:** "ClearVisit is a concept healthcare scheduling platform with two products: a mobile app where patients find and book appointments, and a desktop tool where coordinators manage provider calendars. I designed the token system that lets both share one visual language while each keeps the density its users need."

**Visuals:** Hero image of the patient booking screen beside the admin calendar, same status colors visible in both.

**Decisions to explain:** Why tokens first instead of screens first.

**Evidence:** Label clearly as a self-initiated concept project (*Concept*). Your role: *[sole designer / designer + AI assistant]*. Timeframe: *[fill in]*.

## 2. Design system challenge

**Copy:** "Scheduling products fail in predictable ways: 'confirmed' means one color in the app and another in the admin; statuses depend on color alone; a control sized for a mouse becomes a missed tap on a phone. I wanted a system where those decisions are made once and enforced, not remembered."

**Visuals:** A deliberately inconsistent "before" mock (two products, mismatched status chips) vs the unified "after". Label the "before" as illustrative.

**Decisions:** Which drift problems you prioritised and why.

**Evidence:** *Proposed:* a short audit of 2–3 real scheduling products (public screenshots) showing these problems. That would turn an assumed problem into an observed one.

## 3. Goals and constraints

**Copy:** Goals: one semantic vocabulary for two products; WCAG 2.2 AA by construction; light and dark themes; standards-based JSON a developer could consume. Constraints: no existing brand to inherit; DTCG 2025.10 format; Figma's import limits (px dimensions, seconds for durations, no composite variables).

**Visuals:** A simple goals/constraints card.

**Decisions:** Choosing the then-new DTCG 2025.10 Resolver Module over ad-hoc theme files.

**Evidence:** *Done:* the constraints are reflected in generated files (see Figma section).

## 4. Token architecture

**Copy:** "Three layers (primitive, semantic, component) and two independent switches: theme (light/dark) and platform (mobile/desktop). Components never touch primitive colors; the build rejects it."

**Visuals:** Architecture diagram from the reference page; one token traced from `color.blue.600` to `time-slot.selected-bg`.

**Decisions:** Treating platform as a modifier with identical token names, rather than separate mobile and desktop component libraries. Why the two modifiers must not overlap.

**Evidence:** *Done:* 627 tokens per permutation, 4 permutations validated; layering enforced.

## 5. Foundation decisions

**Copy:** "I generated every hue on one perceptual lightness ladder (OKLCH). That makes contrast predictable: step 600 behaves the same in blue, green, red and violet. The typeface, Atkinson Hyperlegible Next, was designed for low-vision readers; in a product built on names, times and room numbers, telling I, l and 1 apart matters."

**Visuals:** Palette grid; type specimen showing Il1 0O; mobile vs desktop sizing table.

**Decisions:** OKLCH ladder; typeface; 48px mobile vs 24px-minimum desktop targets; violet as an added status hue.

**Evidence:** *Done:* contrast results. *Your input needed:* your reasoning on the brand blue. *Proposed:* legibility comparison with your target users.

## 6. Semantic token strategy

**Copy:** "Semantic names describe purpose, not appearance. Every status carries a color, an icon and a label, stored together so design and code can't separate them. Pending is also dashed; cancelled is struck through."

**Visuals:** Status table (badge, icon, light and dark fills); the calendar legend; a grayscale version of the calendar to prove statuses survive without color.

**Decisions:** Which statuses exist; why "completed" is deliberately quiet; treating "conflict" as a state, not a status.

**Evidence:** *Done:* contrast for every status label and icon. *Proposed:* grayscale and color-blindness simulation screenshots (easy to add, high value); a comprehension check with coordinators.

## 7. Component architecture

**Copy:** "I only created component tokens where a component makes a decision the semantic layer can't: a time slot's minimum width, a calendar event's dashed pending outline. Button and badge colors read semantic tokens directly; duplicating them would just add things to keep in sync."

**Visuals:** One component anatomy breakdown (time slot: default, selected, booked) with token callouts. Component spec table excerpt.

**Decisions:** The "only when meaningful" rule and where you drew the line.

**Evidence:** *Done:* 30 components specified, 234 component tokens.

## 8. Mobile and desktop scalability

**Copy:** "The same markup renders at patient or coordinator density by switching one attribute. A 48px mobile button becomes 36px on desktop; 16px body text becomes 14px."

**Visuals:** The density toggle on the reference page, before and after. Phone booking screen next to the admin table.

**Decisions:** What's shared vs platform-specific, and the rule you used to decide.

**Evidence:** *Done:* browser test confirms nested platform scopes resolve correctly. *Concept:* no real devices tested.

## 9. DTCG JSON implementation

**Copy:** "The JSON is the source of truth. A build step validates it (types, references, cycles, completeness, contrast) and generates CSS, Figma import files and resolved bundles. I wrote tests that break the tokens on purpose to prove the validator catches problems."

**Visuals:** Pipeline diagram; JSON → CSS trace; validation results table.

**Decisions:** Building validation into the pipeline instead of reviewing by hand. Keeping aliases as `var()` chains in CSS.

**Evidence:** *Done:* 10/10 negative tests, 13/13 browser tests, 0 undefined CSS variables. *Proposed:* independent validation with Style Dictionary or Terrazzo.

## 10. Figma and development handoff

**Copy:** "Figma imports DTCG JSON per mode, with limits: pixel dimensions only, durations in seconds, no composite tokens. The build produces files that respect those limits, links aliases across collections, and flattens type roles so one text style switches with the platform mode."

**Visuals:** Collection structure (Primitives, Theme, Platform, Components); *after you import:* screenshot of the Variables panel with alias chips.

**Decisions:** Merging spacing and sizing into one Platform collection; single-mode Components collection.

**Evidence:** *Done:* files generated against documented limits. **Not yet done:** an actual import. Do this before publishing the case study; it's the difference between "designed for Figma" and "works in Figma".

## 11. Accessibility and validation

**Copy:** "Contrast is a build requirement: 83 pairs per theme, and the build fails below AA. The first build did fail, on muted text and control borders. I fixed it in the shared lightness ladder rather than patching individual tokens, so the rule still holds for every hue."

**Visuals:** Before/after of the failing pairs; contrast table excerpt; focus ring on several surfaces.

**Decisions:** Fixing at the primitive ladder vs token-level patches; 2px offset focus ring.

**Evidence:** *Done:* automated contrast and target-size values. **Not done:** screen reader, keyboard, zoom and user testing; say so plainly and list them as next steps.

## 12. AI-assisted workflow

**Copy (edit after completing `ai-process.md`):** "I used an AI assistant to draft the generator, validator, token files and documentation from my brief. My role was *[what you actually did: defining the brief, reviewing palette and naming decisions, rejecting X, changing Y]*. Its mistakes were caught by validation I asked for: three contrast failures, a color-encoding bug, and two CSS scoping bugs."

**Visuals:** The contribution log table; the "what the AI got wrong" list.

**Decisions:** Where you overruled or changed AI proposals. *This is the most important part of the section and only you can write it.*

**Evidence:** The completed decision column in `ai-process.md`.

## 13. Outcomes and next steps

**Copy:** Outcomes (*Done*): a validated 627-token system across 4 contexts; CSS and Figma outputs; 30 component specs; a reference site with 5 screens. Next steps (*Proposed*): Figma import and component build; independent DTCG validation; screen reader and keyboard testing; a status-comprehension test with coordinators; resolve the open QA findings (secondary vs muted text, conflict layout at narrow widths).

**Visuals:** The reference site; the open findings list.

**Decisions:** What you'd change in v0.2 and why.

**Evidence:** Avoid impact metrics; there are none. "What I learned" is more credible here than invented results.
