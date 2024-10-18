import keepa

from programms.parts3.domain.interface.i_api_client import IKeepaClient
from programms.parts3.infrastructure.object.dto import MasterData, DetailData, SellerInfoData
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class KeepaClient(IKeepaClient):
    _instance = None

    def __new__(cls, api_key: str) -> 'KeepaClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.api_key = api_key
        return cls._instance
    
    def _initialize(self) -> None:
        self.api = keepa.Keepa(self.api_key)

    # return asins = List[str]
    def search_asin_by_seller(self, seller: str) -> List[MasterData]:
        try:
            products = self.api.seller_query(seller, domain='JP', storefront=True)
            asins = products[seller]['asinList']
            return asins
        except Exception as e:
            logging.error(f"Error fetching ASINs for seller {seller}: {e}")
            return []

## for seller
    def query_seller_info(self, asin: str) -> Dict[SellerInfoData]:
        infos = self.api.query(asin, domain='JP', history=False, offers=20, only_live_offers=True)[0]['offers']
        data = []
        for info in infos:
            datums = SellerInfoData(info)
            data.append(datums)
        return data

    def search_three_month_sales(self, asin: str) -> int:
        products = self.api.query(asin, domain='JP', stats=90)
        sales_rank_drops = products[0]['stats']['salesRankDrops90']
        return sales_rank_drops
    
# api.query_seller_info(asin)    
    '''
        this returns data
        1. data[0][['offers'] : market place object　: read "https://keepa.com/#!discuss/t/marketplace-offer-object/807"
            {
                "offerId": Integer,
                "lastSeen": Integer,
                "sellerId": String,
                "isPrime": Boolean,
                "isFBA": Boolean,
                "isMAP": Boolean,
                "isShippable": Boolean,
                "isAddonItem": Boolean,
                "isPreorder": Boolean,
                "isWarehouseDeal": Boolean,
                "isScam": Boolean,
                "shipsFromChina": Boolean,
                "isAmazon": Boolean,
                "isPrimeExcl": Boolean,
                "coupon": Integer,
                "couponHistory": Integer array,
                "condition": Integer,
                "minOrderQty": Integer,
                "conditionComment": String,
                "offerCSV": Integer array,
                "stockCSV": Integer array,
                "primeExclCSV": Integer array
            }
    '''