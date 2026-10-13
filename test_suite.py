import json
import unittest
from sheypoor_mcp.tools import execute_tool, TOOLS
from sheypoor_mcp.resolve import resolve_city, resolve_category
from sheypoor_mcp.analytics import analyze_prices, find_deals, appraise_listing

class TestSheypoorMCP(unittest.TestCase):
    def test_tools_count(self):
        self.assertGreaterEqual(len(TOOLS), 18)
        print(f"Verified {len(TOOLS)} MCP tool definitions.")

    def test_city_resolution(self):
        tehran = resolve_city("تهران")
        self.assertIsNotNone(tehran)
        self.assertEqual(tehran["id"], 301)


        shiraz = resolve_city("شیراز")
        self.assertIsNotNone(shiraz)
        self.assertEqual(shiraz["id"], 647)

        shahroud = resolve_city("شاهرود")
        self.assertIsNotNone(shahroud)
        self.assertEqual(shahroud["id"], 555)
        print("City resolution tests passed.")

    def test_search(self):
        res = execute_tool("sheypoor_search", {"query": "پیکان وانت", "cities": "شیراز", "page": 1})
        self.assertTrue(res.get("success"))
        self.assertGreater(len(res.get("listings", [])), 0)
        first = res["listings"][0]
        self.assertIn("title", first)
        self.assertIn("id", first)
        print(f"Search test passed. Got {len(res['listings'])} listings.")

    def test_get_listing_and_contact(self):
        search_res = execute_tool("sheypoor_search", {"query": "پیکان وانت", "cities": "شیراز", "page": 1})
        self.assertTrue(search_res.get("success"))
        listing_id = search_res["listings"][0]["id"]
        
        detail_res = execute_tool("sheypoor_get_listing", {"listing_id": listing_id})
        self.assertTrue(detail_res.get("success"))
        self.assertEqual(detail_res["listing"]["id"], listing_id)
        print(f"Get listing test passed for {listing_id}.")

        contact_res = execute_tool("sheypoor_get_contact", {"listing_id": listing_id})
        self.assertTrue(contact_res.get("success"))
        self.assertTrue(bool(contact_res.get("phone")))
        print(f"Get contact test passed: phone={contact_res.get('phone')}")

    def test_similar_listings(self):
        search_res = execute_tool("sheypoor_search", {"query": "پیکان وانت", "cities": "شیراز"})
        listing_id = search_res["listings"][0]["id"]
        sim_res = execute_tool("sheypoor_similar_listings", {"listing_id": listing_id})
        self.assertTrue(sim_res.get("success"))
        print(f"Similar listings test passed: got {len(sim_res.get('listings', []))} items.")

    def test_price_analysis(self):
        res = execute_tool("sheypoor_price_analysis", {"query": "پیکان وانت", "cities": "شیراز"})
        self.assertIn("analysis", res)
        self.assertIn("median_price", res["analysis"])
        print(f"Price analysis test passed: median={res['analysis']['median_price']}")

    def test_find_deals(self):
        res = execute_tool("sheypoor_find_deals", {"query": "پیکان وانت", "cities": "شیراز"})
        self.assertIn("deals", res)
        print(f"Find deals test passed: found {res['deals_count']} deals.")

    def test_list_cities(self):
        res = execute_tool("sheypoor_list_cities", {"search": "شاهرود"})
        self.assertGreater(res.get("count", 0), 0)
        print(f"List cities test passed: found {res['count']} cities.")

    def test_status(self):
        st = execute_tool("sheypoor_status", {})
        self.assertEqual(st.get("server"), "Sheypoor MCP Server")
        self.assertTrue(st.get("endpoints_healthy"))
        print("Status test passed.")

if __name__ == "__main__":
    unittest.main()
