import os
import re
import numpy as np
import pandas as pd
from unicodedata import lookup


def flag(letters, country_codes):
    """
    Betölt egy zászló piktogramot alpha2/3 országkódhoz tartozóan
    """
    if pd.isna(letters) or (letters.lower() not in country_codes):
        return ''
    l_0 = lookup(f'REGIONAL INDICATOR SYMBOL LETTER {letters[0]}')
    l_1 = lookup(f'REGIONAL INDICATOR SYMBOL LETTER {letters[1]}')
    return l_0 + l_1


def get_poverty():
    """
    Betölti és megtisztítja a poverty adathalmazt
    """
    # Adatok előkészítése
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Országok adatainak beolvasása
    country = pd.read_csv(
        os.path.join(current_dir, '../../data/PovStatsCountry.csv'),
        na_values='',
        keep_default_na=False
    )
    country['is_country'] = country['Region'].notna()

    # Az adathalmaz rekordjaihoz a zászló képek hozzárendelése
    country_codes = country[country['is_country']]['2-alpha code'].dropna().str.lower().tolist()
    country['flag'] = [flag(code, country_codes) for code in country['2-alpha code']]

    # Szegénységi adatok
    data = pd.read_csv(os.path.join(current_dir, '../../data/PovStatsData.csv'))
    data = data.drop('Unnamed: 50', axis=1)

    # Kimutatás
    id_vars = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
    data_melt = pd.melt(data, id_vars=id_vars, var_name='year').dropna(subset=['value'])
    data_melt.loc[:, 'year'] = data_melt.loc[:, 'year'].astype(int)
    data_melt.sample(10)

    data_pivot = data_melt.pivot(
        index=['Country Name', 'Country Code', 'year'],
        columns='Indicator Name',
        values='value'
    ).reset_index()

    # Adatok összefűzése
    poverty = pd.merge(data_pivot, country, left_on='Country Code', right_on='Country Code', how='left')

    # Mivel a magas bevételű országok NaN-ként szerepelnek ezeket fel kell tölteni manuálisan
    poverty['is_country'] = [x if x != np.nan else False for x in poverty['is_country']]

    return poverty


def get_income_share_df():
    """
    Betölti és megtisztítja a szegénységi adathalmazt
    """
    poverty = get_poverty()  # Adathalmaz betöltése
    income_share_df = poverty.filter(regex='Country Name|^year$|Income share.*?20').dropna()
    income_share_df = income_share_df.rename(columns={
        'Income share held by lowest 20%': '1 Income share held by lowest 20%',
        'Income share held by second 20%': '2 Income share held by second 20%',
        'Income share held by third 20%': '3 Income share held by third 20%',
        'Income share held by fourth 20%': '4 Income share held by fourth 20%',
        'Income share held by highest 20%': '5 Income share held by highest 20%'
    }).sort_index(axis=1)
    income_share_df.columns = [re.sub(r'\d Income share held by ', '', col).title() for col in income_share_df.columns]
    return income_share_df


if __name__ == '__main__':
    result = get_poverty()
    print(result)
