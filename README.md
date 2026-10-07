# 🔎 LinkScope

> **A lightweight website inspection and link analysis tool built with Streamlit, Requests, BeautifulSoup, and Pandas.**

LinkScope lets you inspect a web page from a simple dashboard and quickly understand its **page title, extracted text, internal links, external links, and linked domains**.

The application performs a single page fetch, processes the HTML, resolves relative URLs into absolute URLs, removes unwanted link schemes, and presents the results through an interactive Streamlit interface.

---

## ✨ Features

### 🌐 Website Inspection
- Accepts URLs with or without `http://` / `https://`.
- Fetches the requested web page using `requests`.
- Follows normal HTTP redirects through the Requests library.
- Extracts the final resolved URL and page title.
- Rejects non-HTML responses such as PDFs and images.
- Uses a request timeout to prevent the application from hanging indefinitely.

### 📝 Text Extraction
- Extracts readable text from the page body.
- Removes unnecessary elements such as:
  - `<script>`
  - `<style>`
  - `<img>`
  - `<input>`
  - `<noscript>`
- Provides an adjustable text preview from **500 to 8,000 characters**.
- Allows the user to switch between the preview and the **full extracted text**.
- Displays:
  - Word count
  - Estimated reading time

### 🔗 Link Analysis
- Extracts links from the page.
- Converts relative URLs into absolute URLs.
- Removes duplicate URLs.
- Ignores:
  - `#anchor` links
  - `javascript:` links
  - `mailto:` links
  - `tel:` links
- Classifies links as:
  - **Internal** — links belonging to the inspected domain
  - **External** — links pointing to another domain

### 📊 Domain Analytics
- Shows the distribution of internal vs. external links.
- Displays the number of links pointing to each domain.
- Provides a visual bar chart for domain frequency.
- Displays a domain-level data table.

### 🔎 Link Search & Filtering
- Filter links by:
  - All
  - Internal
  - External
- Search links using a URL/text search field.
- Display up to 500 matching links in the interface.

### 📥 CSV Export
- Download all discovered links as a CSV file.
- Exported data includes:
  - Link URL
  - Domain
  - Link type

### ⚡ Caching
- Results are cached for **10 minutes** per URL and preview length.
- A **Force refresh** option allows the user to bypass the cache.

### 🎨 User Interface
- Responsive wide-layout Streamlit dashboard.
- Custom styling and SVG assets.
- Custom hero banner and icons.
- Separate tabs for:
  - Page contents
  - Links
  - Top domains

---

## 🖥️ Application Preview

The dashboard is organized around three main analysis sections:

| Section | Purpose |
|---|---|
| **Page Contents** | View the page title, URL, extracted text, word count, and reading time |
| **Links** | Search, filter, inspect, and export discovered links |
| **Top Domains** | Analyze which domains receive the most links |

---

## 🏗️ Project Architecture

```text
User
 │
 │ Enter URL
 ▼
Streamlit UI
 │
 │ Normalize URL
 ▼
fetch_website_data()
 │
 ├── HTTP request
 │
 ├── Validate response
 │
 ├── Parse HTML with BeautifulSoup
 │
 ├── Extract title
 │
 ├── Extract page text
 │
 ├── Extract hyperlinks
 │
 ├── Resolve relative URLs
 │
 └── Remove duplicate / unsupported links
 │
 ▼
Processed Website Data
 │
 ├── Page title
 ├── Full text
 ├── Preview text
 └── Links
      │
      ├── Internal links
      └── External links
 │
 ▼
Streamlit Dashboard
 │
 ├── Summary metrics
 ├── Page contents
 ├── Link filtering/search
 ├── CSV export
 └── Top-domain analytics
```

---

## 📁 Project Structure

```text
linkscope/
│
├── app.py                  # Streamlit application and dashboard
├── scraper.py              # Website fetching, parsing, and link extraction
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
│
└── assets/
    ├── hero.svg            # Dashboard hero/banner
    ├── icon_external.svg   # External-link icon
    ├── icon_internal.svg   # Internal-link icon
    ├── icon_links.svg      # Links icon
    └── icon_title.svg      # Title/page icon
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core application language |
| **Streamlit** | Interactive web interface |
| **Requests** | HTTP requests and website fetching |
| **BeautifulSoup4** | HTML parsing and content extraction |
| **Pandas** | Link data processing and tabular analysis |
| **HTML/CSS** | Dashboard styling |
| **SVG** | Custom offline UI graphics |

---

## ⚙️ Requirements

- Python **3.9+** recommended
- Internet connection for fetching public websites
- `pip`

The required Python packages are listed in `requirements.txt`:

```text
streamlit>=1.32
requests>=2.31
beautifulsoup4>=4.12
pandas>=2.0
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/linkscope.git
cd linkscope
```

> Replace the repository URL with your actual GitHub repository URL.

### 2. Create a virtual environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Application

Start the Streamlit application with:

```bash
streamlit run app.py
```

Streamlit will provide a local URL, normally similar to:

```text
http://localhost:8501
```

Open that address in your browser.

---

## 📖 How to Use

### Step 1 — Enter a URL

Enter a website address in the **Page URL** field.

Examples:

```text
example.com
```

or

```text
https://example.com
```

### Step 2 — Configure the preview

Open **Options** to choose:

- Preview length: 500–8,000 characters
- Force refresh: bypass the 10-minute cache

### Step 3 — Inspect the page

Click:

```text
Inspect page
```

LinkScope fetches and analyzes the page.

### Step 4 — Explore the results

Use the tabs:

#### Page Contents
View:

- Page title
- Final URL
- Extracted text
- Full text
- Word count
- Estimated reading time

#### Links
View:

- Internal links
- External links
- Domains
- Search results
- Filtered results

You can also download the complete link list as:

```text
linkscope_links.csv
```

#### Top Domains
See which domains appear most frequently among the extracted links.

---

## 🔬 How the Scraper Works

The main scraping function is:

```python
fetch_website_data(url, max_chars=2000)
```

It performs the complete page analysis in a **single HTTP request**.

The function returns:

```python
{
    "url": final_url,
    "title": title,
    "full_text": full_text,
    "preview_text": preview,
    "links": links
}
```

### URL Normalization

If a user enters:

```text
example.com
```

the application converts it to:

```text
https://example.com
```

before fetching.

### Relative URL Resolution

For example, if a page contains:

```html
<a href="/about">About</a>
```

and the page is hosted at:

```text
https://example.com
```

LinkScope converts the link to:

```text
https://example.com/about
```

### Link Classification

A link is considered **internal** when its domain matches the inspected page's domain.

Otherwise, it is classified as **external**.

For example:

```text
Inspected page:
https://example.com

Internal:
https://example.com/about

External:
https://github.com/example
```

---

## ⚡ Performance

LinkScope uses Streamlit's data cache:

```python
@st.cache_data(show_spinner=False, ttl=600)
```

This means the same URL and preview configuration can be reused from cache for up to **10 minutes**, reducing unnecessary network requests.

The application also uses `fetch_website_data()` to collect the title, text, and links in one request instead of fetching the same page multiple times.

---

## 🛡️ Error Handling

LinkScope handles common scraping failures and presents readable messages instead of exposing raw stack traces.

Examples include:

- Invalid URL
- Connection failure
- Request timeout
- HTTP errors
- Non-HTML responses
- Unexpected application errors

The scraper raises a custom exception:

```python
FetchError
```

for expected website-fetching failures.

---

## 📊 Example Output

For a page containing:

```text
50 total links
35 internal links
15 external links
```

LinkScope provides:

```text
Total links:       50
Internal links:    35
External links:    15
```

It can then show which domains occur most frequently, for example:

```text
example.com        35
github.com          6
wikipedia.org       4
other-domain.com    5
```

---

## 🔐 Security & Responsible Use

LinkScope is intended for legitimate website inspection, development, research, and educational purposes.

Keep the following in mind:

- Only inspect websites you are authorized to access.
- Respect website terms of service.
- Respect `robots.txt` and applicable crawling policies where relevant.
- Avoid sending excessive requests to websites.
- Do not use the application to bypass authentication or access controls.
- Be mindful of websites that prohibit automated access.
- The application does not bypass CAPTCHAs, authentication, or other access restrictions.

LinkScope is a **single-page inspector**, not a full web crawler.

---

## ⚠️ Current Limitations

- Primarily designed for publicly accessible HTML pages.
- Does not execute JavaScript-rendered page content.
- Does not crawl multiple pages automatically.
- Does not bypass authentication or CAPTCHAs.
- Does not extract links hidden behind JavaScript interactions.
- Non-HTML resources are intentionally rejected.
- Link classification is based on the URL's network location/domain.
- The interface displays a maximum of 500 matching links at once, while the complete dataset remains available through CSV export.

---

## 🔮 Future Improvements

Potential improvements include:

- [ ] Multi-page website crawling
- [ ] Crawl-depth controls
- [ ] Sitemap support
- [ ] Robots.txt awareness
- [ ] Broken-link detection
- [ ] HTTP status-code analysis for discovered links
- [ ] Response-time analysis
- [ ] Anchor-text extraction
- [ ] Link graph visualization
- [ ] Domain categorization
- [ ] Export reports as PDF/Excel
- [ ] URL history
- [ ] Concurrent/asynchronous fetching
- [ ] JavaScript-rendered page support using a browser automation framework
- [ ] SEO-oriented page analysis
- [ ] Meta description and heading analysis

---

## 🧪 Development

Run the application from the project root:

```bash
streamlit run app.py
```

The scraping logic is separated from the UI so that `scraper.py` can also be reused independently.

For example:

```python
from scraper import fetch_website_data

data = fetch_website_data("https://example.com")

print(data["title"])
print(data["links"])
```

---

## 📦 Dependencies

This project intentionally keeps its dependency footprint small:

```text
streamlit
requests
beautifulsoup4
pandas
```

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

Contributions and improvements are welcome.

A typical workflow is:

```bash
git checkout -b feature/your-feature
```

Make your changes, test the application, and then submit a pull request.

When contributing, please keep the following in mind:

- Keep the scraper and UI logic separated.
- Handle network failures gracefully.
- Avoid unnecessary dependencies.
- Preserve the existing user experience where possible.
- Update this README when adding significant functionality.

---

## 📄 License

If this project is published publicly, add the license you intend to use.

For example:

```text
MIT License
```

A `LICENSE` file should be added to the repository if an open-source license is selected.

---

# Author

**Mohammed Saif**

GitHub:

https://github.com/saif-mohammed9505


## License

This project is intended for educational and experimental purposes.


## ⭐ If You Find This Useful

If you found LinkScope useful, consider giving the repository a ⭐ on GitHub.
