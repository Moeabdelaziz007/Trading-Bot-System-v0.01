import asyncio
import ssl
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

SOH = '\x01'

class SimpleFixClient:
    """
    A simple, pure Python FIX 4.4 client for cTrader/IC Markets.
    Supports SSL, Logon, Heartbeats, and basic message exchange.
    """
    def __init__(self, host, port, sender_comp_id, target_comp_id, username, password, target_sub_id="TRADE"):
        self.host = host
        self.port = int(port)
        self.sender_comp_id = sender_comp_id
        self.target_comp_id = target_comp_id
        self.username = username
        self.password = password
        self.target_sub_id = target_sub_id
        self.reader = None
        self.writer = None
        self.msg_seq_num = 1
        self.connected = False
        self.responses = {} # msg_type -> asyncio.Queue
        self.heartbeat_task = None
        self.listen_task = None
        self.logged_in = False

    async def connect(self):
        """Establish SSL connection."""
        context = ssl.create_default_context()
        # Allow self-signed certs or loose validation if needed, but default is safer
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE # Often needed for some broker endpoints if cert chain is incomplete

        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port, ssl=context)
            self.connected = True
            self.listen_task = asyncio.create_task(self._listen_loop())
            logger.info(f"Connected to {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to {self.host}:{self.port} - {e}")
            raise

    async def disconnect(self):
        """Close connection."""
        self.connected = False
        self.logged_in = False

        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        if self.listen_task:
            self.listen_task.cancel()

        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass

        logger.info("Disconnected")

    def _calculate_checksum(self, msg_str):
        total = sum(ord(c) for c in msg_str)
        return f"{total % 256:03d}"

    def _build_header_fields(self, msg_type):
        return [
            (35, msg_type),
            (49, self.sender_comp_id),
            (56, self.target_comp_id),
            (57, self.target_sub_id),
            (50, self.target_sub_id),
            (34, self.msg_seq_num),
            (52, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]),
        ]

    def _serialize_msg(self, msg_type, fields):
        # Construct body fields (everything after Header)
        # Note: FIX 4.4 Header includes 35, 49, 56, 34, 52 etc.
        # 8 and 9 are "Standard Header" prefix.

        header_fields = self._build_header_fields(msg_type)

        # Merge fields into header if they override
        # We assume 'fields' contains body tags mostly.
        # But if we pass header tags in fields, they should override?
        # For simplicity, just append body tags.

        # Prepare content: Tag=Value|Tag=Value|...
        # Order: Header tags, then Body tags.

        # We need specific order for Header?
        # 8, 9, 35, 49, 56, 34, 52 ...

        ordered_header_tags = [35, 49, 56, 57, 50, 34, 52]

        content_parts = []

        # Add Header tags
        for tag in ordered_header_tags:
            val = next((v for k,v in header_fields if k == tag), None)
            if val is not None:
                content_parts.append(f"{tag}={val}")

        # Add Body tags
        for k, v in fields.items():
            content_parts.append(f"{k}={v}")

        content = SOH.join(content_parts) + SOH

        # Calculate BodyLength (Tag 9)
        # Length of message string starting after 9=...| (so from 35...)
        length = len(content)

        prefix = f"8=FIX.4.4{SOH}9={length}{SOH}"
        msg_without_checksum = prefix + content

        checksum = self._calculate_checksum(msg_without_checksum)
        final_msg = msg_without_checksum + f"10={checksum}{SOH}"

        return final_msg

    async def send_message(self, msg_type, fields={}):
        msg = self._serialize_msg(msg_type, fields)
        if self.writer:
            self.writer.write(msg.encode())
            await self.writer.drain()
            self.msg_seq_num += 1
            # logger.debug(f"Sent: {msg_type}")

    async def logon(self, timeout=10):
        fields = {
            98: 0,        # EncryptMethod: None
            108: 30,      # HeartBtInt
            141: 'Y',     # ResetSeqNumFlag
            553: self.username,
            554: self.password
        }
        await self.send_message('A', fields)

        response = await self.wait_for_response('A', timeout)
        if response:
            self.logged_in = True
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            return True
        return False

    async def logout(self):
        if self.connected:
            await self.send_message('5', {})
            await self.disconnect()

    async def _heartbeat_loop(self):
        while self.connected:
            await asyncio.sleep(25) # Slightly less than 30
            try:
                await self.send_message('0', {})
            except:
                break

    async def _listen_loop(self):
        buffer = ""
        while self.connected:
            try:
                data = await self.reader.read(4096)
                if not data:
                    break
                buffer += data.decode(errors='ignore')

                while '8=FIX.4.4' in buffer:
                    start_idx = buffer.find('8=FIX.4.4')

                    # Find BodyLength tag (9=)
                    # 8=FIX.4.4|9=123|...
                    p1 = buffer.find(SOH, start_idx) # End of 8=...
                    if p1 == -1: break

                    p2 = buffer.find(SOH, p1+1) # End of 9=...
                    if p2 == -1: break

                    tag9_part = buffer[p1+1:p2]
                    if not tag9_part.startswith('9='):
                        # Malformed or garbage?
                        buffer = buffer[p1+1:]
                        continue

                    try:
                        body_len = int(tag9_part.split('=')[1])
                    except ValueError:
                        buffer = buffer[p1+1:]
                        continue

                    # Calculate total expected length
                    # msg starts at start_idx
                    # content (body) starts at p2+1
                    # content len = body_len
                    # checksum len = 7 (10=xxx|)

                    # header (8=...|9=...|) length = (p2 + 1) - start_idx
                    header_len = (p2 + 1) - start_idx
                    total_len = header_len + body_len + 7

                    if len(buffer) < start_idx + total_len:
                        break # Wait for more data

                    msg = buffer[start_idx : start_idx + total_len]
                    buffer = buffer[start_idx + total_len:]

                    self._handle_message(msg)

            except Exception as e:
                logger.error(f"Listen loop error: {e}")
                break
        self.connected = False

    def _handle_message(self, msg):
        fields = {}
        parts = msg.split(SOH)
        for p in parts:
            if '=' in p:
                k, v = p.split('=', 1)
                try:
                    fields[int(k)] = v
                except:
                    pass

        msg_type = fields.get(35)

        # Handle Test Request
        if msg_type == '1':
            req_id = fields.get(112)
            asyncio.create_task(self.send_message('0', {112: req_id}))

        # Dispatch to queues
        if msg_type in self.responses:
            self.responses[msg_type].put_nowait(fields)

    async def wait_for_response(self, msg_type, timeout=5):
        if msg_type not in self.responses:
            self.responses[msg_type] = asyncio.Queue()

        try:
            return await asyncio.wait_for(self.responses[msg_type].get(), timeout)
        except asyncio.TimeoutError:
            return None

    async def request_positions(self):
        """
        Request open positions via RequestForPositions (AN).
        Returns list of position dictionaries (from PositionReport AP).
        """
        req_id = str(uuid.uuid4())
        await self.send_message('AN', {
            710: req_id,
            263: 1 # SubscriptionRequestType=Snapshot
        })

        # Initialize queue if needed
        if 'AP' not in self.responses:
            self.responses['AP'] = asyncio.Queue()

        positions = []
        try:
            # Wait for first report
            first = await asyncio.wait_for(self.responses['AP'].get(), 10)

            # Check PosReqResult (728): 0=Valid, 2=No positions
            result = first.get(728)
            if result == '2':
                return []

            positions.append(first)

            # Check TotalNumPosReports (727)
            total = int(first.get(727, 1))

            # Retrieve remaining
            for _ in range(total - 1):
                p = await asyncio.wait_for(self.responses['AP'].get(), 5)
                positions.append(p)

        except asyncio.TimeoutError:
            pass # Return what we have

        return positions
