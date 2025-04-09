import asyncio
from dataclasses import dataclass
import zlib

import serial

from core import PluginBase, Payload, PayloadType


SSDV_TYPE_NORMAL = 0x00
SSDV_TYPE_NOFEC = 0x01

SSDV_PKT_SIZE_HEADER = 0x0F
SSDV_PKT_SIZE_CRC = 0x04
SSDV_PKT_SIZE_RSCODES = 0x20


# This should be a variable, but lets just hardcode it for now
SSDV_PACKET_SIZE = 256


@dataclass
class SSDVHeader:
    type: int
    callsign: str
    image_id: int
    packet_id: int
    width: int
    height: int
    eoi: int
    quality: int
    mcu_mode: int
    mcu_offset: int
    mcu_id: int
    mcu_count: int


def decode_callsign(encoded_callsign):

    if encoded_callsign > 0xF423FFFF:
        return "INVALID"

    callsign = ""

    i = 0
    while i < encoded_callsign:
        s = encoded_callsign % 40
        if s == 0:
            callsign += "-"
        elif s < 11:
            callsign += chr(ord("0") + s - 1)
        elif s < 14:
            callsign += "-"
        else:
            callsign += chr(ord("A") + s - 14)
        encoded_callsign = encoded_callsign // 40

    return callsign


def decode_header(header_data):
    return SSDVHeader(
        type=header_data[1] - 0x66,
        callsign=decode_callsign(
            (header_data[2] << 24)
            | (header_data[3] << 16)
            | (header_data[4] << 8)
            | header_data[5]
        ),
        image_id=header_data[6],
        packet_id=(header_data[7] << 8) | header_data[8],
        width=header_data[9] << 4,
        height=header_data[10] << 4,
        eoi=(header_data[11] >> 2) & 1,
        quality=((header_data[11] >> 3) & 7) ^ 4,
        mcu_mode=header_data[11] & 0x03,
        mcu_offset=header_data[12],
        mcu_id=(header_data[13] << 8) | header_data[14],
        mcu_count=header_data[9] * header_data[10],
    )


def decode_data(data):

    # Find the start of the image data
    for i, byte in enumerate(data):
        if byte != 0x55:
            continue
        if data[i + 1] == 0x66 + SSDV_TYPE_NORMAL:

            payload_size = (
                SSDV_PACKET_SIZE
                - SSDV_PKT_SIZE_HEADER
                - SSDV_PKT_SIZE_CRC
                - SSDV_PKT_SIZE_RSCODES
            )
            crcdata_size = SSDV_PKT_SIZE_HEADER + payload_size - 1

            # Calculate the CRC
            # Skip the first byte as it's a header and not included
            crc = zlib.crc32(data[i + 1 : i + 1 + crcdata_size])

            # Check the CRC
            validation_point = i + 1 + crcdata_size

            validation = (
                (data[validation_point + 3])
                | (data[validation_point + 2] << 8)
                | (data[validation_point + 1] << 16)
                | (data[validation_point] << 24)
            )
            if crc != validation:
                continue

            # Decode the header
            header = decode_header(data[i : i + SSDV_PKT_SIZE_HEADER])
            return header


class ssdv_serial_receiver(PluginBase):

    async def start(self):
        await super().start()
            try:
            self.serial_port = serial.Serial(
                self.config["port"], self.config["baudrate"]
            )
            self.loop.run_in_executor(None, self.read_serial)
        except Exception as e:
            self.logger.error("Failed to open serial port", error=str(e))

    def read_serial(self):
        while True:
            line = self.serial_port.readline().strip()
            self.logger.debug("Received line from serial port", line=line)
            if not line.startswith(b"$$"):
                continue
            self.logger.info(
                "Received line from serial port", line=line, length=len(line)
            )
            try:
                header = decode_data(bytes.fromhex(line.removeprefix(b"$$").decode()))
                payload = Payload(
                    type=PayloadType.SSDV,
                    callsign=header.callsign,
                    payload_id=header.image_id,
                    other_fields={
                        "ssdv": line.removeprefix(b"$$").decode(),
                        "ssdv_header": header,
                    },
                )
            except Exception as e:
                self.logger.error("Failed to parse SSDV payload", error=str(e))
                continue
            asyncio.run(self.core.receive_payload(payload))

    def run(self):
        self.logger.info("Running plugin with config", config=self.config)
