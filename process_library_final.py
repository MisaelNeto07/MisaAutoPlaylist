# --- START OF FILE process_library_final.py ---

import re
import json
import time
import os
from datetime import datetime
import unicodedata
import hashlib 
import subprocess # Para yt-dlp

import google.generativeai as genai

# --- Configuração da API da LLM ---
# SUBSTITUA "SUA_CHAVE_API_VALIDA_AQUI" PELA SUA CHAVE REAL E FUNCIONAL
GOOGLE_API_KEY = "AIzaSyB5lxwv_63vAN0HEYQaRrc2C918XWbjABM" # <<<< COLOQUE SUA CHAVE VÁLIDA AQUI

LLM_INITIALIZED = False
llm_model = None
if GOOGLE_API_KEY and GOOGLE_API_KEY != "YOUR_API_KEY_HERE" and GOOGLE_API_KEY != "AIzaSyD9_g9S2tY9rIouUNUYCBdwPRfL0l_Gd_g": # Evita usar chaves placeholder ou a gratuita antiga
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        generation_config_llm = {
            "temperature": 0.2,
            "top_p": 1, "top_k": 1,
            "max_output_tokens": 2048,
        }
        safety_settings_llm = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        llm_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            generation_config=generation_config_llm,
            safety_settings=safety_settings_llm
        )
        LLM_INITIALIZED = True
        print("API da LLM (Google Gemini) configurada com sucesso.")
    except Exception as e:
        print(f"ERRO: Falha ao configurar ou inicializar a API/modelo LLM: {e}")
        print("A funcionalidade da LLM estará desabilitada.")
else:
    print("ALERTA: GOOGLE_API_KEY não está configurada com uma chave válida. A funcionalidade da LLM estará desabilitada.")

LLM_CACHE_FILE = "llm_cache.json"
llm_cache = {} 

# --- Constantes de Caminho ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTES_DE_DADOS_DIR = os.path.join(BASE_DIR, "fontes_de_dados")
# INPUT_FILES_DIR não será mais a fonte primária se usarmos playlists do YouTube, mas pode ser um fallback.
INPUT_FILES_DIR_FALLBACK = os.path.join(FONTES_DE_DADOS_DIR, "generos") 

CURATED_TITLES_DIR = os.path.join(FONTES_DE_DADOS_DIR, "titulos_curados")
CURATED_TITLES_FILENAME = "My YouTube Library.txt"
CURATED_TITLES_PATH = os.path.join(CURATED_TITLES_DIR, CURATED_TITLES_FILENAME)

COMPARISON_FILE_NAME = "Titulos comparados.txt" # Nome do seu arquivo de comparação
COMPARISON_FILE_PATH = os.path.join(FONTES_DE_DADOS_DIR, COMPARISON_FILE_NAME)


# --- Funções Auxiliares Globais ---
def clean_common_tags(text):
    """Remove tags comuns de títulos de música."""
    if not isinstance(text, str): return text
    # Lista expandida de tags
    tags_to_remove = [
        'official video', 'music video', 'official audio', 'lyric video', 'lyrics',
        'audio', 'visualizer', 'official visualizer', 'hd', '4k remaster', '4k upgrade', 'remastered 20\d{2}',
        'hq', 'full album', 'original version', 'official lyric video', 'official music video',
        'official', 'live', 'original mix', 'remastered', 'video clip', 'clipe oficial',
        'pseudo vídeo', 'versão oficial', 'áudio oficial', 'sub español', 'español', 'subtitulado',
        'legendado(?: pt-br)?', 'tradução', 'promo', 'teaser', 'trailer',
        '\(single\)', '\(ep\)', '\(album version\)', '\(radio edit\)', '\(extended mix\)',
        'video oficial', 'audio oficial', 'letra', 'con letra',
        '#\w+' # Remove hashtags genéricas no final
    ]
    original_text = text # Para comparação no final
    for tag in tags_to_remove:
        # Regex para remover tags entre [], () ou após | ou //, ou no final.
        text = re.sub(r'\s*\[\s*' + re.escape(tag) + r'\s*\]\s*', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\(\s*' + re.escape(tag) + r'\s*\)\s*', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\|\s*' + re.escape(tag) + r'\b', ' ', text, flags=re.IGNORECASE) # Tag após pipe
        text = re.sub(r'\s*//\s*' + re.escape(tag) + r'\b', ' ', text, flags=re.IGNORECASE) # Tag após //
        text = re.sub(r'\b' + re.escape(tag) + r'$', ' ', text, flags=re.IGNORECASE) # Tag no final da string

    text = re.sub(r'\s*\|\s*(?:official video|music video|official audio|lyric video|lyrics|audio|visualizer|clipe oficial|legendado(?: pt-br)?|prod[^\)]*|tema de .*|soundtrack)\s*', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*#\w+\s*$', ' ', text, flags=re.IGNORECASE) # Remove hashtags no final
    text = re.sub(r'\s*\[\s*\]\s*|\s*\(\s*\)\s*', ' ', text) # Remove colchetes/parênteses vazios
    
    # Remoção de padrões de produção/animação no final
    text = re.sub(r'\s*\(prod[^\)]*\)\s*$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*\[prod[^\]]*\]\s*$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*\(animated by[^\)]*\)\s*$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*\(from the series[^\)]+\)\s*$', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*\(from[^\)]+\)\s*$', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*\[[^\]]*soundtrack[^\]]*\]\s*$', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*\([^\)]*soundtrack[^\)]*\)\s*$', ' ', text, flags=re.IGNORECASE)
    
    # Remove parênteses/colchetes genéricos no final se não contiverem feat/prod/remix/etc.
    text = re.sub(r'\s+\((?!.*\b(?:feat|ft|prod|remix|edit|version|mix|part|live)\b)[^)]*\)\s*$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+\[(?!.*\b(?:feat|ft|prod|remix|edit|version|mix|part|live)\b)[^\]]*\]\s*$', '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\s+\blive\b\s*$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*-\s*topic\s*$', '', text, flags=re.IGNORECASE) # Remove "- Topic" no final
    text = text.replace('()', '').replace('[]', '') # Remove resquícios
    text = re.sub(r'\s+', ' ', text).strip() # Normaliza espaços

    # Se a limpeza removeu quase tudo, pode ser um título que era só tags.
    if len(text) < 3 and len(original_text.split()) > 2: # Ex: "(Official Video)" vira ""
        return original_text # Retorna o original se a limpeza foi excessiva
    return text

def capitalize_name(name):
    if not name or not isinstance(name, str): return None
    name_stripped = name.strip()
    if not name_stripped: return None

    words_to_upper = ["MC", "DJ", "JR", "SR", "DR", "AC", "DC", "EV", "MR", "MS", "MD", "XV", "RE", "ST", "II", "III", "IV", "VI", "VII", "VIII", "IX", "XL", "MGMT", "J.I.D", "JID", "IDK", "ITR", "S.J.", "OFWGKTA", "MF", "DOOM", "TLC", "NSYNC", "BPM", "EDM", "U.S.", "U.K."]
    lowercase_words = ["a", "an", "the", "and", "but", "or", "for", "nor", "on", "at", "to", "from", "by", "with", "in", "of", "e", "de", "do", "da", "dos", "das", "la", "le", "el", "los", "las", "du", "del", "y", "en", "por", "para"]

    parts = []
    # Trata nomes com hífens primeiro, capitalizando cada parte do hífen
    hyphen_parts = name_stripped.split('-')
    processed_hyphen_parts = []
    for hp_idx, hyphen_part_original in enumerate(hyphen_parts):
        temp_parts_for_hyphen_segment = []
        for i, word_original_case in enumerate(hyphen_part_original.split()):
            word = word_original_case.lower()
            if word_original_case.upper() in words_to_upper:
                temp_parts_for_hyphen_segment.append(word_original_case.upper())
            elif re.fullmatch(r"[a-z]\.[a-z]\.(?:[a-z]\.)?", word): # A.B. ou A.B.C.
                 temp_parts_for_hyphen_segment.append(word.upper())
            elif re.fullmatch(r"(\w\.)+", word_original_case): # Mantém J. Cole como J. Cole
                temp_parts_for_hyphen_segment.append(word_original_case)
            elif re.match(r"^\d+[a-zA-Z]+[0-9]*$", word_original_case) or re.match(r"^[a-zA-Z]+\d+[a-zA-Z0-9]*$",word_original_case): # Mantém 2Pac, 50Cent
                temp_parts_for_hyphen_segment.append(word_original_case)
            elif (i > 0 or hp_idx > 0) and word in lowercase_words: # Não coloca em minúsculo se for a primeira palavra do nome ou do segmento de hífen
                temp_parts_for_hyphen_segment.append(word)
            else:
                if "'" in word and len(word.split("'")[0]) == 1 and len(word) > 1: 
                    sub_parts = word_original_case.split("'")
                    temp_parts_for_hyphen_segment.append(sub_parts[0].lower() + "'" + sub_parts[1].capitalize())
                else:
                    # Capitaliza corretamente palavras como "McDonald's" ou "O'Malley"
                    if any(c.islower() for c in word_original_case) or not any(c.isupper() for c in word_original_case): # Se não for tudo maiúsculo
                        temp_parts_for_hyphen_segment.append(word_original_case.capitalize())
                    else: # Mantém palavras todas em maiúsculo (ex: Racionais MC'S)
                        temp_parts_for_hyphen_segment.append(word_original_case)
        processed_hyphen_parts.append(' '.join(temp_parts_for_hyphen_segment))
    return '-'.join(processed_hyphen_parts)


def normalize_string_for_match(s, lower=True):
    if not isinstance(s, str): s = str(s)
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8') # Remove acentos
    if lower: s = s.lower()
    s = re.sub(r'[^\w\s-]', '', s) # Remove pontuação exceto hífen
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def generate_track_id(title, artist_names):
    norm_title = normalize_string_for_match(title)
    if isinstance(artist_names, list):
        norm_artists = sorted([normalize_string_for_match(name) for name in artist_names if name])
    else:
        norm_artists = [normalize_string_for_match(artist_names)] if artist_names else []
    id_string = f"{norm_title}|{'&'.join(norm_artists)}"
    return hashlib.md5(id_string.encode('utf-8')).hexdigest()

def load_curated_titles(curated_titles_path):
    curated_map = {}
    try:
        with open(curated_titles_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line:
                    curated_map[normalize_string_for_match(stripped_line, lower=True)] = stripped_line
    except FileNotFoundError:
        print(f"AVISO: Arquivo de títulos curados ('My YouTube Library.txt') não encontrado em: {curated_titles_path}")
    return curated_map

def load_comparison_titles(comparison_file_path):
    comparison_map = {}
    try:
        with open(comparison_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        start_processing = False
        for line_idx, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped: continue
            if "Título Original do YouTube" in line and "My YouTube Library" in line:
                start_processing = True
                continue
            if not start_processing: continue
            
            parts = line_stripped.split('\t', 1) # Divide apenas no primeiro tab
            if len(parts) < 2 and '   ' in line_stripped: # Heurística para múltiplos espaços
                parts = re.split(r'\s{3,}', line_stripped, 1)

            if len(parts) == 2:
                my_yt_library_title = parts[0].strip() # Coluna "My YouTube Library"
                original_yt_title_from_comparison = parts[1].strip() # Coluna "Título Original do YouTube"
                if my_yt_library_title and original_yt_title_from_comparison:
                    comparison_map[normalize_string_for_match(original_yt_title_from_comparison, lower=True)] = my_yt_library_title
            # else:
                # print(f"DEBUG: Linha ignorada no arquivo de comparação (formato inesperado): '{line_stripped}' na linha {line_idx+1}")
    except FileNotFoundError:
        print(f"AVISO: Arquivo de comparação de títulos ('{COMPARISON_FILE_NAME}') não encontrado em: {comparison_file_path}")
    except Exception as e:
        print(f"ERRO ao carregar arquivo de comparação de títulos: {e}")
    return comparison_map

# --- Funções de Extração e Lógica Principal --- (is_likely_music_video, extract_song_artist_from_title, etc.)
def is_likely_music_video(title_info):
    title_str = title_info['title'].lower()
    original_title_str = title_info['title'] 

    music_keywords = [
        'ft.', 'feat.', 'featuring', 'prod.', 'produced by', 'official video', 'music video',
        'lyric video', 'lyrics', 'official audio', 'audio', 'remix', 'live', 'album',
        'song', 'music', 'track', 'single', 'records', 'official visualizer', 'visualizer',
        'acústico', 'unplugged', 'cover', 'live session', 'tiny desk', 'colors show',
        'clipe oficial', 'pseudo vídeo', 'versão oficial', 'áudio oficial', '(ep)',
        'live at', 'tema de', 'soundtrack', 'ost', 'hd', 'opening', 'ending', 'op', 'ed',
        'parody', 'paródia', 'musical', 'animated music video', 'starbomb', 'the living tombstone',
        'amv', 'mv', 'mashup', 'medley', 'concerto', 'symphony', 'ballad', 'serenade', 'rhapsody',
        'full version', 'full song', 'pancadão', 'axé music', 'freestyle', 'cypher', 'mixtape',
        'show completo', 'dvd completo', 'set mix', 'dj set', 'live set'
    ]
    non_music_keywords_general = [
        'episode', 'review', 'gameplay', 'trailer', 'tutorial', 'vlog',
        'podcast', 'how to', 'unboxing', 'documentary', 'news',
        'commentary', 'preview', 'hfil', 'minecraft', 'tekken',
        'dragon ball', 'street fighter', 'photoshop', 'asmr', 
        'standup', 'explained', 'science', 'reaction', 'interview',
        'highlights', 'full cast', 'deep dive', 'analysis', 'showcase',
        'old is cool', 'dicas e curiosidades', 'gaveta', 'cortes do flow',
        'nerdologia', 'manual do mundo', 'einerd', 'recipe', 'cooking', 'kitchen',
        'mod', 'modpack', 'speedrun', 'walkthrough', 'let\'s play', 'tier list', 'ranking',
        'ufc', 'mma', 'wwe', 'workout', 'fitness', 'bodybuilding', 'clash royale',
        'yu-gi-oh', 'yugioh', 'pokemon', 'magic the gathering', 'd&d', 'rpg',
        'financial', 'stocks', 'crypto', 'diy', 'life hack', 'ytpbr', 'análise', 'guia',
        'reel', 'efeito', 'redesign', 'prompts', 'features', 'updates', 'platform',
        'startup', 'workflow', 'hack', 'tricks', 'plugin', 'intervalo', 'comerciais',
        'aula', 'curso', 'palestra', 'webinar', 'behind the scenes', 'bloopers',
        'compilado', 'reação', 'react', 'assistindo', 'jogando', 'legendado'
    ]
    tech_design_non_music_keywords = [
        "davinci resolve", "framer", "chatgpt", "openai", "comfyui", "gemini",
        "photoshop", "ai news", "text to speech", "n8n", "runway gen-3"
    ]

    if original_title_str == "Michael Jackson - History": return True
    if "pink guy" in title_str and "teriyaki god" in title_str: return True
    if "mc neguinho itr e mc digu" in title_str and "forte pra dar sorte" in title_str: return True
    if "mc" in title_str and any(prod_kw in title_str for prod_kw in ['prod.', 'produced by']): return True
    if "paródia musical" in title_str: return True
    if "axé music" in title_str and "kame kame kame ha" in title_str and "dragon ball" in title_str: return True

    if "narrando o clipe" in title_str:
        if " - " in title_str or "#" in original_title_str or any(mkw in title_str for mkw in ['song', 'music', 'clipe', 'parody', 'remix', 'cover', 'ft.']):
            return True
        if "one direction" in title_str and "what makes you beautiful" in title_str: return True
        return True 

    if any(kw in title_str for kw in tech_design_non_music_keywords): return False
    if "pipoca e nanquim" in title_str or "kitinete hq" in title_str: return False
    if "neil gaiman" in title_str and any(kw in title_str for kw in ["sandman", "graphic novel", "interview", "documentary"]): return False
    if "virtual barber shop" in title_str or "o barbeiro virtual audio 3d" in title_str: return False
    if "ytpbr" in title_str : return False
    if title_str.startswith("como ganhar flexibilidade"): return False
    if "mrpoladoful" in title_str and not any(kw in title_str for kw in ["song", "clipe", "paródia", "musical"]): return False 
    if "asmr" in title_str and not any(kw in title_str for kw in ["song", "music", "singing", "cover"]): return False
    if "vampire the masquerade" in title_str and "review" in title_str: return False
    if original_title_str == "The Scariest Comic of All Time": return False

    if "starbomb" in title_str or "erb" in original_title_str or "epic rap battles of history" in title_str: return True
    if "the living tombstone" in title_str: return True
    if "paródia" in title_str and any(artist_parody in title_str for artist_parody in ["matuê", "emicouto", "mc vv", "eminem", "rihanna", "psy", "luan santana"]): return True
    if "leod" in title_str and any(kw in title_str for kw in ["mashup", "remix", "anos 80", "anos 90", "ft."]): return True
    if any(poze_kw in title_str for poze_kw in ["mc poze nos anos", "say poze", "marlboro poze", "sopa de macaco"]): return True
    if "smosh" in title_str and "song" in title_str : return True
    if "asdfmovie" in title_str and "song" in title_str: return True
    if "(egoraptor)" in title_str and "minecraft is for everyone" in title_str: return True
    if "tetris rap animated" in title_str: return True
    if "cyberpunk 2077" in title_str and "never fade away" in title_str and "by samurai" in title_str : return True

    anime_op_ed_pattern = r'(?:opening|ending|op|ed)\s*\d*\s*(?:full|version|hd|creditless|ncorp|nced)?\s*(?:\[|﹝|『|「|<|\||$)'
    if re.search(anime_op_ed_pattern, title_str) or \
       (any(anime_name in title_str for anime_name in ["jojo", "noragami", "naruto", "one punch man", "death parade"]) and any(op_ed_kw in title_str for op_ed_kw in ["opening", "ending", "op", "ed", "theme"])):
        return True

    common_music_pattern_strict = r"^\s*[^-\n\[\(/:·]{2,}\s*(?:-|–|—|:|·|\/)\s*[^-\n\[\(/:·]{2,}"
    common_music_pattern_spaced = r"^\s*[^-\n\[\(/:·]{2,}\s+(?:-|–|—|:|·|\/)\s+[^-\n\[\(/:·]{2,}"
    is_common_artist_song_pattern = re.match(common_music_pattern_spaced, title_str, flags=re.IGNORECASE) or \
                                   re.match(common_music_pattern_strict, original_title_str.replace(':', ' - ', 1).replace('/', ' / '), flags=re.IGNORECASE)
    has_music_keyword = any(keyword in title_str for keyword in music_keywords)
    has_non_music_keyword_general = any(keyword in title_str for keyword in non_music_keywords_general)

    if is_common_artist_song_pattern:
        strong_overriding_non_music = ['tutorial', 'review', 'gameplay', 'vlog', 'podcast', 'documentary', 'commentary', 'explained', 'episode', 'unboxing', 'how to', 'aula', 'curso', 'palestra', 'reação', 'react', 'análise', 'dicas']
        very_strong_music_indicators = ['official music video', 'clipe oficial', 'official song', 'album completo', 'full album', 'paródia musical', 'official audio', 'live session', 'acústico']
        if any(strong_nmk in title_str for strong_nmk in strong_overriding_non_music):
            if any(very_strong_mk in title_str for very_strong_mk in very_strong_music_indicators): return True
            return False 
        return True 

    if has_music_keyword:
        if has_non_music_keyword_general:
            if any(specific_music_type in title_str for specific_music_type in ["paródia", "musical", "axé music", "freestyle", "cypher"]):
                if not any(nmk_override in title_str for nmk_override in ['tutorial', 'review', 'how to make', 'gameplay', 'documentary', 'explained']): return True
            if "tutorial" in title_str and "plugin" in title_str: return False
            if "song" in title_str and any(nm_kw in title_str for nm_kw in ['tutorial', 'review', 'analysis', 'explained', 'how to make', 'ranking']): return False
            if "album" in title_str and any(nm_kw in title_str for nm_kw in ['review', 'analysis', 'unboxing', 'explained']): return False
            return False # Se tem keywords de música e não-música, e não se encaixou nas exceções, é mais seguro ser não-música
        return True # Apenas keywords de música

    if has_non_music_keyword_general: return False
    return False # Fallback final

def extract_song_artist_from_title(title_to_process, channel_name_hint=None):
    title_str_original_case = title_to_process 
    title_str = title_to_process.lower()
    title_str = title_str.replace('—', '-').replace('–', '-').replace('−', '-')

    artists_extracted = [] 
    song_title = None
    featured_artists = []
    producers = []

    # --- Regras Específicas de Artista/Título ---
    # (Seu código de regras específicas existente vai aqui - Eminem, ERB, Starbomb, LEOD, MCs, Michael Jackson etc.)
    # Vou adicionar apenas algumas como exemplo da estrutura:
    if "eminem" in title_str and "without me" in title_str:
        artists_extracted = ["Eminem"]; song_title = "Without Me"
        return artists_extracted, song_title, featured_artists, producers
    if "epic rap battles of history" in title_str or "erb" in title_str:
        artists_extracted = ["Epic Rap Battles of History"]
        match_erb = re.match(r"(.+?)\s+vs\.?\s+(.+?)(?:\.|$)", title_str_original_case, re.IGNORECASE)
        song_title = f"{capitalize_name(match_erb.group(1).strip())} vs {capitalize_name(match_erb.group(2).strip())}" if match_erb else re.sub(r'\s*\.\s*epic rap battles of history.*$', '', title_str_original_case, flags=re.IGNORECASE).strip()
        return artists_extracted, song_title, [], []
    # ... (ADICIONE SUAS OUTRAS REGRAS ESPECÍFICAS AQUI) ...

    # --- Lógica Principal de Extração ---
    temp_title_str_main_extraction = title_str_original_case
    non_feat_prod_parts = [] 
    last_match_end = 0
    all_matches = [] 
    ft_pattern = r'(ft\.|feat\.|featuring|with|part\.)\s*([\w\s,&\'./+~-]+?(?=\s*\(|\s*\[|\s*\||$|\s+prod\.|\s+prod by|\s+x\s+[\w\s]|\s+vs\.))'
    prod_pattern = r'(prod\.|produced by)\s*([\w\s,&\'./+~-]+?(?=\s*\(|\s*\[|\s*\||$))'
    for match_iter in re.finditer(ft_pattern, temp_title_str_main_extraction, flags=re.IGNORECASE): all_matches.append({'match': match_iter, 'type': 'feat'})
    for match_iter in re.finditer(prod_pattern, temp_title_str_main_extraction, flags=re.IGNORECASE): all_matches.append({'match': match_iter, 'type': 'prod'})
    all_matches.sort(key=lambda m: m['match'].start())
    for item in all_matches:
        match = item['match']
        match_type = item['type']
        non_feat_prod_parts.append(temp_title_str_main_extraction[last_match_end:match.start()])
        last_match_end = match.end()
        items_str = match.group(2).strip()
        split_regex = r'\s*,\s*|\s*&\s*|\s+e\s+|\s+and\s+'
        if match_type == 'feat': split_regex += r'|\s+with\s+|\s+part\.\s+'
        new_items = [it.strip() for it in re.split(split_regex, items_str) if it.strip() and it.lower() not in ['x', 'vs']]
        if match_type == 'feat': featured_artists.extend(new_items)
        else: producers.extend(new_items)
    non_feat_prod_parts.append(temp_title_str_main_extraction[last_match_end:])
    main_title_candidate = "".join(non_feat_prod_parts).strip()
    main_title_candidate_cleaned = clean_common_tags(main_title_candidate)

    artist_candidate = None
    
    if artists_extracted and song_title: pass 
    elif main_title_candidate_cleaned:
        parts = []
        separators_to_try = [r"\s+-\s+", r"\s+–\s+", r"\s+—\s+", r"\s+:\s+"] 
        for sep_regex in separators_to_try:
            match_obj = re.match(r"(.+?)" + sep_regex + r"(.+)", main_title_candidate_cleaned, re.IGNORECASE)
            if match_obj:
                parts = [match_obj.group(1).strip(), match_obj.group(2).strip()]
                break
        if not parts:
            other_separators = [r"\s+\|\s+", r"\s+/\s+"] 
            for sep_regex in other_separators:
                match_obj = re.match(r"(.+?)" + sep_regex + r"(.+)", main_title_candidate_cleaned, re.IGNORECASE)
                if match_obj:
                    parts = [match_obj.group(1).strip(), match_obj.group(2).strip()]
                    break
        if not parts and "-" in main_title_candidate_cleaned and main_title_candidate_cleaned.count('-') == 1 and \
           re.match(r"^[^- \t\n\r\f\v]+-[^- \t\n\r\f\v]+$", main_title_candidate_cleaned):
             parts = [p.strip() for p in main_title_candidate_cleaned.split("-", 1)]

        if len(parts) == 2:
            part1_cleaned, part2_cleaned = clean_common_tags(parts[0]), clean_common_tags(parts[1])
            part1_lower, part2_lower = part1_cleaned.lower(), part2_cleaned.lower()
            song_indicator_keywords = ['lyric video', 'lyrics', 'official audio', 'audio', 'remix', 'live', 'album', 'visualizer', 'parody', 'paródia', 'cover', 'instrumental', 'acústico', 'unplugged', 'session', 'opening', 'ending', 'theme', 'soundtrack', 'ost', 'video', 'clipe', 'full version', 'radio edit', 'extended mix', 'single', 'track', 'ep']
            artist_indicator_keywords = [' ft', ' feat', ' & ', ' e ', ' vs ', ' x ', ' with ', ' apresent', ' part.']
            part1_has_song_indicators = any(kw in part1_lower for kw in song_indicator_keywords)
            part2_has_song_indicators = any(kw in part2_lower for kw in song_indicator_keywords)
            part1_has_artist_indicators = any(kw in part1_lower for kw in artist_indicator_keywords) or 'mc ' in part1_lower or 'dj ' in part1_lower
            part2_has_artist_indicators = any(kw in part2_lower for kw in artist_indicator_keywords) or 'mc ' in part2_lower or 'dj ' in part2_lower
            part1_is_channel_hint = channel_name_hint and normalize_string_for_match(part1_cleaned, lower=True) == normalize_string_for_match(channel_name_hint, lower=True)
            part2_is_channel_hint = channel_name_hint and normalize_string_for_match(part2_cleaned, lower=True) == normalize_string_for_match(channel_name_hint, lower=True)

            if part1_is_channel_hint and not part2_is_channel_hint: artist_candidate, song_title = part1_cleaned, part2_cleaned
            elif part2_is_channel_hint and not part1_is_channel_hint: artist_candidate, song_title = part2_cleaned, part1_cleaned
            elif part2_has_song_indicators and not part1_has_song_indicators: artist_candidate, song_title = part1_cleaned, part2_cleaned
            elif part1_has_song_indicators and not part2_has_song_indicators: artist_candidate, song_title = part2_cleaned, part1_cleaned
            elif part1_has_artist_indicators and not part2_has_artist_indicators: artist_candidate, song_title = part1_cleaned, part2_cleaned
            elif part2_has_artist_indicators and not part1_has_artist_indicators: artist_candidate, song_title = part2_cleaned, part1_cleaned
            # Priorizar canal se o outro lado for muito genérico ou apenas tags
            elif part1_is_channel_hint and (part2_has_song_indicators or len(part2_cleaned.split()) > 5): artist_candidate, song_title = part1_cleaned, part2_cleaned
            elif part2_is_channel_hint and (part1_has_song_indicators or len(part1_cleaned.split()) > 5): artist_candidate, song_title = part2_cleaned, part1_cleaned
            # Lógica de comprimento
            elif len(part1_cleaned.split()) <= len(part2_cleaned.split()) and len(part1_cleaned.split()) <= 4 and not part1_has_song_indicators: artist_candidate, song_title = part1_cleaned, part2_cleaned
            elif len(part2_cleaned.split()) < len(part1_cleaned.split()) and len(part2_cleaned.split()) <= 4 and not part2_has_song_indicators: artist_candidate, song_title = part2_cleaned, part1_cleaned
            else: artist_candidate, song_title = part1_cleaned, part2_cleaned # Fallback: assume Artista - Música
            
            if artist_candidate and song_title: artists_extracted = [artist_candidate]
        
        elif not artists_extracted: 
            cleaned_lookup_title = clean_common_tags(main_title_candidate.lower()) 
            short_music_map = {
                "noid": (["Yves Tumor"], "Noid"), "not like us": (["Kendrick Lamar"], "Not Like Us"),
                "sorry not sorry": (["Demi Lovato"], "Sorry Not Sorry"), "wharf talk": (["Tyler, The Creator"], "Wharf Talk"),
                "heaven to me": (["Tyler, The Creator"], "Heaven To Me"), "dogtooth": (["Tyler, The Creator"], "Dogtooth"),
                "wusyaname": (["Tyler, The Creator"], "Wusyaname"), "lemonhead": (["Tyler, The Creator"], "Lemonhead"),
                "corso": (["Tyler, The Creator"], "Corso"), "i think": (["Tyler, The Creator"], "I Think"),
                "a boy is a gun*": (["Tyler, The Creator"], "A Boy Is A Gun*"), "o oitavo anjo": (["509-E"], "O Oitavo Anjo"),
                "remember the time": (["Michael Jackson"], "Remember The Time"), "velocidade da luz": (["Revelação"], "Velocidade da Luz"),
                "onda onda (olha a onda)": (["Tchakabum"], "Onda Onda (Olha a Onda)"), "mr bombastic": (["Shaggy"], "Boombastic"),
                "indian moonlight": (["S. J. Jananiy"], "Indian Moonlight"), "bonfire/cursed images meme": (["Shikoku Meeting"], "Bonfire"), 
                "teriyaki god": (["Pink Guy (Joji)"], "Teriyaki God"), "o sino da igrejinha": (["Unknown"], "O Sino da Igrejinha"),
                "st chroma x rah tah tah": (["ST CHROMA"], "Rah Tah Tah"),
                "mademoiselle noir": (["Peppermoon"], "Mademoiselle Noir"), # Corrigido
                "rock around the clock-bill haley-original song-1955": (["Bill Haley & His Comets"], "Rock Around the Clock"),
                "tetris rap animated": (["Starbomb"], "Tetris Rap")
            }
            if cleaned_lookup_title in short_music_map: 
                artists_extracted, song_title = short_music_map[cleaned_lookup_title]
            elif "narrando o clipe" in main_title_candidate.lower():
                if "one direction" in main_title_candidate.lower() and "what makes you beautiful" in main_title_candidate.lower():
                    artists_extracted = ["One Direction"]; song_title = "What Makes You Beautiful (Narrando o Clipe)"
                else:
                    artists_extracted = ["Narrando o Clipe"]; song_title = re.sub(r'narrando o clipe\s*', '', main_title_candidate, flags=re.IGNORECASE).strip("- ")
            if not artists_extracted : 
                song_title = main_title_candidate_cleaned 
                artists_extracted = ["Unknown"] 

    elif not artists_extracted and not song_title: 
        song_title = clean_common_tags(title_str_original_case) 
        artists_extracted = ["Unknown"]

    if artist_candidate and not artists_extracted: artists_extracted = [artist_candidate]
    
    final_artists_list = []
    if artists_extracted and artists_extracted != ["Unknown"] and isinstance(artists_extracted[0], str):
        temp_artist_string = artists_extracted[0]
        temp_artist_string = re.sub(r'\bft\.','FT_PLACEHOLDER', temp_artist_string, flags=re.IGNORECASE)
        temp_artist_string = re.sub(r'\bfeat\.','FEAT_PLACEHOLDER', temp_artist_string, flags=re.IGNORECASE)
        potential_artists = re.split(r'\s+(?:&|e|x|versus|vs\.?)\s+|\s*,\s*(?![^\[]*\])(?![^(]*\))(?!\s*(?:jr|sr)\.?)', temp_artist_string, flags=re.IGNORECASE)
        for pa in potential_artists:
            pa = pa.replace('FT_PLACEHOLDER', 'ft.').replace('FEAT_PLACEHOLDER', 'feat.')
            cap_name = capitalize_name(pa.strip())
            if cap_name and cap_name.lower() != "unknown": final_artists_list.append(cap_name)
        if not final_artists_list:
            cap_single_artist = capitalize_name(artists_extracted[0])
            if cap_single_artist and cap_single_artist.lower() != "unknown": final_artists_list = [cap_single_artist]
            else: final_artists_list = ["Unknown"]
    elif artists_extracted and artists_extracted == ["Unknown"]: final_artists_list = ["Unknown"]
    elif not artists_extracted: final_artists_list = ["Unknown"]

    song_title_final = capitalize_name(song_title) if song_title else "Unknown"

    if final_artists_list == ["Unknown"] and channel_name_hint:
        potential_artist_from_channel = capitalize_name(channel_name_hint) 
        if potential_artist_from_channel:
            _papc = potential_artist_from_channel
            _papc = re.sub(r'\s*-\s*Topic$', '', _papc, flags=re.IGNORECASE).strip()
            _papc = re.sub(r'\s*VEVO$', '', _papc, flags=re.IGNORECASE).strip()
            _papc = re.sub(r'\s*Official(?! Artist Channel)$', '', _papc, flags=re.IGNORECASE).strip() # Evita remover "Official Artist Channel"
            _papc = re.sub(r'\s*Music$', '', _papc, flags=re.IGNORECASE).strip()
            generic_channel_keywords = ["various artists", "official", "music", "topic", "channel", "records", "canal", "gravadora", "lyrics", "traduções", "themes", "soundtracks"]
            is_generic_channel = any(gck in _papc.lower() for gck in generic_channel_keywords) or _papc.lower() == "unknown"
            if _papc and len(_papc.split()) < 5 and not is_generic_channel and _papc.lower() != title_to_process.lower().strip():
                cleaned_title_as_song = clean_common_tags(title_to_process)
                cleaned_title_as_song_capitalized = capitalize_name(cleaned_title_as_song)
                if cleaned_title_as_song_capitalized and cleaned_title_as_song_capitalized.lower() != _papc.lower():
                    current_song_candidate = cleaned_title_as_song_capitalized
                    if _papc.lower() in current_song_candidate.lower():
                        escaped_artist_for_regex = re.escape(_papc)
                        pattern_prefix = r"^{}\s*[-–—:|\/]\s*".format(escaped_artist_for_regex)
                        pattern_suffix_dash = r"\s*[-–—:|\/]\s*{}$".format(escaped_artist_for_regex)
                        pattern_suffix_paren = r"\s*\({}\)$".format(escaped_artist_for_regex)
                        removed_prefix_song = re.sub(pattern_prefix, "", current_song_candidate, flags=re.IGNORECASE).strip()
                        if removed_prefix_song and removed_prefix_song.lower() != current_song_candidate.lower(): current_song_candidate = removed_prefix_song
                        else:
                            removed_suffix_song_dash = re.sub(pattern_suffix_dash, "", current_song_candidate, flags=re.IGNORECASE).strip()
                            if removed_suffix_song_dash and removed_suffix_song_dash.lower() != current_song_candidate.lower(): current_song_candidate = removed_suffix_song_dash
                            else:
                                removed_suffix_song_paren = re.sub(pattern_suffix_paren, "", current_song_candidate, flags=re.IGNORECASE).strip()
                                if removed_suffix_song_paren and removed_suffix_song_paren.lower() != current_song_candidate.lower(): current_song_candidate = removed_suffix_song_paren
                                elif len(current_song_candidate.replace(_papc, '').strip()) > 2 : current_song_candidate = current_song_candidate.replace(_papc, '').strip(" -:()[]").strip()
                    current_song_candidate = capitalize_name(current_song_candidate)
                    if current_song_candidate and len(current_song_candidate.split()) < 10 and current_song_candidate.lower() != "unknown" and current_song_candidate.lower() != _papc.lower():
                        final_artists_list = [_papc]
                        song_title_final = current_song_candidate
                    elif current_song_candidate and current_song_candidate.lower() == _papc.lower():
                        final_artists_list = [_papc] 
                        song_title_final = capitalize_name(clean_common_tags(title_to_process))
                        if song_title_final.lower() == final_artists_list[0].lower(): final_artists_list = ["Unknown"]
    
    if isinstance(song_title_final, str):
        song_title_final = clean_common_tags(song_title_final)
        song_title_final = re.sub(r'\s*\((?:Audio|Lyrics|Official|Video|Music|Lyric|Visualizer|Remix|Live|Version|Cover|Parody|Traduzido|Legendado|HD|4K|EP)\s*\)\s*$', '', song_title_final, flags=re.IGNORECASE).strip()
        song_title_final = re.sub(r'\s*\[(?:Audio|Lyrics|Official|Video|Music|Lyric|Visualizer|Remix|Live|Version|Cover|Parody|Traduzido|Legendado|HD|4K|EP)\s*\]\s*$', '', song_title_final, flags=re.IGNORECASE).strip()
        song_title_final = re.sub(r'\s*\(\s*\)\s*|\s*\[\s*\]\s*', '', song_title_final).strip()
        song_title_final = re.sub(r'\s+\blive\b\s*$', '', song_title_final, flags=re.IGNORECASE).strip()

    featured_artists_final = sorted(list(set(filter(None, [capitalize_name(fa) for fa in featured_artists if fa]))))
    producers_final = sorted(list(set(filter(None, [capitalize_name(p) for p in producers if p]))))

    if not song_title_final or song_title_final.lower() == "unknown": song_title_final = "Unknown"
    if not final_artists_list or final_artists_list == ["Unknown"]: final_artists_list = ["Unknown"]

    if final_artists_list == [title_str_original_case] and song_title_final == "Unknown":
        final_artists_list = ["Unknown"]; song_title_final = capitalize_name(clean_common_tags(title_str_original_case))

    if final_artists_list != ["Unknown"] and isinstance(song_title_final, str) and song_title_final != "Unknown":
        temp_song_title_for_artist_removal = song_title_final
        for art_name in final_artists_list:
            if art_name.lower() in temp_song_title_for_artist_removal.lower():
                # Tentativa de remoção mais cuidadosa: "Artista - Música" ou "Música (Artista)"
                # Evita remover substrings que não sejam o artista completo separado.
                # Regex para remover "Artista - " ou "Artista: " etc. do início
                temp_song_title_for_artist_removal = re.sub(r"^\s*" + re.escape(art_name) + r"\s*[-–—:|/\s]+\s*", "", temp_song_title_for_artist_removal, flags=re.IGNORECASE).strip()
                # Regex para remover " - Artista" ou " (Artista)" etc. do final
                temp_song_title_for_artist_removal = re.sub(r"\s*[-–—:|/\s]+\s*" + re.escape(art_name) + r"\s*$", "", temp_song_title_for_artist_removal, flags=re.IGNORECASE).strip()
                temp_song_title_for_artist_removal = re.sub(r"\s*\(\s*" + re.escape(art_name) + r"\s*\)\s*$", "", temp_song_title_for_artist_removal, flags=re.IGNORECASE).strip()

        cleaned_candidate = capitalize_name(temp_song_title_for_artist_removal)
        if cleaned_candidate and cleaned_candidate.lower() != "unknown" and cleaned_candidate.lower() not in [a.lower() for a in final_artists_list]:
            song_title_final = cleaned_candidate
        elif not cleaned_candidate and song_title_final.lower() in [a.lower() for a in final_artists_list]:
            song_title_final = "Unknown" # Se o título virou vazio e era só o nome do artista
        # Se o título original já era só o nome do artista, e foi limpo, pode ser que song_title_final seja ""
        # Nesse caso, é melhor marcar como Unknown do que ter um título vazio.
        if not song_title_final and song_title != "Unknown": # Se ficou vazio mas não era Unknown antes
             song_title_final = "Unknown"


    if final_artists_list == ["Unknown"] and isinstance(song_title_final, str) and song_title_final != "Unknown":
        common_separators = [" - ", " : ", " | ", " / "]
        for sep in common_separators:
            if sep in song_title_final: 
                parts_fallback = song_title_final.split(sep, 1)
                if len(parts_fallback[0].split()) <= 5 and len(parts_fallback[0].split()) > 0 and len(parts_fallback[0]) < 35:
                    potential_artist = capitalize_name(parts_fallback[0].strip())
                    potential_song = capitalize_name(parts_fallback[1].strip())
                    if potential_artist and potential_song and potential_artist.lower() != "unknown" and potential_artist.lower() != potential_song.lower():
                         final_artists_list = [potential_artist]; song_title_final = potential_song; break
    
    if len(final_artists_list) == 1 and isinstance(final_artists_list[0], str) and " x " in final_artists_list[0].lower():
        main_artist_str = final_artists_list[0]
        if not (main_artist_str.lower() == "lil nas x" or (main_artist_str.lower().endswith(" x") and len(main_artist_str.split())==1)):
            sub_artists = [capitalize_name(sa.strip()) for sa in re.split(r'\s+x\s+', main_artist_str, flags=re.IGNORECASE)]
            if len(sub_artists) > 1 and all(s.strip() for s in sub_artists): 
                final_artists_list = sub_artists

    if len(final_artists_list) > 1 and "Unknown" in final_artists_list:
        final_artists_list = [a for a in final_artists_list if a != "Unknown"]
    if not final_artists_list: final_artists_list = ["Unknown"]

    if final_artists_list != ["Unknown"]:
        main_artist_names_lower = [a.lower() for a in final_artists_list]
        featured_artists_final = [fa for fa in featured_artists_final if capitalize_name(fa) and capitalize_name(fa).lower() not in main_artist_names_lower]
        producers_final = [p for p in producers_final if capitalize_name(p) and capitalize_name(p).lower() not in main_artist_names_lower]

    if final_artists_list == ["Unknown"] and song_title_final != "Unknown" and " - " in song_title_final:
        parts_last_chance = song_title_final.split(" - ", 1)
        if len(parts_last_chance[0].split()) < 4 and len(parts_last_chance[0]) > 0 :
            potential_artist_lc = capitalize_name(parts_last_chance[0])
            potential_song_lc = capitalize_name(parts_last_chance[1])
            if potential_artist_lc and potential_artist_lc.lower() not in ["unknown", "official video", "lyrics"] and len(potential_artist_lc) > 1 :
                final_artists_list = [potential_artist_lc]
                song_title_final = potential_song_lc
            
    if song_title_final == "Unknown" and final_artists_list == ["Unknown"]:
         song_title_final = capitalize_name(clean_common_tags(title_str_original_case))
    if not song_title_final: # Garante que song_title_final não seja None ou vazio
        song_title_final = "Unknown"

    return final_artists_list, song_title_final, featured_artists_final, producers_final


# --- Funções para buscar vídeos de playlists e interagir com LLM ---
def fetch_playlist_videos_yt_dlp(playlist_url, playlist_name_for_source):
    """Busca vídeos de uma playlist do YouTube usando yt-dlp."""
    videos = []
    # Comando yt-dlp para extrair título, URL, nome do canal e data de upload em formato JSON
    # O campo 'uploader' é o nome do canal, 'upload_date' é YYYYMMDD
    command = [
        'yt-dlp',
        '-j',  # Saída JSON por linha
        '--flat-playlist', # Processa a playlist como uma lista plana, sem extrair infos de cada vídeo (mais rápido)
                           # Para mais detalhes por vídeo, removeria --flat-playlist e processaria URLs individuais
        '--skip-download', # Não baixa o vídeo
        '--extractor-args', 'youtube:player_client=web;youtube:skip=dash,hls', # Otimizações
        playlist_url
    ]
    try:
        print(f"Buscando vídeos da playlist '{playlist_name_for_source}': {playlist_url}")
        # Definir um timeout maior para playlists longas
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        stdout, stderr = process.communicate(timeout=600) # Timeout de 10 minutos

        if process.returncode != 0:
            print(f"Erro ao buscar playlist '{playlist_name_for_source}' com yt-dlp (código {process.returncode}):")
            # print(f"  Comando: {' '.join(command)}") # Para depuração
            # print(f"  Stderr: {stderr}")
            return videos

        for line in stdout.splitlines():
            if line.strip():
                try:
                    video_meta = json.loads(line)
                    title = video_meta.get('title')
                    video_id = video_meta.get('id') # ID do vídeo
                    if not video_id and 'url' in video_meta: # Fallback se 'id' não estiver presente mas 'url' sim
                        match_id = re.search(r"v=([^&]+)", video_meta['url'])
                        if match_id: video_id = match_id.group(1)

                    if title and video_id:
                        # yt-dlp com --flat-playlist não fornece 'uploader' ou 'upload_date' diretamente na entrada da playlist.
                        # Para esses detalhes, seria necessário uma chamada adicional por vídeo ou uma biblioteca diferente.
                        # Por enquanto, vamos manter 'channel_name' e 'upload_date' como None/Unknown.
                        # Se você precisar desses dados, precisaremos de uma abordagem mais intensiva.
                        videos.append({
                            "original_youtube_title": title,
                            "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
                            "channel_name": video_meta.get('channel', video_meta.get('uploader', "Unknown")), # Tenta 'channel' primeiro, depois 'uploader'
                            "upload_date": None, # Não disponível com --flat-playlist de forma confiável
                            "video_id_yt": video_id # Armazena o ID do YouTube
                        })
                except json.JSONDecodeError:
                    # print(f"Aviso: Erro ao decodificar JSON para uma linha da playlist '{playlist_name_for_source}': {line[:100]}...")
                    pass # Ignora linhas que não são JSON válido
        print(f"Encontradas {len(videos)} entradas na playlist '{playlist_name_for_source}'.")
    except subprocess.TimeoutExpired:
        print(f"Timeout ao buscar playlist '{playlist_name_for_source}'.")
    except FileNotFoundError:
        print("ERRO: yt-dlp não encontrado. Certifique-se de que está instalado e no PATH do sistema, ou forneça o caminho completo.")
    except Exception as e:
        print(f"Erro inesperado ao buscar playlist '{playlist_name_for_source}': {e}")
    return videos

# (Funções da LLM: call_llm_with_cache, llm_extract_artist_song, llm_normalize_artist_name - MANTENHA COMO ESTÃO)
# (Função enrich_track_details_with_search - MANTENHA COMO ESTÁ)
# (Função process_library_data - MANTENHA COMO ESTÁ, mas verifique a chamada para curated_titles_map se necessário)


# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    all_videos_data = [] 
    
    # Carrega títulos curados do "My YouTube Library.txt"
    curated_titles_map = load_curated_titles(CURATED_TITLES_PATH)
    print(f"Carregados {len(curated_titles_map)} títulos curados de '{CURATED_TITLES_PATH}'.")

    # Carrega o arquivo de comparação "Titulos comparados.txt"
    comparison_titles_map = load_comparison_titles(COMPARISON_FILE_PATH)
    print(f"Carregados {len(comparison_titles_map)} mapeamentos do arquivo de comparação '{COMPARISON_FILE_PATH}'.")

    # LISTA DE PLAYLISTS DO YOUTUBE PARA PROCESSAR
    # Cada item pode ser uma string (URL) ou uma tupla (URL, "Nome da Playlist para Tag")
    playlists_to_process = [
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9yqnxKGIiAuIqW7rGcE0Uy1", "Afro-Indígena"), # Exemplo, ajuste o nome
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9y8LvfZH56hyn1iuWc_nRDN", "Anti-Music"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9zMNa89TvLkwCBsVC8VCKBZ", "B A S S"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9yjFLmSFjiyJDW4WWlWGi-f", "Brasil"),
        ("https://www.youtube.com/playlist?list=PLu_j_syHExYT99QhNShk4UjrPvPQ3CH9g", "Brazilian Hip Hop (Matheus)"), # Playlist do Matheus
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9wOb9eY6OccQbYtxGWuBJuF", "Casório Matias"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9zh144R9B8FiTGM-YjpXw35", "Classic & Hard Rock"), # !!!!
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9yQd_jqkz3HWEHoM1S5SLgG", "Embolada"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9wgrHXlxA8V_Onv_XUyFmsb", "ERB"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9yPZHkR7icxJUKW2kcugV_P", "Fazendinha e afins"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9zDNU25q0dZNh4YTzUf-iQr", "Folk"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9y5xFVPeDfnG9WLgVSndhGh", "Funk"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9wtLfxnnjyPhjiftTkkEP8S", "Gothic Metal"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9yZFG4BdsYKfs5nYr8OtrTL", "Gothic"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9w79Witfv4COFLFk_C8fLxk", "Great"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9y3uEu-S9wd9Dj2RYPlW5q4", "Hip Hop"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9yQ6ERfCQ0MkECavEaqGY1L", "JAV"), # Japan Audio Visual?
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9wIAH56UJP9h7hWJHQf5Sgv", "Meditação (Misael)"), # Playlist do Misael
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9zGvRE1SEPm8z3Gd_4R4nVf", "Memes, Paródias e Anti-Music"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9yZl9q8WSZfPQVUiBwDf5jM", "Metal"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9xUtu2y2KZjZg8wm-PgBrvg", "meu amô"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9xWRC6MUnqsWUy8qOmIwWls", "MJ - Só as Braba"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9zYEQ24pniv7ClfBa1MnpSt", "Muasicas do Kuduairo - Matheus"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9y5ZPUrmeZgQ07ZHKbD-ElJ", "Muasicas do Kuduairo - Misa"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9xegMYz9Xyw7UzBVCi8Cw77", "Nostalgia"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9yWTn0E7G3ld5YbizZVXV6L", "Pontos de Umbanda"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9yXeuXaunF0byK437xGY0hE", "Pop"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9w2xYaJ0QH_k1WX5_wCnyOL", "Reggae"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9xJlOHZuGhVi7WAns_AQ4nH", "Relax"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9zFAWJwaVXH7vCfMMh4gL6V", "Rock Alternativo"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9wVMs4HUampbWKCDDJcenp0", "Sertanejo"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9wcswF268ytqQ9F62e55UzH", "ShitTrap"),
        ("https://www.youtube.com/playlist?list=PLtUbo3GMSoRzYA57lqWG428Mus3urCebL", "some bully good shanties"), # GOOD SHANTIES
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9zf9_KgHg0nOdz_6g5OUUql", "STARBOMB"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9z1StiFf_vZP-sf5pxVhdEd", "Trap"),
        #("https://www.youtube.com/playlist?list=PLK7ygg6VFq9yYL53xWjqVn2sLIMrfgx-G", "TudoJunto"), # Se "TudoJuntoLeve" for mais completo, pode omitir este
        ("https://www.youtube.com/playlist?list=PLu20DUVqPCRDEYQv8dtYKIavJTwnLY640", "TudoJuntoLeve (Alternativa)"), # Outra playlist TudoJuntoLeve
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9yacPqcXFkxULUSYpBIHlvA", "Underground Rap"),
        ("https://www.youtube.com/playlist?list=PLK7ygg6VFq9yC4jni9tyfWg0KTBr291xy", "Xtreme Metal")
    ]

    for item in playlists_to_process:
        playlist_url, source_playlist_name = "", ""
        if isinstance(item, tuple):
            playlist_url, source_playlist_name = item
        elif isinstance(item, str):
            playlist_url = item
            # Tenta extrair um nome da URL ou usa um genérico
            playlist_id_match = re.search(r"[&?]list=([^&]+)", playlist_url)
            source_playlist_name = playlist_id_match.group(1) if playlist_id_match else f"Playlist_{playlists_to_process.index(item)+1}"
        else:
            continue # Ignora item se não for string ou tupla

        playlist_videos = fetch_playlist_videos_yt_dlp(playlist_url, source_playlist_name)
        for video_from_yt in playlist_videos:
            video_from_yt["source_playlist_name"] = source_playlist_name 
            
            original_title_from_yt = video_from_yt.get("original_youtube_title", "")
            
            # 1. Tenta usar o "Titulos comparados.txt"
            normalized_title_for_comparison_lookup = normalize_string_for_match(original_title_from_yt, lower=True)
            title_from_comparison_file = comparison_titles_map.get(normalized_title_for_comparison_lookup)

            if title_from_comparison_file:
                video_from_yt["title_for_extraction"] = title_from_comparison_file
            else:
                # 2. Se não encontrou no comparison, tenta "My YouTube Library.txt"
                normalized_original_for_curated_lookup = normalize_string_for_match(original_title_from_yt, lower=True)
                title_from_curated_library = curated_titles_map.get(normalized_original_for_curated_lookup)
                if title_from_curated_library:
                    video_from_yt["title_for_extraction"] = title_from_curated_library
                else:
                    # 3. Se não encontrou em nenhum, usa o título original do YouTube
                    video_from_yt["title_for_extraction"] = original_title_from_yt
            
            all_videos_data.append(video_from_yt)
    
    if not all_videos_data:
        print("Nenhum dado de vídeo coletado das playlists ou arquivos locais. Saindo.")
        exit()
    
    print(f"\nTotal de {len(all_videos_data)} entradas de vídeo coletadas.")

    # Criação de diretório de saída e nomes de arquivo
    now = datetime.now()
    output_folder_name = now.strftime("%Y-%m-%d_%H-%M-%S") + "_run_final_yt" # Adicionado _yt
    output_root_dir = os.path.join(BASE_DIR, "output_script_principal") 
    if not os.path.exists(output_root_dir): os.makedirs(output_root_dir)
    output_directory_path = os.path.join(output_root_dir, output_folder_name)
    if not os.path.exists(output_directory_path): os.makedirs(output_directory_path)
    print(f"Criado diretório de saída: {output_directory_path}")

    output_json_filename = os.path.join(output_directory_path, "music_data_final.json")
    unknown_extraction_filename = os.path.join(output_directory_path, "unknown_extraction_videos_final.txt")
    skipped_videos_filename = os.path.join(output_directory_path, "skipped_videos_final.txt")
    report_filename = os.path.join(output_directory_path, "processing_report_final.txt")

    # Processa os dados da biblioteca
    # Passa curated_titles_map para o caso de alguma lógica interna ainda precisar dele,
    # mas o title_for_extraction já deve estar definido.
    music_data, report_string, skipped_titles_list = process_library_data(all_videos_data, curated_titles_map) 
    report_string = report_string.replace("[output_folder_path]", output_directory_path)

    print("\n" + "="*50 + "\n"); print(report_string); print("\n" + "="*50 + "\n")
    
    # Salva vídeos com extração desconhecida
    unknown_extraction_data_entries = []
    for entry in music_data:
        if entry.get("artists") == ["Unknown"] or entry.get("song_title") == "Unknown":
            source_playlist = entry.get('genre', ['UnknownSource'])[0] 
            unknown_extraction_data_entries.append(
                f"Título Original: {entry.get('original_youtube_title')}\n"
                f"  Título Processado: {entry.get('processed_title_for_extraction')}\n"
                f"  Extraído: Artista(s)='{', '.join(entry.get('artists', ['Unknown']))}', Música='{entry.get('song_title', 'Unknown')}' (Fonte Extr.: {entry.get('extraction_source')})\n"
                f"  Canal: {entry.get('channel_name')}, Playlist de Origem: {source_playlist}\n"
                f"  URL: {entry.get('youtube_url')}\n"
                f"  ID YouTube: {entry.get('video_id_yt', 'N/A')}\n"
                f"--------------------------------------------------"
            )

    if unknown_extraction_data_entries:
        try:
            with open(unknown_extraction_filename, 'w', encoding='utf-8') as f_unknown:
                for item_str in unknown_extraction_data_entries: f_unknown.write(item_str + "\n")
            print(f"Lista de vídeos com extração 'Unknown' salva em: {unknown_extraction_filename}")
        except Exception as e: print(f"ERRO ao salvar lista de extração unknown: {e}")

    # Salva vídeos pulados
    if skipped_titles_list:
        try:
            with open(skipped_videos_filename, 'w', encoding='utf-8') as f_skipped:
                for title in skipped_titles_list: f_skipped.write(title + "\n")
            print(f"Lista de vídeos pulados salva em: {skipped_videos_filename}")
        except Exception as e: print(f"ERRO ao salvar lista de vídeos pulados: {e}")

    # Salva os dados musicais em JSON
    try:
        with open(output_json_filename, 'w', encoding='utf-8') as f_json: json.dump(music_data, f_json, indent=2, ensure_ascii=False)
        print(f"\nDados salvos com sucesso em {output_json_filename}")
    except Exception as e: print(f"ERRO ao salvar dados em json: {e}")

    # Salva o relatório
    try:
        with open(report_filename, 'w', encoding='utf-8') as f_report: f_report.write(report_string)
        print(f"Relatório salvo em {report_filename}")
    except Exception as e: print(f"ERRO ao salvar relatório: {e}")

# --- END OF FILE process_library_final.py ---