from __future__ import annotations
from datetime import datetime
import json


class InvoiceData:
    invoice_number: str | None = None
    purchase_order_number: str | None = None
    customer_name: str | None = None
    customer_address: str | None = None
    delivery_date: str | None = None
    payable_by: str | None = None
    products: list[InvoiceProduct] | None = None
    returns: list[InvoiceProduct] | None = None
    total_quantity: float | None = None
    total_price: float | None = None
    products_signatures: list[InvoiceSignature] | None = None
    returns_signatures: list[InvoiceSignature] | None = None

    @staticmethod
    def empty() -> InvoiceData:
        result = InvoiceData()
        result.invoice_number = ""
        result.purchase_order_number = ""
        result.customer_name = ""
        result.customer_address = ""
        result.delivery_date = datetime.now().isoformat()
        result.payable_by = datetime.now().isoformat()
        result.products = [
            InvoiceProduct.empty()
        ]
        result.returns = [
            InvoiceProduct.empty()
        ]
        result.total_quantity = 0
        result.total_price = 0
        result.products_signatures = [
            InvoiceSignature.empty()
        ]
        result.returns_signatures = [
            InvoiceSignature.empty()
        ]
        return result

    def to_dict(self) -> dict:
        return {
            "invoice_number": self.invoice_number,
            "purchase_order_number": self.purchase_order_number,
            "customer_name": self.customer_name,
            "customer_address": self.customer_address,
            "delivery_date": self.delivery_date,
            "payable_by": self.payable_by,
            "products": [p.to_dict() for p in self.products],
            "returns": [p.to_dict() for p in self.returns],
            "total_quantity": self.total_quantity,
            "total_price": self.total_price,
            "products_signatures": [s.to_dict() for s in self.products_signatures],
            "returns_signatures": [s.to_dict() for s in self.returns_signatures]
        }

    @staticmethod
    def to_json(obj: InvoiceData) -> str:
        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> InvoiceData:
        return InvoiceData.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> InvoiceData:
        result = InvoiceData()
        result.invoice_number = obj["invoice_number"]
        result.purchase_order_number = obj["purchase_order_number"]
        result.customer_name = obj["customer_name"]
        result.customer_address = obj["customer_address"]
        result.delivery_date = obj["delivery_date"]
        result.payable_by = obj["payable_by"]
        result.products = [InvoiceProduct.from_dict(
            p) for p in obj["products"]]
        result.returns = [InvoiceProduct.from_dict(p) for p in obj["returns"]]
        result.total_quantity = obj["total_quantity"]
        result.total_price = obj["total_price"]
        result.products_signatures = [InvoiceSignature.from_dict(
            s) for s in obj["products_signatures"]]
        result.returns_signatures = [InvoiceSignature.from_dict(
            s) for s in obj["returns_signatures"]]
        return result


class InvoiceProduct:
    id: str | None = None
    description: str | None = None
    unit_price: float | None = None
    quantity: float | None = None
    total: float | None = None
    reason: str | None = None

    @staticmethod
    def empty() -> InvoiceProduct:
        result = InvoiceProduct()
        result.id = ""
        result.description = ""
        result.unit_price = 0
        result.quantity = 0
        result.total = 0
        result.reason = ""
        return result

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "unit_price": self.unit_price,
            "quantity": self.quantity,
            "total": self.total,
            "reason": self.reason
        }

    @staticmethod
    def to_json(obj: InvoiceProduct) -> str:
        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> InvoiceProduct:
        return InvoiceProduct.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> InvoiceProduct:
        result = InvoiceProduct()
        result.id = obj["id"]
        result.description = obj["description"]
        result.unit_price = obj["unit_price"]
        result.quantity = obj["quantity"]
        result.total = obj["total"]
        result.reason = obj["reason"]
        return result


class InvoiceSignature:
    type: str | None = None
    name: str | None = None
    is_signed: bool | None = None

    @staticmethod
    def empty() -> InvoiceSignature:
        result = InvoiceSignature()
        result.type = ""
        result.name = ""
        result.is_signed = False
        return result

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "name": self.name,
            "is_signed": self.is_signed
        }

    @staticmethod
    def to_json(obj: InvoiceSignature) -> str:
        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> InvoiceSignature:
        return InvoiceSignature.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> InvoiceSignature:
        result = InvoiceSignature()
        result.type = obj["type"]
        result.name = obj["name"]
        result.is_signed = obj["is_signed"]
        return result
