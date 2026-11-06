"""One-button assessment with independently counted responses on each side."""
from collections import Counter
import secrets

from .families import family_for, reference_issue, PROFILES, GENERIC
from .planning import assessment_plan, ASSESSMENT_PROMPT_BYTES
from .statistics import MINIMUM_PAIRED_SAMPLES, compare_paired, spending_alpha
from .suites import quality_case
from .transport import EndpointError

VERSION = 'assessment-v2'
RESPONSE_ISSUES = frozenset(('output_limit', 'stream_interrupted', 'empty_answer', 'response_filtered', 'incomplete_output'))


def assessment_cases(model, samples, seed):
    tasks = PROFILES.get(family_for(model), GENERIC).tasks
    for index in range(samples):
        difficulty = 1 + (index // len(tasks)) % 4
        yield quality_case(tasks[index % len(tasks)], seed + index, difficulty=difficulty), difficulty


def run_assessment(service, monitor, samples, result, *, seed=None):
    plan = assessment_plan(monitor, samples)
    seed = secrets.randbelow(2**31) if seed is None else seed
    cases = list(assessment_cases(monitor.target.model, plan['sample_count'], seed))
    paired = plan['matched_reference']
    longest = max(len(case.prompt.encode()) for case, _ in cases)
    if longest > ASSESSMENT_PROMPT_BYTES:
        raise EndpointError('invalid_synthetic_case')
    counts = {
        source: dict(source_kind=source, sample_count=len(cases), attempted=0, response_count=0, valid=0, correct=0)
        for source in ((monitor.target.role, 'reference') if paired else (monitor.target.role,))
    }
    target_counts = counts[monitor.target.role]
    result.update(
        suite_version=VERSION, model_family=family_for(monitor.target.model), task_seed=seed, task_count=len(cases),
        sample_count=plan['required_requests'], reference_state=plan['reference_state'],
        reference_error=reference_issue(monitor),
        capability_attempted=0, capability_completed=0, capability_valid=0, capability_correct=0,
        response_count=0, network_failures=0, invalid_responses=0,
        identity_state='not_tested', assessment_tasks=[], assessment_counts=list(counts.values()), response_issues=[],
    )
    diagnostics = Counter()
    task_rows = {}
    pairs = []
    output_bound = monitor.target.protocol.max_output_tokens
    if paired:
        output_bound = max(output_bound, monitor.reference.protocol.max_output_tokens)
    batch = service.store.reserve_batch(plan['required_requests'], longest + output_bound + 256)
    service.set_progress(plan['required_requests'])

    def read(case, reference, row):
        if reference and result.get('reference_error'):
            return None
        side = counts['reference'] if reference else target_counts
        try:
            response = service._call(monitor, case, reference=reference, batch=batch)
        except EndpointError as error:
            response = None
            result['network_failures'] += 1
            diagnostics[(reference, str(error))] += 1
            if reference and monitor.reference_error:
                result['reference_error'] = monitor.reference_error
        side['attempted'] += 1
        if not reference:
            row['attempted'] += 1
        if response is None:
            return None
        side['response_count'] += 1
        result['response_count'] += 1
        issue = response.issue if response.issue in RESPONSE_ISSUES else None
        if not response.complete:
            issue = issue or 'incomplete_output'
        elif not response.text.strip():
            issue = 'empty_answer'
        if not issue:
            grade = case.grade(response.text)
            if grade['valid']:
                side['valid'] += 1
                side['correct'] += grade['correct']
                if not reference:
                    row['valid'] += 1
                    row['correct'] += grade['correct']
                return grade['correct']
            issue = 'answer_format'
        diagnostics[(reference, issue)] += 1
        result['invalid_responses'] += 1
        return None

    try:
        for index, (case, difficulty) in enumerate(cases):
            level = difficulty if case.kind in ('code', 'constraints', 'document') else None
            row = task_rows.setdefault((case.kind, level), {
                'task_kind': case.kind, 'difficulty': level, 'attempted': 0, 'valid': 0, 'correct': 0,
            })
            sides = ((True, False) if index % 2 else (False, True)) if paired else (False,)
            answers = {reference: read(case, reference, row) for reference in sides}
            actual = answers[False]
            if paired:
                reference = answers[True]
                pairs.append((reference, actual))
                if reference is not None and actual is not None:
                    row['valid_pairs'] = row.get('valid_pairs', 0) + 1
                    row['reference_correct'] = row.get('reference_correct', 0) + int(reference)
                    row['target_correct'] = row.get('target_correct', 0) + int(actual)
        if paired:
            valid = [(ref, actual) for ref, actual in pairs if ref is not None and actual is not None]
            # Descriptive screens and incomplete runs cannot reject, so spend no formal decision budget.
            decision_ready = len(valid) == len(pairs) and len(valid) >= MINIMUM_PAIRED_SAMPLES
            if decision_ready:
                audit_index, alpha = service.store.next_audit()
            else:
                audit_index, alpha = None, spending_alpha(1)
            comparison = compare_paired(pairs, alpha=alpha)
            if not decision_ready:
                comparison['alpha'] = None
            comparison.update(reference_correct=sum(ref for ref, _ in valid), target_correct=sum(actual for _, actual in valid))
            result.update(paired_result=comparison, capability_state=comparison['status'],
                          detected_anomaly=comparison['status'] == 'degraded',
                          audit_index=audit_index)
            if valid:
                result['provenance_level'] = 'same_time_official_reference'
        else:
            result['capability_state'] = ('insufficient_data' if not target_counts['valid'] else
                'incomplete_comparison' if target_counts['valid'] < len(cases) else
                'observed_answers_correct' if target_counts['correct'] == len(cases) else 'screening_failure')
        return result
    finally:
        result.update(capability_attempted=target_counts['attempted'], capability_completed=target_counts['response_count'],
                      capability_valid=target_counts['valid'], capability_correct=target_counts['correct'])
        result['assessment_tasks'] = list(task_rows.values())
        result['response_issues'] = [
            {'source_kind': 'reference' if reference else monitor.target.role, 'error_code': issue, 'sample_count': count}
            for (reference, issue), count in diagnostics.items()
        ]
        service.store.release_batch(batch)
