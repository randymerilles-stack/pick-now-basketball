"""Offline log loss and fixed-bin reliability, after frozen-scorer validation.

Every accepted canonical game contributes total weight one per outcome class;
decisions within that game split its weight. Away outcomes are complementary,
not extra independent observations. Bins are fixed, never tuned on test labels.
"""
from bisect import bisect_right
import math
from statistics import mean
from forecast_scoring import score_frozen_forecasts

BIN_EDGES = tuple(i/10 for i in range(11))
CLASSES = ('home_win', 'home_loss', 'push')


def diagnose_probabilities(forecasts, outcomes, *, test_event_ids, model_versions):
    """Return descriptive metrics only; no calibration fitting or pick approval.

    A zero probability for the observed class means infinite log loss. Report
    it explicitly with null numeric mean rather than silently clipping/dropping.
    Empty accepted data returns insufficient_data. Sparse reliability bins are
    descriptive and do not establish held-out calibration or adequate power.
    """
    forecasts, outcomes = list(forecasts), list(outcomes)
    scored = score_frozen_forecasts(forecasts, outcomes, test_event_ids=test_event_ids,
                                    model_versions=model_versions)
    accepted = {row['canonical_event_id'] for row in scored['events']}
    groups = {event: [] for event in accepted}
    labels = {r['canonical_event_id']: r for r in outcomes
              if isinstance(r, dict) and isinstance(r.get('canonical_event_id'), str)
              and r['canonical_event_id'] in accepted}
    for row in forecasts:
        if (isinstance(row, dict) and isinstance(row.get('canonical_event_id'), str)
                and row['canonical_event_id'] in accepted):
            groups[row['canonical_event_id']].append(row)
    n = len(accepted)
    models = {}
    for model in ('candidate', 'baseline'):
        cells = [[dict(weight=0., predicted=0., observed=0., decisions=0, events=set())
                  for _ in range(10)] for _ in CLASSES]
        event_losses, infinite_events, zero_decisions = [], 0, 0
        for event, rows in sorted(groups.items()):
            losses = []
            zeros = 0
            within_weight = 1/len(rows)
            margin = labels[event]['final_home_margin']
            for row in rows:
                adjusted = margin + row['home_line']
                target = 0 if adjusted > 0 else 1 if adjusted < 0 else 2
                probs = row[model+'_home']
                if probs[target] == 0:
                    zeros += 1
                else:
                    losses.append(-math.log(probs[target]))
                for index, probability in enumerate(probs):
                    bin_index = min(9, bisect_right(BIN_EDGES, probability)-1)
                    cell = cells[index][bin_index]
                    cell['weight'] += within_weight
                    cell['predicted'] += within_weight*probability
                    cell['observed'] += within_weight*int(index == target)
                    cell['decisions'] += 1
                    cell['events'].add(event)
            zero_decisions += zeros
            if zeros:
                infinite_events += 1
            else:
                event_losses.append(mean(losses))
        reliability, class_errors = {}, []
        for index, name in enumerate(CLASSES):
            bins = []
            error = 0.
            for b, cell in enumerate(cells[index]):
                weight = cell['weight']
                predicted = cell['predicted']/weight if weight else None
                observed = cell['observed']/weight if weight else None
                mass = weight/n if n else 0.
                if weight:
                    error += mass*abs(predicted-observed)
                bins.append(dict(lower=BIN_EDGES[b], upper=BIN_EDGES[b+1],
                                 upper_inclusive=b == 9, event_weight_mass=mass,
                                 participating_events=len(cell['events']), decision_count=cell['decisions'],
                                 mean_probability=predicted, observed_frequency=observed))
            reliability[name] = bins
            class_errors.append(error)
        models[model] = dict(mean_event_log_loss=mean(event_losses) if n and not infinite_events else None,
                            log_loss_status='infinite' if infinite_events else 'finite' if n else 'no_data',
                            zero_target_probability_events=infinite_events,
                            zero_target_probability_decisions=zero_decisions,
                            fixed_bin_macro_ece=mean(class_errors) if n else None,
                            reliability=reliability)
    return dict(status='descriptive_only' if n else 'insufficient_data', independent_events=n,
                models=models, model_versions=list(model_versions), scoring_rejected=scored['rejected'],
                missing_forecast_events=scored['missing_forecast_events'], approved_for_picks=False,
                statistical_power_established=False,
                limitations=['Fixed bins [0,.1),...,[.9,1], natural-log loss; no clipping.',
                             'Participating event counts overlap across bins; they are not additive independent games.',
                             'Sparse bins and low ECE do not establish calibration, source verification or predictive improvement.',
                             'No timing selection, model fitting, power analysis or replication performed.'])
