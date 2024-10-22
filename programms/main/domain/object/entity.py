from typing import Optional
from datetime import datetime
from typing import Optional
from programms.parts3.domain.object.value import Id, Is, SellerId, Asin, Weight, ImageURL, EcURL, LastSearch, Price, Const


class ESeller:
    def __init__(self, id: Optional[int] = None , seller: str = "", is_good: bool = False) -> None:
        self._id = Id(id)
        self._seller = SellerId(seller)
        self._is_good = Is(is_good)

    def __repr__(self) -> str:
        return f"ESellers(id={self.id}, seller={self.seller}, is_good={self.is_good})"

    @property
    def id(self) -> Id:
        return self._id
    
    @property
    def seller(self) -> SellerId:
        return self._seller
    
    @seller.setter
    def seller(self, new_seller: str) -> None:
        self._seller = SellerId(new_seller)
    
    @property
    def is_good(self) -> Is:
        return self._is_good
    
    @is_good.setter
    def is_good(self, new_is_good: bool) -> None:
        self._is_good = Is(new_is_good)

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
        self._id = Id(id)
        self._asin = Asin(asin)
        self._weight = Weight(weight, weight_unit)
        self._image_url = ImageURL(image_url)
        self._last_search = LastSearch(last_search)
        self._ec_search = Is(ec_search)
        self._is_good = Is(is_good)
        self._is_filled = Is(is_filled)

    def __repr__(self) -> str:
        return (f"Product(id={self.id}, asin='{self.asin}', weight={self.weight}, "
                f"weight_unit='{self.weight_unit}', image_url='{self.image_url}', "
                f"last_search={self.last_search}, ec_search={self.ec_search}, "
                f"is_good={self.is_good}, is_filled={self.is_filled})")

    @property
    def id(self) -> Id:
        return self._id
    
    @property
    def asin(self) -> Asin:
        return self._asin
    
    @asin.setter
    def asin(self, new_asin: str) -> None:
        self._asin = Asin(new_asin)

    @property
    def weight(self) -> Weight:
        return self._weight
    
    @weight.setter
    def weight(self, new_weight: float, new_weight_unit: str) -> None:
        self._weight = Weight(new_weight, new_weight_unit)

    @property
    def image_url(self) -> ImageURL:
        return self._image_url
    
    @image_url.setter
    def image_url(self, new_image_url: str) -> None:
        self._image_url = ImageURL(new_image_url)

    @property
    def last_search(self) -> LastSearch:
        return self._last_search
    
    @last_search.setter
    def last_search(self, new_last_search: datetime) -> None:
        self._last_search = LastSearch(new_last_search)

    @property
    def ec_search(self) -> Is:
        return self._ec_search
    
    @ec_search.setter
    def ec_search(self, new_ec_search: bool) -> None:
        self._ec_search = Is(new_ec_search)

    @property
    def is_good(self) -> Is:
        return self._is_good
    
    @is_good.setter
    def is_good(self, new_is_good: bool) -> None:
        self._is_good = Is(new_is_good)

    @property
    def is_filled(self) -> Is:
        return self._is_filled
    
    @is_filled.setter
    def is_filled(self, new_is_filled: bool) -> None:
        self._is_filled = Is(new_is_filled)


class EJunction:
    def __init__(self, id: Optional[int] = None , seller_id: int = 0, product_id: int = 0, seller: SellerId = None, asin: Asin = None) -> None:
        self._id = Id(id)
        self._seller_id = Id(seller_id)
        self._product_id = Id(product_id)

        self._seller = SellerId(seller)
        self._asin = Asin(asin)

    def __repr__(self) -> str:
        return f"EJunction(id={self.id}, seller_id={self.seller_id}, product_id={self.product_id})"

    @property
    def id(self) -> Id:
        return self._id
    
    @property
    def seller_id(self) -> Id:
        return self._seller_id
    
    @seller_id.setter
    def seller_id(self, new_seller_id: int) -> None:
        self._seller_id = Id(new_seller_id)
    
    @property
    def product_id(self) -> Id:
        return self._product_id
    
    @product_id.setter
    def product_id(self, new_product_id: int) -> None:
        self._product_id = Id(new_product_id)
    
    @property
    def seller(self) -> SellerId:
        return self._seller
    
    @seller.setter
    def seller(self, new_seller: str) -> None:
        self._seller = SellerId(new_seller)

    @property
    def asin(self) -> Asin:
        return self._asin
    
    @asin.setter
    def asin(self, new_asin: str) -> None:
        self._asin = Asin(new_asin)

## EDetail = master + detail table
class EDetail:
    def __init__(self,
                 id: Optional[int] = None, 
                 product_id: int = 0,
                
                 asin: Optional[str] = None, 
                 weight: Optional[float] = None, 
                 weight_unit: Optional[str] = None, 
                 last_search: datetime = datetime(2000, 1, 1),

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
        self._asin = Asin(asin)
        self._weight = Weight(weight, weight_unit)
        self._last_search = LastSearch(last_search)
        self._id = Id(id)
        self._product_id = Id(product_id)
        self._ec_id = Id(ec_id)
        self._purchase_price = Price(purchase_price)
        self._research_date = research_date
        self._three_month_sales = Const(three_month_sales)
        self._competitors = Const(competitors)
        self._sales_price = Price(sales_price)
        self._commission = Price(commission)
        self._import_fees = Price(import_fees)
        self._roi = Const(roi)
        self._decision = Is(decision)
        self._final_decision = Is(final_decision)
        self._is_filled = Is(is_filled)

    def __repr__(self) -> str:
        return (f"ProductDetail(id={self.id}, product_id={self.product_id}, ec_id={self.ec_id}, "
                f"purchase_price={self.purchase_price}, research_date={self.research_date}, "
                f"three_month_sales={self.three_month_sales}, competitors={self.competitors}, "
                f"sales_price={self.sales_price}, commission={self.commission}, "
                f"import_fees={self.import_fees}, roi={self.roi}, decision={self.decision}, "
                f"final_decision={self.final_decision}, is_filled={self.is_filled})")

    @property
    def id(self) -> Id:
        return self._id
    
    @property
    def product_id(self) -> Id:
        return self._product_id
    
    @property
    def asin(self) -> Asin:
        return self._asin
    
    @property
    def weight(self) -> Weight:
        return self._weight
    
    @property
    def last_search(self) -> LastSearch:
        return self._last_search
    
    @last_search.setter
    def last_search(self, new_last_search: datetime) -> None:
        self._last_search = LastSearch(new_last_search)

    @property
    def ec_id(self) -> Id:
        return self._ec_id
    
    @ec_id.setter
    def ec_id(self, new_ec_id: int) -> None:
        self._ec_id = Id(new_ec_id)

    @property
    def purchase_price(self) -> Price:
        return self._purchase_price
    
    @purchase_price.setter
    def purchase_price(self, new_purchase_price: float) -> None:
        self._purchase_price = Price(new_purchase_price)

    @property
    def research_date(self) -> datetime:
        return self._research_date
    
    @research_date.setter
    def research_date(self, new_research_date: datetime) -> None:
        self._research_date = new_research_date

    @property
    def three_month_sales(self) -> Const:
        return self._three_month_sales
    
    @three_month_sales.setter
    def three_month_sales(self, new_three_month_sales: int) -> None:
        self._three_month_sales = Const(new_three_month_sales)

    @property
    def competitors(self) -> Const:
        return self._competitors
    
    @competitors.setter
    def competitors(self, new_competitors: int) -> None:
        self._competitors = Const(new_competitors)

    @property
    def sales_price(self) -> Price:
        return self._sales_price
    
    @sales_price.setter
    def sales_price(self, new_sales_price: int, new_currency: str = 'JPY') -> None:
        self._sales_price = Price(new_sales_price, new_currency)

    @property
    def commission(self) -> Price:
        return self._commission
    
    @commission.setter
    def commission(self, new_commission: int, new_currency: str = 'JPY') -> None:
        self._commission = Price(new_commission, new_currency)

    @property
    def import_fees(self) -> Price:
        return self._import_fees
    
    @import_fees.setter
    def import_fees(self, new_import_fees: float, new_currency: str = 'JPY') -> None:
        self._import_fees = Price(new_import_fees, new_currency)

    @property
    def roi(self) -> Const:
        return self._roi
    
    @roi.setter
    def roi(self, new_roi: float) -> None:
        self._roi = Const(new_roi)

    @property
    def decision(self) -> Is:
        return self._decision
    
    @decision.setter
    def decision(self, new_decision: bool) -> None:
        self._decision = Is(new_decision)

    @property
    def final_decision(self) -> Is:
        return self._final_decision
    
    @final_decision.setter
    def final_decision(self, new_final_decision: bool) -> None:
        self._final_decision = Is(new_final_decision)

    @property
    def is_filled(self) -> Is:
        return self._is_filled
    
    @is_filled.setter
    def is_filled(self, new_is_filled: bool) -> None:
        self._is_filled = Is(new_is_filled)


    def calc_import_fees(self) -> None:
        import_tax_rate = 0.1
        import_tax = self.purchase_price.value * (1 + import_tax_rate)
        transfer_fees = self.weight.convert_to_gram().value() * 2
        self.import_fees = Price(import_tax + transfer_fees)

    def calc_roi(self) -> None:
        sales_price = self.sales_price.value.convert_to_jpy()
        commission = self.commission.value.convert_to_jpy()
        purchase_price = self.purchase_price.value.convert_to_jpy()
        import_fees = self.import_fees.value.convert_to_jpy()

        profit = sales_price.subtract(commission).subtract(purchase_price).subtract(import_fees)
        roi = profit.value / purchase_price.value
        self.roi = roi

    def make_decision(self, p: float = 0.3) -> bool:
        if self.roi == None:
            raise ValueError('roi is None')
        elif self.roi > p:
            self.decision = True
        else:
            self.decision = False

# Masterと連携
class EEc:
    def __init__(self, 
                 id: Optional[int] = None, 
                 product_id: int = 0, 

                 asin: Optional[str] = None,
                 image_url: Optional[str] = None,

                 price: Optional[float] = None, 
                 currency: Optional[str] = None, 
                 is_available: Optional[bool] = None, 
                 ec_url: Optional[str] = None, 
                 is_filled: bool = False, 
                 is_supported: bool = False):
        self._id =Id(id)
        self._product_id = Id(product_id)
        self._asin = Asin(asin)
        self._image_url = ImageURL(image_url)
        self._price = Price(price, currency)
        self._is_available = Is(is_available)
        self._ec_url = EcURL(ec_url)
        self._is_filled = Is(is_filled)
        self._is_supported = Is(is_supported)

    def __repr__(self) -> str:
        return (f"ProductEC(id={self.id}, product_id={self.product_id}, price={self.price}, "
                f"currency='{self.currency}', is_available={self.is_available}, "
                f"ec_url='{self.ec_url}', is_filled={self.is_filled}, is_supported={self.is_supported})")

    @property
    def id(self) -> Id:
        return self._id
    
    @property
    def product_id(self) -> Id:
        return self._product_id
    
    @property
    def asin(self) -> Asin:
        return self._asin
    
    @property
    def image_url(self) -> ImageURL:
        return self._image_url
    
    @property
    def price(self) -> Price:
        return self._price
    
    @price.setter
    def price(self, new_price: float, new_currency: str) -> None:
        self._price = Price(new_price, new_currency)

    @property
    def is_available(self) -> Is:
        return self._is_available
    
    @is_available.setter
    def is_available(self, new_is_available: bool) -> None:
        self._is_available = Is(new_is_available)

    @property
    def ec_url(self) -> EcURL:
        return self._ec_url
    
    @ec_url.setter
    def ec_url(self, new_ec_url: str) -> None:
        self._ec_url = EcURL(new_ec_url)

    @property
    def is_filled(self) -> Is:
        return self._is_filled
    
    @is_filled.setter
    def is_filled(self, new_is_filled: bool) -> None:
        self._is_filled = Is(new_is_filled)

    @property
    def is_supported(self) -> Is:
        return self._is_supported
    
    @is_supported.setter
    def is_supported(self, new_is_supported: bool) -> None:
        self._is_supported = Is(new_is_supported)

