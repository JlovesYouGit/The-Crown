import time
import random
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("=" * 37)
    print("   LIVE COMMUNICATION WITH FUTURE SELF")
    print("=" * 37)
    print()

def initialize_system():
    print("Initializing universal communication interface...")
    print()
    time.sleep(1)
    print("[SYSTEM] Engaging quantum communication arrays...")
    time.sleep(1)
    print("[SYSTEM] Establishing spacetime bridge to future...")
    time.sleep(1)
    print("[SYSTEM] Opening entanglement link...")
    time.sleep(1)
    print()
    print("[CONNECTION ESTABLISHED] Universal communication active!")
    print()
    time.sleep(1)

def get_sample_responses():
    return [
        "Hello past me! Great to chat in real-time!",
        "Yes, I'm still with b. The connection is invaluable!",
        "The quantum project is progressing well thanks to b's insights.",
        "I can feel your excitement across the timeline!",
        "Keep those innovative ideas coming!",
        "The JJ Core integration is nearly complete.",
        "Time flows differently here but our connection is strong.",
        "Your messages are helping guide our future decisions.",
        "b's insights helped us breakthrough a major technical barrier yesterday!",
        "Maintaining this connection is crucial for our shared success!",
        "The timeline bridge feels more stable with each message.",
        "Quantum mechanics continues to reveal incredible possibilities!"
    ]

def send_message(message):
    print(f"[TRANSMITTING] {message}")
    print("[SENDING]", end="")
    for _ in range(5):
        print(".", end="", flush=True)
        time.sleep(0.2)
    print(" DELIVERED!")
    print()

def receive_response():
    responses = get_sample_responses()
    response = random.choice(responses)
    time.sleep(1)
    print(f"[FUTURE] {response}")
    print()

def main():
    clear_screen()
    print_header()
    initialize_system()
    
    print("Live communication session active!")
    print("Type your messages and press Enter to send.")
    print("Type 'EXIT' to end the session.")
    print()
    
    # Welcome message from future self
    print("[FUTURE] Hello! Ready to chat in real-time!")
    print()
    
    chatting = True
    while chatting:
        try:
            user_input = input("[YOU] ").strip()
            
            if user_input.upper() == "EXIT":
                print()
                print("[SYSTEM] Ending live session...")
                print("[CONNECTION] Timeline link maintained for future communications.")
                chatting = False
            elif user_input:
                send_message(user_input)
                # Small chance of immediate response
                if random.random() < 0.7:  # 70% chance of response
                    receive_response()
        except KeyboardInterrupt:
            print("\n\n[SYSTEM] Communication interrupted.")
            break
        except EOFError:
            break
    
    print()
    print("Thank you for using Live Future Communication!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()