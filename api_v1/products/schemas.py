from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    price: int
    description: str


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductCreate):
    pass


class Particular_uptade_prodact(ProductCreate):
    name: str | None = None
    price: int | None = None
    description: str | None = None


class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
