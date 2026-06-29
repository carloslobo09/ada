from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.cross_validation import ComparisonType

EstadoPromptVersion = Literal["borrador", "publicada", "archivada"]


class CrossFieldSchema(BaseModel):
    field: str
    comparison: ComparisonType
    critical: bool
    required_expected: bool = False


class PromptVersionCreate(BaseModel):
    tipo_documento_id: str
    prompt_text: str = Field(min_length=1)
    cross_validation_config: list[CrossFieldSchema]


class PromptVersionOut(BaseModel):
    id: str
    numero: int
    tipo_documento_id: str
    prompt_text: str
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
