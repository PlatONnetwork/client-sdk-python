from client_sdk_python.module import (
    Module,
)


class Personal(Module):
    """
    https://github.com/ethereum/go-ethereum/wiki/Management-APIs#personal
    """
    def importRawKey(self, private_key, passphrase):
        return self.web3.manager.request_blocking(
            "personal_importRawKey",
            [private_key, passphrase],
        )

    def newAccount(self, password):
        return self.web3.manager.request_blocking(
            "personal_newAccount", [password],
        )

    @property
    def listAccounts(self):
        return self.web3.manager.request_blocking(
            "personal_listAccounts", [],
        )

    @property
    def listWallets(self):
        return self.web3.manager.request_blocking(
            "personal_listWallets", [],
        )

    def sendTransaction(self, transaction, passphrase):
        return self.web3.manager.request_blocking(
            "personal_sendTransaction",
            [transaction, passphrase],
        )

    def lockAccount(self, account):
        return self.web3.manager.request_blocking(
            "personal_lockAccount",
            [account],
        )

    def unlockAccount(self, account, passphrase, duration=None):
        try:
            return self.web3.manager.request_blocking(
                "personal_unlockAccount",
                [account, passphrase, duration],
            )
        except ValueError as err:
            if "could not decrypt" in str(err):
                # Hack to handle go-ethereum error response.
                return False
            else:
                raise

    def sign(self, message, signer, passphrase):
        return self.web3.manager.request_blocking(
            'personal_sign',
            [message, signer, passphrase],
        )

    def signTransaction(self, transaction_dict, passphrase):
        return self.web3.manager.request_blocking(
            'personal_signTransaction',
            [transaction_dict, passphrase],
        )

    def ecRecover(self, message, signature):
        return self.web3.manager.request_blocking(
            'personal_ecRecover',
            [message, signature],
        )

    def openWallet(self, url, passphrase):
        return self.web3.manager.request_blocking(
            'personal_openWallet',
            [url, passphrase],
        )
