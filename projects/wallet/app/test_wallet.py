import pytest
from wallet import Wallet

def test_deposit():
    wallet = Wallet(100)
    assert wallet.deposit(50) == 150
    assert wallet.balance == 150

def test_withdraw():
    wallet = Wallet(100)
    assert wallet.withdraw(30) == 70
    assert wallet.balance == 70

def test_deposit_negative_amount():
    wallet = Wallet()
    with pytest.raises(ValueError, match="Deposit amount must be positive"):
        wallet.deposit(-10)

def test_withdraw_more_than_balance():
    wallet = Wallet(50)
    with pytest.raises(ValueError, match="Insufficient funds"):
        wallet.withdraw(100)
