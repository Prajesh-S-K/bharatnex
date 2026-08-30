"""Typed request models for prototype operator and inspection workflows."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class LoginRequest(BaseModel):
    role: Literal["OPERATOR", "ADMIN", "INSPECTION", "VIEWER"]
    pin: str = Field(min_length=4, max_length=32)
    unit_id: Literal["ALPHA", "BRAVO"] | None = None

    @model_validator(mode="after")
    def inspection_requires_unit(self):
        if self.role == "INSPECTION" and self.unit_id is None:
            raise ValueError("Inspection login requires a unit identity")
        return self


class InspectionUpdateRequest(BaseModel):
    status: Literal[
        "ACCEPTED",
        "EN_ROUTE",
        "ON_SITE",
        "INSPECTION_STARTED",
        "COMPLETED",
        "REJECTED",
        "ASSISTANCE_REQUESTED",
    ]
    notes: str | None = Field(default=None, max_length=2000)
    severity: Literal["LOW", "MODERATE", "HIGH", "URGENT"] | None = None
    checklist: dict[str, bool] = Field(default_factory=dict)
    photos: list[str] = Field(default_factory=list, max_length=3)
    rejection_reason: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def rejection_needs_reason(self):
        if self.status == "REJECTED" and not self.rejection_reason:
            raise ValueError("A rejection reason is required")
        return self


class ResolveRequest(BaseModel):
    notes: str = Field(min_length=3, max_length=2000)


class AcknowledgeRequest(BaseModel):
    actor: str = Field(default="OPERATOR", min_length=2, max_length=60)
