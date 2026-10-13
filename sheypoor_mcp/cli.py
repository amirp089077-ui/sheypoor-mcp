"""
CLI interface for Sheypoor MCP.
"""

import sys
import json
import argparse
from .client import SheypoorClient
from .tools import execute_tool, TOOLS

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")



def main():
    parser = argparse.ArgumentParser(description="Sheypoor MCP CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Search
    search_p = subparsers.add_parser("search", help="Search Sheypoor listings")
    search_p.add_argument("query", nargs="?", default="", help="Search query")
    search_p.add_argument("--cities", "-c", default="", help="Cities (e.g. 'تهران' or 'شیراز,شاهرود')")
    search_p.add_argument("--category", default="", help="Category name or ID")
    search_p.add_argument("--page", "-p", type=int, default=1, help="Page number")
    search_p.add_argument("--min-price", type=int, default=None, help="Min price")
    search_p.add_argument("--max-price", type=int, default=None, help="Max price")

    # Get listing
    get_p = subparsers.add_parser("get", help="Get listing details")
    get_p.add_argument("listing_id", help="Listing ID")

    # Contact
    contact_p = subparsers.add_parser("contact", help="Get seller contact info")
    contact_p.add_argument("listing_id", help="Listing ID")

    # Status
    subparsers.add_parser("status", help="Check server & auth status")

    # Serve
    subparsers.add_parser("serve", help="Run MCP JSON-RPC Server")

    args = parser.parse_args()

    if args.command == "serve" or len(sys.argv) == 1:
        from .server import main as server_main
        server_main()
        return

    client = SheypoorClient()

    if args.command == "search":
        res = client.search(
            query=args.query,
            cities=args.cities,
            category=args.category,
            page=args.page,
            min_price=args.min_price,
            max_price=args.max_price,
        )
        print(f"Total results: {res.get('totalCount')}")
        for item in res.get("listings", []):
            print(f"- [{item['id']}] {item['title']} | {item['price_string']} | {item['city']}")

    elif args.command == "get":
        res = client.get_listing(args.listing_id)
        if res.get("success"):
            print(json.dumps(res["listing"], ensure_ascii=False, indent=2))
        else:
            print("Error:", res.get("error"))

    elif args.command == "contact":
        res = client.get_contact(args.listing_id)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif args.command == "status":
        print(json.dumps(execute_tool("sheypoor_status", {}), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
