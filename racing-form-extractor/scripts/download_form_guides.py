import os
import sys
import argparse
from playwright.sync_api import sync_playwright

def download_pdfs(meetings_list_file):
    print("Semi-automated PDF downloader starting...")
    print("Remember: YOU must log in and solve Cloudflare when the browser opens.")
    
    if not os.path.exists(meetings_list_file):
        print(f"Error: {meetings_list_file} not found.")
        sys.exit(1)
        
    with open(meetings_list_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
    if not urls:
        print("No URLs found to process.")
        return

    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "input")
    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print("\nBrowser launched. Navigate to the first URL and log in if necessary.")
        print("Wait for the page to fully load and solve any Cloudflare challenges.")
        input("Press Enter here in the console ONCE you have cleared Cloudflare and can see the page...")

        for url in urls:
            print(f"\nNavigating to: {url}")
            try:
                page.goto(url)
                page.wait_for_load_state("domcontentloaded")
                
                # Check for Cloudflare again
                if "Just a moment" in page.title():
                    print("Cloudflare challenge detected! Please solve it in the browser.")
                    input("Press Enter here once you have solved it...")

                # This is a stub for the clicking logic described in SKILL.md.
                # In full implementation, we'd find the "Enhanced PDF" button and click it to trigger download.
                print("Simulating PDF download click for this URL...")
                # with page.expect_download() as download_info:
                #     page.click("text='Enhanced PDF'")
                # download = download_info.value
                # download.save_as(os.path.join(output_dir, download.suggested_filename))
                
                print("Download completed (simulated).")
                
            except Exception as e:
                print(f"Failed to process {url}: {e}")

        browser.close()
        print("\nAll downloads finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download form guides")
    parser.add_argument("--list", type=str, required=True, help="Path to meetings.txt")
    args = parser.parse_args()
    
    download_pdfs(args.list)
