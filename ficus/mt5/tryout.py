from abc import ABC, abstractmethod

# Interface for Main
class IMain(ABC):
    @abstractmethod
    def notify(self, message: str):
        pass

# Manager class
class Manager:
    def __init__(self, main: IMain):
        self.main = main

    def manage(self):
        print("Manager is managing...")
        self.main.notify("Manager has done its job")

# Listener class
class Listener:
    def listen(self):
        print("Listener is listening...")

# Main class
class Main(IMain):
    def __init__(self):
        self.listener = Listener()
        self.manager = Manager(self)

    def notify(self, message: str):
        print(f"Main received notification: {message}")

    def start(self):
        self.listener.listen()
        self.manager.manage()

# Example of interaction
if __name__ == "__main__":
    main = Main()
    main.start()
