from typing import Optional, Union
import re
import datetime
import yfinance as yf
from __future__ import annotations

class Id:
    def __init__(self, id: Optional[int] = None) -> None:
        if type(id) != int:
            raise ValueError("id must be an integer")
        self._id = id

    @property
    def value(self) -> int:
        return self._id

    def is_equal(self, other: Id) -> bool:
        return self.value == other.value
    
class ProductId:
    def __init__(self, product_id: Optional[int] = None) -> None:
        if type(product_id) != int:
            raise ValueError("product_id must be an integer")
        self._product_id = product_id

    @property
    def value(self) -> int:
        return self._product_id
    
    def is_equal(self, other: ProductId) -> bool:
        return self.value == other.value

class Is:
    def __init__(self, is_: bool = False) -> None:
        if type(is_) != bool:
            raise ValueError("is_ must be a boolean")
        self._is_ = is_

    @property
    def value(self) -> bool:
        return self._is_

    @value.setter
    def value(self, new_is_: bool) -> None:
        if not isinstance(new_is_, bool):
            raise ValueError("new_is_ must be a boolean")
        self._is_ = new_is_
        
    def is_equal(self, other: Is) -> bool:
        return self.value == other.value

class SellerId:
    _PATTERN = r'([A-Z0-9]{13, 14})?$'
    
    def __init__(self, sellerId: Optional[str] = None) -> None:
        if re.fullmatch(self._PATTERN, sellerId):
            self._value = sellerId
        else:
            raise ValueError("sellerId dose not match the pattern")
        
    @property
    def value(self) -> str:
        return self._value
    
    @value.setter
    def value(self, new_sellerId: str) -> None:
        if re.fullmatch(self._PATTERN, new_sellerId):
            self._value = new_sellerId
        else:
            raise ValueError("New sellerId dose not match the pattern")

    def is_equal(self, other: SellerId) -> bool:
        return self.value == other.value

class Asin:
    _PATTERN = r'(^B0[A-Z0-9]{8})?$'

    def __init__(self, asin: Optional[str] = None) -> None:
        if re.fullmatch(self._PATTERN, asin):
            self._value = asin
        else:
            raise ValueError("asin dose not match the pattern")
        
    @property
    def value(self) -> str:
        return self._value
    
    @value.setter
    def value(self, new_asin: str) -> None:
        if re.fullmatch(self._PATTERN, new_asin):
            self._value = new_asin
        else:
            raise ValueError("New asin dose not match the pattern")
            
    def is_equal(self, other: Asin) -> bool:
        return self.value == other.value
    
class Weight:
    _VALID_UNITS = {'kilogram', 'gram', 'pound', 'ounce'}
    _CONVERSION_RATIO = {
        'gram' : 1, 'kilogram' : 1000, 'pound' : 453.6, 'ounce' : 28.35
    }

    def __init__(self, weight: Optional[float] = None, weight_unit: Optional[str] = None) -> None:
        if type(weight) != float:
            raise ValueError("weight must be a float")
        elif weight_unit not in self._VALID_UNITS:
            raise ValueError("weight_unit is not valid unit")
        self._weight = weight
        self._unit = weight_unit

    @property
    def amount(self) -> float:
        return self._weight
    
    @property
    def unit(self) -> str:
        return self._unit

    @amount.setter
    def amount(self, new_weight: float) -> None:
        self._weight = new_weight

    @unit.setter
    def unit(self, new_unit: str) -> None:
        if new_unit not in self._VALID_UNITS:
            raise ValueError("new_unit is not valid unit")
        self._unit = new_unit

    def convert_to_gram(self) -> float:
        if self.unit in self._CONVERSION_RATIO:
            self.amount = self.amount * self._CONVERSION_RATIO[self.unit]
            self.unit = 'gram'
            return self

    def add(self, other: Weight) -> Weight:
        if self.unit != other.unit:
            raise ValueError("Unit mismatch")
        return Weight(self.amount + other.amount, self.unit)
    
    def is_equal(self, other: Weight) -> bool:
        if not self.unit == other.unit:
            raise ValueError('Unit mismatch')
        return self.amount == other.amount

class ImageURL:
    _PATTERN = r'https:\/\/m\.media\-amazon\.com\/images\/I\/.*\.jpg|None'

    def __init__(self, image_url: Optional[str] = None) -> None:
        if re.fullmatch(self._PATTERN, image_url):
            self._value = image_url
        else:
            raise ValueError("image_url dose not match the pattern")
        
    @property
    def value(self) -> str:
        return self._value
    
    @value.setter
    def value(self, new_image_url: str) -> None:
        if re.fullmatch(self._PATTERN, new_image_url):
            self._value = new_image_url
        else:
            raise ValueError("New image_url dose not match the pattern")

    def is_equal(self, other: ImageURL) -> bool:
        return self.value == other.value
    
class EcURL:
    _PATTERN = {
        "Amazon" : r"https:\\\\/\\\\/www\\\\.amazon\\\\.(com(\\\\.au|\\\\.be|\\\\.br|\\\\.mx|\\\\.cn|\\\\.sg)?|ca|cn|eg|fr|de|in|it|co\\\\.(jp|uk)|nl|pl|sa|sg|es|se|com\\\\.tr|ae)\\\\/(?:dp|gp|[^\\\\/]+\\\\/dp)\\\\/[A-Z0-9]{10}(?:\\\\/[^\\\\/]*)?(?:\\\\?[^ ]*)?",
        "Walmart" : r"https:\\\\/\\\\/www\\\\.walmart\\\\.(com|ca)\\\\/ip\\\\/[A-Za-z0-9-]+\\\\/[A-Za-z0-9]+",
        "Ebay" : r"https:\/\/www\.ebay\.com\/itm\/.*"
    }

    def __init__(self, ec_url: Optional[str] = None) -> None:
        if ec_url is not None and not self._matches_any_pattern(ec_url):
            raise ValueError(f"Value '{ec_url}' does not match any of the allowed patterns.")
        self._value = ec_url

    def _matches_any_pattern(self, ec_url: str) -> bool:
        return any(re.fullmatch(pattern, ec_url) for pattern in self._PATTERNS.values())

    @property
    def value(self) -> Optional[str]:
        return self._value
    
    @value.setter
    def value(self, new_ec_url: Optional[str]) -> None:
        if new_ec_url is not None and not self._matches_any_pattern(new_ec_url):
            raise ValueError(f"Value '{new_ec_url}' does not match any of the allowed patterns.")
        self._value = new_ec_url

    def is_equal(self, other: EcURL) -> bool:
        return self.value == other.value
    
# Dateクラスでよくね？
class LastSearch:
    _SEARCH_PERIOD = 30

    def __init__(self, last_search: datetime = datetime(2000, 1, 1)) -> None:
        if type(last_search) != datetime:
            raise ValueError("last_search must be a datetime")
        self._value = last_search

    @property
    def value(self) -> datetime:
        return self._value
    
    def to_researh(self) -> bool:
        last_search = self.value
        period = datetime.now() - last_search
        if period.days >= self._SEARCH_PERIOD:
            return True
        else:
            return False

class Const:
    def __init__(self, value: Optional[Union[int, float]] = None) -> None:
        self._value = value

    @property
    def value(self) -> Optional[Union[int, float]]:
        return self._value
    
    def is_equal(self, other: Const) -> bool:
        return self.value == other.value

class PriceConverter:
    def __init__(self):
        self.exchange_rates = self._get_exchange_rates()

    def _get_exchange_rates(self, currency: str) -> float:
        if currency == 'JPY':
            return 1.0
        ticker = f'{currency}JPY=X'
        data = yf.Ticker(ticker)
        exchange_rate = data.history(period="1d")['Close'][0]
        return exchange_rate
    
    def convert_to_jpy(self, price: float, currency: str) -> float:
        exchange_rate = self.exchange_rates[currency]
        return price * exchange_rate
    
class Price(PriceConverter):
    _CURRENCY = {'USD', 'EUR', 'JPY', 'CNY'}

    def __init__(self, price: Optional[float] = None, currency: Optional[str] = 'JPY') -> None:
        if type(price) != float:
            raise ValueError("price must be a float")
        elif currency not in self._CURRENCY:
            raise ValueError("currency is not supported")
        self._price = price
        self._currency = currency

    @property
    def amount(self) -> float:
        return self._price
    
    @property
    def currency(self) -> str:
        return self._currency
    
    @amount.setter
    def amount(self, new_price: float) -> None:
        self._price = new_price

    @currency.setter
    def currency(self, new_currency: str) -> None:
        if new_currency not in self._CURRENCY:
            raise ValueError("new_currency is not supported")
        self._currency = new_currency

    def convert_to_jpy(self) -> float:
        return self.convert_to_jpy(self.price, self.currency)
    
    def add(self, other: Price) -> Price:
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Price(self.price + other.price, self.currency)
    
    def subtract(self, other: Price) -> Price:
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Price(self.price - other.price, self.currency)
    
    def is_equal(self, other: Price) -> bool:
        if self.currency != other.currency:
            raise ValueError('Currency mismatch')
        return self.amount == other.amount