import dbus_utils
import dbussy
import ravel

BUS_NAME = 'org.bluez.obex'
ERROR_REJECTED = 'org.bluez.Error.Rejected'
INTERFACE_AGENT = 'org.bluez.obex.Agent1'
INTERFACE_AGENT_MANAGER = 'org.bluez.obex.AgentManager1'
PATH_OBEX = '/org/bluez/obex'
PATH_AGENT = '/kodi/agent/obex'


@ravel.interface(ravel.INTERFACE.SERVER, name=INTERFACE_AGENT)
class Agent(object):

    agent = None

    @classmethod
    def register_agent(cls, *args, **kwargs):
        if cls.agent is not None:
            raise RuntimeError('An agent is already registered')
        manager_register_agent()
        cls.agent = cls(*args, **kwargs)
        dbus_utils.BUS.request_name(
            BUS_NAME, flags=dbussy.DBUS.NAME_FLAG_DO_NOT_QUEUE)
        dbus_utils.BUS.register(
            path=PATH_AGENT, interface=cls.agent, fallback=True)
        return cls.agent

    @ravel.method(
        in_signature='o',
        out_signature='s',
        arg_keys=['path'],
        result_keyword='reply'
    )
    def AuthorizePush(self, path):
        name = self.authorize_push(path)
        reply[0] = (dbus.Signature('s'), name)

    @ravel.method(
        in_signature='',
        out_signature=''
    )
    def Cancel(self):
        pass

    @ravel.method(
        in_signature='',
        out_signature=''
    )
    def Release(self):
        pass

    def reject(self, message):
        raise dbus.DBusError(ERROR_REJECTED, message)


def manager_register_agent():
    return dbus_utils.call_method(BUS_NAME, PATH_OBEX, INTERFACE_AGENT_MANAGER, 'RegisterAgent', PATH_AGENT)
