import os

def organizar_titulos_em_tabela(nome_arquivo_entrada="Titulos Comparados.txt"):
    """
    Lê um arquivo de títulos, extrai pares de "Título My YouTube Library" e 
    "Título Original do YouTube" e os formata em uma tabela de texto.

    A estrutura esperada no arquivo de entrada (após o cabeçalho) é:
    Linha contendo "Título My YouTube Library"
    Linha contendo apenas um caractere de tabulação '\t'
    Linha em branco
    Linha contendo "Título Original do YouTube"
    Linha em branco (opcional, antes do próximo bloco)
    """
    pares_de_titulos = []
    
    # Verifica se o arquivo de entrada existe
    if not os.path.exists(nome_arquivo_entrada):
        print(f"Erro: O arquivo '{nome_arquivo_entrada}' não foi encontrado.")
        print(f"Por favor, certifique-se de que o arquivo está no mesmo diretório que o script ou forneça o caminho completo.")
        return None

    try:
        with open(nome_arquivo_entrada, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return None

    # Processa as linhas para extrair os títulos relevantes
    titulos_processados = []
    for linha in linhas:
        linha_strip = linha.strip()
        # Adiciona a linha se não estiver vazia e não for apenas um tab
        if linha_strip and linha_strip != '\t':
            titulos_processados.append(linha_strip)

    # O cabeçalho no arquivo "Titulos Comparados.txt" tem um formato específico
    # **My YouTube Library
    # Título Original do YouTube**
    # Vamos encontrar o início dos dados reais.
    # Os dados começam após "Título Original do YouTube**".
    try:
        # Encontra o índice da linha que marca o fim do cabeçalho
        # O cabeçalho pode variar, mas os dados reais começam com o primeiro título da biblioteca.
        # A heurística usada anteriormente de pular os 2 primeiros é baseada na estrutura filtrada.
        # Se "Titulos Comparados.txt" sempre tiver "**My YouTube Library" e "Título Original do YouTube**" como as duas primeiras linhas *relevantes*,
        # então podemos pular essas duas.
        if titulos_processados[0].startswith("**My YouTube Library") and \
           titulos_processados[1] == "Título Original do YouTube**":
            dados_reais_titulos = titulos_processados[2:]
        else:
            # Se o cabeçalho não for encontrado como esperado, tenta processar tudo.
            # Isso pode precisar de ajuste se o cabeçalho for diferente.
            print("Aviso: Cabeçalho esperado não encontrado. Tentando processar todas as linhas como dados.")
            dados_reais_titulos = titulos_processados
            if len(dados_reais_titulos) % 2 != 0 and dados_reais_titulos: # Se for ímpar e não vazio, remove o último para formar pares
                print("Aviso: Número ímpar de títulos após filtragem e sem cabeçalho claro. O último título pode ser ignorado.")
                dados_reais_titulos.pop()


    except IndexError:
        print("Erro: Arquivo parece estar vazio ou com formato inesperado após a filtragem inicial.")
        return None

    # Agrupa os títulos em pares
    for i in range(0, len(dados_reais_titulos), 2):
        titulo_myl = dados_reais_titulos[i]
        if i + 1 < len(dados_reais_titulos):
            titulo_yt = dados_reais_titulos[i+1]
            pares_de_titulos.append((titulo_myl, titulo_yt))
        else:
            # Caso haja um título da My YouTube Library sem par (última linha ímpar)
            pares_de_titulos.append((titulo_myl, "N/A - Título original não encontrado"))
            print(f"Aviso: Título da My YouTube Library '{titulo_myl}' não possui par de título original do YouTube.")

    if not pares_de_titulos:
        print("Nenhum par de títulos foi extraído. Verifique o formato do arquivo.")
        return None

    # Define os cabeçalhos das colunas
    cabecalho_col1 = "Título My YouTube Library"
    cabecalho_col2 = "Título Original do YouTube"

    # Calcula a largura máxima para a primeira coluna (Título My YouTube Library)
    # Inclui o cabeçalho no cálculo para garantir que ele também caiba
    try:
        max_len_col1 = max(len(par[0]) for par in pares_de_titulos)
        max_len_col1 = max(max_len_col1, len(cabecalho_col1))
    except ValueError: # Ocorre se pares_de_titulos estiver vazio, mas já verificamos
        max_len_col1 = len(cabecalho_col1)


    # Calcula a largura máxima para a segunda coluna (Título Original do YouTube)
    # Inclui o cabeçalho no cálculo
    try:
        max_len_col2 = max(len(par[1]) for par in pares_de_titulos if par[1])
        max_len_col2 = max(max_len_col2, len(cabecalho_col2))
    except ValueError: # Ocorre se todos os par[1] forem None ou vazios
        max_len_col2 = len(cabecalho_col2)


    # Monta a tabela formatada
    tabela_formatada = []
    
    # Linha de cabeçalho
    linha_h = f"{cabecalho_col1.ljust(max_len_col1)} | {cabecalho_col2.ljust(max_len_col2)}"
    tabela_formatada.append(linha_h)
    
    # Linha separadora
    linha_s = "-" * max_len_col1 + " | " + "-" * max_len_col2
    tabela_formatada.append(linha_s)

    # Linhas de dados
    for titulo_myl, titulo_yt in pares_de_titulos:
        linha_d = f"{titulo_myl.ljust(max_len_col1)} | {(titulo_yt if titulo_yt else '').ljust(max_len_col2)}"
        tabela_formatada.append(linha_d)
    
    return "\n".join(tabela_formatada)

if __name__ == '__main__':
    # Nome do arquivo de entrada (pode ser alterado se necessário)
    # Certifique-se de que "Titulos Comparados.txt" está no mesmo diretório que o script
    # ou forneça o caminho completo para o arquivo.
    arquivo_entrada = "Titulos Comparados.txt" 
    
    tabela = organizar_titulos_em_tabela(arquivo_entrada)
    
    if tabela:
        print("\nTabela de Títulos Organizados:\n")
        print(tabela)
        
        # Sugestão para salvar em arquivo:
        # nome_arquivo_saida = "Titulos_Organizados.txt"
        # with open(nome_arquivo_saida, 'w', encoding='utf-8') as f_out:
        #     f_out.write(tabela)
        # print(f"\n\nA tabela também foi salva em '{nome_arquivo_saida}'")

