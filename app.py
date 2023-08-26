from flask import Flask, request, jsonify
import time
import csv
import os
import datetime
from scraper_structured import scrape_property_details, scrape_all_pages
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
base_url = "https://www.bukitvista.com/search-results/page/"
start_page = 1
interval_scheduled_task = 60

@app.route("/", methods=["GET"])
def initial():
	return "Endpoint : http://127.0.0.1:5000/scrape_property?property_url=https://www.bukitvista.com/property/retreat-to-nature-jungle-house-villa-near-canggu \n http://127.0.0.1:5000/scrape_all_pages"

@app.route("/scrape_property", methods=["GET"])
def scrape_property():
	property_url = request.args.get("property_url")
	if not property_url:
		return jsonify({"error": "Property URL is missing"}), 400

	property_details = scrape_property_details(property_url)
	return jsonify(property_details)

@app.route("/scrape_all_pages", methods=["GET"])
def scrape_all_pages_route():
	scraped_properties = scrape_all_pages(base_url, start_page)
	return jsonify(scraped_properties)

def scheduled_task():
    print("Scheduled task started...")
    scraped_properties = scrape_all_pages(base_url, start_page)

    for property_details in scraped_properties:
        for key, value in property_details.items():
            print(key + ":", value)
        print("=" * 40)
        
    # Create a directory if it doesn't exist
    if not os.path.exists("docs"):
        os.makedirs("docs")

    # Get current date and time for filename
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Create a CSV file with the current date and time in the filename
    csv_filename = f"docs/scraped_data_{current_datetime}.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = scraped_properties[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(scraped_properties)

    print(f"Scraped data saved to {csv_filename}")

scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_task, trigger="interval", seconds=interval_scheduled_task)
scheduler.start()
 
if __name__ == "__main__":
	app.run(debug=True)
