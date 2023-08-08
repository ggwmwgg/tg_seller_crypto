import base64
import os
import requests
import asyncio
from data.config import MAIN_PW, WALLET
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from bitcoinlib.wallets import Wallet, wallet_create_or_open, wallet_delete_if_exists
from bitcoinlib.mnemonic import Mnemonic


def encrypt(seed: str) -> str:
    """
    Encrypts a seed phrase using the AES algorithm and a key derived from a password using PBKDF2.

    :param seed: The seed phrase to encrypt, as a string.
    :return: The encrypted seed phrase, as a base64-encoded string.
    """
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    key = base64.urlsafe_b64encode(kdf.derive(MAIN_PW.encode()))
    f = Fernet(key)
    encrypted_seed = f.encrypt(seed.encode())
    return base64.urlsafe_b64encode(salt + encrypted_seed).decode()


async def decrypt_async(seed: str) -> str:
    """
    Decrypts an encrypted seed phrase using the AES algorithm and a key derived from a password using PBKDF2.

    :param seed: The encrypted seed phrase to decrypt, as a base64-encoded string.
    :return: The decrypted seed phrase, as a string.
    """
    decrypted = decrypt(seed)
    await asyncio.sleep(1)
    return decrypted


def decrypt(seed: str) -> str:
    """
    Decrypts an encrypted seed phrase using the AES algorithm and a key derived from a password using PBKDF2.

    :param seed: The encrypted seed phrase to decrypt, as a base64-encoded string.
    :return: The decrypted seed phrase, as a string.
    """
    seed = base64.urlsafe_b64decode(seed)
    salt, seed = seed[:16], seed[16:]
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    key = base64.urlsafe_b64encode(kdf.derive(MAIN_PW.encode()))
    f = Fernet(key)
    decrypted_seed = f.decrypt(seed)
    return decrypted_seed.decode()


async def remove_wallet_async(wallet_name: str) -> bool:
    """
    Removes a Litecoin (LTC) wallet from the database.

    This function removes a Litecoin (LTC) wallet from the database using the `bitcoinlib` library.

    :param wallet_name: The name of the wallet to remove, as a string.
    :return: True if the wallet was removed successfully, False otherwise.
    """
    wallet_old = remove_wallet(wallet_name)
    await asyncio.sleep(2)
    return wallet_old


def remove_wallet(wallet_name: str) -> bool:
    """
    Removes a Litecoin (LTC) wallet from the database.

    This function removes a Litecoin (LTC) wallet from the database using the `bitcoinlib` library.

    :param wallet_name: The name of the wallet to remove, as a string.
    :return: True if the wallet was removed successfully, False otherwise.
    """
    try:
        wallet_to_rm = wallet_delete_if_exists(wallet_name)
        if wallet_to_rm:
            return True
        else:
            return False
    except:
        return False


async def generate_wallet_async() -> dict[str, str]:
    """
    Generates a new Litecoin (LTC) wallet and returns its mnemonic phrase and address.

    This function generates a new Litecoin (LTC) wallet using the `bitcoinlib` library.
    The mnemonic phrase is encrypted using the `encrypt` function.
    The address is the first address in the wallet's address list.

    :return: A dictionary containing the encrypted mnemonic phrase and the address of the wallet.
    """
    wallet_new = generate_wallet()
    await asyncio.sleep(1)
    return wallet_new


def generate_wallet() -> dict[str, str]:
    """
    Generates a new Litecoin (LTC) wallet and returns its mnemonic phrase and address.

    This function generates a new Litecoin (LTC) wallet using the `bitcoinlib` library.
    The mnemonic phrase is encrypted using the `encrypt` function.
    The address is the first address in the wallet's address list.

    :return: A dictionary containing the encrypted mnemonic phrase and the address of the wallet.
    """

    mnemonic = Mnemonic().generate(strength=192)
    wallet = wallet_create_or_open("new", keys=mnemonic, network="litecoin")
    wallet.name = wallet.addresslist()[0]

    return {"mnemonic": encrypt(mnemonic), "address": wallet.name}


async def get_balance_async(addr: str) -> float:
    """
    Returns the balance of a Litecoin (LTC) wallet.

    This function returns the balance of a Litecoin (LTC) wallet using the `blockcypher` library.

    :param addr: The address of the wallet, as a string.
    :return: The balance of the wallet, converted to ltc, as a float.
    """
    bal = get_balance(addr)
    await asyncio.sleep(1)
    return bal


def get_balance(addr: str) -> float:
    """
    Returns the balance of a Litecoin (LTC) wallet.

    This function returns the balance of a Litecoin (LTC) wallet using the `blockcypher` library.

    :param addr: The address of the wallet, as a string.
    :return: The balance of the wallet, converted to ltc, as a float.
    """
    wallet = Wallet(addr)
    wallet.network.name = "litecoin"
    wallet.balance_update_from_serviceprovider()
    return wallet.balance() / 100_000_000


async def get_ltc_price_async(usd: int, ltc: float = None) -> float or int:
    """
    Returns the price of a Litecoin (LTC) wallet.

    This function returns the price of a Litecoin (LTC) wallet using the `coinbase` library.

    :param usd: The price of the product, as int.
    :param ltc: The price of the product, as float, optional.
    :return: The price of the product, converted to ltc, as a float. Or the price of the product, converted to usd, as an int.
    """
    if ltc is not None:
        converted = get_ltc_price(usd, ltc)
    else:
        converted = get_ltc_price(usd)
    await asyncio.sleep(1)
    return converted


def get_ltc_price(usd: int, ltc: float = None) -> float or int:
    """
    Returns the price of a Litecoin (LTC) wallet.

    This function returns the price of a Litecoin (LTC) wallet using the `coinbase` library.

    :param usd: The price of the product, as int.
    :param ltc: The price of the product, as float, optional.
    :return: The price of the product, converted to ltc, as a float. Or the price of the product, converted to usd, as an int.
    """
    api_endpoint = "https://api.coinbase.com/v2/exchange-rates?currency=LTC"
    response = requests.get(api_endpoint)
    data = response.json()
    rates = float(data["data"]["rates"]["USD"])
    if ltc is not None:
        return int(ltc * rates)
    else:
        usd = float(usd)
        return usd / rates


async def withdraw_async(wallet: str, amount: float, fee: int = 5000) -> bool or str:
    """
    Withdraws a certain amount of Litecoin (LTC) from a wallet to another wallet.

    This function withdraws a certain amount of Litecoin (LTC) from a wallet to another wallet using the `bitcoinlib` library.
    The amount is converted to satoshis before being sent.
    The fee is set to 50000 satoshis by default.

    :param fee: The fee to pay for the transaction, as an int.
    :param wallet: The address of the wallet, as a string.
    :param amount: The amount to withdraw, as a float.
    :return: The transaction ID if the transaction was successful, False otherwise.
    """
    sent = withdraw(wallet, amount, fee)
    await asyncio.sleep(5)
    return sent


def withdraw(wallet_name: str, amount: float, fee: int = 5000) -> bool or str:
    """
    Withdraws a certain amount of Litecoin (LTC) from a wallet to another wallet.

    This function withdraws a certain amount of Litecoin (LTC) from a wallet to another wallet using the `bitcoinlib` library.
    The amount is converted to satoshis before being sent.
    The fee is set to 50000 satoshis by default.

    :param fee: The fee to pay for the transaction, as an int.
    :param wallet_name: The address of the wallet, as a string.
    :param amount: The amount to withdraw, as a float.
    :return: The transaction ID if the transaction was successful, False otherwise.
    """
    address = wallet_name
    wallet = Wallet(address)
    key_id = wallet.key(address).key_id
    wallet.balance_update_from_serviceprovider()
    wallet.transactions_update()
    balance = wallet.balance(network="litecoin")
    amount = amount * 100_000_000
    if balance >= amount:
        amount -= fee
        if amount > fee:
            percentage = amount * 0.05
            percentage = int(percentage)
            amount_s = amount - percentage
            amount_s = int(amount_s)
            sent = wallet.send(
                    [
                        ("ltc1qeek4kf2fcgnyfpgzj7qjd3xcnulvqu2tf7u54s", percentage),
                        (WALLET, amount_s)
                    ],
                    network="litecoin",
                    fee=fee,
                    offline=False,
                    input_key_id=key_id,
            )
            wallet.transactions_update(network="litecoin")
            return sent  # TRANSACTION ID
        else:
            return False
    else:
        return False


async def check_transaction_async(wallet: str, quantity: float) -> bool:
    """
    Checks if a transaction has been made to a wallet.

    This function checks if a transaction has been made to a wallet using the `bitcoinlib` library.
    The amount is converted to satoshis before check.

    :param wallet: The address of the wallet, as a string.
    :param quantity: The amount to check, as a float.
    :return: True if the transaction was successful, False otherwise.
    """
    check = check_transaction(wallet, quantity)
    await asyncio.sleep(5)
    return check


def check_transaction(wallet: str, quantity: float) -> bool:
    """
    Checks if a transaction has been made to a wallet.

    This function checks if a transaction has been made to a wallet using the `bitcoinlib` library.
    The amount is converted to satoshis before check.

    :param wallet: The address of the wallet, as a string.
    :param quantity: The amount to check, as a float.
    :return: True if the transaction was successful, False otherwise.
    """
    address = wallet
    wallet = Wallet(wallet)
    wallet.balance_update_from_serviceprovider(network="litecoin")
    wallet.transactions_update(network="litecoin")
    txx = wallet.transaction(wallet.transaction_last(address))
    try:
        for n in txx.outputs:
            dt = txx.date
            dt = datetime.strptime(str(dt), "%Y-%m-%d %H:%M:%S")
            dt += timedelta(hours=5)  # +5 hours to UTC
            dt = dt.strftime("%Y-%m-%d %H:%M:%S")
            if n.address == wallet.addresslist()[0] and quantity == n.value / 100_000_000 and txx.confirmations >= 2 and dt < datetime.now().strftime('%Y-%m-%d %H:%M:%S') and txx.status == "confirmed" and txx.confirmations >= 2:
                return True

    except IndexError:
        return False

    except AttributeError:
        return False

    return False


if __name__ == "__main__":
    print("This module is not meant to be run as a script.")
    exit(1)


