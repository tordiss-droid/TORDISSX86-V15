import os
import json
from datetime import datetime

REPORT_FOLDER = "learning_reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)

LESSONS = {
    "1": {
        "title": "CYBERSECURITY FUNDAMENTALS",
        "content": [
            "Cybersecurity protects computers, networks and information.",
            "CIA Triad:",
            "- Confidentiality: Prevent unauthorized information access.",
            "- Integrity: Protect information from unauthorized changes.",
            "- Availability: Keep systems accessible when needed.",
            "Authentication verifies identity.",
            "Authorization determines permitted actions."
        ]
    },
    "2": {
        "title": "NETWORKING BASICS",
        "content": [
            "An IP address identifies a device on a network.",
            "DNS translates domain names into IP addresses.",
            "HTTP is a protocol for web communication.",
            "HTTPS protects web communication using TLS.",
            "A router connects different networks.",
            "A port identifies a network service."
        ]
    },
    "3": {
        "title": "LINUX AND TERMUX",
        "content": [
            "Linux is an operating system family.",
            "pwd: Display the current directory.",
            "ls: List files and folders.",
            "cd: Change directory.",
            "mkdir: Create a directory.",
            "cp: Copy files.",
            "mv: Move or rename files.",
            "cat: Display file contents."
        ]
    },
    "4": {
        "title": "OSINT FUNDAMENTALS",
        "content": [
            "OSINT means Open Source Intelligence.",
            "It uses publicly available information.",
            "Sources include public websites and documents.",
            "Verify information using multiple reliable sources.",
            "Respect privacy and applicable laws.",
            "Do not access private accounts or restricted systems."
        ]
    },
    "5": {
        "title": "CRYPTOGRAPHY BASICS",
        "content": [
            "Cryptography protects information.",
            "Encryption converts readable data into protected data.",
            "Decryption restores encrypted data.",
            "Hashing creates a fixed-length digest.",
            "SHA-256 is a cryptographic hash function.",
            "A digital signature helps verify authenticity."
        ]
    },
    "6": {
        "title": "DIGITAL FORENSICS",
        "content": [
            "Digital forensics examines digital evidence.",
            "Preserve original evidence.",
            "Record where evidence came from.",
            "Use SHA-256 to check file integrity.",
            "Maintain a clear evidence log.",
            "Only examine devices and files you are authorized to access."
        ]
    }
}

QUESTIONS = [
    {
        "question": "What does CIA stand for in cybersecurity?",
        "options": [
            "A. Confidentiality, Integrity, Availability",
            "B. Computer Internet Access",
            "C. Central Information Application"
        ],
        "answer": "A"
    },
    {
        "question": "What does DNS do?",
        "options": [
            "A. Encrypts files",
            "B. Translates domain names into IP addresses",
            "C. Deletes network logs"
        ],
        "answer": "B"
    },
    {
        "question": "Which command displays the current directory?",
        "options": [
            "A. pwd",
            "B. mkdir",
            "C. clear"
        ],
        "answer": "A"
    },
    {
        "question": "What does OSINT mean?",
        "options": [
            "A. Open System Internet Network",
            "B. Open Source Intelligence",
            "C. Online Security Internal Network"
        ],
        "answer": "B"
    },
    {
        "question": "Which algorithm is commonly used for file hashing?",
        "options": [
            "A. SHA-256",
            "B. HTML",
            "C. HTTP"
        ],
        "answer": "A"
    }
]

def show_lessons():
    while True:
        os.system("clear")
        print("=" * 45)
        print("TORDISSX86 LEARNING CENTER")
        print("=" * 45)

        for key, lesson in LESSONS.items():
            print(f"[{key}] {lesson['title']}")

        print("[0] Back")

        choice = input("\nSelect lesson: ").strip()

        if choice == "0":
            break

        lesson = LESSONS.get(choice)

        if lesson:
            print("\n" + lesson["title"])
            print("=" * 45)

            for line in lesson["content"]:
                print(line)

            input("\nPress ENTER to continue...")

def start_quiz():
    score = 0
    answers = []

    for number, question in enumerate(QUESTIONS, 1):
        os.system("clear")
        print("TORDISSX86 CYBERSECURITY QUIZ")
        print("=" * 40)
        print(f"\nQuestion {number}: {question['question']}")

        for option in question["options"]:
            print(option)

        answer = input("\nYour answer (A/B/C): ").strip().upper()

        if answer == question["answer"]:
            score += 1
            print("Correct!")
        else:
            print("Incorrect.")
            print("Correct answer:", question["answer"])

        answers.append({
            "question": question["question"],
            "your_answer": answer,
            "correct_answer": question["answer"]
        })

        input("\nPress ENTER to continue...")

    result = {
        "date": datetime.now().isoformat(),
        "score": score,
        "total": len(QUESTIONS),
        "answers": answers
    }

    filename = datetime.now().strftime("QUIZ_%Y%m%d_%H%M%S.json")
    path = os.path.join(REPORT_FOLDER, filename)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4)

    print("\nQUIZ COMPLETED")
    print("Score:", score, "/", len(QUESTIONS))
    print("Report saved:", path)
    input("\nPress ENTER to return...")

def main():
    while True:
        os.system("clear")
        print("=" * 45)
        print("TORDISSX86 v5.0")
        print("CYBERSECURITY LEARNING CENTER")
        print("=" * 45)
        print("[1] Study Lessons")
        print("[2] Start Security Quiz")
        print("[3] View Quiz Reports")
        print("[0] Exit")
        print("=" * 45)

        choice = input("Select option: ").strip()

        if choice == "1":
            show_lessons()
        elif choice == "2":
            start_quiz()
        elif choice == "3":
            files = sorted(os.listdir(REPORT_FOLDER))

            for filename in files:
                print(filename)

            if not files:
                print("No reports available.")

            input("\nPress ENTER to continue...")
        elif choice == "0":
            break
        else:
            print("Invalid option.")
            input("\nPress ENTER to continue...")

if __name__ == "__main__":
    main()
