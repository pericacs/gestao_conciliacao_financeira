from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from unidecode import unidecode
from datetime import datetime
from dotenv import load_dotenv
from .forms import CarregarCSVForm
import psycopg2
import os
import pandas as pd
import json


@csrf_exempt
def carregar_csv(request):
    if request.method == 'POST':
        form = CarregarCSVForm(request.POST, request.FILES)
        if form.is_valid():
           # Salvar o arquivo temporariamente em disco            
            # csv_file = request.FILES['arquivo_csv']
            arquivo_csv = form.cleaned_data['arquivo_csv']
            pasta_destino = "C:\\Estudo\\gestao_conciliacao_financeira\\arquivo"
            if not os.path.exists(pasta_destino):
                os.makedirs(pasta_destino)
            caminho_arquivo = os.path.join(pasta_destino, arquivo_csv.name)                
            with open(caminho_arquivo, 'wb+') as destino:
                for chunk in arquivo_csv.chunks():
                    destino.write(chunk)
            jsonFilePath = excel_to_json_francesinha(caminho_arquivo)
            importar_json_francesinha(jsonFilePath)
            # Faça o que for necessário com o arquivo            
            return JsonResponse({'message': 'Arquivo processado com sucesso', 'jsonFilePath': jsonFilePath})
        else:
            return JsonResponse({'error': 'Formulário inválido'}, status=400)
    else:
        form = CarregarCSVForm()
        return render(request, 'conciliacao/pages/carregar_csv.html', {'form': form})
    
def converter_valor_monetario_francesinha(valor_string):
     # Remover todos os pontos de milhar
    valor_string = valor_string.replace('.', '')    
    # Remover o símbolo 'R$' e substituir ',' por '.' 
    valor_string = valor_string.replace('R$', '').replace(',', '.')
    
    # Remover todos os espaços em branco antes de tentar converter para float
    valor_string = valor_string.strip().replace(' ', '')

    valor_string = valor_string.replace('%', '')
    
    # Se o valor estiver vazio, retornar zero
    if valor_string == '':
        return 0.0
    
    # Se o valor contiver apenas um sinal de negativo, retornar zero
    if valor_string == '-':
        return 0.0
    
    # Se não for vazio, converter para float
    valor_float = float(valor_string)
    
    return valor_float
   

def excel_to_json_francesinha(csvFilePath):
    if os.path.exists(csvFilePath):
        jsonArray = []

         # Carregar o arquivo Excel
        df = pd.read_csv(csvFilePath, skiprows=0, delimiter=';', encoding='latin1')  # Começa a ler a partir da 5ª linha

        # Converter o DataFrame para uma lista de dicionários
        data = df.to_dict(orient='records')

        # Converter caracteres acentuados para ASCII
        data = [{unidecode(str(key)): unidecode(str(value)) for key, value in row.items()} for row in data]

        # Adicionar os dicionários à lista jsonArray
        jsonArray.extend(data)

        # Converter o jsonArray para uma string JSON e escrever no arquivo
        jsonFilePath = csvFilePath.replace('.csv', '.json')
        with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
            jsonString = json.dumps(jsonArray, indent=4)
            jsonf.write(jsonString)
        
        # Retornar o nome do arquivo gerado
        return os.path.basename(jsonFilePath)
    else:
        return "Arquivo CSV não encontrado"        

# Create your views here.
def importar_json_francesinha(jsonFilePath):
    # carregar arquivo cvs, converter para json 
    # jsonFilePath = excel_to_json_francesinha(csvFilePath)

    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()

    # Acessar as variáveis de ambiente
    dbname = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')

    # Conectar ao banco de dados usando as variáveis de ambiente
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

    data_atual = datetime.now()
    data_formatada = data_atual.strftime("%m/%d/%Y %H:%M:%S")
    
    # Dados JSON
    with open(jsonFilePath) as file:
        data = json.load(file)


    # Conectar-se ao banco de dados    
    cursor = conn.cursor()
    contador = 0
    for row in data:
        
        # Converte a data para o formato correto (YYYY-MM-DD)
        if row['DATA REFERENCIA'] == '-':
            dt_referencia = None
        else:
            dt_referencia = datetime.strptime(row['DATA REFERENCIA'], "%d/%m/%Y").date()
        
        if row['DATA EMISSAO'] == '-':
            dt_emissao = None
        else:
            dt_emissao = datetime.strptime(row['DATA EMISSAO'], "%d/%m/%Y").date()
        
        if row['DATA VCTO'] == '-':
            dt_vencimento = None
        else:
            dt_vencimento = datetime.strptime(row['DATA VCTO'], "%d/%m/%Y").date()
        
        if row['DATA LANCAMENTO CONTABIL'] == '-':
            dt_lancamento_contabil = None
        else:
            dt_lancamento_contabil = datetime.strptime(row['DATA LANCAMENTO CONTABIL'], "%d/%m/%Y").date()      

        if row['DATA BX. OPERACIONAL'] == '-':
            dt_bx_operacional = None
        else:
            dt_bx_operacional = datetime.strptime(row['DATA BX. OPERACIONAL'], "%d/%m/%Y").date()   
 
        # Converte os valores monetários para o formato numeric(10,2)
        row['VALOR TITULO'] = converter_valor_monetario_francesinha(row['VALOR TITULO'])
        row['VALOR DESCONTO'] = converter_valor_monetario_francesinha(row['VALOR DESCONTO'])
        row['VALOR ABATIMENTO'] = converter_valor_monetario_francesinha(row['VALOR ABATIMENTO'])
        row['VALOR ENCARGO'] = converter_valor_monetario_francesinha(row['VALOR ENCARGO'])
        row['VALOR MORA'] = converter_valor_monetario_francesinha(row['VALOR MORA'])
        row['VALOR MULTA'] = converter_valor_monetario_francesinha(row['VALOR MULTA'])      
        row['VALOR ATU'] = converter_valor_monetario_francesinha(row['VALOR ATU'])        
        row['VALOR IOF'] = converter_valor_monetario_francesinha(row['VALOR IOF'])    
        row['VALOR TARIFA'] = converter_valor_monetario_francesinha(row['VALOR TARIFA'])      
        row['VALOR LANCAMENTO CONTA'] = converter_valor_monetario_francesinha(row['VALOR LANCAMENTO CONTA'])        
        row['VALOR LANCADO CC'] = converter_valor_monetario_francesinha(row['VALOR LANCADO CC'])
        row['VALOR BX. OPERACIONAL'] = converter_valor_monetario_francesinha(row['VALOR BX. OPERACIONAL'])        

        insert_query = '''
        INSERT INTO webhook_arbi_francesinha 
        (
            sacado, nossonumero, historico, data_referencia, data_emissao, data_vcto, valor_titulo,	
            valor_desconto,	valor_abatimento, valor_encargo, valor_mora, valor_multa, valor_atu,
            valor_iof, valor_tarifa, valor_lancamento_conta, data_lancamento_contabil,	agencia_lancamento,
            conta_lancamento, nro_movimento, historico_lancado_cc, valor_lancado_cc, data_bx_operacional, valor_bx_operacional
        )
        VALUES (  
            %s, -- SACADO            
            %s, -- NOSSO NUMERO
            %s, -- HISTORICO
            %s, -- DATA REFERENCIA
            %s, -- DATA EMISSAO
            %s, -- DATA VCTO
            %s, -- VALOR TITULO
            %s, -- VALOR DESCONTO
            %s, -- VALOR ABATIMENTO
            %s, -- VALOR ENCARGO
            %s, -- VALOR MORA
            %s, -- VALOR MULTA
            %s, -- VALOR ATU
            %s, -- VALOR IOF
            %s, -- VALOR TARIFA
            %s, -- VALOR LANCAMENTO CONTA
            %s, -- DATA LANCAMENTO CONTABIL
            %s, -- AGENCIA LANCAMENTO
            %s, -- CONTA LANCAMENTO
            %s, -- NRO MOVIMENTO
            %s, -- HISTORICO LANCADO CC
            %s, -- VALOR LANCADO CC
            %s, -- DATA BX. OPERACIONAL
            %s -- VALOR BX. OPERACIONAL    
        );
        '''
        # Montando a tupla de valores
        values = (                    
            row['SACADO'],             
            row['NOSSO NUMERO'], 
            row['HISTORICO'], 
            dt_referencia,             
            dt_emissao,  
            dt_vencimento, 
            row['VALOR TITULO'], 
            row['VALOR DESCONTO'], 
            row['VALOR ABATIMENTO'],
            row['VALOR ENCARGO'], 
            row['VALOR MORA'], 
            row['VALOR MULTA'],
            row['VALOR ATU'], 
            row['VALOR IOF'], 
            row['VALOR TARIFA'],
            row['VALOR LANCAMENTO CONTA'],
            dt_lancamento_contabil,             
            row['AGENCIA LANCAMENTO'], 
            row['CONTA LANCAMENTO'],
            row['NRO MOVIMENTO'], 
            row['HISTORICO LANCADO CC'], 
            row['VALOR LANCADO CC'], 
            dt_bx_operacional, 
            row['VALOR BX. OPERACIONAL']   
        )
        contador += 1
        print(contador)     
        cursor.execute(insert_query, values)
        conn.commit()

    # Fechar a conexão com o banco de dados
    cursor.close()
    conn.close()


