# Ahmed Search Quality Repair Plan (v5)

## Goal
Optimize CareerOS for Ahmed's real hiring target in Timișoara/Romania: English-first office roles that leverage 10+ years of Tax/Law/Compliance/Administration/Operations experience, while preserving logistics/production as a fallback rather than the primary career identity.

## Current findings

1. `main` is currently `a268e0f` and already contains the IT-specialist false-positive fix; the repository reports 322 tests in the latest merge.
2. `careeros/search.py` limits preset search queries with `MAX_QUERIES = 6`. Full Career Scan currently seeds only operations coordinator, financial operations, back office, accounts payable, customer support, and compliance officer.
3. `careeros/profile.py` mixes office career identity with temporary production and delivery work. Production/driving should remain available but should not dominate office matching.
4. `careeros/tracks.py` already has useful track-aware scoring. Do not replace the 40/35/25 Match/Eligibility/Hiring architecture.
5. Romanian classification is already graded (`reject/risky/friendly/none`) and should remain graded. Advanced Romanian remains a hard filter; ordinary Romanian requirement should be handled by eligibility/filtering.
6. `hard_filter_job()` is intentionally conservative. Do not weaken unrelated-language or geographic hard filters. The primary quality problem is search coverage/taxonomy, not the 40/35/25 blend.

## Required implementation

### 1. Add a dedicated Ahmed office track
Add a track named approximately `🇷🇴 Ahmed – English-First Office` with high weights for:
- Tax / Compliance / Legal / Administration
- Operations / Back Office
- Customer Support / BPO
- KYC / AML / Banking Operations
- English and Arabic
- Timișoara / Romania / Romania-eligible remote

Keep Logistics & Production as a separate track.

### 2. Expand Full Career Scan search coverage
Replace the current six narrow seeds with a balanced set of query families covering:
- tax specialist / tax compliance / tax consultant / fiscal specialist
- compliance specialist / compliance analyst / KYC analyst / AML analyst / regulatory compliance
- operations specialist / operations coordinator / back office / business operations
- customer support / customer service / customer care / client support
- legal specialist / legal assistant / contract administrator / contract specialist
- Arabic customer support / Arabic operations / Arabic-English roles
- finance operations / banking operations / shared services / order management

Do not turn these into one giant bag-of-words query. Each query must remain a meaningful phrase.

### 3. Increase query budget safely
Raise the preset/query budget from 6 to a modest configurable value (target 12–18), but preserve provider limits and deduplication. Avoid an unbounded query explosion.

### 4. Improve query expansion
Make expansion deterministic and phrase-aware. A query such as `back office` must not degrade into generic `office` matching. Keep the existing domain-anchor protection in `sources/providers.py`.

### 5. Separate career identity from fallback work
Keep `production`, `warehouse`, and `driving` skills in the profile for fallback searches, but prevent them from becoming primary evidence in the new office track unless the selected track is Logistics & Production or Driving.

### 6. Preserve Romanian logic
Desired behavior:
- C1/C2/fluent/native Romanian mandatory -> hard reject for Ahmed.
- Romanian required without advanced level -> keep but penalize/risk in eligibility.
- Romanian preferred / plus -> keep with little/no penalty.
- Romanian not mentioned -> keep.
- English B2 -> acceptable.
- English C1/C2/native mandatory -> reject because Ahmed's ceiling is B2.
- Any additional EU language mandatory -> hard reject.

### 7. Keep location semantics
Primary: Timișoara.
Secondary: remote jobs legally/work-authorized from Romania.
Other Romanian cities: retain only if the user has enabled Romania-wide/relocation; do not silently treat them as Timișoara.
Remote Europe/EU/worldwide/Romania -> potentially reachable.
Remote tied to one foreign country -> not reachable from Romania unless the listing explicitly allows Romania.

### 8. Do not change the core blend
Keep:
- Match 40%
- Eligibility 35%
- Hiring Reality 25%
- weak-match cap

Do not solve low result counts by lowering the scoring bar or manufacturing bonuses.

## Acceptance tests

A good repair should make these behaviors true:

1. `tax compliance` can enter the search pipeline.
2. `KYC analyst` and `AML analyst` can enter the search pipeline.
3. `legal specialist` and `contract administrator` can enter the search pipeline.
4. `Arabic customer support` remains discoverable.
5. `Office Cleaner` is not admitted merely because `back office` contains `office`.
6. A job requiring `Romanian C1` is rejected.
7. A job saying `Romanian is a plus` is retained.
8. A job requiring German is rejected for Ahmed.
9. A Timișoara customer-support role with English B2 and no Romanian requirement scores as a realistic target.
10. A production-operator role is still discoverable under Logistics & Production but does not dominate the new office track.
11. Existing regression tests remain green; add targeted tests for every behavior above.

## Collaboration rule
Claude Code may implement this plan. Do not overwrite or reset unrelated commits. Prefer a dedicated branch/PR and run the complete test suite before merge. The branch created for this work is `fix/ahmed-search-quality-v5`.
