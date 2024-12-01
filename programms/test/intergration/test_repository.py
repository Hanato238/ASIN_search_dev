import unittest

from programms.main.domain.object.entity import ESeller, EMaster, EJunction, EDetail, EEc
from programms.main.infrastructure.repository.repository import RepoForSeller, RepoForMaster, RepoForJunction, RepoForDetail, RepoForEc

class TestRepoForSeller(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = RepoForSeller()

    def test_save(self) -> None:
        entity = ESeller(seller='test')
        self.repository.save(entity)
        self.assertTrue(self.repository.find_by_column(seller='test'))