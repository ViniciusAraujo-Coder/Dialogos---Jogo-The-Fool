import pygame
import sys
import os
import math

# ═══════════════════════════════════════════════════════════════
#  CENA DE DIÁLOGO — VINNY (The Fool)
#  Universidade São Judas Tadeu
# ═══════════════════════════════════════════════════════════════

pygame.init()
pygame.mixer.init()

# ── Resolução base e janela ───────────────────────────────────
BASE_W, BASE_H = 1280, 720   # resolução de design
LARGURA, ALTURA = BASE_W, BASE_H
FPS = 60

# Surface de render sempre em resolução base; escala para tela inteira no fullscreen
render_surf = pygame.Surface((BASE_W, BASE_H))
tela        = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("The Fool — Vinny")
clock = pygame.time.Clock()

fullscreen = False

def toggle_fullscreen():
    global tela, fullscreen, LARGURA, ALTURA
    fullscreen = not fullscreen
    if fullscreen:
        tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        tela = pygame.display.set_mode((BASE_W, BASE_H))
    LARGURA, ALTURA = tela.get_size()

def blit_scaled(destino, fonte):
    """Escala render_surf (BASE_W×BASE_H) para preencher destino."""
    dw, dh = destino.get_size()
    if (dw, dh) == (BASE_W, BASE_H):
        destino.blit(fonte, (0, 0))
    else:
        scaled = pygame.transform.smoothscale(fonte, (dw, dh))
        destino.blit(scaled, (0, 0))

def mouse_em_base():
    """Converte posição real do mouse para coordenadas da surface de base."""
    mx, my = pygame.mouse.get_pos()
    sw, sh = tela.get_size()
    bx = int(mx * BASE_W / sw)
    by = int(my * BASE_H / sh)
    return (bx, by)

# Cores
COR_NOME_NPC     = (255, 210, 80)
COR_NOME_JOGADOR = (255, 255, 255)
COR_TEXTO_NPC    = (255, 230, 150)
COR_TEXTO_JOG    = (220, 220, 220)
COR_OPCAO_NORMAL = (180, 180, 180)
COR_OPCAO_HOVER  = (255, 255, 180)
BORDA            = (200, 200, 200)

# Fontes (tamanho relativo ao BASE_W)
fonte_nome  = pygame.font.SysFont("Courier New", 22, bold=True)
fonte_texto = pygame.font.SysFont("Courier New", 26)
fonte_opcao = pygame.font.SysFont("Courier New", 22)
fonte_dica  = pygame.font.SysFont("Courier New", 16)
fonte_hint  = pygame.font.SysFont("Courier New", 18, bold=True)

# ═══════════════════════════════════════════════════════════════
#  ASSETS
# ═══════════════════════════════════════════════════════════════

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))

def caminho(subpasta, nome):
    return os.path.join(PASTA_BASE, subpasta, nome)

SPRITES = {
    "sentado_com_taco": caminho("imgs_vinny", "Sentado_com_taco.png"),
    "sentado_sem_taco": caminho("imgs_vinny", "Sentado_sem_taco.png"),
    "surpreso":         caminho("imgs_vinny", "Vini_Surpreso.png"),
    "confiante":        caminho("imgs_vinny", "Vini_Confiante.png"),
    "confuso":          caminho("imgs_vinny", "Vini_Confuso.png"),
    "preocupado":       caminho("imgs_vinny", "Vini_Preocupado.png"),
    "entregando_taco":  caminho("imgs_vinny", "Vini_Entregando_Taco.png"),
}

SONS = {
    "ambiente":     caminho("sons_vinny", "ambiente_quarto.mp3"),
    "entrega_taco": caminho("sons_vinny", "entrega_taco.mp3"),
    "muda_humor":   caminho("sons_vinny", "muda_humor.mp3"),
}
VOLUME = {"ambiente": 0.2, "entrega_taco": 0.8, "muda_humor": 0.5}

def carregar_som(chave):
    try:
        s = pygame.mixer.Sound(SONS[chave])
        s.set_volume(VOLUME[chave])
        return s
    except Exception:
        print(f"[AVISO] Som não encontrado: {SONS.get(chave,'?')}")
        return None


# ═══════════════════════════════════════════════════════════════
#  REVELAÇÃO DE NOME GLITCHADO
# ═══════════════════════════════════════════════════════════════

nome_vinny_revelado   = False
_GLITCH_FRAMES_VINNY  = ["???", "#̷@̵?̶", "█▓▒░", "▓█?▒", "??!"]

def nome_exibido_vinny(nome):
    if nome == "Vinny" and not nome_vinny_revelado:
        idx = (pygame.time.get_ticks() // 300) % len(_GLITCH_FRAMES_VINNY)
        return _GLITCH_FRAMES_VINNY[idx]
    return nome

def revelar_nome_vinny():
    global nome_vinny_revelado
    nome_vinny_revelado = True


# ═══════════════════════════════════════════════════════════════
#  GERENCIADOR DE SPRITES  (sempre em BASE_W × BASE_H)
# ═══════════════════════════════════════════════════════════════

class GerenciadorSprite:
    def __init__(self):
        self.sprites = {}
        self.atual = self.chave_atual = None
        self._carregar()

    def _carregar(self):
        for chave, path in SPRITES.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (BASE_W, BASE_H))
                self.sprites[chave] = img
            except FileNotFoundError:
                ph = pygame.Surface((BASE_W, BASE_H)); ph.fill((20,20,30))
                self.sprites[chave] = ph
        self.set_sprite("sentado_com_taco")

    def set_sprite(self, chave):
        if chave in self.sprites and chave != self.chave_atual:
            self.atual = self.sprites[chave]
            self.chave_atual = chave
            if chave in ("surpreso", "preocupado"):
                som = carregar_som("muda_humor")
                if som: som.play()

    def desenhar(self, surf):
        if self.atual:
            surf.blit(self.atual, (0, 0))


# ═══════════════════════════════════════════════════════════════
#  HITBOX DO VINNY — calibrada pela imagem Espaço_HitBox.jpg
#  (ref 1190×893 → retângulo vermelho ≈ x:440 y:415 w:250 h:225)
#  Em proporção: x≈37% y≈46% w≈21% h≈25%  (sobre BASE_W/BASE_H)
# ═══════════════════════════════════════════════════════════════

HITBOX_VINNY = pygame.Rect(
    int(BASE_W * 0.46),   # x  ← ajuste aqui se precisar
    int(BASE_H * 0.465),   # y
    int(BASE_W * 0.15),   # largura
    int(BASE_H * 0.255),   # altura
)


# ═══════════════════════════════════════════════════════════════
#  CAIXA DE DIÁLOGO
# ═══════════════════════════════════════════════════════════════

class CaixaDialogo:
    VEL_PADRAO   = 2
    CAIXA_L      = 900
    CAIXA_H      = 160
    MARGEM_BTM   = 24
    PADDING      = 18

    def __init__(self, nome, texto, velocidade=None):
        self.nome = nome
        self.texto = texto
        self.velocidade = velocidade if velocidade is not None else self.VEL_PADRAO
        self.texto_visivel = ""
        self.indice = self.contador = 0
        self.completo = False

    def atualizar(self):
        if self.completo: return
        self.contador += 1
        if self.contador >= self.velocidade:
            self.contador = 0
            if self.indice < len(self.texto):
                self.texto_visivel += self.texto[self.indice]
                self.indice += 1
            else:
                self.completo = True

    def pular(self):
        self.texto_visivel = self.texto
        self.indice = len(self.texto)
        self.completo = True

    def _cor_nome(self):
        return COR_NOME_JOGADOR if self.nome == "S/N" else COR_NOME_NPC

    def _cor_texto(self):
        return COR_TEXTO_JOG if self.nome == "S/N" else COR_TEXTO_NPC

    def desenhar(self, surf, offset_y=0, alpha=255):
        cw, ch = self.CAIXA_L, self.CAIXA_H
        cx = (BASE_W - cw) // 2
        cy = BASE_H - ch - self.MARGEM_BTM + offset_y
        p  = self.PADDING

        tmp = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)
        af  = int(180 * alpha / 255)

        fundo = pygame.Surface((cw, ch), pygame.SRCALPHA)
        fundo.fill((0, 0, 0, af))
        tmp.blit(fundo, (cx, cy))
        pygame.draw.rect(tmp, (*BORDA, alpha), (cx, cy, cw, ch), 2)

        nome_display = nome_exibido_vinny(self.nome)
        nome_surf    = fonte_nome.render(nome_display, True, self._cor_nome())
        nb_w = nome_surf.get_width() + 20
        nb_h = nome_surf.get_height() + 8
        nx, ny = cx, cy - nb_h - 2

        nb = pygame.Surface((nb_w, nb_h), pygame.SRCALPHA)
        nb.fill((0, 0, 0, af))
        tmp.blit(nb, (nx, ny))
        pygame.draw.rect(tmp, (*BORDA, alpha), (nx, ny, nb_w, nb_h), 2)
        na = pygame.Surface(nome_surf.get_size(), pygame.SRCALPHA)
        na.blit(nome_surf, (0, 0))
        na.set_alpha(alpha)
        tmp.blit(na, (nx + 10, ny + 4))

        self._render_texto(tmp, self.texto_visivel,
                           cx+p, cy+p, cw-p*2, ch-p*2, alpha)

        if self.completo and alpha == 255:
            if (pygame.time.get_ticks() // 500) % 2:
                d = fonte_dica.render("▼", True, BORDA)
                tmp.blit(d, (cx+cw-d.get_width()-p, cy+ch-d.get_height()-8))

        surf.blit(tmp, (0, 0))

    def _render_texto(self, surf, texto, x, y, lmax, hmax, alpha):
        palavras = texto.split(" ")
        linha = ""
        py    = y
        lh    = fonte_texto.get_height() + 5
        cor   = self._cor_texto()
        for p in palavras:
            t = linha + p + " "
            if fonte_texto.size(t)[0] <= lmax:
                linha = t
            else:
                if py + lh > y + hmax: break
                s = fonte_texto.render(linha.rstrip(), True, cor)
                s.set_alpha(alpha)
                surf.blit(s, (x, py))
                linha = p + " "
                py += lh
        if linha and py + lh <= y + hmax:
            s = fonte_texto.render(linha.rstrip(), True, cor)
            s.set_alpha(alpha)
            surf.blit(s, (x, py))


# ═══════════════════════════════════════════════════════════════
#  MENU DE ESCOLHAS
#  Teclado: 1/2/3/4/5   Mouse: clique esquerdo
# ═══════════════════════════════════════════════════════════════

class MenuEscolhas:
    ITEM_H   = 42
    MENU_L   = 900
    MARG_BTM = 24

    def __init__(self, opcoes):
        self.opcoes = opcoes
        self.hover  = -1

    def _rects(self):
        total = len(self.opcoes) * self.ITEM_H
        iy    = BASE_H - total - self.MARG_BTM
        cx    = (BASE_W - self.MENU_L) // 2
        return [pygame.Rect(cx, iy + i*self.ITEM_H, self.MENU_L, self.ITEM_H-4)
                for i in range(len(self.opcoes))]

    def atualizar_hover(self, pos_base):
        self.hover = -1
        for i, r in enumerate(self._rects()):
            if r.collidepoint(pos_base): self.hover = i

    def checar_clique(self, pos_base):
        for i, r in enumerate(self._rects()):
            if r.collidepoint(pos_base): return i
        return None

    def checar_teclado(self, tecla):
        """1→0, 2→1, 3→2, 4→3, 5→4"""
        return {pygame.K_1:0, pygame.K_2:1, pygame.K_3:2,
                pygame.K_4:3, pygame.K_5:4}.get(tecla)

    def desenhar(self, surf):
        tmp   = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)
        rects = self._rects()
        for i, (rect, opcao) in enumerate(zip(rects, self.opcoes)):
            bg = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            bg.fill((40,40,20,200) if i==self.hover else (0,0,0,160))
            tmp.blit(bg, (rect.x, rect.y))
            pygame.draw.rect(tmp, (*BORDA, 200), rect, 1)
            cor   = COR_OPCAO_HOVER if i==self.hover else COR_OPCAO_NORMAL
            label = f"[{i+1}]  {opcao}"
            s     = fonte_opcao.render(label, True, cor)
            tmp.blit(s, (rect.x+14, rect.y+(rect.h-s.get_height())//2))
        surf.blit(tmp, (0, 0))


# ═══════════════════════════════════════════════════════════════
#  ÁRVORE DE DIÁLOGOS
# ═══════════════════════════════════════════════════════════════

ARVORE = {
    "entrada": {
        "sprite": "sentado_com_taco",
        "falas": [
            ("Vinny", "..."),
            ("Vinny", "Oi.", 4),
            ("Vinny", "..."),
            ("Vinny", "Se você for alucinação...", 3),
            ("Vinny", "Tá bem convincente."),
        ],
        "proximo": "dialogo_1",
    },
    "dialogo_1": {
        "sprite": "confiante",
        "falas": [],
        "opcoes": [
            {"texto": "Esse quarto é seu?",         "delta_san": 0, "sprite": "confuso",    "proximo": "quarto_seu"},
            {"texto": "O que aconteceu aqui?",       "delta_san": 1, "sprite": "preocupado", "proximo": "o_que_aconteceu"},
            {"texto": "Você tá bem?",                "delta_san": 2, "sprite": "confiante",  "proximo": "voce_ta_bem"},
        ],
    },
    "quarto_seu": {
        "sprite": "confuso",
        "falas": [
            ("Vinny", "...Era."),
            ("Vinny", "Antes era arrumado."),
            ("Vinny", "Agora tá mais... sincero."),
            ("S/N",   "Você fez isso?"),
            ("Vinny", "...Fiz."),
            ("Vinny", "Parecia mais fácil bagunçar o quarto do que a cabeça."),
        ],
        "proximo": "dialogo_2",
    },
    "o_que_aconteceu": {
        "sprite": "preocupado",
        "falas": [
            ("Vinny", "Tempo demais sozinho."),
            ("Vinny", "Pensamento demais."),
            ("Vinny", "A parede virou meu bloco de notas."),
        ],
        "proximo": "dialogo_2",
    },
    "voce_ta_bem": {
        "sprite": "confiante",
        "falas": [
            ("Vinny", "...Tentando."),
            ("Vinny", "Ainda sei meu nome."),
            ("Vinny", "Então já é alguma coisa."),
        ],
        "proximo": "dialogo_2",
    },
    "dialogo_2": {
        "sprite": "confiante",
        "falas": [("S/N", "Você observa melhor o quarto...")],
        "opcoes": [
            {"texto": "O que são esses rabiscos?",                "delta_san": 3, "sprite": "confuso",    "proximo": "rabiscos"},
            {"texto": "Você ficou aqui sozinho esse tempo todo?",  "delta_san": 2, "sprite": "preocupado", "proximo": "sozinho"},
            {"texto": "Por que você tá com esse taco?",            "delta_san": 1, "sprite": "confiante",  "proximo": "por_que_taco"},
        ],
    },
    "rabiscos": {
        "sprite": "confuso",
        "falas": [
            ("Vinny", "Lembretes."),
            ("Vinny", "Ou avisos."),
            ("Vinny", "Ou surtos temporários."),
            ("Vinny", "Ainda não classifiquei tudo.", 3),
            ("Vinny", "No começo eu escrevia pra organizar pensamento."),
            ("Vinny", "Depois comecei a escrever pra não esquecer coisa estranha."),
            ("Vinny", "Tipo sons. Portas. Sonhos."),
            ("Vinny", "...Ou seja lá o que isso tudo é.", 4),
        ],
        "proximo": "dialogo_3",
    },
    "sozinho": {
        "sprite": "preocupado",
        "falas": [
            ("Vinny", "...Acho que sim."),
            ("Vinny", "Quer dizer—"),
            ("Vinny", "Sozinho sozinho... talvez."),
            ("Vinny", "Mas às vezes parecia que tinha coisa me observando."),
            ("Vinny", "Então escolhi a opção emocionalmente saudável:"),
            ("Vinny", "Fingir que não.", 4),
        ],
        "proximo": "dialogo_3",
    },
    "por_que_taco": {
        "sprite": "confiante",
        "falas": [
            ("Vinny", "Porque paranoia sem ferramenta vira só desvantagem."),
            ("Vinny", "Além disso..."),
            ("Vinny", "Se alguma coisa estranha entrar aqui..."),
            ("Vinny", "Prefiro parecer minimamente preparado."),
        ],
        "proximo": "dialogo_3",
    },
    "dialogo_3": {
        "sprite": "confiante",
        "falas": [],
        "opcoes": [
            {"texto": "Você tentou sair?",             "delta_san": 5, "sprite": "preocupado", "proximo": "tentou_sair"},
            {"texto": "Encontrou alguém além de mim?", "delta_san": 4, "sprite": "surpreso",   "proximo": "encontrou_alguem"},
            {"texto": "E aquele negócio na parede?",   "delta_san": 0, "sprite": "confuso",    "proximo": "negocio_parede"},
        ],
    },
    "tentou_sair": {
        "sprite": "preocupado",
        "falas": [
            ("Vinny", "Tentei."),
            ("Vinny", "Corredor."),
            ("Vinny", "Mais corredor."),
            ("Vinny", "Mais corredor."),
            ("Vinny", "Depois decidi que explorar sem plano talvez fosse só uma forma mais demorada de enlouquecer.", 3),
            ("Vinny", "Então voltei."),
            ("Vinny", "Aqui era horrível..."),
            ("Vinny", "Mas era meu horrível.", 4),
        ],
        "proximo": "dialogo_4",
    },
    "encontrou_alguem": {
        "sprite": "surpreso",
        "falas": [
            ("Vinny", "...Não exatamente."),
            ("Vinny", "Já ouvi coisa."),
            ("Vinny", "Passo. Barulho. Voz."),
            ("Vinny", "Mas honestamente?"),
            ("Vinny", "Nesse lugar, ouvir nem sempre significa encontrar.", 3),
            ("Vinny", "Então eu só... evitei descobrir."),
        ],
        "proximo": "dialogo_4",
    },
    "negocio_parede": {
        "sprite": "confuso",
        "falas": [
            ("Vinny", "...Ah, aquilo."),
            ("Vinny", "Vi."),
            ("Vinny", "Mas tenho uma regra bem sólida:"),
            ("Vinny", "Se parece problema..."),
            ("Vinny", "Eu não cutuco.", 3),
            ("Vinny", "Já tenho caos suficiente sem apertar botão misterioso."),
        ],
        "proximo": "dialogo_4",
    },
    "dialogo_4": {
        "sprite": "confiante",
        "falas": [],
        "opcoes": [
            {"texto": "Que taco é esse?",     "delta_san": 1, "sprite": "confiante", "proximo": "que_taco"},
            {"texto": "Isso é uma arma?",     "delta_san": 2, "sprite": "surpreso",  "proximo": "e_arma"},
            {"texto": "Você dorme com isso?", "delta_san": 3, "sprite": "confuso",   "proximo": "dorme_com_isso"},
        ],
    },
    "que_taco": {
        "sprite": "confiante",
        "falas": [("Vinny", "...TACORAME."), ("Vinny", "Não julga.")],
        "proximo": "dialogo_5",
    },
    "e_arma": {
        "sprite": "surpreso",
        "falas": [("Vinny", "...Prefiro 'apoio emocional'.")],
        "proximo": "dialogo_5",
    },
    "dorme_com_isso": {
        "sprite": "confuso",
        "falas": [("Vinny", "...Talvez."), ("Vinny", "Não me orgulho.")],
        "proximo": "dialogo_5",
    },
    "dialogo_5": {
        "sprite": "confiante",
        "falas": [
            ("Vinny", "..."),
            ("Vinny", "Tá.", 4),
            ("Vinny", "Cê parece mais preparado que eu."),
            ("Vinny", "Ou mais doido."),
            ("Vinny", "De qualquer forma..."),
            ("Vinny", "Fica com isso.", 3),
        ],
        "acao": "entregar_taco",
        "proximo": "dialogo_5b",
    },
    "dialogo_5b": {
        "sprite": "entregando_taco",
        "falas": [
            ("S/N",   "O TACORAME?"),
            ("Vinny", "É."),
            ("Vinny", "Se encontrar coisa estranha..."),
            ("Vinny", "Melhor ter do que não ter."),
            ("S/N",   "(TACORAME adquirido.)"),
            ("Vinny", "Só tenta não morrer com meu taco."),
        ],
        "proximo": "dialogo_6",
    },
    "dialogo_6": {
        "sprite": "sentado_sem_taco",
        "falas": [
            ("S/N", "Sem o TACORAME..."),
            ("S/N", "Vinny parece meio estranho."),
            ("S/N", "Mas também... um pouco mais leve."),
        ],
        "proximo": "dialogo_7",
    },
    "dialogo_7": {
        "sprite": "sentado_sem_taco",
        "falas": [
            ("Vinny", "Ei..."),
            ("Vinny", "Cuida bem dele."),
            ("Vinny", "...Tenho apego emocional."),
        ],
        "acao": "fim",
    },
}


# ═══════════════════════════════════════════════════════════════
#  CONTROLADOR DA CENA
# ═══════════════════════════════════════════════════════════════

class CenaVinny:
    def __init__(self):
        self.sprite_mgr      = GerenciadorSprite()
        self.no_atual_key    = "entrada"
        self.no_atual        = ARVORE["entrada"]
        self.indice_fala     = 0
        self.caixa           = None
        self.menu            = None
        self.saindo          = False
        self.offset_saida    = 0
        self.alpha_saida     = 255
        self.encerrada       = False
        self.tacorame_obtido = False
        self.delta_san_total = 0

        self.aguardando_clique = True
        self.hover_vinny       = False

        self.som_ambiente = carregar_som("ambiente")
        if self.som_ambiente:
            self.som_ambiente.play(-1)

    # ── Nó ────────────────────────────────────────────────────

    def _iniciar_no(self, chave):
        self.no_atual_key = chave
        self.no_atual     = ARVORE[chave]
        self.indice_fala  = 0
        self.menu         = None
        self.sprite_mgr.set_sprite(self.no_atual.get("sprite", "sentado_com_taco"))

        falas = self.no_atual.get("falas", [])
        if falas:
            self.caixa = CaixaDialogo(*falas[0])
            self._checar_revelacao(falas[0])
        else:
            self.caixa = None
            self._abrir_menu()

    def _checar_revelacao(self, fala):
        if fala[0] == "Vinny" and fala[1].strip() == "Oi.":
            revelar_nome_vinny()

    # ── Avanço ────────────────────────────────────────────────

    def _avancar(self):
        if self.caixa and not self.caixa.completo:
            self.caixa.pular()
            return

        falas = self.no_atual.get("falas", [])
        self.indice_fala += 1

        if self.indice_fala < len(falas):
            fala = falas[self.indice_fala]
            self.caixa = CaixaDialogo(*fala)
            self._checar_revelacao(fala)
            return

        acao = self.no_atual.get("acao")
        if acao == "entregar_taco":
            self.tacorame_obtido = True
            som = carregar_som("entrega_taco")
            if som: som.play()

        if self.no_atual.get("opcoes"):
            self.caixa = None
            self._abrir_menu()
        elif "proximo" in self.no_atual:
            self._iniciar_no(self.no_atual["proximo"])
        elif acao == "fim":
            self.saindo = True
            if self.som_ambiente: self.som_ambiente.stop()

    def _abrir_menu(self):
        ops = self.no_atual.get("opcoes", [])
        if ops:
            self.menu = MenuEscolhas([op["texto"] for op in ops])

    def _escolher_opcao(self, idx):
        ops = self.no_atual.get("opcoes", [])
        if idx >= len(ops): return
        op = ops[idx]
        self.delta_san_total += op.get("delta_san", 0)
        if op.get("sprite"): self.sprite_mgr.set_sprite(op["sprite"])
        self.menu = None
        self._iniciar_no(op["proximo"])

    # ── Eventos ───────────────────────────────────────────────

    def processar_evento(self, evento):
        if self.encerrada or self.saindo:
            return

        # Converte mouse para coordenadas base
        pos_base = mouse_em_base()

        # ── Tela de espera ────────────────────────────────────
        if self.aguardando_clique:
            if evento.type == pygame.MOUSEMOTION:
                self.hover_vinny = HITBOX_VINNY.collidepoint(pos_base)
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if HITBOX_VINNY.collidepoint(pos_base):
                    self.aguardando_clique = False
                    self._iniciar_no("entrada")
            return

        # ── Diálogo ───────────────────────────────────────────
        if evento.type == pygame.MOUSEMOTION and self.menu:
            self.menu.atualizar_hover(pos_base)

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.menu:
                idx = self.menu.checar_clique(pos_base)
                if idx is not None: self._escolher_opcao(idx)
            else:
                self._avancar()

        if evento.type == pygame.KEYDOWN:
            if self.menu:
                # ★ Teclas 1-5 selecionam opções diretamente
                idx = self.menu.checar_teclado(evento.key)
                if idx is not None:
                    self._escolher_opcao(idx)
            elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._avancar()

    # ── Atualização ───────────────────────────────────────────

    def atualizar(self):
        if self.caixa and not self.encerrada and not self.aguardando_clique:
            self.caixa.atualizar()
        if self.saindo:
            self.offset_saida += 10
            self.alpha_saida   = max(0, self.alpha_saida - 12)
            if self.alpha_saida <= 0 or self.offset_saida >= 250:
                self.encerrada = True
                self.saindo    = False

    # ── Desenho (tudo em render_surf/BASE coords) ─────────────

    def desenhar(self, surf):
        self.sprite_mgr.desenhar(surf)

        if self.aguardando_clique:
            self._desenhar_hint(surf)
            return

        if not self.encerrada:
            alpha = self.alpha_saida if self.saindo else 255
            if self.caixa:
                self.caixa.desenhar(surf, offset_y=self.offset_saida, alpha=alpha)
            if self.menu:
                self.menu.desenhar(surf)

    def _desenhar_hint(self, surf):
        t = pygame.time.get_ticks()
        if self.hover_vinny:
            pulso = int(120 + 100 * math.sin(t / 250))

            # Leve overlay dourado sobre a hitbox
            ov = pygame.Surface((HITBOX_VINNY.w, HITBOX_VINNY.h), pygame.SRCALPHA)
            ov.fill((255, 210, 80, 25))
            surf.blit(ov, (HITBOX_VINNY.x, HITBOX_VINNY.y))

            # Contorno pulsante
            bd = pygame.Surface((HITBOX_VINNY.w, HITBOX_VINNY.h), pygame.SRCALPHA)
            pygame.draw.rect(bd, (255, 210, 80, pulso),
                             (0, 0, HITBOX_VINNY.w, HITBOX_VINNY.h), 2)
            surf.blit(bd, (HITBOX_VINNY.x, HITBOX_VINNY.y))

            # Texto hint
            hint = fonte_hint.render("[ Interagir ]", True, (255, 210, 80))
            hint.set_alpha(pulso)
            surf.blit(hint, (HITBOX_VINNY.centerx - hint.get_width()//2,
                              HITBOX_VINNY.bottom + 8))

        # Descomente para ver a hitbox em vermelho (debug):
        # pygame.draw.rect(surf, (255, 0, 0), HITBOX_VINNY, 2)


# ═══════════════════════════════════════════════════════════════
#  LOOP PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def main():
    cena = CenaVinny()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F11:
                    toggle_fullscreen()
                elif evento.key == pygame.K_ESCAPE:
                    if fullscreen:
                        toggle_fullscreen()
                    else:
                        pygame.quit(); sys.exit()

            if cena.encerrada and evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    print(f"[INFO] Cena Vinny encerrada.")
                    print(f"       TACORAME obtido : {cena.tacorame_obtido}")
                    print(f"       delta_san_total : {cena.delta_san_total}")
                    pygame.quit(); sys.exit()

            cena.processar_evento(evento)

        cena.atualizar()

        # Renderiza tudo na surface base (1280×720)
        render_surf.fill((0, 0, 0))
        cena.desenhar(render_surf)

        # Escala para a tela real (funciona em fullscreen qualquer resolução)
        blit_scaled(tela, render_surf)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
