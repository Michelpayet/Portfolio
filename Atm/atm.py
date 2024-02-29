class Account:
    def __init__(self, card_number, pin, balance):
        self.card_number = card_number
        self.pin = pin
        self.balance = balance


class ATM:
    def __init__(self):
        self.accounts = {}

    def add_account(self, account):
        self.accounts[account.card_number] = account

    def authenticate_user(self, card_number, pin):
        if card_number in self.accounts and self.accounts[card_number].pin == pin:
            return True
        else:
            return False

    def display_balance(self, card_number):
        return self.accounts[card_number].balance

    def deposit(self, card_number, amount):
        self.accounts[card_number].balance += amount
        return self.accounts[card_number].balance

    def withdraw(self, card_number, amount):
        if amount <= self.accounts[card_number].balance:
            self.accounts[card_number].balance -= amount
            return self.accounts[card_number].balance
        else:
            return "Insufficient funds"


