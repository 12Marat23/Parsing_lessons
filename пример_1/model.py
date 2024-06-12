from dataclasses import dataclass

@dataclass
class Product:
    count: int
    sku: int
    name: str
    link: str
    price: float
