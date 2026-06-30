from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.cross_validation import ComparisonType, NormalizationType

EstadoPromptVersion = Literal["borrador", "publicada", "archivada"]


class ExtractionFieldSchema(BaseModel):
    name: str = Field(min_length=1, max_length=80, pattern=r"^[a-z][a-z0-9_]*$")
    label: str = Field(min_length=1, max_length=120)


class CrossFieldSchema(BaseModel):
    field: str
    normalization: list[NormalizationType] = Field(default_factory=list)
    comparison: ComparisonType
    critical: bool
    required_expected: bool = False


class PromptVersionCreate(BaseModel):
    tipo_documento_id: str
    prompt_text: str = Field(min_length=1)
    extraction_fields: list[ExtractionFieldSchema] = Field(min_length=1)
    cross_validation_config: list[CrossFieldSchema]


class PromptVersionOut(BaseModel):
    id: str
    numero: int
    tipo_documento_id: str
    prompt_text: str
    extraction_fields: list[ExtractionFieldSchema]
    cross_validation_config: list[CrossFieldSchema]
    estado: EstadoPromptVersion
    ref_usuario_creador: str | None
    ref_usuario_publicador: str | None
    created_at: datetime
    activated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class PromptVersionListItem(BaseModel):
    id: str
    numero: int
    tipo_documento_id: str
    estado: EstadoPromptVersion
    created_at: datetime
    activated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
