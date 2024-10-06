from pydantic import BaseModel, Field
from typing import List

from app.models import Resource


class ResourceRequest(BaseModel):
    id: str = Field(None)
    cpu_cores: int = Field(..., gt=0)
    memory: float = Field(..., gt=0)
    storage: float = Field(..., gt=0)
    network_bandwidth: float = Field(..., gt=0)
    energy_consumption: float = Field(..., gt=0)
    status: str = Field(..., pattern="^(ACTIVE|INACTIVE)$")

    def to_model(self):
        return Resource(
            id=self.id,
            cpu_cores=self.cpu_cores,
            memory=self.memory,
            storage=self.storage,
            network_bandwidth=self.network_bandwidth,
            energy_consumption=self.energy_consumption,
            status=self.status,
        )


class VMRequest(BaseModel):
    id: str = Field(None)
    cpu_cores: int = Field(..., gt=0)
    memory: float = Field(..., gt=0)
    storage: float = Field(..., gt=0)
    network_bandwidth: float = Field(..., gt=0)

class PredictRequest(BaseModel):
    population_size: int = Field(..., gt=0)
    generations: int = Field(..., gt=0)
    chance_mutation: int = Field(..., ge=0, le=100)
    vms: List[VMRequest] = Field(..., min_length=1)
