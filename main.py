"""
main.py: třetí projekt do Engeto Online Python Akademie

author: Michaela Bardodějová
email: misa.bardodejova@gmail.com
"""

import requests
from bs4 import BeautifulSoup as bs
import csv
import sys
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict


def content_pages(url: str) -> bs:
    """
    Fetch the HTML content of a given URL with a timeout and return a BeautifulSoup object.
    """
    try:
        page = requests.get(url, timeout=10)
        page.raise_for_status()
        return bs(page.text, features="html.parser")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None


def object_list(soup: bs, atribut_values: List[str]) -> List[str]:
    """
    Extracts text values from <td> elements in the provided BeautifulSoup object
    based on the specified header attribute values.

    Args:
        soup (bs4.BeautifulSoup): The parsed HTML content.
        atribut_values (List[str]): List of header attribute values to match.

    Returns:
        List[str]: A list of extracted text values.
    """
    td_dict: Dict[str, List[str]] = {}
    object_list: List[str] = []
    tables = soup.find_all("table")

    for td in soup.find_all("td"):
        header = td.get("headers")
        if header:
            header_str = " ".join(header) if isinstance(header, list) else header
            td_dict.setdefault(header_str, []).append(td.get_text(strip=True))

    for atribut_value in atribut_values:
        if "_" in atribut_value:
            for i in range(1, len(tables) + 1):
                value_atribut = atribut_value.replace("_", str(i))
                object_list.extend(td_dict.get(value_atribut, []))
        else:
            object_list.extend(td_dict.get(atribut_value, []))

    return object_list


def web_list(soup: bs, atribut_value: str) -> List[str]:
    """
    Extracts and builds absolute URLs from <a> tags inside <td> elements based on headers.

    Args:
        soup (bs4.BeautifulSoup): The parsed HTML content.
        atribut_value (str): Header attribute value pattern to match.

    Returns:
        List[str]: A list of absolute URLs found in the HTML.
    """
    base = "https://www.volby.cz/pls/ps2017nss/"
    td_dict: Dict[str, List[str]] = {}
    web_list_result: List[str] = []
    tables = soup.find_all("table")

    for td in soup.find_all("td"):
        header = td.get("headers")
        if header:
            for a in td.find_all("a"):
                href = a.get("href")
                if href:
                    header_str = " ".join(header) if isinstance(header, list) else header
                    td_dict.setdefault(header_str, []).append(urljoin(base, href))

    if "_" in atribut_value:
        for i in range(1, len(tables) + 1):
            value_atribut = atribut_value.replace("_", str(i))
            web_list_result.extend(td_dict.get(value_atribut, []))
    else:
        web_list_result.extend(td_dict.get(atribut_value, []))

    return web_list_result


def writer_csv(data: List[List[str]], name_csv: str) -> None:
    """
    Writes a 2D list of data into a CSV file using ';' as a delimiter.

    Args:
        data (List[List[str]]): Data to be written to the CSV file.
        name_csv (str): Output CSV filename.
    """
    with open(name_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerows(data)


def frist_line(web: str) -> List[str]:
    """
    Extracts header information from the given web page to create the first line of the CSV file.

    Args:
        web (str): The URL of the page to extract headers from.

    Returns:
        List[str]: A list of column names (first row of the CSV file).
    """
    help_0 = ["code", "location", "registered", "envelopes", "valid"]
    soup = content_pages(web)
    for i in range(1, len(soup.find_all("table")) + 1):
        value_atribut = f"t{i}sa1 t{i}sb2"
        help_0.extend([element.get_text(strip=True) for element in soup.find_all("td", headers=value_atribut)])
    return help_0

def check_args() -> tuple[str, str]:
    """
    Check command-line arguments and return web URL and CSV filename.

    Returns:
        Tuple[str, str]: web URL, CSV filename.
    """
    if len(sys.argv) != 3:
        print("Usage: python main.py <URL> <output_file.csv>")
        sys.exit(1)
    web = sys.argv[1]
    name_csv = sys.argv[2]
    return web, name_csv

def validate_web(web: str) -> bool:
    """
    Validate that the provided web URL is on the main election page.

    Args:
        web (str): Web URL to check.

    Returns:
        bool: True if URL is valid, False otherwise.
    """
    main_soup = content_pages("https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ")
    t_sa3_list = web_list(main_soup, "t_sa3")
    return web in t_sa3_list

def process_web1(web1: str, data_code_item: str, data_location_item: str) -> List[str]:
    """
    Process a single web page, fetch linked pages in parallel if needed,
    and extract election data.

    Args:
        web1 (str): URL of the web page to process.
        data_code_item (str): Code value for this row.
        data_location_item (str): Location value for this row.

    Returns:
        List[str]: Extracted data for this row.
    """
    soup1 = content_pages(web1)
    help_if = object_list(soup1, ["sa2"])

    help_3 = [data_code_item, data_location_item]

    if len(help_if) == 0:
        help_1 = []
        cross_list = web_list(soup1, "s1")

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(content_pages, url): url for url in cross_list}
            results = {}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result(timeout=15)
                except Exception as e:
                    print(f" Failed {url}: {e}")
                    results[url] = None

        for web_cross in cross_list:
            soup2 = results[web_cross]
            if soup2 is None:
                continue
            help_2 = object_list(soup2, ["sa2", "sa3", "sa6", "t_sa2 t_sb3"])

            if help_1:
                for i in range(len(help_1)):
                    if help_2[i] != "-":
                        try:
                            help_1[i] = int(help_2[i]) + int(help_1[i])
                        except ValueError:
                            help_1[i] = int(help_2[i].replace("\xa0","")) + int(str(help_1[i]).replace("\xa0",""))
            else:
                help_1 = help_2

        help_3.extend(help_1)
    else:
        help_3.extend(object_list(soup1, ["sa2", "sa3", "sa6", "t_sa2 t_sb3"]))

    return help_3

def process_all_webs(web: str, name_csv: str) -> None:
    """
    Process all main web pages, collect election data, and write to CSV.

    Args:
        web (str): Main web URL to process.
        name_csv (str): Output CSV filename.
    """
    soup = content_pages(web)
    data_code = object_list(soup, ["t_sa1 t_sb1"])
    data_location = object_list(soup, ["t_sa1 t_sb2"])
    webs = web_list(soup, "t_sa2")

    data = []
    for i, web1 in enumerate(webs):
        help_3 = process_web1(web1, data_code[i], data_location[i])
        print(f"I have {i+1} out of {len(webs)} parts ready.")
        data.append(help_3)

    data.insert(0, frist_line(webs[0]))
    writer_csv(data, name_csv)
    print("CSV file is ready.")

def main():
    """
    Main function: checks arguments, validates web URL,
    and processes all pages.
    """
    web, name_csv = check_args()

    if validate_web(web):
        print("The script is running.")
        process_all_webs(web, name_csv)
    else:
        print(f"\nYour web address {web} or CSV file name {name_csv} is incorrect.\n")

if __name__ == "__main__":
    main()