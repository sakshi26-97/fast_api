from typing import Optional, List, Set
from pydantic import BaseModel, Field, HttpUrl

class Image(BaseModel):
  url: HttpUrl
  name: str

class Item(BaseModel):
  name: str
  price: float = Field(..., gt=0, description="The price must be greater than zero")
  description: Optional[str] = Field(..., description="Description of the item", max_length=300)
  is_offer: bool = Field(default=False)
  tax: Optional[float] = None
  tags: Set[str] = set()
  images: Optional[List[Image]] = None

  class Config:
    schema_extra = {
        "example": {
            "name": "Foo",
            "price": 35.4,
            "is_offer": 1,
            "description": "A very nice Item",
            "tax": 3.2,
            "tags": [
              "rock",
              "metal",
              "bar"
            ],
            "images": [
                {
                    "url": "http://example.com/baz.jpg",
                    "name": "The Foo live"
                },
                {
                    "url": "http://example.com/dave.jpg",
                    "name": "The Baz"
                }
            ]
        }
    }

fake_db_items = {
  1: {
      "name": "Foo",
      "price": 35.4,
      "is_offer": 1,
      "description": "A very nice Item",
      "tax": 3.2,
      "tags": [
        "rock",
        "metal",
        "bar"
      ],
      "images": [
          {
              "url": "http://example.com/baz.jpg",
              "name": "The Foo live"
          },
          {
              "url": "http://example.com/dave.jpg",
              "name": "The Baz"
          }
      ]
    }
}