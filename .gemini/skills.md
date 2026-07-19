# Greyhound Edge Engine v3.2 - Skill Registry

This registry defines the 9 composable analytical skills required for greyhound analysis.

## 1. form_extraction
**Description**: Parses raw form guide input (plain text paste OR Excel data) into structured runner data.
**Trigger Conditions**: User pastes text resembling a racing form guide, or provides data from the racing-form-extractor.
**Inputs**: Raw text or Excel data.
**Process**: Extract Box, Dog Name, Trainer, Sire, Dam, Age/Sex, Rating, Days Since Last, Run Style. Extract track/distance records and the last 3-6 past runs.
**Output**: Structured runner dictionaries.

## 2. integrity_checker
**Description**: Validates that all runners are captured and confirms race metadata.
**Trigger Conditions**: Follows form_extraction.
**Inputs**: Structured runner data.
**Process**: Ensure the number of runners matches the field size. Never skip a runner. Confirm Track, Distance, Grade/Class, Field Size, PBD (Yes/No/Unknown), Scratches, Track Condition.
**Output**: Section A Parse + Data Integrity Check.

## 3. speed_profiler
**Description**: Builds recency-weighted speed profiles per dog, including trainer and track experience metrics.
**Trigger Conditions**: Follows integrity_checker.
**Inputs**: Validated runner past runs.
**Process**: Calculate Speed Figure (SF), Ability Score (AS), Early Speed Rating (ESR), and Mid/Finish Rating (MFR). Apply recency weights: w1=0.42, w2=0.28, w3=0.15, w4=0.10, w5=0.05. Calculate Track Experience (TrE) penalties. Evaluate Trainer Edge (TE) to be used strictly as a tie-breaker. Scale 0-10.
**Output**: Quantitative speed features per dog (including TE and TrE).

## 4. start_reliability
**Description**: Computes start consistency and volatility.
**Trigger Conditions**: Follows speed_profiler.
**Inputs**: Runner past runs and early splits.
**Process**: Calculate Start Reliability (SR) based on consistency of early splits. Calculate SR Volatility. Apply Distance Non-Native Penalty (DNP: 0=Proven, 1=Some evidence, 2=Unproven). Apply Freshness decay (>14 days). Scale 0-10.
**Output**: Start and reliability features per dog.

## 5. pressure_conflict
**Description**: Models early race pressure and trouble risk.
**Trigger Conditions**: Follows start_reliability.
**Inputs**: Early Speed Ratings (ESR) and Start Reliability (SR) of all runners.
**Process**: Calculate Pressure Index (PI). Squeeze boxes (3, 4, 5, 6) receive base penalties unless neighbors are slow/vacant. Identify specific conflict pairs/triples into the first turn. Assign Trouble Risk (Low/Med/High) and type (squeeze/cross/check/rail crowd/wide push).
**Output**: Pressure Index and conflict map.

## 6. class_movement
**Description**: Analyzes class movement and margin context.
**Trigger Conditions**: Follows pressure_conflict.
**Inputs**: Past runs (Class, Margin).
**Process**: Determine if the dog is moving Up, Same, or Down in class compared to its last 3-6 runs. Evaluate margin context (e.g., close finish in stronger grade = positive).
**Output**: Class Edge (+/-) per runner.

## 7. scenario_mapper
**Description**: Builds the dual speed map scenarios.
**Trigger Conditions**: Follows class_movement.
**Inputs**: ESR, MFR, SR, PI, and Conflict Map.
**Process**: 
- Build Scenario A (Mainline, 70-80%): Predict the positional order at 20m, 50m, 1st turn, and back straight assuming standard breaks.
- Build Scenario B (Jam/Sweep, 20-30%): A mandatory upset scenario where leaders crash/crowd, benefiting midfielders and strong finishers (high MFR).
**Output**: Scenario A and Scenario B speed maps and narratives.

## 8. probability_engine
**Description**: Computes scenario-weighted probabilities.
**Trigger Conditions**: Follows scenario_mapper.
**Inputs**: All quant features and the two scenarios.
**Process**: Build a performance score from AS/ESR/MFR minus PI/trouble/DNP/freshness. Convert to WinProb for Scenario A and Scenario B. Mix scenarios (WinProb = wA*WinProb_A + wB*WinProb_B). Compute separate Top3% and Top4% probabilities prioritizing clear-run/survival traits.
**Output**: Probability table (Win%, Top3%, Top4%).

## 9. value_classifier
**Description**: Evaluates market value, filters false favourites, and builds betting structures.
**Trigger Conditions**: Follows probability_engine.
**Inputs**: Probability table, Market Odds (if provided).
**Process**: 
- Convert odds to implied probabilities (remove overround).
- False Fav Filter: If odds <= 2.80 (implied >= 35%), require SR >= 8 AND PI <= 4. If fail, flag "FALSE FAV RISK = YES" and apply a 10-20% win-prob haircut redistributed to Scenario B runners.
- Identify value bets using edges: Win >= 1.12, Place >= 1.08, Top4 >= 1.06.
- Select Probable Winner and 2 Best Top4 Anchors.
- Build map-driven Trifecta and First 4 combinations (Scenario A structure vs Scenario B structure).
- Apply 0.25 Kelly staking, capped at 2% single bet, 3.5% race exposure.
**Output**: Final betting recommendations and One-Screen Summary.
