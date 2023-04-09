import dis


class ClientVerifier(type):
    def __init__(cls, name, bases, namespace):
        methods = []
        for _, attr in namespace.items():
            try:
                res = dis.get_instructions(attr)
            except TypeError:
                pass
            else:
                for i in res:
                    if i.opname == "LOAD_GLOBAL":
                        if i.argval not in methods:
                            methods.append(i.argval)
        for method in methods:
            if method in ("listen", "accept", "socket"):
                raise TypeError(f"Вызов {method} внутри класса 'Client' запрещен.")
        if "send_message" in methods or "get_message" in methods:
            pass
        else:
            raise TypeError("Нет вызовов, работающих с сокетами.")
        super().__init__(name, bases, namespace)


class ServerVerifier(type):
    def __init__(cls, name, bases, namespace):
        methods = []
        attributes = []
        for _, attr in namespace.items():
            try:
                res = dis.get_instructions(attr)
            except TypeError:
                pass
            else:
                for i in res:
                    if i.opname == "LOAD_GLOBAL":
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == "LOAD_ATTR":
                        if i.argval not in attributes:
                            attributes.append(i.argval)
        if "connect" in methods:
            raise TypeError("Вызов 'connect' внутри класса 'Server' запрещен.")
        if not ("SOCK_STREAM" in attributes and "AF_INET" in attributes):
            raise TypeError("Сокет не инициализирован.")
        super().__init__(name, bases, namespace)
