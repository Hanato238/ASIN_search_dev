from programms.parts3.domain.interface.i_api_client import IGasClient
import pandas as pd

class GasClient(IGasClient):
    def write_to_spreadsheet(self, records) -> None:
        return
    
    def read_from_spreadsheet(self) -> None:
        return