#!/usr/bin/env python3

import bs4
import requests
import sys
import os
import json


def main(save='../census-dict-2021.json'):
    ## Excluding variable pages that are not in the usual format
    exclusions = {'ANCP', 'ANC1P', 'ANC2P',
                  'BPLP', 'BPFP', 'BPMP',
                  'CDCF', 'CDCUF', 'CDSF', 'CNDCF',
                  'DTWP',
                  'EETP',
                  'FIDF',
                  'FMCF',
                  'FMGF',
                  'HCFMD', 'HCFMF',
                  'HEAP',
                  'HHCD',
                  'HIDD',
                  'INDP',
                  'LANP',
                  'OCC06P', 'OCCP',
                  'POWP',
                  'QALFP', 'QALLP',
                  'RELP',
                  'RLGP', 'RLHP', 'RPIP',
                  'STRD'}
    vars_info = load_index()
    for var_info in vars_info:
        if var_info['code'] not in exclusions:
            var_info['categories'] = load_var_categories(var_info)
    census_dict = {'variables': vars_info}
    if save:
        with open(save, 'w') as f_out:
            json.dump(census_dict, f_out, indent=2)
    else:
        sys.stdout.write(json.dumps(census_dict, indent=2))


def load_index(save='htmls/varindex.html', overwrite=False):
    ## Note the 'download as csv' option on the page does not include the 
    ## linked urls.
    ## They look like they are probably derivable from the other fields,
    ## but easier just to pull them from the html.
    if overwrite or not os.path.exists(save):
        url = 'https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-index'
        text = requests.get(url).text
        if save:
            with open(save, 'w') as f_out:
                f_out.write(text)
    else:
        with open(save) as f_in:
            text = f_in.read()
    return parse_index(text)


def parse_index(index_page_text):
    soup = bs4.BeautifulSoup(index_page_text, 'html.parser')
    table = soup.find(class_='complex-table')
    rows = table.tbody.find_all('tr')[1:]
        ## Skip first row because header row is in `tbody` for some reason 
    vars_info = []
    for row in rows:
        vals = [elem.text.strip() for elem in row.find_all('td')]
        code, name, topic, release, new, *_ = vals + [''] 
            ## Add an extra item because the last column ('New') does not have a 
            ## `td` element if blank
        url = f'https://www.abs.gov.au{row.td.a["href"]}'
        var = {'code': code, 'name': name, 'topic': topic, 'release': release,
               'new_2021': 'New' in new, 'url': url}
        vars_info.append(var)
    return vars_info


def load_var_categories(var_info, save='htmls', overwrite=False):
    save_file = os.path.join(save, f'{var_info["code"]}.html') if save else ''
    if overwrite or not os.path.exists(save_file):
        text = requests.get(var_info['url']).text
        if save:
            with open(save_file, 'w') as f_out:
                f_out.write(text)
    else:
        with open(save_file) as f_in:
            text = f_in.read()
    return parse_categories(text)


def parse_categories(var_page_text):
    soup = bs4.BeautifulSoup(var_page_text, 'html.parser')
    tables = soup.find_all(class_='complex-table')
    if not tables:
        print('No "complex-table" found.',
              file=sys.stderr)
    if len(tables) > 1:
        print('More than one table found; using first one.',
              file=sys.stderr)
    table = tables[0]
    headings = table.thead.find_all('th')
    if headings[0].text.strip() != 'Code' or \
            headings[1].text.strip() not in ('Category', 'Categories'):
        raise Exception(f'Unexpected heading(s): {headings}')
    if len(headings) > 2:
        print(f'Additional columns found: {headings[2:]}',
              file=sys.stderr)
    cats = []
    for row in table.tbody.find_all('tr'):
        vals = [elem.text for elem in row.find_all('td')]
        cats.append({'code': vals[0], 'category': vals[1]})
    return cats


if __name__ == '__main__':
    main()

