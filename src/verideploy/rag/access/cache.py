from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from typing import Generic, TypeVar
from .schemas import EffectiveRetrievalScope
T=TypeVar("T")
@dataclass
class ScopedRetrievalCache(Generic[T]):
    def __post_init__(self): self._data:dict[tuple[str,str],T]={}
    def get(self,key:str,scope:EffectiveRetrievalScope)->T|None:
        value=self._data.get((key,scope.fingerprint())); return deepcopy(value) if value is not None else None
    def put(self,key:str,scope:EffectiveRetrievalScope,value:T)->None:
        self._data[(key,scope.fingerprint())]=deepcopy(value)
    def size(self)->int:return len(self._data)
