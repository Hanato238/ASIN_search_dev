from typing import Optional
from datetime import datetime
from typing import Optional
from programms.parts3.domain.object.value import Id, Is, SellerId, Asin, Weight, ImageURL, EcURL, LastSearch, Price


class ESeller:
    def __init__(self, id: Optional[int] = None , seller: str = "", is_good: bool = False) -> None:
        self.id = Id(id)
        self.seller = SellerId(seller)
        self.is_good = Is(is_good)

    def __repr__(self) -> str:
        return f"ESellers(id={self.id}, seller={self.seller}, is_good={self.is_good})"

## EMasterとEDetailは連結すべき
class EMaster:
    def __init__(self, 
                 id: Optional[int] = None, 
                 asin: Optional[str] = None, 
                 weight: Optional[float] = None, 
                 weight_unit: Optional[str] = None, 
                 image_url: Optional[str] = None, 
                 last_search: datetime = datetime(2000, 1, 1), 
                 ec_search: bool = False, 
                 is_good: bool = False, 
                 is_filled: bool = False):
        self.id = Id(id)
        self.asin = Asin(asin)
        self.weight = Weight(weight, weight_unit)
        self.image_url = ImageURL(image_url)
        self.last_search = LastSearch(last_search)
        self.ec_search = Is(ec_search)
        self.is_good = Is(is_good)
        self.is_filled = Is(is_filled)

    def __repr__(self) -> str:
        return (f"Product(id={self.id}, asin='{self.asin}', weight={self.weight}, "
                f"weight_unit='{self.weight_unit}', image_url='{self.image_url}', "
                f"last_search={self.last_search}, ec_search={self.ec_search}, "
                f"is_good={self.is_good}, is_filled={self.is_filled})")

class EJunction:
    def __init__(self, id: Optional[int] = None , seller_id: int = 0, product_id: int = 0) -> None:
        self.id = Id(id)
        self.seller_id = Id(seller_id)
        self.product_id = Id(product_id)

    def __repr__(self) -> str:
        return f"EJunction(id={self.id}, seller_id={self.seller_id}, product_id={self.product_id})"
    
class EDetail:
    def __init__(self, 
                 id: Optional[int] = None, 
                 product_id: int = 0, 
                 ec_id: Optional[int] = None, 
                 purchase_price: Optional[float] = None, 
                 research_date: Optional[datetime] = None, 
                 three_month_sales: Optional[float] = None, 
                 competitors: Optional[int] = None, 
                 sales_price: Optional[int] = None, 
                 commission: Optional[int] = None, 
                 import_fees: Optional[float] = None, 
                 roi: Optional[float] = None, 
                 decision: Optional[bool] = None, 
                 final_decision: Optional[bool] = None, 
                 is_filled: bool = False):
        self.id = Id(id)
        self.product_id = Id(product_id)
        self.ec_id = Id(ec_id)
        self.purchase_price = Price(purchase_price)
        self.research_date = research_date
        self.three_month_sales = three_month_sales
        self.competitors = competitors
        self.sales_price = Price(sales_price)
        self.commission = Price(commission)
        self.import_fees = Price(import_fees)
        self.roi = roi
        self.decision = Is(decision)
        self.final_decision = Is(final_decision)
        self.is_filled = Is(is_filled)

    def __repr__(self) -> str:
        return (f"ProductDetail(id={self.id}, product_id={self.product_id}, ec_id={self.ec_id}, "
                f"purchase_price={self.purchase_price}, research_date={self.research_date}, "
                f"three_month_sales={self.three_month_sales}, competitors={self.competitors}, "
                f"sales_price={self.sales_price}, commission={self.commission}, "
                f"import_fees={self.import_fees}, roi={self.roi}, decision={self.decision}, "
                f"final_decision={self.final_decision}, is_filled={self.is_filled})")

class EEc:
    def __init__(self, 
                 id: Optional[int] = None, 
                 product_id: int = 0, 
                 price: Optional[float] = None, 
                 currency: Optional[str] = None, 
                 is_available: Optional[bool] = None, 
                 ec_url: Optional[str] = None, 
                 is_filled: bool = False, 
                 is_supported: bool = False):
        self.id =Id(id)
        self.product_id = Id(product_id)
        self.price = Price(price, currency)
        self.is_available = Is(is_available)
        self.ec_url = EcURL(ec_url)
        self.is_filled = Is(is_filled)
        self.is_supported = Is(is_supported)

    def __repr__(self) -> str:
        return (f"ProductEC(id={self.id}, product_id={self.product_id}, price={self.price}, "
                f"currency='{self.currency}', is_available={self.is_available}, "
                f"ec_url='{self.ec_url}', is_filled={self.is_filled}, is_supported={self.is_supported})")
