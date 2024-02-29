from atm import Account
from atm import ATM


def interface():
    atm = ATM()

    # Accounts
    visa = Account("123456789", "1234", 1000)
    master_card = Account("987654321", "4321", 500)
    american_express = Account("100000000", "1000", 1000)

    atm.add_account(visa)
    atm.add_account(master_card)
    atm.add_account(american_express)

    while True:
        print("\n====== Welcome to BOV ======\n")
        print("\n----- Select an option -----")
        print("1. Log In")
        print("2. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            card_number = input("Enter your card number: ")
            pin = input("Enter your PIN: ")

            if atm.authenticate_user(card_number, pin):
                while True:
                    print("\n----- Account Menu -----")
                    print("1. Display Balance")
                    print("2. Deposit")
                    print("3. Withdraw")
                    print("4. Log Out")

                    user_choice = input("Enter your choice: ")

                    if user_choice == "1":
                        balance = atm.display_balance(card_number)
                        print(f"Current balance: ${balance}")
                    elif user_choice == "2":
                        amount = float(input("Enter deposit amount: $"))
                        balance = atm.deposit(card_number, amount)
                        print(f"${amount} deposited. New balance: ${balance}")
                    elif user_choice == "3":
                        amount = float(input("Enter withdrawal amount: $"))
                        result = atm.withdraw(card_number, amount)
                        if isinstance(result, str):
                            print(result)
                        else:
                            print(f"${amount} withdrawn. New balance: ${result}")
                    elif user_choice == "4":
                        print("Logged out.")
                        break
                    else:
                        print("Invalid choice. Please try again.")
            else:
                print("Invalid card number or PIN. Please try again.")
        elif choice == "2":
            print("Exiting. Thank you!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    interface()
