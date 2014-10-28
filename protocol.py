import json
protocol_map = {'subscription': Subscription,
                'credential': Credential,
                'market_info': Market_Info}

class WSProtocol(object):
    def to_json(self):
        pass

    def from_json(self):
        pass

class Subscription(WSProtocol):
    def __init__(self):
        pass

class Credential(WSProtocol):
    def __init__(self):
        pass

class Market_Info(WSProtocol):
    def __init__(self):
        pass


