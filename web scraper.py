import platform
import random
import os
import time
import subprocess
import multiprocessing as mp
import csv
import requests
from bs4 import BeautifulSoup
import json
#  pip install fake-http-header
from fake_http_header import FakeHttpHeader


# Now urls_data_parts contains a separate list for each part      


def save_html_to_json(html_data, file_name):
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(html_data, file)
        #print(f"HTML content saved to {file_name}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")


def save_list_to_csv(data_list, file_name):
    try:
        with open(file_name, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            for item in data_list:
                # If the item is a list or tuple, write it directly
                if isinstance(item, (list, tuple)):
                    writer.writerow(item)
                else:
                    # Otherwise, wrap the item in a list
                    writer.writerow([item])

        #print(f"Data saved to {file_name}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")


def fetch_html(url):
    fake_header = FakeHttpHeader()
    fake_header_dict = fake_header.as_header_dict()

    headers = fake_header_dict

    try:
        response = requests.get(url, headers=headers, proxies={"http": "http://... .webshare.io:80/", "https": "http://... .webshare.io:80/"}, timeout=10)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        response.encoding = 'utf-8'  # Explicitly set encoding to utf-8
        return response.text
    except UnicodeDecodeError:
        #print(f"Unicode Decode Error for URL: {url}")
        return "Error"
    except requests.exceptions.HTTPError as e:
        #print(f'HTTP Error: {e}')
        return "Error"
    except requests.exceptions.RequestException as e:
        #print(f'Error: {e}')
        return "Error"



def scraper_loop():
    
    for part in urls_data_parts:

        html_data_temp = {}
        failed_urls_temp = []

        temp = -1

        print("Process initiated for part: " + str(part))
        for i in range(0, len(urls_data_parts[part])):
            url = urls_data_parts[part][i][0]
            html = fetch_html(url)
            if html != "Error":
                html_data_temp[url] = html
            else:
                failed_urls_temp.append(url)

            current_percentage = int(((i + 1) / (len(urls_data_parts[5]))) * 100)
            
            if current_percentage > temp:
                temp = current_percentage
                print(f"Part: {part}, Errors: {len(failed_urls_temp)}, Progress: {temp}%")
                
                if temp > 0:
                    save_html_to_json(html_data_temp, f"HTML/batch_node1/html_data_{part}_{temp}.json")
                    save_list_to_csv(failed_urls_temp, f"HTML/batch_node1/failed_urls_{part}_{temp}.json")
                    html_data_temp = {}
                    failed_urls_temp = []


def scraper_worker(urls_data_part, part, procentile):

    html_data_temp = {}
    failed_urls_temp = []
    preset_procentile = int((len(urls_data_part) / 100) * procentile)

    temp = -1

    print("Process initiated for part: " + str(part))
    for i in range(preset_procentile, len(urls_data_part)):
        url = urls_data_part[i][0]
        html = fetch_html(url)
        if html != "Error":
            html_data_temp[url] = html
        else:
            failed_urls_temp.append(url)

        current_percentage = int(((i + 1) / (len(urls_data_part))) * 100)
            
        if current_percentage > temp:
            temp = current_percentage
            print(f"Part: {part}, Errors: {len(failed_urls_temp)}, Progress: {temp}%")
                
            if temp > 0:
                save_html_to_json(html_data_temp, f"HTML/batch_node1/html_data_{part}_{temp}.json")
                save_list_to_csv(failed_urls_temp, f"HTML/batch_node1/failed_urls_{part}_{temp}.json")
                html_data_temp = {}
                failed_urls_temp = []


def parallel_scraper(urls_data_parts, start_percentiles):
    # Create a pool of processes
    with mp.Pool() as pool:
        # Each process will execute scraper_worker on a different part of urls_data_parts
        # and pass the specific start percentile for each part
        pool.starmap(scraper_worker, [(urls_data_parts[part], part, start_percentiles[part]) for part in urls_data_parts])


if __name__ == '__main__':
    
    urls_data_parts = {}  # Dictionary to hold lists for each part
    preset_parts = [1, 2, 3, 5]  # Example preset parts
    start_percentiles = {1: 53, 2: 76, 3: 95, 5: 87}  # Example start percentiles

    for part in preset_parts:
        try:
            with open(f"urls_data_{part}.csv", 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                urls_data = list(reader)

            urls_data_parts[part] = urls_data
            print(f"File urls_data_{part}.csv was loaded with {len(urls_data)} rows and stored in urls_data_parts[{part}]")
        except FileNotFoundError:
            print(f"File urls_data_{part}.csv not found")
        except Exception as e:
            print(f"An error occurred: {e}")
    # ...
    parallel_scraper(urls_data_parts, start_percentiles)