import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_openalex_flow import fill,build
class FlowPreservation(unittest.TestCase):
    def test_preserves_zero_and_unknown_age_existing_values(self):
        old={'CitationCount_OpenAlex':0,'OpenAccessStatus':'closed','ReviewStatus':'Excluded','CitationMetricsObservedUTC':'shared'}
        result,status=fill(old,{'OpenAlexWorkID':'W1','CitationCount_OpenAlex':99,'OpenAccessStatus_OpenAlex':'gold'})
        self.assertEqual(result['CitationCount_OpenAlex'],0)
        for key in old:self.assertEqual(old[key],result[key])
    def test_null_candidate_and_conflicting_work_preserve_target(self):
        old={'OpenAlexID':'W2','CitationCount_OpenAlex':None}
        self.assertEqual(fill(old,{'OpenAlexWorkID':'W1','CitationCount_OpenAlex':1}),(old,'work_id_conflict'))
        self.assertEqual(fill({}, {'CitationCount_OpenAlex':None})[0],{})
    def test_missing_count_can_fill_with_zero(self):
        self.assertEqual(fill({'CitationCount_OpenAlex':None},{'CitationCount_OpenAlex':0})[0]['CitationCount_OpenAlex'],0)
    def test_authoring_preserves_original_query_triggers_and_unrelated_params(self):
        params={'item/field_17':'Included','item/field_19':'initial'}
        definition={'triggers':{'Recurrence':{'unchanged':True}},'actions':{
            'Run_publication_rows_query':{'inputs':{'parameters':{'specification/query':'original'}},'type':'OpenApiConnection'},
            'Apply_to_each_Publication':{'runtimeConfiguration':{'concurrency':{'repetitions':1}},'runAfter':{'Condition_Invalid_SourceKeys':['Succeeded']},'actions':{
                'Condition_Is_New_Publication':{'actions':{'SharePoint_Create_item':{'inputs':{'parameters':params}}},'else':{'actions':{'SharePoint_Update_item':{'inputs':{'parameters':{'item/field_20':'latest'}}}}}}}}}}
        result=build(definition)
        self.assertEqual(result['triggers'],definition['triggers'])
        self.assertEqual(result['actions']['Run_publication_rows_query'],definition['actions']['Run_publication_rows_query'])
        create=result['actions']['Apply_to_each_Publication']['actions']['Condition_Is_New_Publication']['actions']['SharePoint_Create_item']['inputs']['parameters']
        for k,v in params.items():self.assertEqual(create[k],v)

class SubmissionNormalisation(unittest.TestCase):
    def test_only_known_service_injected_auth_is_omitted(self):
        from prepare_openalex_flow import transport_definition
        original={'actions':{'Scope':{'actions':{'Read':{'inputs':{'authentication':"@parameters('$authentication')",'parameters':{'target':'unchanged'}}}}}}}
        result=transport_definition(original)
        self.assertEqual(result['actions']['Scope']['actions']['Read']['inputs'],{'parameters':{'target':'unchanged'}})
        self.assertIn('authentication',original['actions']['Scope']['actions']['Read']['inputs'])
    def test_unknown_auth_cannot_be_silently_removed(self):
        from prepare_openalex_flow import transport_definition
        with self.assertRaises(ValueError):transport_definition({'actions':{'Read':{'inputs':{'authentication':{'type':'other'}}}}})
