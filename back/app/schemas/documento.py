from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentoOut(BaseModel):
    id: str
    tipo_documento_id: str
    ubicacion_s3: str
    hash_integridad: str
    fecha_recepcion: datetime
    content_type: str
    file_size: int

    model_config = ConfigDict(from_attributes=True)
