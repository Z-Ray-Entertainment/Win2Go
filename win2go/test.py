import struct
import uuid

uuid_str = "BEF2AFB5-766F-4BD6-B4F8-40992645652B"
uuid_obj = uuid.UUID(uuid_str)
print(uuid_str)
print(uuid_obj.bytes.hex().upper())
print(uuid_obj.urn)