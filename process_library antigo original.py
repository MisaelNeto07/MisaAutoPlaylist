import re
import json
import time
import os
from datetime import datetime

def is_likely_music_video(title_info):
    title_str = title_info['title'].lower()
    original_title_str = title_info['title'] # Para verificações case-sensitive se necessário

    music_keywords = [
        'ft.', 'feat.', 'featuring', 'prod.', 'produced by', 'official video', 'music video',
        'lyric video', 'lyrics', 'official audio', 'audio', 'remix', 'live', 'album',
        'song', 'music', 'track', 'single', 'records', 'official visualizer', 'visualizer',
        'acústico', 'unplugged', 'cover', 'live session', 'tiny desk', 'colors show',
        'clipe oficial', 'pseudo vídeo', 'versão oficial', 'áudio oficial', '(ep)',
        'live at', 'tema de', 'soundtrack', 'ost', 'hd', 'opening', 'ending', 'op', 'ed',
        'parody', 'paródia', 'musical', 'animated music video', 'starbomb', 'the living tombstone',
        'amv', 'mv', # Music Video / Animated Music Video
        'mashup', 'remix', 'medley', 'concerto', 'symphony', 'ballad', 'serenade', 'rhapsody',
        'full version', 'full song', 'pancadão', 'axé music' # Adicionado 'axé music'
    ]
    non_music_keywords_general = [
        'episode', 'review', 'gameplay', 'trailer', 'tutorial', 'vlog',
        'podcast', 'how to', 'unboxing', 'documentary', 'news',
        'commentary', 'preview', 'hfil', 'minecraft', 'tekken',
        'dragon ball', 'street fighter', 'photoshop', 'asmr', # 'dragon ball' é problemático com 'axé music'
        'standup', 'explained', 'science', 'reaction', 'interview',
        'highlights', 'full cast', 'deep dive', 'analysis', 'showcase',
        'old is cool', 'dicas e curiosidades', 'gaveta', 'cortes do flow',
        'nerdologia', 'manual do mundo', 'einerd',
        'recipe', 'cooking', 'kitchen', 'cake', 'food', 'restaurant',
        'mod', 'modpack', 'speedrun', 'walkthrough', 'let\'s play',
        'tier list', 'ranking', 'vs',
        'ufc', 'mma', 'wwe', 'workout', 'fitness', 'bodybuilding',
        'clash royale', 'yu-gi-oh', 'yugioh', 'pokemon', 'magic the gathering',
        'd&d', 'rpg', 'baldurs gate', 'skyrim', 'fallout', 'gta', 'witcher 3', # Adicionado witcher 3
        'financial', 'stocks', 'crypto', 'diy', 'life hack',
        'ytpbr', 'análise', 'guia', 'dicas', 'segredos',
        'reel', 'efeito', 'redesign', 'prompts', 'features', 'updates',
        'platform', 'startup', 'workflow', 'hack', 'tricks',
        'plugin', 'intervalo', 'comerciais', 'coleção de comerciais',
        'aula', 'curso', 'palestra', 'webinar', 'behind the scenes',
        'erros de gravação', 'bloopers', 'deleted scenes',
        'compilado', 'reação', 'react', 'assistindo', 'jogando',
        'legendado'
    ]

    tech_design_non_music_keywords = [
        "davinci resolve", "framer", "chatgpt", "image generator", "openai",
        "ai agents", "comfyui", "gemini 2.5", "ai image/video platform",
        "photoshop running slow", "copy paste colors", "ai news", "text to speech",
        "flux", "n8n", "feedhive", "runway gen-3", "speed ramping", "collage video effect",
        "parallax", "llm in comfyui"
    ]

    # --- Regras de Alta Prioridade ---
    if original_title_str == "Michael Jackson - History": return True
    if "pink guy" in title_str and "teriyaki god" in title_str: return True
    if "mc neguinho itr e mc digu" in title_str and "forte pra dar sorte" in title_str: return True
    if "mc twist e mc brinquedo" in title_str and "ela caiu caillou" in title_str: return True
    if "mc pikachu" in title_str and "tava no fluxo" in title_str: return True

    # Se tiver "MC" E "Prod.", é muito provável que seja música, mesmo com "news", "ep." ou "vlog"
    # Ex: Ep. 134 - MC SID - "Rap News" [Prod. Velho Beats]
    # Ex: MC VV - Daily Vlog (prod. JANGO & LAUNZERA)
    if "mc" in title_str and any(prod_kw in title_str for prod_kw in ['prod.', 'produced by']):
        return True

    if "paródia musical" in title_str: # Ex: Witcher 3 - Trailer Literal - MrPoladoful (Paródia Musical)
        return True
    
    if "axé music" in title_str and "kame kame kame ha" in title_str and "dragon ball" in title_str: # Caso específico
        return True


    if "narrando o clipe" in title_str:
        if " - " in title_str or "#" in original_title_str or \
           any(mkw in title_str for mkw in ['song', 'music', 'clipe', 'parody', 'paródia', 'remix', 'cover', 'ft.', 'feat.']):
            return True
        if "one direction" in title_str and "what makes you beautiful" in title_str:
            return True
        return True

    if any(kw in title_str for kw in tech_design_non_music_keywords): return False
    if "pipoca e nanquim" in title_str or "kitinete hq" in title_str: return False
    if "neil gaiman" in title_str and any(kw in title_str for kw in ["sandman", "cost", "graphic novel", "explained", "interview", "documentary", "stories within us", "success of", "behind the scenes", "first look", "trailer", "audible", "changes from comic", "on netflix"]):
        return False
    if "virtual barber shop" in title_str or "o barbeiro virtual audio 3d" in title_str: return False
    if "ytpbr" in title_str : return False
    if title_str.startswith("como ganhar flexibilidade") or title_str.startswith("alongamento geral básico"): return False
    if "mrpoladoful" in title_str and not any(kw in title_str for kw in ["song", "clipe oficial", "paródia", "musical", "paródia musical"]): return False # Adicionado paródia musical à exceção
    if "asmr" in title_str and not any(kw in title_str for kw in ["song", "music", "singing", "cover"]): return False
    if title_str.startswith("qual endereço você usou"): return False
    if "rogerinho se descontrola #choquedecultura" in title_str: return False
    if "vampire the masquerade" in title_str and "review" in title_str: return False
    if "the death and rebirth of vampire: bloodlines" in title_str: return False
    if "easy dreadlocks styles" in title_str: return False
    if original_title_str == "The Scariest Comic of All Time": return False

    if "starbomb" in title_str or "erB" in original_title_str or "epic rap battles of history" in title_str: return True
    if "the living tombstone" in title_str: return True
    if "paródia" in title_str and any(artist_parody in title_str for artist_parody in ["matuê", "hungria hip hop", "costa gold", "emicouto", "mc vv", "eminem", "rihanna", "pollo", "psy", "alicia keys", "bruno mars", "chainsmokers", "luan santana", "restart"]): return True
    if "leod" in title_str and any(kw in title_str for kw in ["|", "mashup", "remix", "anos 80", "anos 90", "pt.", "ft.", "version", "extended", "kawaii", "club"]): return True
    if any(poze_kw in title_str for poze_kw in ["mc poze nos anos", "say poze", "marlboro poze", "descobridor dos sete pozes", "cheiro de say so", "cheiro de daft punk", "cheiro de pneu queimado", "sopa de macaco"]): return True
    if "smosh" in title_str and "song" in title_str : return True
    if "asdfmovie" in title_str and "song" in title_str: return True
    if "(egoraptor)" in title_str and "minecraft is for everyone" in title_str: return True
    if "tetris rap animated" in title_str: return True
    if "cyberpunk 2077" in title_str and "never fade away" in title_str and "by samurai" in title_str : return True
    if "charlie brown jr" in title_str and "lutar pelo que é meu" in title_str : return True
    if "revelação" in title_str and "velocidade da luz" in title_str: return True
    if "os tincoas" in title_str and "cordeiro de nanã" in title_str : return True
    if "king harvest" in title_str and "dancing in the moonlight" in title_str: return True
    if "terezinha e roque josé" in title_str and "emboladores" in title_str: return True

    anime_op_ed_pattern = r'(?:opening|ending|op|ed)\s*\d*\s*(?:full|version|hd|creditless|ncorp|nced)?\s*(?:\[|﹝|『|「|<|\||$)'
    if re.search(anime_op_ed_pattern, title_str) or \
       (any(anime_name in title_str for anime_name in ["jojo's bizarre adventure", "noragami", "naruto", "one punch man", "toriko", "mirai nikki", "one piece", "death parade"]) and any(op_ed_kw in title_str for op_ed_kw in ["opening", "ending", "op", "ed", "theme"])):
        return True
    if "hello sleepwalkers" in title_str and "午夜の待ち合わせ" in original_title_str: return True
    if "the oral cigarettes" in title_str and "狂乱 hey kids!!" in original_title_str: return True

    # --- Lógica de Decisão Principal Refinada ---
    common_music_pattern_strict = r"^\s*[^-\n\[\(/:·]{2,}\s*(?:-|–|—|:|·|\/)\s*[^-\n\[\(/:·]{2,}"
    common_music_pattern_spaced = r"^\s*[^-\n\[\(/:·]{2,}\s+(?:-|–|—|:|·|\/)\s+[^-\n\[\(/:·]{2,}"
    is_common_artist_song_pattern = re.match(common_music_pattern_spaced, title_str, flags=re.IGNORECASE) or \
                                   re.match(common_music_pattern_strict, original_title_str.replace(':', ' - ', 1).replace('/', ' / '), flags=re.IGNORECASE)

    has_music_keyword = any(keyword in title_str for keyword in music_keywords)
    has_non_music_keyword_general = any(keyword in title_str for keyword in non_music_keywords_general)

    # Caso 1: Padrão "Artista - Música" é forte
    if is_common_artist_song_pattern:
        # Palavras-chave não musicais muito fortes que podem anular o padrão comum
        strong_overriding_non_music = ['tutorial', 'review', 'gameplay', 'vlog', 'podcast', 'documentary', 'commentary', 'explained', 'episode', 'unboxing', 'how to', 'aula', 'curso', 'palestra', 'reação', 'react', 'análise', 'dicas']
        # Palavras-chave musicais muito fortes que podem salvar o padrão comum, mesmo com uma palavra não musical fraca
        very_strong_music_indicators = ['official music video', 'clipe oficial', 'official song', 'album completo', 'full album', 'paródia musical', 'official audio', 'live session', 'acústico']

        # Verifica se há uma palavra-chave não musical forte que anula
        if any(strong_nmk in title_str for strong_nmk in strong_overriding_non_music):
            # Se também tiver um indicador musical muito forte, pode ser música (ex: "Review do Clipe Oficial")
            if any(very_strong_mk in title_str for very_strong_mk in very_strong_music_indicators):
                return True
            return False # Padrão comum anulado por palavra não musical forte
        return True # Padrão comum e sem anulação forte

    # Caso 2: Possui palavras-chave musicais
    if has_music_keyword:
        if has_non_music_keyword_general:
            # Se "paródia" ou "musical" ou "axé music" estão presentes, é provável que seja música,
            # a menos que palavras não musicais muito fortes como 'tutorial' estejam presentes.
            if any(specific_music_type in title_str for specific_music_type in ["paródia", "musical", "axé music"]):
                if not any(nmk_override in title_str for nmk_override in ['tutorial', 'review', 'how to make', 'gameplay', 'documentary', 'explained']):
                    return True
            
            # Lógica original para combinações específicas de palavras-chave não musicais e musicais
            if "tutorial" in title_str and "plugin" in title_str: return False
            if "song" in title_str and any(nm_kw in title_str for nm_kw in ['tutorial', 'review', 'analysis', 'explained', 'how to make', 'ranking', 'behind the scenes']): return False
            if "album" in title_str and any(nm_kw in title_str for nm_kw in ['review', 'analysis', 'unboxing', 'explained']): return False
            if "audio" in title_str and not any(other_music_kw in title_str for other_music_kw in ['song', 'track', 'album', 'remix', 'official audio', 'music']):
                 if any(techy_kw in title_str for techy_kw in ['platform', 'generator', 'text to speech', 'ai news']): return False
            
            # Se chegou até aqui com palavras-chave mistas e não foi classificado como música, é mais seguro pular.
            return False
        return True # Possui palavras-chave musicais e nenhuma não musical

    # Caso 3: Sem palavras-chave musicais fortes, mas talvez seja um título curto conhecido
    short_music_titles_map = {
        "noid": ("Yves Tumor", "Noid"), "not like us": ("Kendrick Lamar", "Not Like Us"),
        "sorry not sorry": ("Demi Lovato", "Sorry Not Sorry"), "wharf talk": ("Tyler, The Creator", "Wharf Talk"),
        "heaven to me": ("Tyler, The Creator", "Heaven To Me"), "dogtooth": ("Tyler, The Creator", "Dogtooth"),
        "corso (audio)": ("Tyler, The Creator", "Corso"),
        "lemonhead (audio)": ("Tyler, The Creator", "Lemonhead"),
        "wusyaname (audio)": ("Tyler, The Creator", "Wusyaname"),
        "i think": ("Tyler, The Creator", "I Think"),
        "a boy is a gun*": ("Tyler, The Creator", "A Boy Is A Gun*"),
        "o oitavo anjo": ("509-E", "O Oitavo Anjo"),
        "remember the time": ("Michael Jackson", "Remember The Time"),
        "that guy": ("Tyler, The Creator", "That Guy"), "squabble up": ("Central Cee", "Squabble Up"),
        "sincronizadamente":("AOM", "Sincronizadamente"),
        "feel this aom moment":("AOM", "Feel This AOM Moment"), "teriyaki god": ("Pink Guy (Joji)", "Teriyaki God")
    }
    if title_str.strip() in short_music_titles_map or original_title_str.strip() in short_music_titles_map:
        return True

    # Caso 4: Sem palavras-chave musicais, mas com palavras-chave não musicais
    if has_non_music_keyword_general:
        return False

    return False # Padrão: se não houver evidência suficiente, não é música


def extract_song_artist_from_title(title_str_original_case):
    title_str_bkp = title_str_original_case
    title_str = title_str_original_case.lower()
    title_str = title_str.replace('—', '-').replace('–', '-').replace('−', '-')

    artist = None
    song_title = None
    featured_artists = []
    producers = []

    def clean_common_tags(text):
        if not isinstance(text, str): return text
        tags_to_remove = [
            'official video', 'music video', 'official audio', 'lyric video', 'lyrics',
            'audio', 'visualizer', 'official visualizer', 'hd', '4k remaster', '4k upgrade',
            'hq', 'full album', 'original version', 'official lyric video', 'official music video',
            'official', 'live', 'original mix', 'remastered', 'video clip', 'clipe oficial',
            'pseudo vídeo', 'versão oficial', 'áudio oficial', 'sub español', 'español',
            'subtitulado', 'legendado(?: pt-br)?', 'promo', 'tradução', 'emboladores',
            'dj kr3', 'dj felipe único', 'lyrics in both', 'the ultimate collection'
        ]
        for tag in tags_to_remove:
            text = re.sub(r'\s*\[\s*' + re.escape(tag) + r'\s*\]\s*', ' ', text, flags=re.IGNORECASE)
            text = re.sub(r'\s*\(\s*' + re.escape(tag) + r'\s*\)\s*', ' ', text, flags=re.IGNORECASE)

        text = re.sub(r'\s*\|\s*(official video|music video|official audio|lyric video|lyrics|audio|visualizer|clipe oficial|legendado(?: pt-br)?|prod[^\)]*)\s*', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*#shorts\s*$', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\[\s*\]\s*|\s*\(\s*\)\s*', ' ', text)
        text = re.sub(r'\s*\(prod[^\)]*\)\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\[prod[^\]]*\]\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\(animated by[^\)]*\)\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\(from the series[^\)]+\)\s*', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\(from[^\)]+\)\s*', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\[[^\]]*soundtrack[^\]]*\]', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*\([^\)]*soundtrack[^\)]*\)', ' ', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*//\s*official music video\s*//.*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+\((?!.*\b(?:feat|ft|prod)\b)[^)]*\)\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+\[(?!.*\b(?:feat|ft|prod)\b)[^\]]*\]\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+\blive\b\s*$', '', text, flags=re.IGNORECASE)
        return text.strip()

    def capitalize_name(name):
        if not name or not isinstance(name, str): return None
        name = name.strip()
        if not name: return None

        words_to_upper = ["MC", "DJ", "JR", "SR", "DR", "AC", "DC", "EV", "MR", "MS", "MD", "XV", "RE", "ST", "II", "III", "IV", "VI", "VII", "VIII", "IX", "XL", "MGMT", "J.I.D", "JID", "IDK", "ITR", "S.J."]
        lowercase_words = ["a", "an", "the", "and", "but", "or", "for", "nor", "on", "at", "to", "from", "by", "with", "in", "of", "e", "de", "do", "da", "dos", "das", "la", "le", "el", "los", "las", "du", "del"]

        parts = []
        for i, word_original_case in enumerate(name.split()):
            word = word_original_case.lower()
            if word_original_case == "S.J." :
                parts.append("S.J.")
                continue
            if word_original_case.upper() in words_to_upper:
                parts.append(word_original_case.upper())
            elif re.match(r"^[a-z]\.[a-z]\.(?:[a-z]\.)?[a-z]?$", word):
                 parts.append(word.upper().replace('.', '.').strip('.'))
            elif re.match(r"^\d+[a-z]+[0-9]*$", word) or re.match(r"^[a-z]+\d+[a-z0-9]*$",word):
                parts.append(word_original_case)
            elif i > 0 and word in lowercase_words:
                parts.append(word)
            else:
                if "'" in word and len(word.split("'")[0]) == 1 and len(word) > 1:
                    sub_parts = word_original_case.split("'")
                    parts.append(sub_parts[0].lower() + "'" + sub_parts[1].capitalize())
                else:
                    parts.append(word_original_case.capitalize())
        return ' '.join(parts)

    # --- Start of specific artist/title rules ---
    if "eminem" in title_str and "without me" in title_str and "official music video" in title_str: # Specific fix
        artist = "Eminem"
        song_title = "Without Me"
        return artist, song_title, featured_artists, producers

    if "epic rap battles of history" in title_str or "erb" in title_str:
        artist = "Epic Rap Battles of History"
        match_erb = re.match(r"(.+?)\s+vs\.?\s+(.+?)(?:\.|$)", title_str_original_case, re.IGNORECASE)
        if match_erb: song_title = f"{capitalize_name(match_erb.group(1).strip())} vs {capitalize_name(match_erb.group(2).strip())}"
        else: song_title = re.sub(r'\s*\.\s*epic rap battles of history.*$', '', title_str_original_case, flags=re.IGNORECASE).strip()
        return artist, song_title, [], []

    specific_artists_map = { "starbomb": "Starbomb", "the living tombstone": "The Living Tombstone", "egoraptor": "Egoraptor" }
    for key, art_name in specific_artists_map.items():
        if key in title_str:
            artist = art_name
            temp_song_title_val = title_str_original_case
            if f"({key})" in temp_song_title_val.lower():
                temp_song_title_val = re.sub(r'\s*\(' + re.escape(key) + r'\)\s*', ' ', temp_song_title_val, flags=re.IGNORECASE)
            elif f"{key} -" in temp_song_title_val.lower():
                 temp_song_title_val = temp_song_title_val.lower().split(f"{key} -",1)[-1]
            temp_song_title_val = clean_common_tags(temp_song_title_val)
            if " - " in temp_song_title_val: temp_song_title_val = temp_song_title_val.split(" - ",1)[0]
            song_title = temp_song_title_val.strip()
            if key == "starbomb":
                if "by grind3h" in title_str and "pokerap" in title_str: song_title = "The New Pokerap"
                elif "animated by" in title_str:
                     song_title = title_str.split("animated by")[0].strip("- ")
                     if "starbomb" in song_title.lower(): song_title = song_title.lower().split("starbomb -",1)[-1].strip()
                if "overwatch rap music video" in title_str: song_title = "Overwatch Rap"
                if "vegeta's serenade" in title_str : song_title = "Vegeta's Serenade"
                if "robots in need of disguise" in title_str: song_title = "Robots in Need of Disguise"
            elif key == "the living tombstone" and "no mercy" in title_str and "overwatch" in title_str:
                song_title = "No Mercy (Overwatch Song)"
            elif key == "egoraptor" and "minecraft is for everyone" in title_str:
                song_title = "Minecraft Is For Everyone"
            if not song_title or song_title == key : song_title = "Unknown"
            return artist, song_title, featured_artists, producers

    if any(k in title_str for k in ["| leod", "leod -", "leod mashup", "leod remix", "leod anos", "mc poze nos anos", "say poze", "marlboro poze", "descobridor dos sete pozes", "doki doki mc poze", "doki doki popotão", "cheiro de kimi no toriko", "rei do kuduro", "sopa de macaco", "cheiro de pneu", "cheiro de say so", "cheiro de tame impala", "cheiro de daft punk", "cheiro de friends", "cheiro de ben 10", "vulgofk -", "bactéria get lucky", "blinding azeitona", "shake it bololô"]):
        artist = "LEOD"
        song_title_val = title_str_original_case
        song_title_val = re.sub(r'(\||-) leod.*$', '', song_title_val, flags=re.IGNORECASE).strip()
        song_title_val = re.sub(r'\s*pt\.\s*\w+', '', song_title_val, flags=re.IGNORECASE).strip()
        song_title_val = re.sub(r'\s*\(.*version\)', '', song_title_val, flags=re.IGNORECASE).strip()
        if "vulgofk -" in song_title_val.lower(): song_title_val = song_title_val.lower().split("vulgofk -",1)[-1].strip()
        if "bactéria get lucky" in song_title_val.lower(): song_title_val = "Bactéria Get Lucky"
        if "blinding azeitona" in song_title_val.lower(): song_title_val = "Blinding Azeitona"
        if "shake it bololô" in song_title_val.lower(): song_title_val = "Shake It Bololô"
        song_title = clean_common_tags(song_title_val)
        return artist, song_title, [], []

    if "pink guy (joji)" in title_str and "teriyaki god" in title_str:
        artist = "Pink Guy (Joji)"; song_title = "Teriyaki God"; return artist, song_title, [], []
    if "mc neguinho itr e mc digu" in title_str and "forte pra dar sorte" in title_str:
        artist = "MC Neguinho ITR e MC Digu"; song_title = "Forte pra Dar Sorte"
        if "(dj kr3)" in title_str: featured_artists.append("DJ KR3")
        return artist, song_title, featured_artists, producers
    if "mc pikachu" in title_str and "tava no fluxo" in title_str:
        artist = "MC Pikachu"; song_title = "Tava no Fluxo"
        if "(dj felipe único)" in title_str: featured_artists.append("DJ Felipe Único")
        return artist, song_title, featured_artists, producers
    if "mc twist e mc brinquedo" in title_str and "ela caiu caillou" in title_str:
        artist = "MC Twist e MC Brinquedo"; song_title = "Ela Caiu Caillou"; return artist, song_title, featured_artists, producers
    if "terezinha e roque josé" in title_str and "emboladores" in title_str and "dona terezinha e roque" in title_str:
        artist = "Terezinha e Roque José (Emboladores)"; song_title = "Dona Terezinha e Roque"; return artist, song_title, [], []

    if "michael jackson" in title_str and "the ultimate collection" in title_str:
        artist = "Michael Jackson"
        cleaned_for_mj = clean_common_tags(title_str_original_case.replace("[HD]", ""))
        song_cand_match1 = re.match(r"^\s*(?:\d+\s+)?(.+?)\s*-\s*michael jackson\s*-\s*the ultimate collection", cleaned_for_mj, re.IGNORECASE)
        if song_cand_match1: song_title = song_cand_match1.group(1).strip()
        else:
            song_cand_match2 = re.match(r"michael jackson\s*-\s*(.+?)\s*-\s*the ultimate collection", cleaned_for_mj, re.IGNORECASE)
            if song_cand_match2: song_title = song_cand_match2.group(1).strip()
        if song_title: return capitalize_name(artist), capitalize_name(clean_common_tags(song_title)), featured_artists, producers
    # --- End of specific artist/title rules ---

    temp_title_str_main_extraction = title_str_original_case
    non_feat_prod_parts = []
    last_match_end = 0
    all_matches = []
    ft_pattern = r'(ft\.|feat\.|featuring|with)\s*([\w\s,&\'./+~-]+?(?=\s*\(|\s*\[|\s*\||$|\s+prod\.|\s+prod by|\s+x\s+[\w\s]|\s+vs\.))'
    prod_pattern = r'(prod\.|produced by)\s*([\w\s,&\'./+~-]+?(?=\s*\(|\s*\[|\s*\||$))'

    for match in re.finditer(ft_pattern, temp_title_str_main_extraction, flags=re.IGNORECASE): all_matches.append({'match': match, 'type': 'feat'})
    for match in re.finditer(prod_pattern, temp_title_str_main_extraction, flags=re.IGNORECASE): all_matches.append({'match': match, 'type': 'prod'})
    all_matches.sort(key=lambda m: m['match'].start())

    for item in all_matches:
        match = item['match']
        match_type = item['type']
        non_feat_prod_parts.append(temp_title_str_main_extraction[last_match_end:match.start()])
        last_match_end = match.end()
        items_str = match.group(2).strip()
        split_regex = r'\s*,\s*|\s*&\s*|\s+e\s+|\s+and\s+'
        if match_type == 'feat': split_regex += r'|\s+with\s+'
        new_items = [it.strip() for it in re.split(split_regex, items_str) if it.strip() and it.lower() not in ['x', 'vs']]
        if match_type == 'feat': featured_artists.extend(new_items)
        else: producers.extend(new_items)
    non_feat_prod_parts.append(temp_title_str_main_extraction[last_match_end:])
    main_title_candidate = "".join(non_feat_prod_parts).strip()
    main_title_candidate_cleaned = clean_common_tags(main_title_candidate)

    if artist and song_title: pass
    elif main_title_candidate_cleaned:
        parts = []
        separators_to_try = [r"\s+-\s+", r"\s+:\s+", r"\s+\|\s+", r"\s+/\s+", r"\s+X\s+"] # "X" com espaços como separador
        for sep_regex in separators_to_try:
            match_obj = re.match(r"(.+?)" + sep_regex + r"(.+)", main_title_candidate_cleaned, re.IGNORECASE)
            if match_obj:
                parts = [match_obj.group(1).strip(), match_obj.group(2).strip()]
                break
        if not parts and "-" in main_title_candidate_cleaned and main_title_candidate_cleaned.count('-') == 1 and \
           re.match(r"^[^- \t\n\r\f\v]+-[^- \t\n\r\f\v]+$", main_title_candidate_cleaned):
             parts = [p.strip() for p in main_title_candidate_cleaned.split("-", 1)]

        if len(parts) == 2:
            part1, part2 = parts
            part1 = clean_common_tags(part1); part2 = clean_common_tags(part2)
            artist_keywords_list = ["band", "project", "dj", "mc", "squad", "trio", "duo", "ensemble", "orquestra", "choir", "group", "clan", "mob", "clvb", "vs"]
            song_keywords_strict_list = ["song", "track", "theme", "anthem", "concerto", "symphony", "ballad", "serenade", "interlude", "prelude", "overture", "rhapsody", "suite", "remix", "live", "version", "cover", "acoustic", "medley", "session", "parody", "paródia", "opening", "ending", "soundtrack", "ost", "mix", "legendado", "lyrics", "tradução"]
            part1_has_artist_ind = any(akw in part1.lower() for akw in [",", "&", " e ", " x ", " ft.", " feat.", " with"])
            part2_has_artist_ind = any(akw in part2.lower() for akw in [",", "&", " e ", " x ", " ft.", " feat.", " with"])

            if part1_has_artist_ind and not part2_has_artist_ind and len(part2.split()) < 6 : artist, song_title = part1, part2
            elif not part1_has_artist_ind and part2_has_artist_ind and len(part1.split()) < 6: artist, song_title = part2, part1
            else:
                p1_is_art_kw = any(akw in part1.split() for akw in artist_keywords_list)
                p2_is_art_kw = any(akw in part2.split() for akw in artist_keywords_list)
                p1_is_song_kw = any(skw in part1.lower() for skw in song_keywords_strict_list)
                p2_is_song_kw = any(skw in part2.lower() for skw in song_keywords_strict_list)
                if "yun li" in part1.lower(): artist, song_title = part1, part2
                elif "yun li" in part2.lower(): artist, song_title = part2, part1
                elif p1_is_art_kw and not p2_is_art_kw: artist, song_title = part1, part2
                elif p2_is_art_kw and not p1_is_art_kw: artist, song_title = part2, part1
                elif p2_is_song_kw and not p1_is_song_kw: artist, song_title = part1, part2
                elif p1_is_song_kw and not p2_is_song_kw: artist, song_title = part2, part1
                elif len(part1.split()) <= len(part2.split()) and len(part1.split()) <= 5 and not p1_is_song_kw : artist, song_title = part1, part2
                elif len(part2.split()) < len(part1.split()) and len(part2.split()) <= 5 and not p2_is_song_kw : artist, song_title = part2, part1
                else: artist, song_title = part1, part2
        elif not artist:
            cleaned_lookup_title = clean_common_tags(main_title_candidate.lower())
            short_music_map = {
                "noid": ("Yves Tumor", "Noid"), "not like us": ("Kendrick Lamar", "Not Like Us"),
                "sorry not sorry": ("Demi Lovato", "Sorry Not Sorry"), "wharf talk": ("Tyler, The Creator", "Wharf Talk"),
                "heaven to me": ("Tyler, The Creator", "Heaven To Me"), "dogtooth": ("Tyler, The Creator", "Dogtooth"),
                "wusyaname": ("Tyler, The Creator", "Wusyaname"), "lemonhead": ("Tyler, The Creator", "Lemonhead"),
                "corso": ("Tyler, The Creator", "Corso"), "i think": ("Tyler, The Creator", "I Think"),
                "a boy is a gun*": ("Tyler, The Creator", "A Boy Is A Gun*"), "o oitavo anjo": ("509-E", "O Oitavo Anjo"),
                "remember the time": ("Michael Jackson", "Remember The Time"), "velocidade da luz": ("Revelação", "Velocidade da Luz"),
                "onda onda (olha a onda)": ("Tchakabum", "Onda Onda (Olha a Onda)"), "mr bombastic": ("Shaggy", "Boombastic"),
                "indian moonlight": ("S. J. Jananiy", "Indian Moonlight"), "bonfire/cursed images meme": ("Shikoku Meeting", "Bonfire"),
                "teriyaki god": ("Pink Guy (Joji)", "Teriyaki God"), "o sino da igrejinha": ("Unknown", "O Sino da Igrejinha"),
                "st chroma x rah tah tah": ("ST CHROMA", "Rah Tah Tah"), "canto para mãe iemanjá e mãe oxum": ("Unknown", "Canto Para Mãe Iemanjá e Mãe Oxum"),
                "death to the world": ("Unknown", "Death To The World"), "dedo no cu e gritaria": ("Unknown", "Dedo no Cu e Gritaria"),
                "ly o lay ale loya (circle dance) ~ native song": ("Native Song Circle", "Ly O Lay Ale Loya (Circle Dance)"),
                "mademoiselle noir": ("Unknown", "Mademoiselle Noir"),
                "rock around the clock-bill haley-original song-1955": ("Bill Haley & His Comets", "Rock Around the Clock"),
                "tetris rap animated": ("Starbomb", "Tetris Rap")
            }
            if cleaned_lookup_title in short_music_map: artist, song_title = short_music_map[cleaned_lookup_title]
            elif "narrando o clipe" in main_title_candidate.lower():
                if "one direction" in main_title_candidate.lower() and "what makes you beautiful" in main_title_candidate.lower():
                    artist = "One Direction"; song_title = "What Makes You Beautiful (Narrando o Clipe)"
                else:
                    artist = "Narrando o Clipe"; song_title = re.sub(r'narrando o clipe\s*', '', main_title_candidate, flags=re.IGNORECASE).strip("- ")
            elif not artist: song_title = main_title_candidate_cleaned; artist = "Unknown"
    elif not artist and not song_title:
        song_title = clean_common_tags(title_str_original_case); artist = "Unknown"

    artist_final = capitalize_name(artist) if artist else "Unknown"
    song_title_final = capitalize_name(song_title) if song_title else "Unknown"

    if isinstance(song_title_final, str):
        song_title_final = re.sub(r'\s*\((?:Audio|Lyrics|Official|Video|Music|Lyric|Visualizer|Remix|Live|Version|Cover|Parody|Traduzido|Legendado|HD|4K|EP|Emboladores|DJ KR3|DJ Felipe Único|The Ultimate Collection)\s*\)\s*$', '', song_title_final, flags=re.IGNORECASE).strip()
        song_title_final = re.sub(r'\s*\[(?:Audio|Lyrics|Official|Video|Music|Lyric|Visualizer|Remix|Live|Version|Cover|Parody|Traduzido|Legendado|HD|4K|EP|Emboladores|The Ultimate Collection)\s*\]\s*$', '', song_title_final, flags=re.IGNORECASE).strip()
        song_title_final = re.sub(r'\s*\(\s*\)\s*|\s*\[\s*\]\s*', '', song_title_final).strip()
        song_title_final = re.sub(r'\s+\((?!.*\b(?:feat|ft|prod)\b)[^)]*\)\s*$', '', song_title_final, flags=re.IGNORECASE).strip()
        song_title_final = re.sub(r'\s+\[(?!.*\b(?:feat|ft|prod)\b)[^\]]*\]\s*$', '', song_title_final, flags=re.IGNORECASE).strip()
        song_title_final = re.sub(r'\s+\blive\b\s*$', '', song_title_final, flags=re.IGNORECASE).strip()

    featured_artists_final = sorted(list(set(filter(None, [capitalize_name(fa) for fa in featured_artists if fa]))))
    producers_final = sorted(list(set(filter(None, [capitalize_name(p) for p in producers if p]))))

    if not song_title_final or song_title_final.lower() == "unknown": song_title_final = "Unknown"
    if not artist_final or artist_final.lower() == "unknown": artist_final = "Unknown"

    if artist_final == title_str_original_case and song_title_final == "Unknown":
        artist_final = "Unknown"; song_title_final = capitalize_name(clean_common_tags(title_str_original_case))

    if artist_final != "Unknown" and isinstance(song_title_final, str):
        # This block tries to remove feat/prod from song title if they were missed
        # However, it might be too aggressive or redundant if main extraction is good.
        # Consider simplifying or ensuring it doesn't remove valid song title parts.
        pass # Placeholder for potential refinement or removal of this block if causing issues

    if artist_final == "Unknown" and isinstance(song_title_final, str):
        common_separators = [" - ", " : ", " | ", " / ", " X "]
        for sep in common_separators:
            if sep in song_title_final:
                parts_fallback = song_title_final.split(sep, 1)
                if len(parts_fallback[0].split()) <= 5 and len(parts_fallback[0].split()) > 0 and len(parts_fallback[0]) < 35:
                    potential_artist = capitalize_name(parts_fallback[0].strip())
                    potential_song = capitalize_name(parts_fallback[1].strip())
                    if potential_artist and potential_song and potential_artist.lower() != "unknown":
                         artist_final = potential_artist; song_title_final = potential_song; break
    if artist_final and " x " in artist_final.lower():
        if not (artist_final.lower() == "lil nas x" or (artist_final.lower().endswith(" x") and len(artist_final.split())==1)):
            sub_artists = [capitalize_name(sa.strip()) for sa in re.split(r'\s+x\s+', artist_final, flags=re.IGNORECASE)]
            if len(sub_artists) > 1 and all(sub_artists): artist_final = ", ".join(sub_artists)

    if isinstance(artist_final, str) and ", Unknown" in artist_final: artist_final = artist_final.replace(", Unknown", "").strip()
    if isinstance(artist_final, str) and "Unknown, " in artist_final: artist_final = artist_final.replace("Unknown, ", "").strip()

    if artist_final and artist_final != "Unknown":
        main_artist_names_list = [a.strip().lower() for a in re.split(r'\s*,\s*|\s*&\s*|\s+e\s+|\s+and\s+', artist_final)]
        featured_artists_final = [fa for fa in featured_artists_final if not (capitalize_name(fa) and capitalize_name(fa).lower() in main_artist_names_list)]
        producers_final = [p for p in producers_final if not (capitalize_name(p) and capitalize_name(p).lower() in main_artist_names_list)]


    if artist_final == "Unknown" and song_title_final != "Unknown" and " - " in song_title_final:
        parts_last_chance = song_title_final.split(" - ", 1)
        if len(parts_last_chance[0].split()) < 4 and len(parts_last_chance[0]) > 0 :
            artist_final = capitalize_name(parts_last_chance[0]); song_title_final = capitalize_name(parts_last_chance[1])

    return artist_final, song_title_final, featured_artists_final, producers_final

def enrich_track_details_with_search(track_info, concise_search_tool):
    artist = track_info.get("artist")
    song_title = track_info.get("song_title")
    if not artist or artist == "Unknown" or not song_title or song_title == "Unknown":
        return False
    return True

def concise_search(query: str, max_num_results: int = 3):
  pass

def process_youtube_library(video_titles_text, concise_search_tool_func):
    start_time = time.time()
    processed_music = []
    skipped_video_titles = []
    if isinstance(video_titles_text, str): lines = video_titles_text.strip().split('\n')
    elif isinstance(video_titles_text, list): lines = video_titles_text
    else: lines = []

    total_videos_processed = 0; music_videos_identified = 0; videos_skipped_not_music = 0
    music_extraction_successful = 0; music_extraction_failed_artist = 0; music_extraction_failed_song = 0
    music_extraction_fully_failed = 0; passed_to_mock_search = 0; errors_during_processing = 0

    for line_num, line_content in enumerate(lines):
        total_videos_processed += 1
        cleaned_line_content = str(line_content).strip() if line_content is not None else ""
        if not cleaned_line_content:
            videos_skipped_not_music +=1; skipped_video_titles.append(f"[EMPTY LINE at original line {line_num+1}]"); continue
        video_info_dict = {"title": cleaned_line_content, "original_title": str(line_content).strip(), "youtube_url": f"https://www.youtube.com/watch?v=placeholder_for_line_{line_num+1}", "channel_name": "Unknown"}
        try:
            if is_likely_music_video(video_info_dict):
                music_videos_identified += 1
                artist, song_title_extracted, ft, prod = extract_song_artist_from_title(video_info_dict["original_title"])
                music_entry = {
                    "original_youtube_title": video_info_dict["original_title"], "artist": artist if artist else "Unknown",
                    "song_title": song_title_extracted if song_title_extracted else "Unknown", "featured_artists": ft, "producers": prod,
                    "album": None, "release_year": None, "genre": [], "youtube_url": video_info_dict["youtube_url"],
                    "spotify_url": None, "language": None, "country_of_origin": None, "other_info": {}
                }
                is_artist_unknown = (music_entry["artist"] == "Unknown")
                is_song_unknown = (music_entry["song_title"] == "Unknown" or not music_entry["song_title"])
                if not is_artist_unknown and not is_song_unknown: music_extraction_successful += 1
                else:
                    if is_artist_unknown and is_song_unknown: music_extraction_fully_failed +=1
                    if is_artist_unknown: music_extraction_failed_artist += 1
                    if is_song_unknown: music_extraction_failed_song +=1
                if enrich_track_details_with_search(music_entry, concise_search_tool_func): passed_to_mock_search +=1
                processed_music.append(music_entry)
            else:
                videos_skipped_not_music += 1; skipped_video_titles.append(video_info_dict['original_title'])
        except Exception as e:
            errors_during_processing += 1; skipped_video_titles.append(f"[ERROR SKIPPING] {video_info_dict['original_title']} (Error: {e})")
    end_time = time.time(); processing_duration = end_time - start_time
    report = [
        "--- SCRIPT EXECUTION REPORT ---", f"Processing Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}",
        f"Processing End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}", f"Total Processing Duration: {processing_duration:.2f} seconds",
        "\n--- Video Processing Summary ---", f"Total video titles read from input: {total_videos_processed}",
        f"Videos identified as music: {music_videos_identified}", f"Videos skipped (classified as non-music, empty, or error during skip): {videos_skipped_not_music}",
        "\n--- Music Information Extraction (for identified music videos) ---", f"Successfully extracted Artist AND Song title: {music_extraction_successful}",
        f"Artist could not be determined (marked 'Unknown'): {music_extraction_failed_artist}", f"Song title could not be determined (marked 'Unknown'): {music_extraction_failed_song}",
        f"Both Artist AND Song title were 'Unknown': {music_extraction_fully_failed}", "Note: 'Artist/Song could not be determined' counts may overlap if both failed for the same track.",
        "\n--- Data Enrichment (Mock Search) ---", f"Music entries passed to MOCK search function: {passed_to_mock_search}",
        "IMPORTANT: The search function ('enrich_track_details_with_search') is currently a MOCK.", "Fields like 'album', 'release_year', 'genre', 'spotify_url' remain 'None' or empty unless manually filled.",
        "\n--- Errors ---", f"Errors encountered during processing of individual lines: {errors_during_processing}",
        "\n--- Output ---", "Structured music data saved to: [output_folder_path]/music_data.json",
        "List of videos with 'Unknown' artist OR 'Unknown' song saved to: [output_folder_path]/unknown_extraction_videos.txt",
        "List of skipped videos saved to: [output_folder_path]/skipped_videos.txt", "This report saved to: [output_folder_path]/processing_report.txt",
        "\n--- Recommendations ---"
    ]
    if music_extraction_failed_artist > 0 or music_extraction_failed_song > 0 :
        report.append("- Review titles where artist/song extraction failed (see 'unknown_extraction_videos.txt' in the output folder). The 'extract_song_artist_from_title' function might need refinement.")
    if videos_skipped_not_music > 0 :
         report.append("- Review 'skipped_videos.txt' in the output folder. If actual music videos were skipped, the 'is_likely_music_video' heuristics and keywords need adjustment.")
    report.append("- For actual data enrichment, replace the mock 'concise_search' function with a real search implementation.")
    return processed_music, "\n".join(report), skipped_video_titles

if __name__ == "__main__":
    input_filename = "My YouTube Library.txt"
    now = datetime.now()
    output_folder_name = now.strftime("%Y-%m-%d_%H-%M-%S") + "_run_v7_correcoes"
    output_directory_path = output_folder_name
    if not os.path.exists(output_directory_path):
        os.makedirs(output_directory_path); print(f"Created output directory: {output_directory_path}")
    output_json_filename = os.path.join(output_directory_path, "music_data.json")
    unknown_extraction_filename = os.path.join(output_directory_path, "unknown_extraction_videos.txt")
    skipped_videos_filename = os.path.join(output_directory_path, "skipped_videos.txt")
    report_filename = os.path.join(output_directory_path, "processing_report.txt")
    try:
        with open(input_filename, "r", encoding="utf-8") as f: youtube_library_content = f.read()
    except FileNotFoundError:
        print(f"ERROR: Input file '{input_filename}' not found."); youtube_library_content = ""
        print(f"WARNING: Input file '{input_filename}' not found. Proceeding with empty content.")
    except Exception as e: print(f"ERROR reading input file '{input_filename}': {e}"); exit()
    music_data, report_string, skipped_titles_list = process_youtube_library(youtube_library_content, concise_search)
    report_string = report_string.replace("[output_folder_path]", output_directory_path)
    print("\n" + "="*50 + "\n"); print(report_string); print("\n" + "="*50 + "\n")
    unknown_extraction_data_titles = []
    for entry in music_data:
        if entry.get("artist") == "Unknown" or entry.get("song_title") == "Unknown":
            unknown_extraction_data_titles.append(entry.get("original_youtube_title"))
    if unknown_extraction_data_titles:
        try:
            with open(unknown_extraction_filename, 'w', encoding='utf-8') as f_unknown:
                for title in unknown_extraction_data_titles: f_unknown.write(title + "\n")
            print(f"Lista de vídeos com extração 'Unknown' (artista ou música) salva em: {unknown_extraction_filename}")
        except Exception as e: print(f"ERROR saving unknown extraction list to '{unknown_extraction_filename}': {e}")
    if skipped_titles_list:
        try:
            with open(skipped_videos_filename, 'w', encoding='utf-8') as f_skipped:
                for title in skipped_titles_list: f_skipped.write(title + "\n")
            print(f"Lista de vídeos pulados salva em: {skipped_videos_filename}")
        except Exception as e: print(f"ERROR saving skipped videos list to '{skipped_videos_filename}': {e}")
    try:
        with open(output_json_filename, 'w', encoding='utf-8') as f_json: json.dump(music_data, f_json, indent=2, ensure_ascii=False)
        print(f"\nData successfully saved to {output_json_filename}")
    except Exception as e: print(f"ERROR saving data to '{output_json_filename}': {e}")
    try:
        with open(report_filename, 'w', encoding='utf-8') as f_report: f_report.write(report_string)
        print(f"Report saved to {report_filename}")
    except Exception as e: print(f"ERROR saving report to '{report_filename}': {e}")

