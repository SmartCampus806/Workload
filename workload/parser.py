import pandas as pd
import warnings
import pprint
import xlrd
import openpyxl

warnings.simplefilter(action="ignore", category=UserWarning)
pd.set_option('future.no_silent_downcasting', True)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

mapping_dict = {"нагр.": "нагрузка",
                "нагр": "нагрузка",
                "гр": "групп",
                "Практичзанятия": "Практические занятия",
                "Лаборатработы": "Лабораторные работы",
                "Курсработа": "Курсовая работа",
                "Курспроект": "Курсовой проект",
                "Экзам": "Экзамен"}


def clean_text(text):
    if isinstance(text, str):
        return text.replace('\n', '')
    return text


def find_occurrences_index_by_word(df, word):
    found = []
    for index, row in df.iterrows():
        if row.astype(str).str.contains(word).any():
            found.append((index, df.iloc[index, 0]))
    return found


def rename_col_and_contribute_info(found, name_of_col, df):
    found.append((df.shape[0], found[-1][1]))
    for num in range(0, len(found) - 1):
        i = int(found[num][0])
        j = int(found[num + 1][0])
        df.loc[i:j, name_of_col] = found[num][1]
    return df


def delete_row_by_occurrence(df, word, found):
    for _ in range(len(found) + 1):
        df = df[~df["Название"].str.contains(word)]
    return df


def find_occurrences_index_volume(df):
    found = []
    for index, row in df.iterrows():
        if row.astype(str).str.contains("внебюджетное").any():
            if row.astype(str).str.contains("РАСЧЕТ ОБЪЕМА").any():
                found.append((index, "внебюджетное", "РАСЧЕТ ОБЪЕМА"))
            else:
                found.append((index, "внебюджетное"))

        elif row.astype(str).str.contains("бюджетное").any():
            if row.astype(str).str.contains("РАСЧЕТ ОБЪЕМА").any():
                found.append((index, "бюджетное", "РАСЧЕТ ОБЪЕМА"))
            else:
                found.append((index, "бюджетное"))

    return found


def delete_occurrences_index_volume(df):
    for index, row in df.iterrows():

        if row.astype(str).str.contains("РАСЧЕТ ОБЪЕМА").any() and not(row.astype(str).str.contains("внебюджетное финансирование").any()):
            continue

        elif row.astype(str).str.contains("РАСЧЕТ ОБЪЕМА").any() and row.astype(str).str.contains("внебюджетное финансирование").any():
            i = index - 1
            j = index + 6
            for ind in range(i, j+1):
                df.drop(ind, inplace=True)

        elif (row.astype(str).str.contains("бюджетное финансирование").any() and
              not (row.astype(str).str.contains("РАСЧЕТ ОБЪЕМА").any())):
            i = index
            j = index + 2
            for ind in range(i, j + 1):
                df.drop(ind, inplace=True)

    return df


def find_discipline_indexes(df):
    regex_pattern = r'(.*-.*-2.)|Нагрузка каф\. 806'
    found = []
    for index, row in df.iterrows():
        if not(row.astype(str).str.contains(regex_pattern, regex=True).any()):
            found.append((index, df.iloc[index, 0]))
            df.iloc[index, 0] = "del"
    return found



def main():
    df = pd.read_excel("D:\Code\Meeting\workload\input.xls")
    df = df.map(clean_text).dropna(axis=1, how='all')

    found = find_occurrences_index_volume(df)
    df = rename_col_and_contribute_info(found, "Тип финансирования", df)
    df = delete_occurrences_index_volume(df)
    df = df.dropna(axis=1, how='all')
    df = df.reset_index(drop=True)

    word = "Курс"
    df = df.loc[find_occurrences_index_by_word(df, word)[0][0]:]

    df = df.replace(mapping_dict)
    df.iloc[0] = df.iloc[0].ffill()
    second_row_filled = df.iloc[1].fillna('')
    df.iloc[0] = df.iloc[0] + ' ' + second_row_filled
    df = df.reset_index(drop=True)
    df = df.drop(index=1)

    df.columns = df.iloc[0]
    df = df[1:]
    df = df.reset_index(drop=True)

    df.rename(columns={df.columns[0]: 'Название', df.columns[-1]: 'Финансирование'}, inplace=True)
    df = df.dropna(axis=1, how='all')
    df = df[~df["Название"].str.contains("Итого по кафедре")]
    df = df.reset_index(drop=True)
    df.loc[df['Название'].str.contains('Общая нагрузка'), 'Название'] += ' (форма обучения)'

    for word in ['Факультет', 'форма обучения', 'семестр']:
        found = find_occurrences_index_by_word(df, word)
        df = rename_col_and_contribute_info(found, word, df)
        df = delete_row_by_occurrence(df, word, found)
        df = df.reset_index(drop=True)

    found = find_discipline_indexes(df)
    df = rename_col_and_contribute_info(found, "Название предмета", df)
    df = delete_row_by_occurrence(df, "del", found)
    df = df.reset_index(drop=True)

    df = df.fillna(0)

    df.to_excel("itog.xlsx")
    print(df.fill)


if __name__ == "__main__":
    main()