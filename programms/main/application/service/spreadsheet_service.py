# GasClient @ infrastructure
# SpreadSheetRepo @ ???
class SpreadSheetService:
    def __init__(self, gas_client: GasClient, repo: SpreadSheetRepo) -> None:
        self.gas_client = gas_client
        self.repo = repo

    def export_to_spreadsheet(self) -> None:
        records = self.repo.get_records()
        self.gas_client.write_to_spreadsheet(records)


# IGasClient @ domain
class IGasClient(ABC):
    @abstractmethod
    def write_to_spreadsheet(self, records) -> None:
        pass

    @abstractmethod
    def read_from_spreadsheet(self) -> None:
        pass

# @ infrastructure
class GasClient(IGasClient):
    def write_to_spreadsheet(self, records) -> None:
        return
    
    def read_from_spreadsheet(self) -> None:
        return
    
# domain layer < application layer
# spreadsheetはあくまでUI.　そのRepoもdomain知識と関係ない
# -> ゆえにそのほかのservice repoもapplication layerにあるべき
class SpreadSheetRepo:
    def save(self) -> None:
        return
    
    def get_records(self) -> None:
        return