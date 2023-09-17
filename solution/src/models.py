import pydantic


class Transaction(pydantic.BaseModel):
    hash: str
    fromAddress: str
    toAddress: str
    blockNumber: int
    executedAt: str
    gasUsed: int
    gasCostInDollars: float
