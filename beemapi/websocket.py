from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import next
from builtins import str
import traceback
import threading
import ssl
import time
import json
import logging
import websocket
from itertools import cycle
from threading import Thread
from .exceptions import NumRetriesReached
from events import Events

log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)


class SteemWebsocket(Events):
    """ Create a websocket connection and request push notifications

        :param str urls: Either a single Websocket URL, or a list of URLs
        :param str user: Username for Authentication
        :param str password: Password for Authentication
        :param int keep_alive: seconds between a ping to the backend (defaults to 25seconds)

        After instanciating this class, you can add event slots for:

        * ``on_block``

        which will be called accordingly with the notification
        message received from the Steem node:

        .. code-block:: python

            ws = SteemWebsocket(
                "wss://gtg.steem.house:8090",
            )
            ws.on_block += print
            ws.run_forever()

        Notices:

        * ``on_block``:

            .. code-block:: js

                '0062f19df70ecf3a478a84b4607d9ad8b3e3b607'


    """
    __events__ = [
        'on_block',
    ]

    def __init__(
        self,
        urls,
        user="",
        password="",
        *args,
        only_block_id=False,
        on_block=None,
        keep_alive=25,
        num_retries=-1,
        **kwargs
    ):

        self.num_retries = num_retries
        self.keepalive = None
        self._request_id = 0
        self.ws = None
        self.user = user
        self.password = password
        self.keep_alive = keep_alive
        self.run_event = threading.Event()
        self.only_block_id = only_block_id
        if isinstance(urls, cycle):
            self.urls = urls
        elif isinstance(urls, list):
            self.urls = cycle(urls)
        else:
            self.urls = cycle([urls])

        # Instanciate Events
        Events.__init__(self)
        self.events = Events()

        # Store the objects we are interested in
        # self.subscription_accounts = accounts

        if on_block:
            self.on_block += on_block
        # if on_account:
        #     self.on_account += on_account

    def cancel_subscriptions(self):
        # self.cancel_all_subscriptions()
        # api call removed in 0.19.1
        log.exception("cancel_all_subscriptions removed from api")

    def on_open(self, ws):
        """ This method will be called once the websocket connection is
            established. It will

            * login,
            * register to the database api, and
            * subscribe to the objects defined if there is a
              callback/slot available for callbacks
        """
        self.login(self.user, self.password, api_id=1)
        # self.database(api_id=1)
        self.__set_subscriptions()
        self.keepalive = threading.Thread(
            target=self._ping,
        )
        self.keepalive.start()

    def reset_subscriptions(self, accounts=[]):
        # self.subscription_accounts = accounts
        self.__set_subscriptions()

    def __set_subscriptions(self):
        # self.cancel_all_subscriptions()
        # Subscribe to events on the Backend and give them a
        # callback number that allows us to identify the event
        # set_pending_transaction_callback is removed from api
        # api call removed in 0.19.1

        if len(self.on_block):
            self.set_block_applied_callback(
                self.__events__.index('on_block'))

    def _ping(self):
        # We keep the connetion alive by requesting a short object
        def ping(self):
            while not self.run_event.wait(self.keep_alive):
                log.debug('Sending ping')
                self.get_chain_properties()

    def process_block(self, data):
        """ This method is called on notices that need processing. Here,
            we call the ``on_block`` slot.
        """
        # id = data["id"]
        block = data["result"]
        if "previous" in block:
            block_id = block["previous"]
            block_number = int(block_id[:8], base=16)
            block["id"] = block_number
            # print(result)
            # print(block_number)
            # self.get_block(block_number)
            self.on_block(block)

    def on_message(self, ws, reply, *args):
        """ This method is called by the websocket connection on every
            message that is received. If we receive a ``notice``, we
            hand over post-processing and signalling of events to
            ``process_notice``.
        """
        log.debug("Received message: %s" % str(reply))
        data = {}
        # print(reply)
        try:
            data = json.loads(reply, strict=False)
        except ValueError:
            raise ValueError("API node returned invalid format. Expected JSON!")

        if data.get("method") == "notice":
            id = data["params"][0]
            # print(data)

            if id >= len(self.__events__):
                log.critical(
                    "Received an id that is out of range\n\n" +
                    str(data)
                )
                return

            # This is a "general" object change notification
            if id == self.__events__.index('on_block'):
                # Let's see if a specific object has changed
                for new_block in data["params"][1]:
                    if not new_block:
                        continue
                    block_id = new_block["previous"]
                    block_number = int(block_id[:8], base=16)
                    # print(new_block)
                    # print(block_number)
                    if self.only_block_id:
                        self.on_block(block_number)
                    else:
                        self.get_block(block_number)
            else:
                # print(data)
                try:
                    callbackname = self.__events__[id]
                    log.debug("Patching through to call %s" % callbackname)
                    [getattr(self.events, callbackname)(x) for x in data["params"][1]]
                except Exception as e:
                    log.critical("Error in {}: {}\n\n{}".format(
                        callbackname, str(e), traceback.format_exc()))
        else:
            self.process_block(data)

    def on_error(self, ws, error):
        """ Called on websocket errors
        """
        print(error)
        log.exception(error)

    def on_close(self, ws):
        """ Called when websocket connection is closed
        """
        log.debug('Closing WebSocket connection with {}'.format(self.url))
        if self.keepalive and self.keepalive.is_alive():
            self.keepalive.do_run = False
            self.keepalive.join()

    def run_forever(self):
        """ This method is used to run the websocket app continuously.
            It will execute callbacks as defined and try to stay
            connected with the provided APIs
        """
        cnt = 0
        while not self.run_event.is_set():
            cnt += 1
            self.url = next(self.urls)
            log.debug("Trying to connect to node %s" % self.url)
            try:
                # websocket.enableTrace(True)
                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open,
                )
                self.ws.run_forever()
            except websocket.WebSocketException as exc:
                if (self.num_retries >= 0 and cnt > self.num_retries):
                    raise NumRetriesReached()

                sleeptime = (cnt - 1) * 2 if cnt < 10 else 10
                if sleeptime:
                    log.warning(
                        "Lost connection to node during wsconnect(): %s (%d/%d) "
                        % (self.url, cnt, self.num_retries) +
                        "Retrying in %d seconds" % sleeptime
                    )
                    time.sleep(sleeptime)

            except KeyboardInterrupt:
                self.ws.keep_running = False
                raise

            except Exception as e:
                log.critical("{}\n\n{}".format(str(e), traceback.format_exc()))

    def get_request_id(self):
        self._request_id += 1
        return self._request_id

    def close(self):
        """ Closes the websocket connection and waits for the ping thread to close
        """
        self.run_event.set()
        self.ws.close()

        if self.keepalive and self.keepalive.is_alive():
            self.keepalive.join()

    """ RPC Calls
    """
    def rpcexec(self, payload):
        """ Execute a call by sending the payload

            :param json payload: Payload data
            :raises ValueError: if the server does not respond in proper JSON format
            :raises RPCError: if the server returns an error
        """
        log.debug(json.dumps(payload))
        self.ws.send(json.dumps(payload, ensure_ascii=False).encode('utf8'))

    def __getattr__(self, name):
        """ Map all methods to RPC calls and pass through the arguments
        """
        if name in self.__events__:
            return getattr(self.events, name)

        def method(*args, **kwargs):

            # Sepcify the api to talk to
            if "api_id" not in kwargs:
                if ("api" in kwargs):
                    if (kwargs["api"] in self.api_id and
                            self.api_id[kwargs["api"]]):
                        api_id = self.api_id[kwargs["api"]]
                    else:
                        raise ValueError(
                            "Unknown API! "
                            "Verify that you have registered to %s"
                            % kwargs["api"]
                        )
                else:
                    api_id = 0
            else:
                api_id = kwargs["api_id"]

            # let's be able to define the num_retries per query
            self.num_retries = kwargs.get("num_retries", self.num_retries)

            query = {"method": "call",
                     "params": [api_id, name, list(args)],
                     "jsonrpc": "2.0",
                     "id": self.get_request_id()}
            r = self.rpcexec(query)
            return r
        return method