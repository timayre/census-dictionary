#!/usr/bin/env python3

import bs4
import requests
import sys
import os
import json


def main(save='../census-dict-2021.json', exc='exceptions.json'):
    with open(exc) as f_in:
        exceptions = json.load(f_in)
    vars_info = load_index()
    for var_info in vars_info:
        varcode = var_info['code']
        multi = exceptions.get(varcode, {}).get('multitable')
        file = exceptions.get(varcode, {}).get('file')
        skip = exceptions.get(varcode, {}).get('skip')
        var_info['category_table'] = load_var_categories(var_info, multi=multi)
        if varcode in exceptions:
            var_info['category_table']['rows'] = format_rows(var_info, exceptions[varcode])
        if varcode not in exceptions or not(skip or file):
            try:
                var_info['categories'] = format_categories_simple(var_info['category_table'])
            except:
                print(f'skipping {varcode=}', file=sys.stderr)
        if file:
            with open(file) as f_in:
                var_info['categories'] = json.load(f_in)
        var_info.pop('category_table', None)
    census_dict = {'variables': vars_info}
    if save:
        with open(save, 'w') as f_out:
            json.dump(census_dict, f_out, indent=2)
    else:
        sys.stdout.write(json.dumps(census_dict, indent=2))


def load_index(save='htmls/varindex.html', overwrite=False):
    """Read or download index HTML file and return extracted variables table
    
    Loads file from `save` location if present, otherwise downloads from
    `https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-index`.
    """
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
    """Extract data from variables table, including hrefs"""
    soup = bs4.BeautifulSoup(index_page_text, 'html.parser')
    table = soup.find(class_='complex-table')
    rows = table.tbody.find_all('tr')[1:]
        ## Skip first row because header row is in `tbody` for some reason 
    vars_info = []
    for row in rows:
        vals = [elem.text.strip() for elem in row.find_all('td')]
        code, name, topic, release, new, *_ = vals + [''] 
            ## Add an extra item because the last column ('New') does not have a 
            ## `td` element when blank
        url = f'https://www.abs.gov.au{row.td.a["href"]}'
        var = {'code': code, 'name': name, 'topic': topic, 'release': release,
               'new_2021': 'New' in new, 'url': url}
        vars_info.append(var)
    return vars_info


def load_var_categories(var_info, save='htmls', overwrite=False, multi=False):
    """Read or download a variable's HTML file and return extracted categories table
    
    Loads file from `save` location if present, otherwise downloads from url
    in `var_info`.
    """
    save_file = os.path.join(save, f'{var_info["code"]}.html') if save else ''
    if overwrite or not os.path.exists(save_file):
        text = requests.get(var_info['url']).text
        if save:
            with open(save_file, 'w') as f_out:
                f_out.write(text)
    else:
        with open(save_file) as f_in:
            text = f_in.read()
    return parse_category_table(text, multi)


def parse_category_table(var_page_text, multi=False):
    soup = bs4.BeautifulSoup(var_page_text, 'html.parser')
    tables = soup.find_all(class_='complex-table')
    if not tables:
        print('No "complex-table" found.',
              file=sys.stderr)
    if not multi:
        if len(tables) > 1:
            print('More than one table found; using first one.',
                  file=sys.stderr)
        tables = tables[:1]
    headings = tables[0].thead.find_all('th') if tables[0].thead else []
    cats = []
    for table in tables:
        for row in table.tbody.find_all('tr'):
            vals = [elem.text.strip() for elem in row.find_all('td')]
            cats.append(vals)
    return {'head': [h.text.strip() for h in headings], 'rows': cats}


def format_categories_simple(category_table, check_headings=False):
    """Handle the normal two-column, rectangular table case"""
    if check_headings:
        headings = category_table['head']
        if headings[0] != 'Code' or \
                headings[1] not in ('Category', 'Categories'):
            raise Exception(f'Unexpected heading(s): {headings}')
        if len(headings) > 2:
            print(f'Additional columns found: {headings[2:]}',
                file=sys.stderr)
    cats = []
    for row in category_table['rows']:
        if len(row) < 2:
            raise Exception('less than 2 columns')
        cats.append({'code': row[0], 'category': replace_nonascii(row[1])})
    return cats


def format_rows(var_info, var_except):
    """Simplify more complex tables and special cases
    
    ... to allow tham to be handled by `format_categories_simple`."""
    rows = var_info['category_table']['rows']
    if var_except.get('indented'):
        rows = format_rows_indented(rows)
    if var_except.get('hyphen_sep'):
        rows = format_rows_hyphensep(rows)
    if var_except.get('subheadings'):
        rows = format_rows_subheadings(rows)
    if var_except.get('multilevel'):
        rows = format_rows_multilev(rows)
    if var_except.get('numeric'):
        rows = expand_numeric(rows, var_except)
    return rows


def format_rows_indented(rows):
    return [[c for c in row if c] for row in rows]


def format_rows_hyphensep(rows):
    return [r[0].split(' - ', 1) for r in rows if r[0] != 'Supplementary Codes']


def format_rows_subheadings(rows):
    return [r for r in rows if len(r) >= 2]


def format_rows_multilev(rows):
    maxchars = max(len(r[0]) for r in rows if r)
    return [r for r in rows if r and len(r[0]) == maxchars] 


def expand_numeric(rows, conf):
    out_rows = []
    for row in rows:
        if row[0] == conf.get('code'):
            digits = conf.get('digits')
            singular = conf.get('singular')
            plural = conf.get('plural')
            for i in range(conf.get('from'), conf.get('to')+1):
                code = f'{i:0>{digits}}'
                desc = f'{i} {singular if i==1 else plural}'.strip()
                out_rows.append([code, desc])
        else:
            out_rows.append(row)
    return out_rows


def replace_nonascii(string, check=False):
    """Replace selected characters
    
    - U+2013 = En Dash => `-`
    - U+2019 = Right Single Quotation Mark => `'`
    - U+00A0 = No-Break Space => ` ` or remove
    
    `check=True` will throw error if there are additional non-ascii characters
    remaining
    """
    out = string.replace('\u2013', '-')\
                .replace('\u2019', "'")\
                .replace(' \u00a0', ' ')\
                .replace('\u00a0 ', ' ')\
                .replace('\u00a0', ' ')
    if check:
        out.encode('ascii')  # will throw exception
    return out


if __name__ == '__main__':
    main()

