import asyncio
import datetime
import logging
import ssl

class SimpleFixClient:
    """
    A minimal, asyncio-based FIX 4.4 client for order placement.
    Supports: Logon, NewOrderSingle, Logout.
    Includes TCP framing and SSL support.
    """

    def __init__(self, host, port, sender_comp_id, target_comp_id, password=None, ssl_enabled=True):
        self.host = host
        self.port = int(port)
        self.sender_comp_id = sender_comp_id
        self.target_comp_id = target_comp_id
        self.password = password
        self.ssl_enabled = ssl_enabled
        self.reader = None
        self.writer = None
        self.seq_num = 1
        self.connected = False
        self.logger = logging.getLogger("fix_client")
        self._buffer = b""

    async def connect(self):
        """Establish TCP connection with optional SSL."""
        self.logger.info(f"Connecting to FIX server {self.host}:{self.port} (SSL={self.ssl_enabled})...")
        try:
            ssl_ctx = None
            if self.ssl_enabled:
                ssl_ctx = ssl.create_default_context()
                # For testing/dev, we might need to disable verification or load specific certs,
                # but default context is safest for production.
                ssl_ctx.check_hostname = False # Often needed for brokers if cert name mismatch
                ssl_ctx.verify_mode = ssl.CERT_NONE # WARNING: For production, should verify. But many brokers have issues.

            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port, ssl=ssl_ctx
            )
            self.connected = True
            self.logger.info("Connected.")
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            raise

    async def disconnect(self):
        """Close TCP connection."""
        if self.writer:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except:
                pass
        self.connected = False
        self.logger.info("Disconnected.")

    def _generate_checksum(self, msg_str):
        # Checksum is sum of all bytes modulo 256
        # msg_str includes 8=... up to the delimiter before 10=
        total = sum(ord(c) for c in msg_str)
        return f"{total % 256:03d}"

    def _format_time(self):
        # UTC timestamp: YYYYMMDD-HH:MM:SS.sss
        return datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]

    def _create_message(self, msg_type, tags):
        """
        Construct a FIX message.
        tags: dict of tag=value
        """
        # Header
        header_tags = {
            8: "FIX.4.4",
            35: msg_type,
            49: self.sender_comp_id,
            56: self.target_comp_id,
            34: self.seq_num,
            52: self._format_time(),
        }

        all_tags = {**header_tags, **tags}

        # Order is important for header: 8, 9, 35 ...
        ordered_parts = []
        ordered_parts.append(f"8={all_tags[8]}")

        # Construct the "content" part (35... to end of body)
        content_parts = []
        content_parts.append(f"35={all_tags[35]}")
        content_parts.append(f"49={all_tags[49]}")
        content_parts.append(f"56={all_tags[56]}")
        content_parts.append(f"34={all_tags[34]}")
        content_parts.append(f"52={all_tags[52]}")

        for tag, value in tags.items():
            if tag not in [8, 9, 35, 49, 56, 34, 52, 10]:
                content_parts.append(f"{tag}={value}")

        content_str = "\x01".join(content_parts) + "\x01"

        # Tag 9
        body_length = len(content_str)

        # Assemble message so far
        msg_so_far = f"8={all_tags[8]}\x019={body_length}\x01{content_str}"

        # Checksum
        checksum = self._generate_checksum(msg_so_far)

        final_msg = f"{msg_so_far}10={checksum}\x01"

        self.seq_num += 1
        return final_msg

    async def send_message(self, msg):
        if not self.writer:
            raise Exception("Not connected")
        self.logger.debug(f"Sending: {msg.replace(chr(1), '|')}")
        self.writer.write(msg.encode('ascii'))
        await self.writer.drain()

    async def read_message(self):
        """
        Reads a single FIX message from the stream, handling fragmentation.
        """
        if not self.reader:
            raise Exception("Not connected")

        while True:
            # Check if we have a full message in buffer
            msg = self._extract_message_from_buffer()
            if msg:
                self.logger.debug(f"Received: {msg.replace(chr(1), '|')}")
                return msg

            # Read more data
            try:
                chunk = await self.reader.read(4096)
                if not chunk:
                    if self._buffer:
                        self.logger.warning("Connection closed with partial data in buffer")
                    return None
                self._buffer += chunk
            except Exception as e:
                self.logger.error(f"Read error: {e}")
                return None

    def _extract_message_from_buffer(self):
        """
        Attempts to parse a complete FIX message from the internal buffer.
        Returns the message string if found, otherwise None.
        """
        if not self._buffer:
            return None

        # Look for start of message "8=FIX..."
        start_idx = self._buffer.find(b"8=FIX")
        if start_idx == -1:
            # Discard garbage if buffer gets too big?
            # For now, keep scanning. If buffer is huge and no start, maybe clear it.
            if len(self._buffer) > 10000:
                self._buffer = b"" # Reset to avoid memory issues
            return None

        # If we have garbage before start, discard it
        if start_idx > 0:
            self._buffer = self._buffer[start_idx:]
            start_idx = 0

        # Need at least header to find body length
        # 8=FIX.4.4|9=LENGTH|
        try:
            # Find first separator after 9=
            # 8=FIX.4.4\x019=
            nine_idx = self._buffer.find(b"\x019=", start_idx)
            if nine_idx == -1: return None

            # Find separator after length value
            length_end_idx = self._buffer.find(b"\x01", nine_idx + 3)
            if length_end_idx == -1: return None

            # Extract body length
            length_str = self._buffer[nine_idx+3:length_end_idx]
            body_length = int(length_str)

            # Total message length calculation:
            # Header up to 9=...| (length_end_idx + 1)
            # + body_length
            # + checksum field "10=XXX|" (7 bytes)

            # Verify body length logic in FIX:
            # Tag 9 is length of message body (starting AFTER tag 9 value and delimiter, up to BEFORE tag 10)
            # i.e. from length_end_idx + 1 ...

            checksum_start = length_end_idx + 1 + body_length

            # Check if we have enough data for checksum tag
            # We expect "10=XXX\x01" at checksum_start
            required_len = checksum_start + 7

            if len(self._buffer) < required_len:
                return None

            # Verify checksum tag presence (optional but good for robustness)
            if self._buffer[checksum_start:checksum_start+3] != b"10=":
                # Malformed or framing error.
                # Strict: discard this start and try again.
                # Loose: assume length was right.
                self.logger.warning("Framing error: expected 10= at calculated position")
                # Discard current header to try finding next message
                self._buffer = self._buffer[1:]
                return None

            full_msg_bytes = self._buffer[:required_len]
            self._buffer = self._buffer[required_len:]

            return full_msg_bytes.decode('ascii')

        except ValueError:
            # Parsing error
            self._buffer = self._buffer[1:]
            return None

    async def logon(self, reset_seq_num=False):
        tags = {
            98: "0", # EncryptMethod: None
            108: "30", # HeartBtInt
        }
        if self.password:
            tags[554] = self.password
        if reset_seq_num:
            tags[141] = "Y"
            self.seq_num = 1

        msg = self._create_message("A", tags)
        await self.send_message(msg)

        # Read until we get Logon response or timeout
        # Some brokers send heartbeats or other info first
        start_time = datetime.datetime.now()
        while (datetime.datetime.now() - start_time).seconds < 10:
            response = await self.read_message()
            if not response:
                return False

            if "35=A" in response:
                self.logger.info("Logon successful.")
                return True
            if "35=5" in response: # Logout/Reject
                self.logger.error(f"Logon rejected: {response}")
                return False

        self.logger.error("Logon timed out")
        return False

    async def logout(self):
        msg = self._create_message("5", {})
        await self.send_message(msg)
        await self.read_message() # Wait for logout response
        await self.disconnect()

    async def place_order(self, symbol, side, qty, price=None, order_type="1"):
        """
        Place New Order Single (35=D)
        """
        cl_ord_id = f"ORD-{datetime.datetime.now().timestamp()}"

        tags = {
            11: cl_ord_id, # ClOrdID
            55: symbol, # Symbol
            54: side, # Side
            60: self._format_time(), # TransactTime
            38: qty, # OrderQty
            40: order_type, # OrdType
        }

        if order_type == "2" and price: # Limit
            tags[44] = price # Price

        msg = self._create_message("D", tags)
        await self.send_message(msg)

        # Wait for execution report
        # Again, might receive other messages first
        start_time = datetime.datetime.now()
        while (datetime.datetime.now() - start_time).seconds < 30:
            response = await self.read_message()
            if not response:
                break

            if "35=8" in response:
                return self._parse_execution_report(response)
            if "35=3" in response: # Reject
                return {"status": "REJECTED", "message": "Order Rejected (35=3)", "raw": response}

        return {"status": "TIMEOUT", "message": "No Execution Report received"}

    def _parse_execution_report(self, msg):
        # A very basic parser
        parts = msg.split("\x01")
        result = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                if k == "39": # OrdStatus
                    result["status"] = "FILLED" if v in ["0", "1", "2"] else "REJECTED"
                if k == "37": # OrderID
                    result["order_id"] = v
                if k == "6": # AvgPx
                    result["avg_price"] = v
                if k == "151": # LeavesQty
                    result["leaves_qty"] = v
                if k == "58": # Text (Reason)
                    result["message"] = v
        return result
