import json
import tempfile
import unittest

from relay_auditor.controller import Service
from relay_auditor.exporting import html_report
from relay_auditor.reports import explain, trend
from relay_auditor.profiles import Profiles
from relay_auditor.protocol import Protocol, make_case
from relay_auditor.suites import quality_case
from relay_auditor.storage import Store
from relay_auditor.transport import APIClient, Completion, Target
from test_sdk_exports import FakeVault
from test_service import FakeClient
from test_transport import Response


class SimulatedClient(FakeClient):
    def complete(self, case):
        if self.target.role == 'official_api' and case.kind == 'repair':
            return Completion('', complete=False, issue='output_limit')
        if self.target.role == 'relay' and self.target.model.startswith('deepseek-') and case.kind == 'constraints':
            return Completion('{"answer":[]}')
        return super().complete(case)


class AssessmentTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.store = Store(directory.name)
        self.addCleanup(self.store.close)
        self.service = Service(self.store, client_factory=SimulatedClient)
        self.deepseek = Protocol(wire_api='deepseek')

    def test_model_family_is_independent_of_protocol_and_no_key_still_gives_capability(self):
        alias = self.service.configure('https://relay.invalid/v1', 'synthetic', 'claude-test', Protocol(wire_api='chat'))
        plan = self.service.estimate(alias, 'assessment')
        self.assertEqual(plan['required_requests'], 10)
        result = self.service.run(alias, 'assessment', seed=42)
        self.assertEqual(result['model_family'], 'claude')
        self.assertIn('document', [row['task_kind'] for row in result['assessment_tasks']])
        self.assertEqual(result['capability_correct'], 10)
        self.assertEqual(result['identity_state'], 'not_tested')
        self.assertIn('证据不足', self.service.ui_snapshot()['report_cards'][alias]['headline'])

    def test_direct_deepseek_has_distinct_accounting_and_diagnosis(self):
        alias = self.service.configure('https://api.deepseek.com/v1', 'synthetic', 'deepseek-v4-flash', self.deepseek)
        result = self.service.run(alias, 'assessment', seed=42)
        self.assertEqual(result['source_kind'], 'official_api')
        self.assertEqual(result['capability_correct'], 8)
        self.assertEqual(result['response_issues'], [{'source_kind':'official_api', 'error_code':'output_limit', 'sample_count':2}])
        usage = self.store.usage()
        self.assertEqual(usage['probe_requests'], 0)
        self.assertEqual(usage['direct_probe_requests'], 10)
        self.assertIn('输出达到上限', self.service.ui_snapshot()['report_cards'][alias]['diagnostics'][0])
        self.assertEqual(result['assessment_counts'], [
            {'source_kind': 'official_api', 'sample_count': 10, 'attempted': 10, 'response_count': 10,
             'valid': 8, 'correct': 8}])
        self.assertIn('无法评分 2', self.service.ui_snapshot()['report_cards'][alias]['capability'])

    def test_matching_official_reference_produces_counts_but_abstains_on_small_sample(self):
        alias = self.service.configure('https://relay.invalid/v1', 'synthetic', 'deepseek-flash', self.deepseek,
                                       reference_key='synthetic-reference')
        self.assertEqual(self.service.monitors[alias].reference.base_url, 'https://api.deepseek.com')
        self.assertEqual(self.service.estimate(alias, 'assessment')['required_requests'], 20)
        result = self.service.run(alias, 'assessment', seed=42)
        self.assertEqual(result['paired_result']['reference_correct'], 10)
        self.assertEqual(result['paired_result']['target_correct'], 6)
        self.assertEqual(result['identity_state'], 'not_tested')
        self.assertEqual(result['suite_version'], 'assessment-v2')
        self.assertIsNone(result.get('audit_index'))
        self.assertEqual(self.store.next_audit()[0], 1)
        reasoning = [row for row in result['assessment_tasks'] if row['task_kind'] == 'constraints']
        self.assertEqual(sum(row['reference_correct'] for row in reasoning), 4)
        self.assertEqual(sum(row['target_correct'] for row in reasoning), 0)
        brief = self.service.ui_snapshot()['report_cards'][alias]
        self.assertIn('证据不足', brief['headline'])
        self.assertIn('答对 6，答错 4', brief['capability'])
        self.assertEqual(result['assessment_counts'][1]['source_kind'], 'reference')
        legacy_counts = [result['assessment_counts'][0], result['assessment_counts'][1] | {'source_kind': None}]
        self.assertIn('答对 6，答错 4', explain(result | {'assessment_counts': legacy_counts})['capability'])
        self.assertIn('中转 6/10', brief['comparison'])
        self.assertIn('官方 10/10', html_report(self.service.snapshot()))

    def test_tool_argument_schema_and_grading_use_the_same_envelope(self):
        case = quality_case('tool_args', 1)
        self.assertIn('Return exactly {"answer":{"name":', case.prompt)
        self.assertEqual(case.prompt.count('Return exactly'), 1)
        self.assertTrue(case.grade(json.dumps({'answer': case.expected}))['correct'])

    def test_history_requires_persistent_drop_across_new_seed_rounds(self):
        common = {'target_id': 'a' * 32, 'status': 'ok', 'suite_version': 'assessment-v2', 'mode': 'assessment',
                  'model': 'gpt-test', 'sample_count': 10, 'capability_completed': 10, 'capability_valid': 10}
        rows = [common | {'evaluated_at': f'2026-11-05T00:00:0{i}+00:00', 'task_seed': i, 'capability_correct': score}
                for i, score in enumerate((10, 10, 8, 9))]
        self.assertEqual(trend(rows[:3])['status'], 'insufficient_data')
        self.assertEqual(trend(rows)['status'], 'historical_decline_signal')
        replay = rows[-1] | {'task_seed': rows[-2]['task_seed']}
        self.assertEqual(trend(rows[:-1] + [replay])['status'], 'insufficient_data')
        recovered = rows[-1] | {'capability_correct': 10}
        self.assertEqual(trend(rows[:-1] + [recovered])['status'], 'no_detected_deviation')

    def test_mismatched_model_reference_is_never_called_by_default(self):
        alias = self.service.configure('https://relay.invalid/v1', 'synthetic', 'deepseek-v4-flash', self.deepseek,
                                       reference_key='synthetic-reference', reference_model='deepseek-v4-pro')
        result = self.service.run(alias, 'assessment', seed=42)
        self.assertEqual(result['reference_state'], 'reference_mismatch')
        self.assertEqual(self.store.usage()['reference_requests'], 0)

    def test_protocol_change_and_restart_keep_existing_reference_destination(self):
        profiles = Profiles(self.store.directory / 'synthetic-profiles', vault=FakeVault())
        service = Service(self.store, profiles=profiles)
        alias = service.configure('https://relay.invalid/v1', 'synthetic', 'gpt-test', Protocol(wire_api='chat'),
                                  reference_key='synthetic-reference', save_credentials=True)
        service.update_target(alias, display_name='Synthetic', model='deepseek-flash', wire_api='deepseek')
        restored = Service(self.store, profiles=profiles)
        self.assertEqual(restored.monitors[alias].reference.base_url, 'https://api.openai.com/v1')
        self.assertFalse(restored.estimate(alias, 'assessment')['matched_reference'])
        restored.credentials(alias, None, reference_key='new-synthetic-reference')
        self.assertEqual(restored.monitors[alias].reference.base_url, 'https://api.deepseek.com')
        self.assertTrue(restored.estimate(alias, 'assessment')['matched_reference'])

    def test_deepseek_wire_payload_and_reason_codes(self):
        captured = []
        target = Target('https://api.deepseek.com', 'synthetic', 'deepseek-v4-flash',
                        Protocol(wire_api='deepseek', reasoning_effort='none'), role='reference')

        def open_request(request, **kwargs):
            captured.append(json.loads(request.data))
            return Response(b'{"choices":[{"message":{"reasoning_content":"synthetic-hidden","content":""},"finish_reason":"length"}]}')

        result = APIClient(target, open_request).complete(make_case('digit', 0))
        self.assertEqual(result.issue, 'output_limit')
        self.assertEqual(result.text, '')
        self.assertEqual(captured[0]['thinking'], {'type':'disabled'})
        self.assertIn('max_tokens', captured[0])
        self.assertNotIn('max_completion_tokens', captured[0])


if __name__ == '__main__':
    unittest.main()
