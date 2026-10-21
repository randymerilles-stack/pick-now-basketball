import copy
from datetime import datetime, timezone
import unittest
from validation import inspect_feed

NOW=datetime(2026,10,20,3,0,tzinfo=timezone.utc)

def sample():
    return {'server_time':NOW.isoformat(),'matches':[{'id':'f1','sport':'basketball',
        'in_play':True,'home':'Home','away':'Away','league':'Test League','score':'40-38',
        'group_status':{'112':{'polled_at':'2026-10-20T02:59:55Z'}},
        'polled_at':'2026-10-20T02:59:55Z','quotes':[
        {'fixture_id':'f1','group_id':'112','group_name':'Game','line':'Line',
         'market_id':'1446','sel_id':str(i),'side':team,'handicap':line,'odds_dec':1.9,
         'phase':'inplay','ts':'2026-10-20T02:58:00Z'}
        for i,team,line in [(1,'Home',-3.5),(2,'Away',3.5)]]}]}

class ValidationTests(unittest.TestCase):
    def test_fresh_fixture_cannot_mask_unconfirmed_handicap_group(self):
        for status in [None,{}, {'104':{'polled_at':NOW.isoformat()}},
                       {'112':{'polled_at':'2026-10-20T02:59:29Z'}},
                       {'112':{'polled_at':'2026-10-20T03:00:06Z'}},
                       {'112':{'polled_at':NOW.isoformat(),'stale':True}},
                       {'112':{'polled_at':NOW.isoformat(),'stale':'false'}}]:
            d=sample();d['matches'][0]['group_status']=status
            result=self.validate(d)
            self.assertEqual(result['data_checked_market_count'],0)
            self.assertEqual(result['rejected']['stale_or_missing_handicap_group_poll'],1)
    def validate(self,d):return inspect_feed(d,NOW)
    def test_pair_passes_data_checks_but_never_picks(self):
        d=self.validate(sample())
        self.assertEqual(d['data_checked_market_count'],1)
        self.assertEqual(d['verified_market_count'],0)
        self.assertEqual(d['markets'],[])
    def test_old_price_with_recent_poll_is_not_stale(self):
        d=sample()
        for q in d['matches'][0]['quotes']:q['ts']='2026-10-19T00:00:00Z'
        self.assertEqual(self.validate(d)['data_checked_market_count'],1)
    def test_stale_missing_and_future_poll_rejected(self):
        for poll in [None,'2026-10-20T02:59:29Z','2026-10-20T03:00:06Z']:
            d=sample();d['matches'][0]['polled_at']=poll
            self.assertEqual(self.validate(d)['data_checked_market_count'],0)
    def test_identity_scope_price_suspension_and_line_fail_closed(self):
        for field,value in [('group_id','104'),('line','To Win'),('period','4'),
            ('phase','prematch'),('fixture_id','other'),('side','Unknown'),
            ('handicap',float('nan')),('odds_dec',float('inf')),('odds_dec',True),
            ('odds_dec',1),('suspended',True),('suspended','false'),('handicap',2.5),
            ('ts','2026-10-20T03:00:01Z')]:
            with self.subTest(field=field,value=value):
                d=sample();d['matches'][0]['quotes'][0][field]=value
                self.assertEqual(self.validate(d)['data_checked_market_count'],0)
    def test_delayed_snapshot_cannot_reset_freshness(self):
        d=sample()
        d['server_time']='2026-10-20T02:59:20Z'
        d['matches'][0]['polled_at']='2026-10-20T02:59:15Z'
        self.assertEqual(self.validate(d)['data_checked_market_count'],0)
    def test_unpaired_duplicate_or_virtual_fixtures_rejected(self):
        d=sample();d['matches'][0]['quotes'].pop()
        self.assertEqual(self.validate(d)['data_checked_market_count'],0)
        d=sample();d['matches'].append(copy.deepcopy(d['matches'][0]))
        self.assertEqual(self.validate(d)['data_checked_market_count'],0)
        d=sample();d['matches'][0]['league']='Ebasketball H2H'
        self.assertEqual(self.validate(d)['data_checked_market_count'],0)
    def test_missing_or_structured_identifiers_rejected(self):
        for value in [None, True, {}, [], '', '   ']:
            with self.subTest(value=value):
                d=sample();d['matches'][0]['id']=value
                for q in d['matches'][0]['quotes']:q['fixture_id']=value
                self.assertEqual(self.validate(d)['data_checked_market_count'],0)
                for field in ['market_id','sel_id']:
                    d=sample();d['matches'][0]['quotes'][0][field]=value
                    self.assertEqual(self.validate(d)['data_checked_market_count'],0)
    def test_future_provider_clock_does_not_hide_future_poll(self):
        d=sample();d['server_time']='2026-10-20T03:00:45Z'
        d['matches'][0]['polled_at']='2026-10-20T03:00:40Z'
        self.assertEqual(self.validate(d)['data_checked_market_count'],0)
        d=sample();d['server_time']='2026-10-20T03:00:45Z'
        d['matches'][0]['quotes'][0]['ts']='2026-10-20T03:00:40Z'
        self.assertEqual(self.validate(d)['data_checked_market_count'],0)
    def test_virtual_marker_in_team_name_is_excluded(self):
        d=sample();d['matches'][0]['home']='Home NBA 2K'
        d['matches'][0]['quotes'][0]['side']='Home NBA 2K'
        self.assertEqual(self.validate(d)['data_checked_market_count'],0)

    def test_missing_future_and_old_feed_timestamps_rejected(self):
        for stamp in [None,'2026-10-19T03:00:00Z','2026-10-20T04:00:00Z']:
            d=sample();d['server_time']=stamp
            self.assertEqual(self.validate(d)['data_checked_market_count'],0)

if __name__=='__main__':unittest.main()
