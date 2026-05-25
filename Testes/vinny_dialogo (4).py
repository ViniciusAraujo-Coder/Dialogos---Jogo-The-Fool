import pygame
import sys
import os

# ═══════════════════════════════════════════════════════════════
#  CENA DE DIÁLOGO — VINNY (The Fool)
#  Universidade São Judas Tadeu
#
#  ★ = seções que você pode editar
# ═══════════════════════════════════════════════════════════════

pygame.init()
pygame.mixer.init()

# ★ Configuração da janela
LARGURA, ALTURA = 1050, 600
FPS             = 60

tela  = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("The Fool — Vinny")
clock = pygame.time.Clock()

# Cores
COR_NOME         = (255, 255, 255)
COR_TEXTO        = (220, 220, 220)
COR_OPCAO_NORMAL = (180, 180, 180)
COR_OPCAO_HOVER  = (255, 255, 180)
BORDA            = (200, 200, 200)

# Fontes
fonte_nome  = pygame.font.SysFont("Courier New", 22, bold=True)
fonte_texto = pygame.font.SysFont("Courier New", 26)
fonte_opcao = pygame.font.SysFont("Courier New", 22)
fonte_dica  = pygame.font.SysFont("Courier New", 16)

# ═══════════════════════════════════════════════════════════════
#  ★ PARTE 1 — CAMINHOS DE ASSETS
#
#  Imagens → pasta  imgs_vinny/
#  Sons    → pasta  sons_vinny/  (quando tiver)
# ═══════════════════════════════════════════════════════════════

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))

def caminho(subpasta, nome_arquivo):
    return os.path.join(PASTA_BASE, subpasta, nome_arquivo)

# Sprites do Vinny
SPRITES = {
    "sentado_com_taco":  caminho("imgs_vinny", "Sentado_com_taco.png"),
    "sentado_sem_taco":  caminho("imgs_vinny", "Sentado_sem_taco.png"),
    "surpreso":          caminho("imgs_vinny", "Vini_Surpreso.png"),
    "confiante":         caminho("imgs_vinny", "Vini_Confiante.png"),
    "confuso":           caminho("imgs_vinny", "Vini_Confuso.png"),
    "preocupado":        caminho("imgs_vinny", "Vini_Preocupado.png"),
    "entregando_taco":   caminho("imgs_vinny", "Vini_Entregando_Taco.png"),
}

# ── ★ Sons ───────────────────────────────────────────────────
#  Coloque os arquivos em:  sons_vinny/
#  Nomes esperados (renomeie à vontade, só ajuste aqui):
#    ambiente_quarto.mp3  → toca em loop durante toda a cena
#    entrega_taco.mp3     → toca no momento que o taco é entregue
#    muda_humor.mp3       → toca ao trocar para surpreso/preocupado
SONS = {
    "ambiente":     caminho("sons_vinny", "ambiente_quarto.mp3"),
    "entrega_taco": caminho("sons_vinny", "entrega_taco.mp3"),
    "muda_humor":   caminho("sons_vinny", "muda_humor.mp3"),
}

# ── ★ Volume de cada som (0.0 = mudo, 1.0 = máximo) ─────────
VOLUME = {
    "ambiente":     0.2,
    "entrega_taco": 0.8,
    "muda_humor":   0.5,
}

def carregar_som(chave):
    """Carrega um som com segurança. Retorna None se o arquivo nao existir."""
    try:
        som = pygame.mixer.Sound(SONS[chave])
        som.set_volume(VOLUME[chave])
        return som
    except FileNotFoundError:
        print(f"[AVISO] Som nao encontrado: {SONS[chave]}")
        return None


# ═══════════════════════════════════════════════════════════════
#  GERENCIADOR DE SPRITES
#  Carrega cada imagem escalada para preencher a tela inteira.
# ═══════════════════════════════════════════════════════════════

class GerenciadorSprite:
    """
    Chaves válidas: 'sentado_com_taco', 'sentado_sem_taco',
                    'surpreso', 'confiante', 'confuso',
                    'preocupado', 'entregando_taco'
    """

    def __init__(self):
        self.sprites     = {}
        self.atual       = None
        self.chave_atual = None
        self._carregar()

    def _carregar(self):
        for chave, path in SPRITES.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                # Escala para preencher a tela inteira
                img = pygame.transform.smoothscale(img, (LARGURA, ALTURA))
                self.sprites[chave] = img
            except FileNotFoundError:
                print(f"[AVISO] Imagem não encontrada: {path}")
                placeholder = pygame.Surface((LARGURA, ALTURA))
                placeholder.fill((20, 20, 30))
                self.sprites[chave] = placeholder

        self.set_sprite("sentado_com_taco")

    def set_sprite(self, chave):
        if chave in self.sprites and chave != self.chave_atual:
            self.atual       = self.sprites[chave]
            self.chave_atual = chave
            # Toca som ao mudar para uma emoção intensa
            if chave in ("surpreso", "preocupado"):
                som = carregar_som("muda_humor")
                if som:
                    som.play()

    def desenhar(self, superficie):
        if self.atual:
            superficie.blit(self.atual, (0, 0))


# ═══════════════════════════════════════════════════════════════
#  CAIXA DE DIÁLOGO — centralizada na parte inferior da tela
# ═══════════════════════════════════════════════════════════════

class CaixaDialogo:
    VELOCIDADE_PADRAO = 2

    # Dimensões da caixa (editável ★)
    CAIXA_LARGURA  = 900
    CAIXA_ALTURA   = 160
    MARGEM_BOTTOM  = 24
    PADDING        = 18

    def __init__(self, nome, texto, velocidade=None):
        self.nome          = nome
        self.texto         = texto
        self.velocidade    = velocidade if velocidade is not None else self.VELOCIDADE_PADRAO
        self.texto_visivel = ""
        self.indice        = 0
        self.contador      = 0
        self.completo      = False

    def atualizar(self):
        if self.completo:
            return
        self.contador += 1
        if self.contador >= self.velocidade:
            self.contador = 0
            if self.indice < len(self.texto):
                self.texto_visivel += self.texto[self.indice]
                self.indice        += 1
            else:
                self.completo = True

    def pular(self):
        self.texto_visivel = self.texto
        self.indice        = len(self.texto)
        self.completo      = True

    def desenhar(self, superficie, offset_y=0, alpha=255):
        cw = self.CAIXA_LARGURA
        ch = self.CAIXA_ALTURA
        cx = (LARGURA - cw) // 2
        cy = ALTURA - ch - self.MARGEM_BOTTOM + offset_y
        p  = self.PADDING

        temp = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

        # Fundo semitransparente
        alpha_fundo = int(180 * alpha / 255)
        fundo = pygame.Surface((cw, ch), pygame.SRCALPHA)
        fundo.fill((0, 0, 0, alpha_fundo))
        temp.blit(fundo, (cx, cy))

        # Borda
        cor_borda = (*BORDA, alpha)
        pygame.draw.rect(temp, cor_borda, (cx, cy, cw, ch), 2)

        # Caixinha do nome
        nome_surf = fonte_nome.render(self.nome, True, COR_NOME)
        nb_w = nome_surf.get_width() + 20
        nb_h = nome_surf.get_height() + 8
        nx   = cx
        ny   = cy - nb_h - 2

        nb = pygame.Surface((nb_w, nb_h), pygame.SRCALPHA)
        nb.fill((0, 0, 0, alpha_fundo))
        temp.blit(nb, (nx, ny))
        pygame.draw.rect(temp, cor_borda, (nx, ny, nb_w, nb_h), 2)

        nome_a = pygame.Surface(nome_surf.get_size(), pygame.SRCALPHA)
        nome_a.blit(nome_surf, (0, 0))
        nome_a.set_alpha(alpha)
        temp.blit(nome_a, (nx + 10, ny + 4))

        # Texto com quebra de linha
        self._desenhar_texto(
            temp,
            self.texto_visivel,
            x          = cx + p,
            y          = cy + p,
            largura_max= cw - p * 2,
            altura_max = ch - p * 2,
            alpha      = alpha
        )

        # Indicador ▼ piscante
        if self.completo and alpha == 255:
            if (pygame.time.get_ticks() // 500) % 2:
                dica = fonte_dica.render("▼", True, BORDA)
                temp.blit(dica, (cx + cw - dica.get_width() - p,
                                 cy + ch - dica.get_height() - 8))

        superficie.blit(temp, (0, 0))

    def _desenhar_texto(self, superficie, texto, x, y, largura_max, altura_max, alpha=255):
        palavras     = texto.split(" ")
        linha_atual  = ""
        pos_y        = y
        altura_linha = fonte_texto.get_height() + 5

        for palavra in palavras:
            teste = linha_atual + palavra + " "
            if fonte_texto.size(teste)[0] <= largura_max:
                linha_atual = teste
            else:
                if pos_y + altura_linha > y + altura_max:
                    break
                surf = fonte_texto.render(linha_atual.rstrip(), True, COR_TEXTO)
                surf.set_alpha(alpha)
                superficie.blit(surf, (x, pos_y))
                linha_atual = palavra + " "
                pos_y      += altura_linha

        if linha_atual and pos_y + altura_linha <= y + altura_max:
            surf = fonte_texto.render(linha_atual.rstrip(), True, COR_TEXTO)
            surf.set_alpha(alpha)
            superficie.blit(surf, (x, pos_y))


# ═══════════════════════════════════════════════════════════════
#  MENU DE ESCOLHAS — centralizado na parte inferior da tela
# ═══════════════════════════════════════════════════════════════

class MenuEscolhas:
    """
    Exibe até 3 opções. Clique ou tecle 1/2/3 para escolher.
    """

    ITEM_ALTURA  = 42
    MENU_LARGURA = 900
    MARGEM_BTM   = 24

    def __init__(self, opcoes):
        self.opcoes = opcoes
        self.hover  = -1

    def atualizar_hover(self, pos_mouse):
        self.hover = -1
        for i, rect in enumerate(self._rects()):
            if rect.collidepoint(pos_mouse):
                self.hover = i

    def checar_clique(self, pos_mouse):
        for i, rect in enumerate(self._rects()):
            if rect.collidepoint(pos_mouse):
                return i
        return None

    def checar_teclado(self, tecla):
        return {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}.get(tecla)

    def _rects(self):
        total_h = len(self.opcoes) * self.ITEM_ALTURA
        inicio_y = ALTURA - total_h - self.MARGEM_BTM
        cx = (LARGURA - self.MENU_LARGURA) // 2
        return [
            pygame.Rect(cx, inicio_y + i * self.ITEM_ALTURA,
                        self.MENU_LARGURA, self.ITEM_ALTURA - 4)
            for i in range(len(self.opcoes))
        ]

    def desenhar(self, superficie):
        temp  = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        rects = self._rects()

        for i, (rect, opcao) in enumerate(zip(rects, self.opcoes)):
            cor_bg = (40, 40, 20, 200) if i == self.hover else (0, 0, 0, 160)
            bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            bg.fill(cor_bg)
            temp.blit(bg, (rect.x, rect.y))
            pygame.draw.rect(temp, (*BORDA, 200), rect, 1)

            cor   = COR_OPCAO_HOVER if i == self.hover else COR_OPCAO_NORMAL
            label = f"[{i+1}]  {opcao}"
            surf  = fonte_opcao.render(label, True, cor)
            temp.blit(surf, (rect.x + 14,
                              rect.y + (rect.height - surf.get_height()) // 2))

        superficie.blit(temp, (0, 0))


# ═══════════════════════════════════════════════════════════════
#  ★ PARTE 2 — ÁRVORE DE DIÁLOGOS DO VINNY
#
#  Cada nó tem:
#    "sprite"  → chave da imagem do Vinny nesse momento
#    "falas"   → lista de (nome, texto) ou (nome, texto, velocidade)
#    "opcoes"  → lista de opções (se houver escolha do jogador)
#    "proximo" → chave do próximo nó (quando não há opções)
#    "acao"    → ação especial: "entregar_taco" ou "fim"
#
#  Cada opção tem:
#    "texto"    → texto exibido no menu
#    "delta_san"→ valor de sanidade a modificar (+ ou -).
#                 ★ Conecte ao sistema de sanidade do grupo aqui.
#    "sprite"   → sprite do Vinny ao escolher (opcional)
#    "proximo"  → próximo nó
# ═══════════════════════════════════════════════════════════════

ARVORE = {

    # ── Entrada — Vinny nota o jogador ───────────────────────
    # Sentado com o taco ao ser encontrado, surpreso nas primeiras falas
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

    # ── Diálogo 1 — idle = confiante (espera da escolha) ─────
    "dialogo_1": {
        "sprite": "confiante",
        "falas": [],
        "opcoes": [
            {"texto": "Esse quarto é seu?",          "delta_san":  0, "sprite": "confuso",     "proximo": "quarto_seu"},
            {"texto": "O que aconteceu aqui?",        "delta_san":  1, "sprite": "preocupado",  "proximo": "o_que_aconteceu"},
            {"texto": "Você tá bem?",                 "delta_san":  2, "sprite": "confiante",   "proximo": "voce_ta_bem"},
        ],
    },

    # "Era meu quarto" — confuso/melancólico, depois confiante ao defender a bagunça
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

    # "O que aconteceu" — preocupado ao falar sobre o isolamento
    "o_que_aconteceu": {
        "sprite": "preocupado",
        "falas": [
            ("Vinny", "Tempo demais sozinho."),
            ("Vinny", "Pensamento demais."),
            ("Vinny", "A parede virou meu bloco de notas."),
        ],
        "proximo": "dialogo_2",
    },

    # "Você tá bem" — confiante ao dizer que ainda sabe o nome
    "voce_ta_bem": {
        "sprite": "confiante",
        "falas": [
            ("Vinny", "...Tentando."),
            ("Vinny", "Ainda sei meu nome."),
            ("Vinny", "Então já é alguma coisa."),
        ],
        "proximo": "dialogo_2",
    },

    # ── Diálogo 2 — idle = confiante ─────────────────────────
    "dialogo_2": {
        "sprite": "confiante",
        "falas": [
            ("S/N", "Você observa melhor o quarto..."),
        ],
        "opcoes": [
            {"texto": "O que são esses rabiscos?",               "delta_san":  3, "sprite": "confuso",    "proximo": "rabiscos"},
            {"texto": "Você ficou aqui sozinho esse tempo todo?", "delta_san":  2, "sprite": "preocupado", "proximo": "sozinho"},
            {"texto": "Por que você tá com esse taco?",           "delta_san":  1, "sprite": "confiante",  "proximo": "por_que_taco"},
        ],
    },

    # "Rabiscos" — confuso ao tentar explicar o que escreveu
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

    # "Sozinho" — preocupado ao admitir que algo o observava
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

    # "Por que o taco" — confiante, defende o taco com orgulho
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

    # ── Diálogo 3 — idle = confiante ─────────────────────────
    "dialogo_3": {
        "sprite": "confiante",
        "falas": [],
        "opcoes": [
            {"texto": "Você tentou sair?",             "delta_san":  5, "sprite": "preocupado", "proximo": "tentou_sair"},
            {"texto": "Encontrou alguém além de mim?", "delta_san":  4, "sprite": "surpreso",   "proximo": "encontrou_alguem"},
            {"texto": "E aquele negócio na parede?",   "delta_san":  0, "sprite": "confuso",    "proximo": "negocio_parede"},
        ],
    },

    # "Tentou sair" — preocupado ao relembrar os corredores sem fim
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

    # "Encontrou alguém" — surpreso ao lembrar das vozes/passos
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

    # "Negócio na parede" — confuso mas deliberadamente ignorando
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

    # ── Diálogo 4 — sobre o taco, idle = confiante ───────────
    "dialogo_4": {
        "sprite": "confiante",
        "falas": [],
        "opcoes": [
            {"texto": "Que taco é esse?",     "delta_san":  1, "sprite": "confiante",  "proximo": "que_taco"},
            {"texto": "Isso é uma arma?",     "delta_san":  2, "sprite": "surpreso",   "proximo": "e_arma"},
            {"texto": "Você dorme com isso?", "delta_san":  3, "sprite": "confuso",    "proximo": "dorme_com_isso"},
        ],
    },

    # "Que taco" — confiante, orgulhoso do TACORAME
    "que_taco": {
        "sprite": "confiante",
        "falas": [
            ("Vinny", "...TACORAME."),
            ("Vinny", "Não julga."),
        ],
        "proximo": "dialogo_5",
    },

    # "É uma arma?" — surpreso com a pergunta direta
    "e_arma": {
        "sprite": "surpreso",
        "falas": [
            ("Vinny", "...Prefiro 'apoio emocional'."),
        ],
        "proximo": "dialogo_5",
    },

    # "Dorme com isso?" — confuso, um pouco envergonhado
    "dorme_com_isso": {
        "sprite": "confuso",
        "falas": [
            ("Vinny", "...Talvez."),
            ("Vinny", "Não me orgulho."),
        ],
        "proximo": "dialogo_5",
    },

    # ── Diálogo 5 — entrega do TACORAME ──────────────────────
    # Confiante ao decidir entregar, entregando_taco no momento da entrega
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
        "acao":   "entregar_taco",
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

    # ── Diálogo 6 — depois da entrega ────────────────────────
    "dialogo_6": {
        "sprite": "sentado_sem_taco",
        "falas": [
            ("S/N", "Sem o TACORAME..."),
            ("S/N", "Vinny parece meio estranho."),
            ("S/N", "Mas também... um pouco mais leve."),
        ],
        "proximo": "dialogo_7",
    },

    # ── Diálogo 7 — idle final ────────────────────────────────
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
    """
    Gerencia o fluxo completo da cena.

    Após encerrar:
      self.encerrada      → True
      self.tacorame_obtido → True/False
      self.delta_san_total → soma de todos os delta_san das escolhas feitas.
                             Repasse esse valor ao sistema de sanidade do grupo.
    """

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

        # ★ Variável de sanidade — acumula os delta_san de cada escolha.
        #   Ao final da cena, passe self.delta_san_total para o sistema
        #   de sanidade do restante do jogo.
        self.delta_san_total = 0

        self._iniciar_no("entrada")

        # Som ambiente — toca em loop durante toda a cena
        self.som_ambiente = carregar_som("ambiente")
        if self.som_ambiente:
            self.som_ambiente.play(-1)  # -1 = loop infinito

    # ── Inicialização de nó ───────────────────────────────────

    def _iniciar_no(self, chave):
        self.no_atual_key = chave
        self.no_atual     = ARVORE[chave]
        self.indice_fala  = 0
        self.menu         = None

        self.sprite_mgr.set_sprite(self.no_atual.get("sprite", "sentado_com_taco"))

        falas = self.no_atual.get("falas", [])
        if falas:
            self.caixa = CaixaDialogo(*falas[0])
        else:
            self.caixa = None
            self._abrir_menu()

    # ── Avanço de fala ────────────────────────────────────────

    def _avancar(self):
        # Se ainda está digitando, pula para o fim
        if self.caixa and not self.caixa.completo:
            self.caixa.pular()
            return

        falas = self.no_atual.get("falas", [])
        self.indice_fala += 1

        if self.indice_fala < len(falas):
            self.caixa = CaixaDialogo(*falas[self.indice_fala])
            return

        # Acabaram as falas — trata ação e avança
        acao = self.no_atual.get("acao")

        if acao == "entregar_taco":
            self.tacorame_obtido = True
            som = carregar_som("entrega_taco")
            if som:
                som.play()

        if self.no_atual.get("opcoes"):
            self.caixa = None
            self._abrir_menu()
        elif "proximo" in self.no_atual:
            self._iniciar_no(self.no_atual["proximo"])
        elif acao == "fim":
            self.saindo = True
            # Para o som ambiente ao encerrar a cena
            if self.som_ambiente:
                self.som_ambiente.stop()

    def _abrir_menu(self):
        opcoes = self.no_atual.get("opcoes", [])
        if opcoes:
            self.menu = MenuEscolhas([op["texto"] for op in opcoes])

    def _escolher_opcao(self, indice):
        opcoes = self.no_atual.get("opcoes", [])
        if indice >= len(opcoes):
            return
        opcao = opcoes[indice]

        # ★ Acumula o delta de sanidade da escolha feita
        self.delta_san_total += opcao.get("delta_san", 0)

        sprite = opcao.get("sprite")
        if sprite:
            self.sprite_mgr.set_sprite(sprite)

        self.menu = None
        self._iniciar_no(opcao["proximo"])

    # ── Eventos ───────────────────────────────────────────────

    def processar_evento(self, evento):
        if self.encerrada or self.saindo:
            return

        if evento.type == pygame.MOUSEMOTION and self.menu:
            self.menu.atualizar_hover(evento.pos)

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.menu:
                idx = self.menu.checar_clique(evento.pos)
                if idx is not None:
                    self._escolher_opcao(idx)
            else:
                self._avancar()

        if evento.type == pygame.KEYDOWN:
            if self.menu:
                idx = self.menu.checar_teclado(evento.key)
                if idx is not None:
                    self._escolher_opcao(idx)
            elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._avancar()

    # ── Atualização por frame ─────────────────────────────────

    def atualizar(self):
        if self.caixa and not self.encerrada:
            self.caixa.atualizar()

        if self.saindo:
            self.offset_saida += 10
            self.alpha_saida   = max(0, self.alpha_saida - 12)
            if self.alpha_saida <= 0 or self.offset_saida >= 250:
                self.encerrada = True
                self.saindo    = False

    # ── Desenho ───────────────────────────────────────────────

    def desenhar(self, superficie):
        # Sprite ocupa a tela inteira
        self.sprite_mgr.desenhar(superficie)

        if not self.encerrada:
            alpha = self.alpha_saida if self.saindo else 255
            if self.caixa:
                self.caixa.desenhar(superficie, offset_y=self.offset_saida, alpha=alpha)
            if self.menu:
                self.menu.desenhar(superficie)


# ═══════════════════════════════════════════════════════════════
#  LOOP PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def main():
    cena = CenaVinny()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # Após encerrar, ENTER fecha / conecta próxima cena
            if cena.encerrada and evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    # ★ Aqui: repasse cena.delta_san_total ao sistema de
                    #   sanidade do grupo e inicie a próxima cena.
                    print(f"[INFO] Cena Vinny encerrada.")
                    print(f"       TACORAME obtido : {cena.tacorame_obtido}")
                    print(f"       delta_san_total : {cena.delta_san_total}")
                    pygame.quit()
                    sys.exit()

            cena.processar_evento(evento)

        cena.atualizar()
        cena.desenhar(tela)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
