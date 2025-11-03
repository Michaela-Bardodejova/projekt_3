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
    Fetch the HTML content of a given URL and return a BeautifulSoup object.

    Args:
        url (str): The URL of the web page to download.

    Returns:
        bs4.BeautifulSoup: Parsed HTML page.
    """
    page = requests.get(url)
    return bs(page.text, features="html.parser")


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


# --- Script Execution ---
web = sys.argv[1]
name_csv = sys.argv[2]
soup = content_pages(web)

if len(sys.argv) != 3:
    print("Usage: python main.py <URL> <output_file.csv>")
    sys.exit(1)
if web in web_list(content_pages("https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"), "t_sa3"):
    print("The script is running.")
    data_code = object_list(soup, ["t_sa1 t_sb1"])
    data_location = object_list(soup, ["t_sa1 t_sb2"])
    webs = web_list(soup, "t_sa2")
    memory_count = 0
    len_webs = len(webs)
    data = []

    for web1 in webs:
        soup1 = content_pages(web1)
        help_3 = [data_code[memory_count], data_location[memory_count]]
        help_if = object_list(soup1, ["sa2"])
        memory_count += 1

        if len(help_if) == 0:
            help_1 = []
            cross_list = web_list(soup1, "s1")

            # Parallel downloading
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_url = {executor.submit(content_pages, web_cross): web_cross for web_cross in cross_list}
                results: Dict[str, bs] = {}
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    results[url] = future.result()

            for web_cross in cross_list:
                soup2 = results[web_cross]
                help_2 = object_list(soup2, ["sa2", "sa3", "sa6", "t_sa2 t_sb3"])

                if len(help_1) != 0:
                    for index in range(len(help_1)):
                        if help_2[index] != "-":
                            try:
                                help_1[index] = int(help_2[index]) + int(help_1[index])
                            except ValueError:
                                if isinstance(help_1[index], str):
                                    help_1[index] = int(help_2[index].replace("\xa0", "")) + int(help_1[index].replace("\xa0", ""))
                                else:
                                    help_1[index] = int(help_2[index].replace("\xa0", "")) + int(help_1[index])
                else:
                    help_1 = help_2

            help_3.extend(help_1)

        else:
            help_3.extend(object_list(soup1, ["sa2", "sa3", "sa6", "t_sa2 t_sb3"]))

        print(f"I have {memory_count} out of {len_webs} parts ready.")
        data.append(help_3)

    data.insert(0, frist_line(cross_list[0]))
    writer_csv(data, name_csv)
    print("CSV file is ready.")
else:
    print(f"""

Your web address {web}
or CSV file name {name_csv} is incorrect.

""")