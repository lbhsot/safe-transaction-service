from django.test import TestCase

from eth_account import Account

from gnosis.eth.tests.ethereum_test_case import EthereumTestCaseMixin

from ..models import EthereumTx
from ..services import IndexService
from ..services.index_service import TransactionNotFoundException
from .factories import EthereumTxFactory


class TestIndexService(EthereumTestCaseMixin, TestCase):
    def test_create_or_update_from_tx_hashes_existing(self):
        index_service = IndexService(self.ethereum_client)
        self.assertListEqual(index_service.txs_create_or_update_from_tx_hashes([]), [])
        tx_hashes = ['0x52fcb05f2ad209d53d84b0a9a7ce6474ab415db88bc364c088758d70c8b5b0ef']
        with self.assertRaisesMessage(TransactionNotFoundException, tx_hashes[0]):
            index_service.txs_create_or_update_from_tx_hashes(tx_hashes)

        # Test with database txs
        ethereum_txs = [EthereumTxFactory() for _ in range(4)]
        tx_hashes = [ethereum_tx.tx_hash for ethereum_tx in ethereum_txs]
        db_txs = index_service.txs_create_or_update_from_tx_hashes(tx_hashes)
        self.assertEqual(len(db_txs), len(tx_hashes))
        for db_tx in db_txs:
            self.assertIsNotNone(db_tx)

        # Test with real txs
        value = 6
        real_tx_hashes = [self.send_ether(Account.create().address, value) for _ in range(2)]
        ethereum_txs = index_service.txs_create_or_update_from_tx_hashes(real_tx_hashes)
        self.assertEqual(len(ethereum_txs), len(ethereum_txs))
        for ethereum_tx in ethereum_txs:
            self.assertEqual(ethereum_tx.value, value)

        # Remove blocks and try again
        EthereumTx.objects.filter(tx_hash__in=real_tx_hashes).update(block=None)
        ethereum_txs = index_service.txs_create_or_update_from_tx_hashes(real_tx_hashes)
        for ethereum_tx in ethereum_txs:
            self.assertIsNotNone(ethereum_tx.block)

        # Test mixed
        tx_hashes = tx_hashes + real_tx_hashes
        mixed_txs = index_service.txs_create_or_update_from_tx_hashes(tx_hashes)
        self.assertEqual(len(mixed_txs), len(tx_hashes))
        for mixed_tx in mixed_txs:
            self.assertIsNotNone(mixed_tx)
