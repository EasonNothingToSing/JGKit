from __future__ import annotations
import logging
import math
import struct
from crc import Calculator, Configuration
from entry import Entry
from exception import ChecksumError, EncodingError, ParameterError


class Ate:
    """Class responsible for Allocation Table Entry decoding/encoding."""

    _SIZE = 32
    _DATA_ALIGNMENT = 4
    _CRC_CALCULATOR = Calculator(Configuration(width=32, polynomial=0x07, init_value=0xff))

    def __init__(self, ate_offset: int, data_id: int, data: bytes, data_offset: int):
        """
        Initializes ATE.

        :param int ate_offset: Offset of ATE
        :param int data_id: ID of data to be allocated
        :param bytes data: Data to be allocated
        :param int data_offset: Offset of data in sector
        """
        if data_offset % Ate._DATA_ALIGNMENT or ate_offset % Ate._DATA_ALIGNMENT:
            raise ParameterError("Offset not aligned")

        self.ate_offset = ate_offset
        self.data_id = data_id
        self.data_offset = data_offset
        self.data = data

    def get_entry(self) -> Entry | None:
        """
        Returns Entry if ATE is not special kind (close of gc).

        :return: Entry or None
        """
        if self.is_close or self.is_gc_done:
            return None
        return Entry(self.data_id, self.data)

    @property
    def data_len(self):
        return 0 if self.data is None else len(self.data)

    @property
    def is_close(self):
        return self.data_id == 0xFFFF and self.data is None and self.data_offset != 0x00

    @property
    def is_gc_done(self):
        return self.data_id == 0xFFFF and self.data is None and self.data_offset == 0x00

    @property
    def aligned_data_size(self):
        return Ate._DATA_ALIGNMENT * math.ceil(self.data_len/Ate._DATA_ALIGNMENT)

    def to_bytes(self, sector_data: bytearray):
        """
        Serializes ATE into given sector.

        :param bytearray sector_data: NVS sector data
        """
        if self.data_offset + self.aligned_data_size > self.ate_offset:
            raise EncodingError("Data does not fit into sector")

        if sector_data[self.ate_offset:self.ate_offset + Ate._SIZE] != b'\xFF' * Ate._SIZE or \
                sector_data[self.data_offset:self.data_offset + self.aligned_data_size] != b'\xFF' * self.aligned_data_size:
            raise EncodingError("Memory not empty")

        ate = struct.pack("<HHHB", self.data_id, self.data_offset, self.data_len, 0xFF)
        ate += Ate._calc_crc(ate).to_bytes(1, 'little')
        if self.data_len:
            sector_data[self.data_offset:self.data_offset + self.data_len] = self.data
        sector_data[self.ate_offset:self.ate_offset + Ate._SIZE] = ate

    def next(self, data_id: int, data: bytes) -> Ate:
        """
        Creates next Ate with given data_id and data.

        :param int data_id: ID of data to be allocated
        :param bytes data: Data to be allocated
        """
        return Ate(self.ate_offset - Ate._SIZE, data_id, data, self.data_offset + self.aligned_data_size)

    @staticmethod
    def _calc_crc(allocation_table_entry: bytes) -> int:
        return Ate._CRC_CALCULATOR.checksum(allocation_table_entry)

    @staticmethod
    def __crc8_ccitt(buf, crc8_value) -> bool:
        crc8_struct_format = "<BBBBBBB"

        crc8_ccitt_small_table = [
            0x00, 0x07, 0x0E, 0x09, 0x1C, 0x1B, 0x12, 0x15,
            0x38, 0x3F, 0x36, 0x31, 0x24, 0x23, 0x2A, 0x2D
        ]

        val = 0xFF
        buf = struct.unpack(crc8_struct_format, bytes(buf[:7]))
        for b in buf:
            val ^= b
            val = (val << 4) ^ crc8_ccitt_small_table[val >> 4]
            val &= 0xFF
            val = (val << 4) ^ crc8_ccitt_small_table[val >> 4]
            val &= 0xFF

        if val == crc8_value:
            return True
        else:
            return False

    @staticmethod
    def from_bytes(ate_offset: int, sector_data: bytes) -> Ate | None:
        """
        Deserializes Ate from bytes.

        :param int ate_offset: Offset of Ate
        :param bytearray sector_data: NVS sector data
        :return: ATE or None if ate_offset points to empty sector data
        """
        ate_data = sector_data[ate_offset:ate_offset + Ate._SIZE]
        if ate_data == bytes.fromhex("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"):
            return None

        # Each entry is 8 bytes
        # 0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7
        # |  ID  | OFFS  |  LEN  | - |CRC|
        data_id, data_offset, data_length, part_value, crc8_value = struct.unpack_from("<HHHBB", ate_data)
        if not Ate.__crc8_ccitt(ate_data, crc8_value):
            # raise ChecksumError(f"ATE CRC is invalid. Data id={hex(data_id)}")
            logging.error(f"ATE CRC is invalid. Data id={hex(data_id)}")
            return None
        return Ate(ate_offset, data_id, sector_data[data_offset:data_offset + data_length] if data_length > 0 else None, data_offset)
