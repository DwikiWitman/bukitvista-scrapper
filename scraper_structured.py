import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor

def scrape_property_details(property_url):
	property_response = requests.get(property_url)
	property_soup = BeautifulSoup(property_response.content, "html.parser")

	def extract_property_id(property_soup):
		element_text = "Property ID:"
		block_content_wrap = property_soup.find("div", class_="detail-wrap")

		if block_content_wrap:
			detail_element = block_content_wrap.find("strong", string=element_text)
			if detail_element:
				property_id = detail_element.find_next("span").text
				return property_id

		return "N/A"

	def extract_detail(element_text):
		detail_element = property_soup.find("strong", string=element_text)
		return detail_element.find_next("span").text if detail_element else "N/A"

	property_id = extract_property_id(property_soup)
	price = extract_detail("Price:")
	bedrooms = extract_detail("Bedrooms:")
	bathrooms = extract_detail("Bathrooms:")
	property_type = extract_detail("Property Type:")
	property_status = extract_detail("Property Status:")
	guest_number = extract_detail("Guest Number:")
	address = extract_detail("Address")
	city = extract_detail("City")
	state_county = extract_detail("State/county")
	zip_postal_code = extract_detail("Zip/Postal Code")
	area = extract_detail("Area")
	country = extract_detail("Country")

	return {
		"Property URL": property_url,
		"Property ID": property_id,
		"Price": price,
		"Bedrooms": bedrooms,
		"Bathrooms": bathrooms,
		"Property Type": property_type,
		"Property Status": property_status,
		"Guest Number": guest_number,
		"Address": address,
		"City": city,
		"State/County": state_county,
		"Zip/Postal Code": zip_postal_code,
		"Area": area,
		"Country": country,
	}

def scrape_page(page_url):
	response = requests.get(page_url)
	soup = BeautifulSoup(response.content, "html.parser")

	# Check for "No results found" message
	if "No results found" in soup.get_text():
		return None

	item_wraps = soup.find_all("div", class_="listing-thumb")

	if not item_wraps:
		return None

	scraped_properties = []

	for item_wrap in item_wraps:
		a_tag = item_wrap.find("a")
		if a_tag:
			property_url = a_tag["href"]
			property_details = scrape_property_details(property_url)
			scraped_properties.append(property_details)
			# Print every attribute for each property
			for key, value in property_details.items():
				print(key + ":", value)
			print("=" * 40)

	return scraped_properties

def scrape_all_pages(base_url, start_page, max_threads=11):
    scraped_properties = []
    total_scraped_pages = 0

    with ThreadPoolExecutor(max_threads) as executor:
        while True:
            futures = []

            for _ in range(max_threads):
                future = executor.submit(scrape_page, f"{base_url}{start_page}")
                futures.append(future)
                start_page += 1

            page_properties = []

            for future in futures:
                properties = future.result()
                if properties:
                    page_properties.extend(properties)

            if not page_properties:
                break

            scraped_properties.extend(page_properties)
            total_scraped_pages += len(page_properties)
            print("Scraped page:", total_scraped_pages)

            time.sleep(1)  # Delay between starting new threads

    print("Total scraped pages:", total_scraped_pages)
    return scraped_properties