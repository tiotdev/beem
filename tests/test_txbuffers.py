from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import super
import unittest
from beem import Steem
from beembase import operations
from beem.instance import set_shared_steem_instance

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
nodes = ["wss://steemd.pevo.science", "wss://gtg.steem.house:8090", "wss://rpc.steemliberator.com", "wss://rpc.buildteam.io",
         "wss://rpc.steemviz.com", "wss://seed.bitcoiner.me", "wss://node.steem.ws", "wss://steemd.steemgigs.org", "wss://steemd.steemit.com",
         "wss://steemd.minnowsupportproject.org"]


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = Steem(
            node=nodes,
            nobroadcast=True,
            keys={"active": wif}
        )
        set_shared_steem_instance(self.bts)
        self.bts.set_default_account("test")


"""
    def test_add_one_proposal_one_op(self):
        bts = self.bts
        tx1 = bts.new_tx()
        proposal1 = bts.new_proposal(tx1, proposer="test")
        op = operations.Transfer(**{
            "fee": {"amount": 0, "asset_id": "SBD"},
            "from": "1.2.0",
            "to": "1.2.0",
            "amount": {"amount": 0, "asset_id": "SBD"},
            "prefix": "TEST"
        })
        proposal1.appendOps(op)
        tx = tx1.json()
        self.assertEqual(tx["operations"][0][0], 22)
        self.assertEqual(len(tx["operations"]), 1)
        ps = tx["operations"][0][1]
        self.assertEqual(len(ps["proposed_ops"]), 1)
        self.assertEqual(ps["proposed_ops"][0]["op"][0], 0)

    def test_add_one_proposal_two_ops(self):
        bts = self.bts
        tx1 = bts.new_tx()
        proposal1 = bts.new_proposal(tx1, proposer="test")
        op = operations.Transfer(**{
            "fee": {"amount": 0, "asset_id": "SBD"},
            "from": "1.2.0",
            "to": "1.2.0",
            "amount": {"amount": 0, "asset_id": "SBD"},
            "prefix": "TEST"
        })
        proposal1.appendOps(op)
        proposal1.appendOps(op)
        tx = tx1.json()
        self.assertEqual(tx["operations"][0][0], 22)
        self.assertEqual(len(tx["operations"]), 1)
        ps = tx["operations"][0][1]
        self.assertEqual(len(ps["proposed_ops"]), 2)
        self.assertEqual(ps["proposed_ops"][0]["op"][0], 0)
        self.assertEqual(ps["proposed_ops"][1]["op"][0], 0)

    def test_have_two_proposals(self):
        bts = self.bts
        tx1 = bts.new_tx()

        # Proposal 1
        proposal1 = bts.new_proposal(tx1, proposer="test")
        op = operations.Transfer(**{
            "fee": {"amount": 0, "asset_id": "SBD"},
            "from": "1.2.0",
            "to": "1.2.0",
            "amount": {"amount": 0, "asset_id": "SBD"},
            "prefix": "TEST"
        })
        for i in range(0, 3):
            proposal1.appendOps(op)

        # Proposal 1
        proposal2 = bts.new_proposal(tx1, proposer="test")
        op = operations.Transfer(**{
            "fee": {"amount": 0, "asset_id": "SBD"},
            "from": "1.2.0",
            "to": "1.2.0",
            "amount": {"amount": 5555555, "asset_id": "SBD"},
            "prefix": "TEST"
        })
        for i in range(0, 2):
            proposal2.appendOps(op)
        tx = tx1.json()

        self.assertEqual(len(tx["operations"]), 2)  # 2 proposals

        # Test proposal 1
        prop = tx["operations"][0]
        self.assertEqual(prop[0], 22)
        ps = prop[1]
        self.assertEqual(len(ps["proposed_ops"]), 3)
        for i in range(0, 3):
            self.assertEqual(ps["proposed_ops"][i]["op"][0], 0)

        # Test proposal 2
        prop = tx["operations"][1]
        self.assertEqual(prop[0], 22)
        ps = prop[1]
        self.assertEqual(len(ps["proposed_ops"]), 2)
        for i in range(0, 2):
            self.assertEqual(ps["proposed_ops"][i]["op"][0], 0)
"""
