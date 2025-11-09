from typing import Annotated

from fastapi import Depends

from aoq_factory.database.connection import Engine, get_engine

EngineDep = Annotated[Engine, Depends(lambda: get_engine())]
