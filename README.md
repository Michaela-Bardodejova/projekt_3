# Czech Election Data Scraper 🇨🇿

This project is a **web scraper** that downloads and processes election results from the official Czech election website [volby.cz](https://www.volby.cz/).  
It collects data about voter turnout, registered voters, and votes for each political party, and saves them to a **CSV file**.

---

## Requirements

- Python 3.9 or newer  
- Internet connection (the script downloads live data from volby.cz)

### Install dependencies

All required Python libraries are listed in `requirements.txt`.  
Install them with:

```bash
pip install -r requirements.txt
```
#### How It Works

1. The script fetches an election overview page from volby.cz.
2. It finds all links to detailed results for each municipality.
3. It visits each link (in parallel for efficiency).
4. It extracts data from HTML tables using BeautifulSoup.
5. It saves all results into a CSV file with ; as the separator.

##### Usage

```bash
python main.py <URL> <output_file.csv>
```
<URL> → The starting page from volby.cz (must be one of the region pages).
<output_file.csv> Name of the output CSV file where the data will be saved.

Exemple:

```bash
python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" vysledky_prostejov.csv
```
The course of the program if every is OK:

The script is running.                                                                        
I have 1 out of 97 parts ready.
I have 2 out of 97 parts ready.
I have 3 out of 97 parts ready.
.
.
.
I have 96 out of 97 parts ready.
I have 97 out of 97 parts ready.
CSV file is ready.


Example Output: 

code	location	registered	envelopes	valid	Občanská demokratická strana	Řád národa - Vlastenecká unie	
506761	Alojzov	          205	    145	      144	           29	                         0
589268	Bedihošť	      834	    527	      524	           51	                         0

Program flow when entering wrong input:

Your web address <URL>
or CSV file name <output_file.csv> is incorrect.

