"""Python Banking System - Module 3 (Object-Oriented Python).

Concepts covered:
- Classes, objects, constructors, methods
- Encapsulation (private balance, read-only property)
- Inheritance (SavingsAccount, CheckingAccount extend Account)
- Polymorphism (each account type has its own withdraw rules)
- Abstraction (Account is an abstract base class)
"""

from abc import ABC, abstractmethod
from datetime import datetime
from itertools import count


class InsufficientFundsError(Exception):
    """Raised when a withdrawal is not allowed."""


class Transaction:
    def __init__(self, kind: str, amount: float, balance_after: float):
        self.kind = kind
        self.amount = amount
        self.balance_after = balance_after
        self.timestamp = datetime.now()

    def __str__(self):
        time = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"{time} | {self.kind:<10} | {self.amount:>10.2f} | Balance: {self.balance_after:.2f}"


class Account(ABC):
    _id_counter = count(1001)

    def __init__(self, owner: str, initial_deposit: float = 0.0):
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative.")
        self.account_number = next(Account._id_counter)
        self.owner = owner
        self.__balance = 0.0  # private (encapsulation)
        self._transactions: list[Transaction] = []
        if initial_deposit > 0:
            self.deposit(initial_deposit)

    @property
    def balance(self) -> float:
        return self.__balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit must be positive.")
        self.__balance += amount
        self._record("Deposit", amount)

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal must be positive.")
        if not self._can_withdraw(amount):
            raise InsufficientFundsError(
                f"Cannot withdraw {amount:.2f} from {self.account_type()} account."
            )
        self.__balance -= amount
        self._record("Withdraw", amount)

    @abstractmethod
    def _can_withdraw(self, amount: float) -> bool:
        """Each account type decides its own withdrawal rule."""

    @abstractmethod
    def account_type(self) -> str:
        ...

    def _record(self, kind: str, amount: float) -> None:
        self._transactions.append(Transaction(kind, amount, self.__balance))

    def history(self) -> list[Transaction]:
        return list(self._transactions)

    def __str__(self):
        return (f"[{self.account_type()}] #{self.account_number} "
                f"{self.owner} - Balance: {self.balance:.2f}")


class SavingsAccount(Account):
    MIN_BALANCE = 500.0

    def _can_withdraw(self, amount: float) -> bool:
        return self.balance - amount >= self.MIN_BALANCE

    def account_type(self) -> str:
        return "Savings"


class CheckingAccount(Account):
    OVERDRAFT_LIMIT = 1000.0

    def _can_withdraw(self, amount: float) -> bool:
        return self.balance - amount >= -self.OVERDRAFT_LIMIT

    def account_type(self) -> str:
        return "Checking"


class Bank:
    def __init__(self, name: str):
        self.name = name
        self._accounts: dict[int, Account] = {}

    def create_account(self, kind: str, owner: str, initial_deposit: float = 0.0) -> Account:
        types = {"savings": SavingsAccount, "checking": CheckingAccount}
        if kind.lower() not in types:
            raise ValueError("Account type must be 'savings' or 'checking'.")
        account = types[kind.lower()](owner, initial_deposit)
        self._accounts[account.account_number] = account
        return account

    def get_account(self, number: int) -> Account:
        if number not in self._accounts:
            raise KeyError(f"Account {number} not found.")
        return self._accounts[number]


def read_float(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")


def main():
    bank = Bank("Codomax Bank")
    menu = """
1. Create account
2. Deposit
3. Withdraw
4. Show balance
5. Transaction history
6. Exit
"""
    while True:
        print(menu)
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                name = input("Owner name: ")
                kind = input("Type (savings/checking): ")
                amount = read_float("Initial deposit: ")
                acc = bank.create_account(kind, name, amount)
                print("Created:", acc)
            elif choice == "2":
                acc = bank.get_account(int(input("Account number: ")))
                acc.deposit(read_float("Amount: "))
                print(acc)
            elif choice == "3":
                acc = bank.get_account(int(input("Account number: ")))
                acc.withdraw(read_float("Amount: "))
                print(acc)
            elif choice == "4":
                print(bank.get_account(int(input("Account number: "))))
            elif choice == "5":
                acc = bank.get_account(int(input("Account number: ")))
                for t in acc.history() or ["No transactions yet."]:
                    print(t)
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid option.")
        except (ValueError, KeyError, InsufficientFundsError) as err:
            print("Error:", err)


if __name__ == "__main__":
    main()
