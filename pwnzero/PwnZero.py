import serial
from enum import Enum

import pwnagotchi.plugins as plugins
import pwnagotchi.ui.faces as faces

class PwnZeroParam(Enum):
    """
    Flipper Zero Parameters
    These are the parameters that can be changed on the Flipper Zero
    The values are the bytes that are being sent to the Flipper Zero
    to change the parameter
    The documentation for the Flipper Zero can be found here:
    https://github.com/Matt-London/pwnagotchi-flipper/blob/main/doc/Protocol.md
    """
    FACE        = 4
    NAME        = 5
    CHANNEL     = 6
    APS         = 7
    UPTIME      = 8
    FRIEND      = 9
    MODE        = 10
    HANDSHAKES  = 11
    MESSAGE     = 12

class PwnMode(Enum):
        """
        Embedded class with the mode
        """
        MANU    = 4
        AUTO    = 5
        AI      = 6

class PwnFace(Enum):
    """
    Embedded class with all face parameters
    """
    NO_FACE         = 4
    DEFAULT_FACE    = 5
    LOOK_R          = 6
    LOOK_L          = 7
    LOOK_R_HAPPY    = 8
    LOOK_L_HAPPY    = 9
    SLEEP           = 10
    SLEEP2          = 11
    AWAKE           = 12
    BORED           = 13
    INTENSE         = 14
    COOL            = 15
    HAPPY           = 16
    GRATEFUL         = 17
    EXCITED         = 18
    MOTIVATED       = 19
    DEMOTIVATED     = 20
    SMART           = 21
    LONELY          = 22
    SAD             = 23
    ANGRY           = 24
    FRIEND          = 25
    BROKEN          = 26
    DEBUG           = 27
    UPLOAD          = 28
    UPLOAD1         = 29
    UPLOAD2         = 30


class PwnZero(plugins.Plugin):
    __author__ = "github.com/Matt-London"
    # Version number for just the pwnagotchi plugin
    __version__ = "1.1.0"
    __license__ = "MIT"
    __description__ = "Plugin to display the Pwnagotchi on the Flipper Zero"

    PROTOCOL_START   = 0x02
    PROTOCOL_END     = 0x03

    def __init__(self, port: str = "/dev/serial0", baud: int = 115200):
        """
        Construct a PwnZero object, this will create the connection

        :param: port: Port on which the UART of the Flipper is connected to
        :param: baud: Baudrate for communication to the Flipper (default 115200)
        """
        self._port = port
        self._baud = baud

        try:
            # open serial connection to Flipper Zero
            self._serialConn = serial.Serial(port, baud)
        except Exception as e:
            # propagate as runtime error for plugin loader
            raise RuntimeError(f"Cannot bind to port {port} with baud {baud}: {e}")

    def close(self):
        """
        Closes the connection to the Flipper Zero
        """
        self._serialConn.close()

    def _is_byte(self, i: int) -> bool:
        """
        Checks if a passed in integer is a valid byte (0 <= i < 256)

        :param: i: Integer to check
        :return: If it is a valid byte
        """
        return 0 <= i < 256

    def _str_to_bytes(self, s: str):
        """
        Converts a string into a list of bytes

        :param: s: String to convert
        :return: List of bytes
        """
        retVal = []
        for c in s:
            retVal.append(ord(c))
        
        return retVal

    def _send_data(self, param: int, args) -> bool:
        """
        Sends data using protocol v2 over the serial port to the Flipper Zero

        :param: param: Parameter that is being changed
        :param: args: Arguments to pass to the flipper
        :return: If transmission was successful
        """
        # Make sure everything is a valid byte
        if not self._is_byte(param):
            return False
        for i in args:
            if not self._is_byte(i):
                return False
        
        # Now we know everything is a valid byte
        
        # Build the sending data
        data = [self.PROTOCOL_START]
        data.append(param)
        for arg in args:
            data.append(arg)
        
        data.append(self.PROTOCOL_END)

        # Send data to flipper as bytes
        data_bytes = bytes(data)
        written = self._serialConn.write(data_bytes)
        return written == len(data_bytes)

    # Public method commands
    def set_face(self, face: PwnFace) -> bool:
        """
        Set the face of the Pwnagotchi

        :param: face: Face to set on the device
        :return: If the command was sent successfully
        """
        return self._send_data(PwnZeroParam.FACE.value, [face.value])

    def set_name(self, name: str) -> bool:
        """
        Set the name of the Pwnagotchi

        :param: name: Name to set on the pwnagotchi
        :return: If the command was sent successfully
        """
        data = self._str_to_bytes(name)
        return self._send_data(PwnZeroParam.NAME.value, data)

    def set_channel(self, channelInfo: str) -> bool:
        """
        Set the channel of the Pwnagotchi
        Send a 0 for * (all channels)

        :param: channelInfo: Channel data from pwnagotchi
        :return: If the command was sent successfully
        """
        data = self._str_to_bytes(channelInfo)
        return self._send_data(PwnZeroParam.CHANNEL.value, data)

    def set_aps(self, apsInfo: str) -> bool:
        """
        Set the APs of the Pwnagotchi

        :param: apsInfo: String from pwnagotchi
        :return: If the command was sent successfully
        """
        data = self._str_to_bytes(apsInfo)
        return self._send_data(PwnZeroParam.APS.value, data)

    def set_uptime(self, uptimeInfo: str) -> bool:
        """
        Sets the uptime of the Pwnagotchi

        :param: uptimeInfo: Uptime data from pwnagotchi
        :return: If the command was sent successfully
        """
        data = self._str_to_bytes(uptimeInfo)
        return self._send_data(PwnZeroParam.UPTIME.value, data)

    def set_friend(self) -> bool:
        """
        Friend is currently not supported
        
        :return: False
        """
        return False

    def set_mode(self, mode: PwnMode) -> bool:
        """
        Set the mode on the Pwnagotchi
        
        :param: mode: Mode to set
        :return: If the command was sent successfully
        """
        return self._send_data(PwnZeroParam.MODE.value, [mode.value])

    def set_handshakes(self, handshakesInfo: str) -> bool:
        """
        Set the number of handshakes on the Pwnagotchi

        :param: handshakesInfo: Handshake stats from pwnagotchi
        :return: If the command was sent successfully
        """
        data = self._str_to_bytes(handshakesInfo)
        return self._send_data(PwnZeroParam.HANDSHAKES.value, data)

    def set_message(self, message: str) -> bool:
        """
        Sets the displayed message on the Pwnagotchi
        
        :param: message: Message to set
        :return: If the command was sent successfully
        """
        data = self._str_to_bytes(message)
        return self._send_data(PwnZeroParam.MESSAGE.value, data)

    def on_ui_setup(self, ui):
        pass

    def on_ui_update(self, ui):
        # Status message
        status = ui.get('status')
        if status is not None:
            self.set_message(str(status))

        # Mode mapping
        mode_str = ui.get('mode')
        if isinstance(mode_str, str):
            mode_key = mode_str.upper()
        else:
            mode_key = None
        mode_mapping = {
            'AI': PwnMode.AI,
            'AUTO': PwnMode.AUTO,
            'MANUAL': PwnMode.MANU,
            'MANU': PwnMode.MANU,
        }
        mode = mode_mapping.get(mode_key)
        if mode:
            self.set_mode(mode)

        # Channel
        channel = ui.get('channel')
        if channel is not None:
            self.set_channel(str(channel))

        # Uptime
        uptime = ui.get('uptime')
        if uptime is not None:
            self.set_uptime(str(uptime))

        # APS (could be tuple or string)
        aps = ui.get('aps')
        if isinstance(aps, (tuple, list)) and len(aps) >= 2:
            aps_str = f"{aps[0]} ({aps[1]})"
        else:
            aps_str = str(aps) if aps is not None else ''
        self.set_aps(aps_str)

        # Name (sanitize > char)
        name = ui.get('name')
        if name is not None:
            self.set_name(str(name).replace('>', ''))

        # Face mapping (fallback to default face)
        face = ui.get('face')
        face_mapping = {
            faces.LOOK_R: PwnFace.LOOK_R,
            faces.LOOK_L: PwnFace.LOOK_L,
            faces.LOOK_R_HAPPY: PwnFace.LOOK_R_HAPPY,
            faces.LOOK_L_HAPPY: PwnFace.LOOK_L_HAPPY,
            faces.SLEEP: PwnFace.SLEEP,
            faces.SLEEP2: PwnFace.SLEEP2,
            faces.AWAKE: PwnFace.AWAKE,
            faces.BORED: PwnFace.BORED,
            faces.INTENSE: PwnFace.INTENSE,
            faces.COOL: PwnFace.COOL,
            faces.HAPPY: PwnFace.HAPPY,
            faces.GRATEFUL: PwnFace.GRATEFUL,
            faces.EXCITED: PwnFace.EXCITED,
            faces.MOTIVATED: PwnFace.MOTIVATED,
            faces.DEMOTIVATED: PwnFace.DEMOTIVATED,
            faces.SMART: PwnFace.SMART,
            faces.LONELY: PwnFace.LONELY,
            faces.SAD: PwnFace.SAD,
            faces.ANGRY: PwnFace.ANGRY,
            faces.FRIEND: PwnFace.FRIEND,
            faces.BROKEN: PwnFace.BROKEN,
            faces.DEBUG: PwnFace.DEBUG,
            faces.UPLOAD: PwnFace.UPLOAD,
            faces.UPLOAD1: PwnFace.UPLOAD1,
            faces.UPLOAD2: PwnFace.UPLOAD2,
        }
        face_enum = face_mapping.get(face, PwnFace.DEFAULT_FACE)
        self.set_face(face_enum)

        # Handshakes (could be tuple or string)
        shakes = ui.get('shakes')
        if isinstance(shakes, (tuple, list)) and len(shakes) >= 2:
            shakes_str = f"{shakes[0]} ({shakes[1]})"
        else:
            shakes_str = str(shakes) if shakes is not None else ''
        self.set_handshakes(shakes_str)
