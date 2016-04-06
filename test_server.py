
import OSC, socket, struct

class TestServer:
  def __init__(self, options={}):
    self.options=options
    self.time_out = False
    self.host = '' #0.0.0.0'#'145.107.196.255'
    self.port = 1234 #int(8080)


    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    self.s.bind((self.host, self.port))

    return
    # create server instance
    self.osc_server = OSC.OSCServer((self.host, self.port))

    # mreq = struct.pack("4sl", socket.inet_aton(self.host), socket.INADDR_ANY)
    # self.osc_server.socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # register time out callback
    self.osc_server.handle_timeout = self._onTimeout
    # register specific OSC messages callback(s)
    self.osc_server.addMsgHandler('/change', self._onChange)

    self.osc_server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.osc_server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


  def _onTimeout(self):
    self.time_out = True

  def run(self):
    try:
      while True:
        self.update()
    except KeyboardInterrupt:
      print('abort')

    self.s.close()
    # self.osc_server.close()

  def update(self):
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
