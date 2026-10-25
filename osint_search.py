import os
import webbrowser
from urllib.parse import quote_plus

def search_web():
    query = input("Enter public search query: ").strip()

    if not query:
        print("Search query cannot be empty.")
        return

    engines = {
        "1": ("Google", "https://www.google.com/search?q="),
        "2": ("Bing", "https://www.bing.com/search?q="),
        "3": ("DuckDuckGo", "https://html.duckduckgo.com/html/?q=")
    }

    print("\nSELECT SEARCH ENGINE")
    for key, value in engines.items():
        print(f"[{key}] {value[0]}")

    choice = input("Select engine: ").strip()

    if choice not in engines:
        print("Invalid selection.")
        return

    name, base_url = engines[choice]
    url = base_url + quote_plus(query)

    print("\nOpening", name)
    print("Search URL:", url)

    try:
        opened = webbrowser.open(url)
        if not opened:
            print("Open this URL manually in your browser.")
    except Exception:
        print("Browser could not be opened.")
        print("Search URL:", url)

def domain_search():
    domain = input("Enter public domain: ").strip().lower()

    if not domain or " " in domain or "." not in domain:
        print("Enter a valid domain.")
        return

    queries = [
        f"site:{domain}",
        f"site:{domain} filetype:pdf",
        f"site:{domain} contact",
        f"site:{domain} about"
    ]

    print("\nPUBLIC DOMAIN SEARCHES")
    print("=" * 40)

    for number, query in enumerate(queries, 1):
        print(f"[{number}] {query}")

    choice = input("\nSelect search: ").strip()

    if choice not in ("1", "2", "3", "4"):
        print("Invalid selection.")
        return

    query = queries[int(choice) - 1]
    url = "https://www.google.com/search?q=" + quote_plus(query)

    print("\nOpening public search...")
    webbrowser.open(url)
    print("URL:", url)

def main():
    while True:
        os.system("clear")
        print("=" * 45)
        print("TORDISSX86 v6.0")
        print("GENERAL OSINT SEARCH CENTER")
        print("=" * 45)
        print("[1] General Public Web Search")
        print("[2] Public Domain Search")
        print("[0] Back to Dashboard")
        print("=" * 45)

        choice = input("Select option: ").strip()

        if choice == "1":
            search_web()
        elif choice == "2":
            domain_search()
        elif choice == "0":
            break
        else:
            print("Invalid option.")

        if choice != "0":
            input("\nPress ENTER to continue...")

if __name__ == "__main__":
    main()
