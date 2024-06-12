import requests
from bs4 import BeautifulSoup
import re
import tldextract
import whois
from urllib.parse import urlparse
import datetime
import joblib
import pandas as pd
import os
def extract_features(url):
    features = {}

    features['url_length'] = len(url)
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ''
    features['hostname_length'] = len(hostname)

    features['total_of.'] = url.count('.')
    features['total_of-'] = url.count('-')
    features['total_of?'] = url.count('?')
    features['total_of='] = url.count('=')
    features['total_of_'] = url.count('_')
    features['total_of%'] = url.count('%')
    features['total_of/'] = url.count('/')

    features['total_of_www'] = 1 if 'www' in url else 0

    features['https_token'] = 1 if url.startswith('https') else 0

    features['ratio_digits_url'] = sum(c.isdigit() for c in url) / len(url)
    features['ratio_digits_host'] = sum(c.isdigit() for c in hostname) / len(hostname)

    features['nb_subdomains'] = len(tldextract.extract(url).subdomain.split('.'))

    features['prefix_suffix'] = 1 if '-' in hostname else 0

    shortening_services = ["bit.ly", "goo.gl", "tinyurl.com", "ow.ly", "is.gd", "buff.ly"]
    features['shortening_service'] = 1 if any(service in hostname for service in shortening_services) else 0

    try:
        response = requests.get(url)
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
    except requests.RequestException:
        return features

    features['nb_redirection'] = len(response.history)

    words_raw = re.findall(r'\w+', url)
    words_host = re.findall(r'\w+', hostname)
    words_path = re.findall(r'\w+', parsed_url.path)

    features['length_words_raw'] = len(words_raw)
    features['char_repeat'] = max((url.count(char) for char in set(url)), default=0)
    features['shortest_words_raw'] = min((len(word) for word in words_raw), default=0)
    features['shortest_word_host'] = min((len(word) for word in words_host), default=0)
    features['shortest_word_path'] = min((len(word) for word in words_path), default=0)
    features['longest_words_raw'] = max((len(word) for word in words_raw), default=0)
    features['longest_word_host'] = max((len(word) for word in words_host), default=0)
    features['longest_word_path'] = max((len(word) for word in words_path), default=0)
    features['avg_words_raw'] = sum(len(word) for word in words_raw) / len(words_raw) if words_raw else 0
    features['avg_word_host'] = sum(len(word) for word in words_host) / len(words_host) if words_host else 0
    features['avg_word_path'] = sum(len(word) for word in words_path) / len(words_path) if words_path else 0

    features['phish_hints'] = len(soup.find_all(string=re.compile(r'phish', re.I)))
    features['domain_in_brand'] = 1 if any(brand in hostname for brand in ['google', 'facebook', 'amazon']) else 0
    features['nb_hyperlinks'] = len(soup.find_all('a'))
    features['ratio_intHyperlinks'] = len([a for a in soup.find_all('a', href=True) if urlparse(a['href']).netloc == hostname]) / len(soup.find_all('a', href=True)) if soup.find_all('a', href=True) else 0
    features['ratio_extHyperlinks'] = len([a for a in soup.find_all('a', href=True) if urlparse(a['href']).netloc != hostname]) / len(soup.find_all('a', href=True)) if soup.find_all('a', href=True) else 0
    features['nb_extCSS'] = len(soup.find_all('link', rel='stylesheet'))
    features['ratio_extRedirection'] = len([a for a in soup.find_all('a', href=True) if a['href'].startswith('http')]) / len(soup.find_all('a', href=True)) if soup.find_all('a', href=True) else 0
    features['ratio_extErrors'] = len([img for img in soup.find_all('img') if 'error' in img.get('src', '')]) / len(soup.find_all('img')) if soup.find_all('img') else 0
    features['external_favicon'] = 1 if soup.find('link', rel='icon', href=True) and urlparse(soup.find('link', rel='icon', href=True)['href']).netloc != hostname else 0
    features['links_in_tags'] = len(soup.find_all(['link', 'script', 'iframe']))
    features['ratio_intMedia'] = len([media for media in soup.find_all(['img', 'video', 'audio']) if urlparse(media['src']).netloc == hostname]) / len(soup.find_all(['img', 'video', 'audio'])) if soup.find_all(['img', 'video', 'audio']) else 0
    features['ratio_extMedia'] = len([media for media in soup.find_all(['img', 'video', 'audio']) if urlparse(media['src']).netloc != hostname]) / len(soup.find_all(['img', 'video', 'audio'])) if soup.find_all(['img', 'video', 'audio']) else 0
    features['safe_anchor'] = len([a for a in soup.find_all('a', href=True) if not re.search(r'[^\w]', a['href'])]) / len(soup.find_all('a', href=True)) if soup.find_all('a', href=True) else 0
    features['empty_title'] = 1 if not soup.title or not soup.title.string else 0
    features['domain_in_title'] = 1 if soup.title and hostname in soup.title.string else 0
    features['domain_with_copyright'] = 1 if soup.find(string=re.compile(r'©\s*' + re.escape(hostname), re.I)) else 0

    try:
        domain = whois.whois(hostname)
        creation_date = domain.creation_date if isinstance(domain.creation_date, datetime.datetime) else domain.creation_date[0]
        expiration_date = domain.expiration_date if isinstance(domain.expiration_date, datetime.datetime) else domain.expiration_date[0]
        features['domain_registration_length'] = (expiration_date - creation_date).days if creation_date and expiration_date else 0
        features['domain_age'] = (datetime.datetime.now() - creation_date).days if creation_date else 0
    except:
        features['domain_registration_length'] = 0
        features['domain_age'] = 0

    alexa_rank_url = f'http://data.alexa.com/data?cli=10&dat=s&url={hostname}'
    try:
        response = requests.get(alexa_rank_url)
        print(response)
        alexa_data = BeautifulSoup(response.text, 'xml')
        alexa_rank = int(alexa_data.find('REACH')['RANK']) if alexa_data.find('REACH') else 0
    except:
        alexa_rank = 0
    features['web_traffic'] = alexa_rank

    #features['dns_record'] = 1 if domain else 0

    google_search_url = f'https://www.google.com/search?q=site:{hostname}'
    try:
        response = requests.get(google_search_url)
        features['google_index'] = 1 if 'did not match any documents' not in response.text else 0
    except:
        features['google_index'] = 0

    features['page_rank'] = alexa_rank

    features['sum_all'] = sum(features.values())
    features['sum'] = sum(features.values())



    return features