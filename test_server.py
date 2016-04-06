
import OSC, socket, struct


"""
The SocketServer module does not provide support for multicast. This module
provides a subclass of SocketServer.UDPServer that can listen on multicast
addresses.
This only supports IPv4
"""

import SocketServer
import socket
import struct

class MulticastServer(SocketServer.UDPServer):
    """Extends UDPServer to join multicast groups and bind
    the local interface properly
    """

    def __init__(self, multicast_address, RequestHandlerClass,
                 listen_interfaces = None):
        """Create a new multicast server.
        multicast_address - two tuple ('multicast address', port)
        RequestHandlerClass - a SocketServer.BaseRequesetHandler
        listen_interfaces - list of local interfaces (identified by IP addresses)
        the server should listen on for multicast packets. If None,
        the system will decide which interface to send the multicast group join
        on
        """
        #to receive multicast packets, must bind the port,
        #set bind_and_active to True.
        #Note: some hosts don't allow bind()'ing to a multicast address,
        #so bind to INADDR_ANY
        SocketServer.UDPServer.__init__(self, ('', multicast_address[1]),
                                              RequestHandlerClass, True)

        #Note: struct ip_mreq { struct in_addr (multicast addr), struct in_addr
        #(local interface) }
        if listen_interfaces is None:
            mreq = struct.pack("4sI", socket.inet_aton(multicast_address[0]),
                               socket.INADDR_ANY)
            self.socket.setsockopt(socket.IPPROTO_IP,
                                       socket.IP_ADD_MEMBERSHIP, mreq)
        else:
            for interface in listen_interfaces:
                mreq = socket.inet_aton(
                    multicast_address[0]) + socket.inet_aton(interface)
                self.socket.setsockopt(socket.IPPROTO_IP,
                                       socket.IP_ADD_MEMBERSHIP, mreq)

    def server_close(self):
        #TODO: leave the multicast groups...
        pass



class TestServer:
  def __init__(self, options={}):
    self.options=options
    self.time_out = False
    self.host = '224.0.0.251' # '145.107.196.255' # '0.0.0.0' #
    self.port = 1234 #int(8080)

    self.multicast_server = None
    self.s = None
    self.osc_server = None

    # # self.request_handler = SocketServer.BaseRequestHandler()
    # self.multicast_server = MulticastServer((self.host, self.port), SocketServer.BaseRequestHandler)
    # return

    # SEEMS TO WORK!!! (with IP address 244.0.0.251 at school, found with `netstat -g`)
    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    mreq = struct.pack("4sl", socket.inet_aton(self.host), socket.INADDR_ANY)
    self.s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    self.s.bind((self.host, self.port))
    return

    # # create server instance
    # self.osc_server = OSC.OSCServer(('', self.port))
    # mreq = struct.pack("4sl", socket.inet_aton(self.host), socket.INADDR_ANY)
    # self.osc_server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # self.osc_server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # self.osc_server.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # register time out callback
    self.osc_server.handle_timeout = self._onTimeout
    # register specific OSC messages callback(s)
    self.osc_server.addMsgHandler('/change', self._onChange)



  def _onTimeout(self):
    self.time_out = True

  def run(self):
    try:
      while True:
        self.update()
    except KeyboardInterrupt:
      print('abort')

    if self.multicast_server:
        self.multicast_server.server_close()

    if self.s:
        self.s.close()

    if self.osc_server:
        self.osc_server.close()

  def update(self):
    if self.s:
        try:
            data, (ip, port) = self.s.recvfrom(1024, socket.MSG_DONTWAIT)
            print(data, ip, port)
        except socket.error as err:
            pass
        return

    if self.osc_server == None:
        return

    # we'll enforce a limit to the number of osc requests
    # we'll handle in a single iteration, otherwise we might
    # get stuck in processing an endless stream of data
    limit = 10
    count = 0

    # clear timed_out flag
    self.osc_server.timed_out = False

    # handle all pending requests then return
    while not self.osc_server.timed_out and count < limit:
        self.osc_server.handle_request()
        count += 1

  def _onChange(self, addr, tags, data, client_address):
    print('Got /change:', data)

if __name__ == '__main__':
    s = TestServer()
    s.run()
