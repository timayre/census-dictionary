
# Australian Census Dictionary, 2021

This repo contains JSON-formatted metadata based on the 2021 [*Census of Population and Housing: Census dictionary*][census_dict_home], published by the Australian Bureau of Statistics (ABS).

This information has been scraped from the ABS website. It is based on ABS material [published under a Creative Commons Attribution licence][abs_copyright].

## JSON file

The metadata for all variables is contained in the file [`census-dict-2021.json`](census-dict-2021.json) (771 kB). (The code used to generate this can be found under the [`project`](./project/) directory.)

### Example

The JSON version of the metadata for the variable "Australian citizenship" (`CITP`) is shown below, followed by a screenshot of the HTML page it is based on (the [*Variables index*][var_index] page is also used to derive some of the information).

```json
{
    "code": "CITP",
    "name": "Australian citizenship",
    "topic": "Cultural diversity",
    "release": "June 2022",
    "new_2021": false,
    "url": "https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/cultural-diversity/australian-citizenship-citp",
    "categories": [
        {
            "code": "1",
            "category": "Australian citizen"
        },
        {
            "code": "2",
            "category": "Not an Australian citizen"
        },
        {
            "code": "&",
            "category": "Not stated"
        },
        {
            "code": "V",
            "category": "Overseas visitor"
        }
    ]
}
```

Image of the [*Australian citizenship (CITP)*][citp] HTML page:

![](project/img/citp.zoom.80pct.border.png)

(The release date "15/10/2021" on the webpage refers that of the Census Dictionary, whereas "June 2022" above refers to the release of the actual Census results for CITP.)

## Caveats and modifications

- No categories are included for:
    - geographic variables ([`PURP`][purp], [`PUR1P`][pur1p], [`PUR5P`][pur5p] and [`POWP`][powp]) (the Census Dictionary only includes the supplementary codes for these anyway);
    - [`MRED`][mred] and [`RNTD`][rntd], which take single-dollar values, up to $9,999.
- Where a range of numeric (integer) values were specified as a single row in the source, these are expanded to list the individual values separately (with the exceptions of `MRED` and `RNTD` as specified above). For example, the source table for [`AGEP`][agep] consists of a single row where "Code" is "000-115" and "Category" is "0 to 115 years of age singly"; in the JSON this is represented in the `categories` array as 116 separate elements ("0 years of age", "1 year of age", etc.).
- Where a variable's classification includes multiple levels or nesting, only the lowest level is included (e.g.: for [`INDP`][indp], only 4-digit codes/categories ("classes") are included; for [`QALLP`][qallp], only 3-digit codes/categories ("detailed levels") are included).
- For [`CDCF`][cdcf], [`CDCUF`][cdcuf], [`CDSF`][cdsf], [`CNDCF`][cndcf], [`FIDF`][fidf] and [`HIDD`][hidd], subheadings have been incorporated into individual category labels. For other variables, any subheadings have been ignored, as they are generally redundant.
- A handful of different non-ASCII characters were present in category labels. As these have reasonable ASCII substitutes and the source is not particularly consistent in its use of these characters, even between categories the same variable ([`TYPP`][typp], for example), they have been replaced or removed as follows:
    - `’` (Right Single Quotation Mark, U+2019) has been replaced by `'` (Apostrophe, U+0027)
    - `–` (En Dash, U+2013) has been replaced by `-` (Hyphen-Minus, U+002D)
    - No-Break Space (U+00A0) has been replaced by Space (U+0020), except where there is an adjacent Space, in which case it is removed 



[census_dict_home]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021

[citp]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/cultural-diversity/australian-citizenship-citp

[var_index]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-index

[abs_copyright]: https://www.abs.gov.au/website-privacy-copyright-and-disclaimer#copyright-and-creative-commons

[purp]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/location/place-usual-residence-purp

[pur1p]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/location/place-usual-residence-one-year-ago-pur1p

[pur5p]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/location/place-usual-residence-five-years-ago-pur5p

[powp]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/location/place-work-powp

[qallp]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/education-and-training/non-school-qualification-level-education-qallp

[indp]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/income-and-work/industry-employment-indp

[mred]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/housing/mortgage-repayments-monthly-dollar-values-mred

[rntd]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/housing/rent-weekly-dollar-values-rntd

[agep]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/population/age-agep

[typp]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/education-and-training/type-educational-institution-attending-typp

[cdcf]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/household-and-families/count-dependent-children-family-cdcf

[cdcuf]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/household-and-families/count-dependent-children-under-15-family-cdcuf

[cdsf]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/household-and-families/count-dependent-students-15-24-years-family-cdsf

[cndcf]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/household-and-families/count-non-dependent-children-family-cndcf

[fidf]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/income-and-work/family-income-derivation-indicator-fidf

[hidd]: https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/income-and-work/household-income-derivation-indicator-hidd


