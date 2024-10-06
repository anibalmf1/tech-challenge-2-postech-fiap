from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from typing import List, Any

Base = declarative_base()


class VM(Base):
    __tablename__ = 'vms'
    id = Column(String, primary_key=True)
    resource_id = Column(String, ForeignKey('resources.id'))
    cpu_cores = Column(Integer)
    memory = Column(Float)
    storage = Column(Float)
    network_bandwidth = Column(Float)    


class Resource(Base):
    __tablename__ = 'resources'

    id = Column(String, primary_key=True)
    cpu_cores = Column(Integer)
    memory = Column(Float)
    storage = Column(Float)
    network_bandwidth = Column(Float)
    energy_consumption = Column(Float)
    status = Column(String)

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        self._vm_allocated: List[VM] = []
    
    def allocate(self, vm):
        self._vm_allocated.append(vm)
        
    def clean(self):
        self._vm_allocated = []
        
    def get_available_cpu_cores(self):
        return self.cpu_cores - sum(vm.cpu_cores for vm in self._vm_allocated)

    def get_available_memory(self):
        return self.memory - sum(vm.memory for vm in self._vm_allocated)

    def get_available_storage(self):
        return self.storage - sum(vm.storage for vm in self._vm_allocated)

    def valid(self):
        return (self.get_available_cpu_cores() >= 0
                and self.get_available_memory() >= 0
                and self.get_available_storage() >= 0)
