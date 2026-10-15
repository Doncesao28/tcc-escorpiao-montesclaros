import re
import pandas as pd


def clean_bairro_name(bairro):
  if not isinstance(bairro, str) or bairro == 'nan':
    return None
  b = bairro.strip().upper()
  b = re.sub(r'\s+', ' ', b)

  replacements = {
      'SANTOS REIS I': 'SANTOS REIS',
      'SÃO JUDAS TADEU I': 'SÃO JUDAS',
      'SÃO JUDAS TADEU': 'SÃO JUDAS',
      'MAJOR PRATES I': 'MAJOR PRATES',
      'MAJOR PRATES II': 'MAJOR PRATES',
      'DELFINO MAGALHAES': 'DELFINO MAGALHÃES',
      'NOVO DELFINO I': 'NOVO DELFINO',
      'INDEPENDENCIA': 'INDEPENDÊNCIA',
      'MARACANA': 'MARACANÃ',
      'JARDIM ELDORADO I': 'JARDIM ELDORADO',
      'VILA ATLANTIDA': 'VILA ATLÂNTIDA',
      'SÃO GERALDO I': 'SÃO GERALDO',
      'SÃO GERALDO II': 'SÃO GERALDO',
  }
  return replacements.get(b, b)


def extract_all_data(file_path, year):
  xls = pd.ExcelFile(file_path)
  all_rows = []

  months_map = {
      'Janeiro': 1,
      'Fevereiro': 2,
      'Março': 3,
      'Abril': 4,
      'Maio': 5,
      'Junho': 6,
      'Julho': 7,
      'Agosto': 8,
      'Setembro': 9,
      'Outubro': 10,
      'Novembro': 11,
      'Dezembro': 12,
  }

  for sheet in xls.sheet_names:
    month_num = next(
        (val for name, val in months_map.items() if name.lower() in sheet.lower()),
        None,
    )
    df = pd.read_excel(xls, sheet_name=sheet)

    header_row = None
    for i in range(min(10, len(df))):
      row_vals = [str(x) for x in df.iloc[i].values]
      if any('Bairro' in v for v in row_vals):
        header_row = i
        break

    if header_row is not None:
      data_df = df.iloc[header_row + 1 :].copy()
      data_df.columns = ['Bairro_Origem', 'Acidentes']
      data_df['Acidentes'] = pd.to_numeric(
          data_df['Acidentes'], errors='coerce'
      ).fillna(0)

      for _, row in data_df.iterrows():
        b_orig = str(row['Bairro_Origem']).strip()
        acidentes = int(row['Acidentes'])

        if (
            'TOTAL' in b_orig.upper()
            or b_orig.lower() == 'nan'
            or acidentes == 0
        ):
          continue

        b_limpo = clean_bairro_name(b_orig)

        all_rows.append({
            'Ano': year,
            'Mês_Num': month_num,
            'Aba_Mês': sheet,
            'Bairro_Original': b_orig,
            'Bairro_Tratado': b_limpo,
            'Acidentes': acidentes,
        })

  return pd.DataFrame(all_rows)


if __name__ == '__main__':
  print('Processando planilhas de 2024 e 2025...')
  df_2024 = extract_all_data(
      'CONSOLIDADO DE CONTROLE DE ESCORPIÃO MENSAL -2024.xlsx', 2024
  )
  df_2025 = extract_all_data(
      'CONSOLIDADO DE CONTROLE DE ESCORPIÃO MENSAL -2025.xlsx', 2025
  )

  df_consolidado = pd.concat([df_2024, df_2025], ignore_index=True)

  output_csv = 'Consolidado_Escorpiao_Montes_Claros_2024_2025.csv'
  df_consolidado.to_csv(output_csv, index=False, encoding='utf-8-sig')

  print('==================================================')
  print(f'SUCESSO! Arquivo criado: {output_csv}')
  print(f'Total de registros extraídos: {len(df_consolidado)}')
  print('==================================================')