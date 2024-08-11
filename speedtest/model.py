"""
model.py

Pydantic-based model of the speedtest time series JSON input (which includes nested JSON objects)
"""

import logging
from datetime import datetime
from pydantic import BaseModel, Field, computed_field, ValidationError, HttpUrl
from loggingrmb import LoggingRmb


logger = LoggingRmb(name='model', console_level=logging.INFO).setup()


class LatencyObject(BaseModel):
    iqm: float
    low: float
    high: float
    jitter: float


class PingObject(BaseModel):
    jitter: float
    latency: float
    low: float
    high: float


class DownloadObject(BaseModel):
    bandwidth: int = Field(ge=0)
    bytes: int = Field(ge=0)
    elapsed: int = Field(gt=0)
    latency: LatencyObject = Field(default=None)

    @computed_field
    @property
    def bw_mbytesec(self) -> float:
        return self.bandwidth / 1000000.0

    @computed_field
    @property
    def mbps(self) -> float:
        return (self.bytes * 8) / (self.elapsed / 1000.0) / 1000000.0  # elapsed is constrained to strictly > 0


class UploadObject(BaseModel):
    bandwidth: int = Field(ge=0)
    bytes: int = Field(ge=0)
    elapsed: int = Field(gt=0)
    latency: LatencyObject = Field(default=None)

    @computed_field
    @property
    def bw_mbytesec(self) -> float:
        return self.bandwidth / 1000000.0

    @computed_field
    @property
    def mbps(self) -> float:
        return (self.bytes * 8) / (self.elapsed / 1000.0) / 1000000.0  # elapsed is constrained to strictly > 0


class InterfaceObject(BaseModel):
    internalIp: str
    name: str
    macAddr: str
    isVpn: bool
    externalIp: str


class ServerObject(BaseModel):
    id: int
    host: str
    port: int
    name: str
    location: str
    country: str
    ip: str


class ResultObject(BaseModel):
    id: str
    url: HttpUrl = Field(default=None, description='(not present if persisted is False)')
    persisted: bool


class MainObject(BaseModel):
    type: str
    timestamp: str = Field(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        description="Timestamp in YYYY-MM-DDTHH:MM:SSZ format (UTC only)"
    )
    ping: PingObject
    download: DownloadObject
    upload: UploadObject
    packetLoss: float = Field(default=None)
    isp: str
    interface: InterfaceObject
    server: ServerObject
    result: ResultObject

    @computed_field
    @property
    def timestamp_(self) -> datetime:
        try:
            return datetime.strptime(self.timestamp, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as ex:
            raise ValidationError
