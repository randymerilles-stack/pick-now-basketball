# Priority Pick prospective evaluation protocol v1
Recorded 21 October 2026 before fitting or testing a score/time model.

## Eligibility before feature construction
Require independently verified Full Game Handicap scope, overtime settlement rule, exact event identity, paired opposite lines and contemporaneous odds. Require explicit period, documented countdown/count-up and clock reference semantics, verified league regulation/extra-period rules, synchronized score/stats/clock and quote observation timestamps. Unknown or stale states are rejected. Current research records do not satisfy these gates and cannot validate Priority Pick.

## Prediction target and symmetry
Predict Full Game Handicap cover for each side at the recorded line and price; outright winner is a different target. Reevaluate both sides at each decision. Include push as a separate settlement state where applicable. Expected return uses win probability, loss probability and push probability with the recorded decimal price. No fixed home/team preference. Abstain on invalid state, weak evidence or nonpositive estimated return. Experimental evaluations remain PAPER ONLY.

## Development and locked testing
Resolve aliases before splitting; all snapshots, sides and markets for the same game belong to one group. Use chronological development, validation and untouched final test blocks. Purge training labels unavailable at the next decision cutoff. Fit transforms, missing-value policies, hyperparameters, calibration and timing selection only inside development/validation. Store a frozen model/version, feature snapshot, probabilities for both sides and timestamp before each test result becomes available. Never regenerate forecasts after seeing outcomes.

Compare a de-vigged market baseline, market-only calibration, and a simple regularized score/time candidate. Start with documented score margin, line, market probability, explicit period and verified regulation time remaining. Any performance stats require a separately checked timestamp. Report the incremental value of score/time against market-only calibration.

## Timing selection
Use normalized regulation time remaining, only after rule/clock verification. Predefine candidate intervals (75-100%, 50-75%, 25-50%, 0-25% of regulation time remaining); treat overtime separately and exclude it initially. Boundaries are deterministic and nonoverlapping: [0,.25), [.25,.50), [.50,.75), [.75,1]. Select any candidate interval on validation only, then freeze it before final testing. Report every interval, rejected records and abstention coverage. Do not choose a winning interval from final-test outcomes.

## Metrics and uncertainty
Primary metric: fixture-grouped paired difference in Brier score versus market-only calibration, with 95% fixture-block bootstrap confidence intervals. Also report log loss, reliability/calibration, count per league/window, abstention coverage and timestamp rejection rates. Paper return after actual prices and settlement is secondary; report uncertainty and all losses/pushes. A positive sample return alone cannot qualify a model.

A final test must have a prespecified power/precision analysis based on a separate development pilot and a fixed effect size, before test outcomes are inspected. For context only, a worst-case independent binary rate needs approximately 385 games for a nominal 95% +/-5 percentage-point interval, or 1068 for +/-3 points (normal approximation). These figures are not training minimums, a power analysis for Brier differences, or evidence of betting edge; grouping, multiple windows and dependence can increase requirements. The current 12 provider-labelled games are insufficient.

## Qualification and release
Require independent odds verification, validated state semantics, adequate prespecified test power, a locked test demonstrating incremental predictive improvement with uncertainty, acceptable held-out calibration and replication on a later chronological block. If evidence is inconclusive, continue abstaining. Any deployment additionally requires owner authentication, stale-selection revocation, English-on-login, both-side refresh and end-to-end acceptance tests. Approved recommendations remain disabled until the existing approval criteria are met. No model is trained or qualified by this document.

## Next concrete work
Establish source clock semantics and league mapping, build eligible feature records, then implement grouped evaluation and forecast persistence. Revisit power design using development data only. Do not repeatedly tune against the same test set.
