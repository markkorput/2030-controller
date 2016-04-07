from SocketServer import UDPServer
import socket, struct

from py2030.utils.color_terminal import ColorTerminal

try:
    import OSC
except ImportError:
    ColorTerminal().warn("importing embedded version of pyOSC library for py2030.utils.osc_broadcast_server")
    import py2030.dependencies.OSC as OSC

class OscBroadcastServer(OSC.OSCServer):

    # main reason for the existence of this class; the constructor
    # of OSC.OSCServer doesn't allow the caller to make changes to
    # the socket handle before it binds to the specified address.
    # In order to allow multiple server instances to bind to the same
    # address and port, the socket most have specific options enabled,
    # which are not enabled by default.
    def __init__(self, server_address, client=None, return_port=0):
        # the 'bind_and_activate' param and the lines below are what this class is all about
        UDPServer.__init__(self, server_address, self.RequestHandlerClass, bind_and_activate=False)

        # self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        mreq = struct.pack("4sl", socket.inet_aton(server_address[0]), socket.INADDR_ANY)
        try:
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except socket.error as err:
            ColorTerminal().fail("{0}\nOscBroadcastServer - got invalid IP address for broadcasting ({1})\nContinuing...".format(err, server_address[0]))

        # self.socket.bind((self.host, self.port))
        # NOW we can bind and activate
        self.server_bind()
        self.server_activate()

        # all the following is exactly the same as the OSC.OSCServer __init__ method
        self.callbacks = {}
        self.setReturnPort(return_port)
        self.error_prefix = ""
        self.info_prefix = "/info"

        self.socket.settimeout(self.socket_timeout)

        self.running = False
        self.client = None

        if client == None:
            self.client = OSC.OSCClient(server=self)
        else:
            self.setClient(client)
