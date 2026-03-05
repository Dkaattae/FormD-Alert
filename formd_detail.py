import os
import json
import pandas as pd
import requests
import time
from lxml import etree


headers = {
    "User-Agent": "BrokerDealerList xchencws@gmail.com" 
}

def format_owners(owner_list):
    if not owner_list:
        return None
    formatted = []
    for d in owner_list:
        fn = d.get('firstName', '')
        ln = d.get('lastName', '')
        name = f"{fn} {ln}".strip()
        role = d.get('role', 'N/A').strip()
        formatted.append(f"{name} ({role})")
    return "; ".join(formatted)

def get_xml_url(cik, accession_clean):
    base_url = "https://www.sec.gov/Archives/"
    
    # Path is: edgar/data/{CIK}/{CleanAccession}/primary_doc.xml
    xml_url = f"{base_url}edgar/data/{cik}/{accession_clean}/primary_doc.xml"
    
    return xml_url

def parse_formd(xml_url):
    response = requests.get(xml_url, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to access: {response.status_code}, url: {xml_url}")
        return None

def extract_form_d_leads(xml_content):
    tree = etree.fromstring(xml_content)
    
    # Get Firm-wide Contact Info
    date_filed = tree.xpath('//signatureDate/text()')[0]
    firm_name = tree.xpath('//primaryIssuer/entityName/text()')[0]
    cik = tree.xpath('//primaryIssuer/cik/text()')[0]
    date_val = tree.xpath('//dateOfFirstSale/value/text()')
    date_first_sale = date_val[0] if date_val else None
    investment_type = tree.xpath(".//investmentFundInfo/investmentFundType/text()")
    investment_type = investment_type[0] if investment_type else "N/A"
    is_equity = tree.xpath(".//typesOfSecuritiesOffered/isEquityType/text()")
    is_equity = is_equity[0] if is_equity else "false"
    phone = tree.xpath('//primaryIssuer/issuerPhoneNumber/text()')[0]
    money = tree.xpath('//offeringSalesAmounts/totalAmountSold/text()')[0]
    remaining_amt = tree.xpath("//offeringSalesAmounts/totalRemaining/text()")[0]

    # Get the "Related Persons" (Owners/Decision Makers)
    # This often returns a list if there are multiple owners
    owners = []
    for person in tree.xpath('//relatedPersonInfo'):
        first = person.xpath('.//firstName/text()')[0]
        last = person.xpath('.//lastName/text()')[0]
        title = person.xpath('.//relationship/text()')[0]
        owners.append({"name": f"{first} {last}", "role": title})
        
    return {
        "firm": firm_name,
        "cik": cik,
        "date_filed": date_filed,
        "phone": phone,
        "owners": format_owners(owners),
        "title": title,
        "date_first_sale": date_first_sale,
        "investment_type": investment_type,
        "is_equity": is_equity,
        "money_raised": money,
        "remaining_amount": remaining_amt
    }

if __name__ == "__main__":
  cik = '0001419945'
  accession_clean = '0001193125-15-163547'.replace('-', '')
  xml_url = get_xml_url(cik, accession_clean)
  xml_content = parse_formd(xml_url)
  formd = extract_form_d_leads(xml_content)
