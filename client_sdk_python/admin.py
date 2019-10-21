from client_sdk_python.module import (
    Module,
)


class Admin(Module):
    def addPeer(self, node_url):
        return self.web3.manager.request_blocking(
            "admin_addPeer", [node_url],
        )

    @property
    def datadir(self):
        return self.web3.manager.request_blocking("admin_datadir", [])

    @property
    def nodeInfo(self):
        return self.web3.manager.request_blocking("admin_nodeInfo", [])

    @property
    def peers(self):
        return self.web3.manager.request_blocking("admin_peers", [])

    def exportChain(self, filePath):
        return self.web3.manager.request_blocking(
            "admin_exportChain", [filePath],
        )

    def importChain(self, filePath):
        return self.web3.manager.request_blocking(
            "admin_importChain", [filePath],
        )

    def removePeer(self, node_url):
        return self.web3.manager.request_blocking(
            "admin_removePeer", [node_url],
        )

    def setSolc(self, solc_path):
        return self.web3.manager.request_blocking(
            "admin_setSolc", [solc_path],
        )

    def startRPC(self, host='localhost', port=6789, cors="", apis="platon,net,web3,debug,admin"):
        return self.web3.manager.request_blocking(
            "admin_startRPC",
            [host, port, cors, apis],
        )

    def startWS(self, host='localhost', port=6790, cors="", apis="platon,net,web3,debug,admin"):
        return self.web3.manager.request_blocking(
            "admin_startWS",
            [host, port, cors, apis],
        )

    def stopRPC(self):
        return self.web3.manager.request_blocking("admin_stopRPC", [])

    def stopWS(self):
        return self.web3.manager.request_blocking("admin_stopWS", [])

    def getProgramVersion(self):
        return self.web3.manager.request_blocking("admin_getProgramVersion", [])

    def getSchnorrNIZKProve(self):
        return self.web3.manager.request_blocking("admin_getSchnorrNIZKProve", [])
